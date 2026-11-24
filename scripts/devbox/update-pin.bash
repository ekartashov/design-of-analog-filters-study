#!/usr/bin/env bash
set -Eeuo pipefail

INI="./distrobox.ini"
ONLY_NAME=""
DRY_RUN=0
NO_RECREATE=0

# Build inputs (overrides; if not set, script can also read comment directives in distrobox.ini)
DEFAULT_CONTAINERFILE=""
DEFAULT_CONTEXT=""

# Build behaviour
PULL_POLICY="${PULL_POLICY:-always}"   # podman build --pull=always|missing|never
NO_BUILD=0

DEBUG=0
SAFE_PATH="${SAFE_PATH:-/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}"

usage() {
  cat <<'EOF'
Usage:
  scripts/devbox/update-pin.bash [options]

Options:
  -f, --file FILE           Path to distrobox.ini (default: ./distrobox.ini)
  -n, --name SECTION        Only update this [SECTION]
      --containerfile PATH  Containerfile to build for the selected section(s)
      --context DIR         Build context dir (default: directory of containerfile)
      --dry-run             Print planned changes only
      --no-build            If containerfile is set, skip building; only repin from existing local image
      --no-recreate         Do not run 'distrobox assemble create --replace' after updating
      --debug               Verbose diagnostics
  -h, --help                Show help

Notes:
- If --containerfile/--context are not provided, the script will also accept per-section
  comment directives in distrobox.ini:
      # containerfile=./scripts/devbox/Containerfile.latex
      # build_context=.

Env:
  PULL_POLICY=always|missing|never   (default: always)
  SAFE_PATH=...
EOF
}

die(){ printf 'error: %s\n' "$*" >&2; exit 1; }
info(){ printf 'info:  %s\n' "$*" >&2; }
dbg(){ ((DEBUG)) && printf 'debug: %s\n' "$*" >&2 || true; }

trim() {
  local s="$1"
  s="${s#"${s%%[!$' \t\r\n']*}"}"
  s="${s%"${s##*[!$' \t\r\n']}"}"
  printf '%s' "$s"
}

strip_bom_cr() {
  local s="$1"
  s="${s#$'\ufeff'}"
  s="${s%$'\r'}"
  printf '%s' "$s"
}

# --- host-exec shim ---
HOSTX=""
if command -v distrobox-host-exec >/dev/null 2>&1; then
  if distrobox-host-exec true >/dev/null 2>&1; then
    HOSTX="distrobox-host-exec"
  fi
fi

xrun() {
  if [[ -n "$HOSTX" ]]; then
    "$HOSTX" env PATH="$SAFE_PATH" "$@"
  else
    env PATH="$SAFE_PATH" "$@"
  fi
}

# IMPORTANT: no login shell, no rc files (avoids pyenv spew)
xsh() {
  local cmd="$1"
  if [[ -n "$HOSTX" ]]; then
    "$HOSTX" env PATH="$SAFE_PATH" bash --noprofile --norc -c "$cmd"
  else
    env PATH="$SAFE_PATH" bash --noprofile --norc -c "$cmd"
  fi
}

have() { xsh "command -v $(printf %q "$1") >/dev/null 2>&1"; }

need_podman() {
  have podman || die "podman not found on host (SAFE_PATH=$SAFE_PATH)"
}

podman_digest() {
  local image_ref="$1"
  local d
  d="$(xrun podman image inspect --format '{{.Digest}}' "$image_ref" 2>/dev/null || true)"
  d="$(trim "$d")"
  [[ "$d" == sha256:* ]] || return 1
  printf '%s' "$d"
}

podman_build() {
  local containerfile="$1"
  local context_dir="$2"
  local tag="$3"

  need_podman
  [[ -f "$containerfile" ]] || die "containerfile not found: $containerfile"
  [[ -d "$context_dir" ]] || die "build context dir not found: $context_dir"

  info "Building $tag (pull policy: $PULL_POLICY) from $containerfile (context: $context_dir)"
  xrun podman build \
    --pull="$PULL_POLICY" \
    -f "$containerfile" \
    -t "$tag" \
    "$context_dir"
}

# --- args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--file) INI="$2"; shift 2;;
    -n|--name) ONLY_NAME="$2"; shift 2;;
    --containerfile) DEFAULT_CONTAINERFILE="$2"; shift 2;;
    --context) DEFAULT_CONTEXT="$2"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    --no-build) NO_BUILD=1; shift;;
    --no-recreate) NO_RECREATE=1; shift;;
    --debug) DEBUG=1; shift;;
    -h|--help) usage; exit 0;;
    *) die "unknown argument: $1 (use --help)";;
  esac
done

[[ -f "$INI" ]] || die "ini not found: $INI"

INI_DIR="$(cd -- "$(dirname -- "$INI")" && pwd)"
INI_BASE="$(basename -- "$INI")"
INI_PATH="${INI_DIR}/${INI_BASE}"

mapfile -t RAW < "$INI_PATH"

# Parse sections:
# - image=...
# - optional directives in comments:
#     # containerfile=...
#     # build_context=...
declare -A SEC_IDX SEC_IMG SEC_PREFIX SEC_SUFFIX SEC_QUOTE
declare -A SEC_CONTAINERFILE SEC_CONTEXT
declare -a SECS=()

current=""
for i in "${!RAW[@]}"; do
  line="$(strip_bom_cr "${RAW[$i]}")"

  if [[ "$line" =~ ^[[:space:]]*\[([^]]+)\][[:space:]]*$ ]]; then
    current="${BASH_REMATCH[1]}"
    continue
  fi

  [[ -n "$current" ]] || continue
  [[ -z "$ONLY_NAME" || "$current" == "$ONLY_NAME" ]] || continue

  # NOTE: regex is quoted because it contains ';' which is a bash token otherwise.
  if [[ "$line" =~ '^[[:space:]]*[#;][[:space:]]*containerfile[[:space:]]*=[[:space:]]*(.+)$' ]]; then
    SEC_CONTAINERFILE["$current"]="$(trim "${BASH_REMATCH[1]}")"
    continue
  fi
  if [[ "$line" =~ '^[[:space:]]*[#;][[:space:]]*build_context[[:space:]]*=[[:space:]]*(.+)$' ]]; then
    SEC_CONTEXT["$current"]="$(trim "${BASH_REMATCH[1]}")"
    continue
  fi

  if [[ "$line" =~ ^([[:space:]]*image[[:space:]]*=[[:space:]]*)(.*)$ ]]; then
    prefix="${BASH_REMATCH[1]}"
    rest="${BASH_REMATCH[2]}"

    value="$rest"
    suffix=""
    # Preserve trailing comment starting with # or ;
    if [[ "$rest" =~ '^([^#;]*)([;#].*)$' ]]; then
      value="${BASH_REMATCH[1]}"
      suffix="${BASH_REMATCH[2]}"
    fi

    value="$(trim "$value")"
    quote=""
    if [[ "$value" == \"*\" && "$value" == *\" ]]; then quote='"'; value="${value:1:${#value}-2}"; fi
    if [[ "$value" == \'*\' && "$value" == *\' ]]; then quote="'"; value="${value:1:${#value}-2}"; fi

    SEC_IDX["$current"]="$i"
    SEC_IMG["$current"]="$value"
    SEC_PREFIX["$current"]="$prefix"
    SEC_SUFFIX["$current"]="$suffix"
    SEC_QUOTE["$current"]="$quote"
    SECS+=("$current")
  fi
done

[[ "${#SECS[@]}" -gt 0 ]] || die "no matching image= entries found (name filter: ${ONLY_NAME:-<none>})"

declare -A SEC_NEW
changed=0

for sec in "${SECS[@]}"; do
  cur="${SEC_IMG[$sec]}"
  base="${cur%%@*}"   # image tag without digest (works whether @sha exists or not)

  # Containerfile selection order:
  # 1) CLI overrides --containerfile/--context
  # 2) per-section comment directives
  cf="${DEFAULT_CONTAINERFILE:-${SEC_CONTAINERFILE[$sec]:-}}"
  ctx="${DEFAULT_CONTEXT:-${SEC_CONTEXT[$sec]:-}}"

  if [[ -n "$cf" ]]; then
    cf_path="$cf"
    [[ "$cf_path" == /* ]] || cf_path="${INI_DIR}/${cf_path}"
    [[ -f "$cf_path" ]] || die "containerfile not found: $cf_path"

    if [[ -z "$ctx" ]]; then
      # default context: directory containing the Containerfile
      ctx_path="$(cd -- "$(dirname -- "$cf_path")" && pwd)"
    else
      [[ "$ctx" == /* ]] && ctx_path="$ctx" || ctx_path="${INI_DIR}/${ctx}"
      ctx_path="$(cd -- "$ctx_path" && pwd)"
    fi

    if (( ! NO_BUILD )); then
      podman_build "$cf_path" "$ctx_path" "$base"
    else
      dbg "Skipping build for [$sec] due to --no-build"
    fi

    dig="$(podman_digest "$base" || true)"
    [[ "$dig" == sha256:* ]] || die "failed to read local digest for built image: $base"
    new="${base}@${dig}"
  else
    # No containerfile specified: image must already exist locally
    dig="$(podman_digest "$base" || true)"
    [[ "$dig" == sha256:* ]] || die "no containerfile=... and image not available locally: $base (build it or pass --containerfile/--context)"
    new="${base}@${dig}"
  fi

  SEC_NEW["$sec"]="$new"
  [[ "$new" != "$cur" ]] && changed=1

  printf '[%s]\n  current: %s\n  update : %s\n' "$sec" "$cur" "$new"
done

(( DRY_RUN )) && { info "Dry-run: no changes made."; exit 0; }
(( changed )) || { info "Already up to date; no file changes."; exit 0; }

bak="${INI_PATH}.bak.$(date +%Y%m%d-%H%M%S)"
cp -p -- "$INI_PATH" "$bak"

tmp="$(mktemp)"
trap 'rm -f -- "$tmp"' EXIT

for i in "${!RAW[@]}"; do
  orig="$(strip_bom_cr "${RAW[$i]}")"
  wrote=0
  for sec in "${SECS[@]}"; do
    if [[ "${SEC_IDX[$sec]}" == "$i" ]]; then
      q="${SEC_QUOTE[$sec]}"
      printf '%s%s%s%s\n' "${SEC_PREFIX[$sec]}" "$q" "${SEC_NEW[$sec]}" "$q${SEC_SUFFIX[$sec]}" >>"$tmp"
      wrote=1
      break
    fi
  done
  (( wrote )) || printf '%s\n' "$orig" >>"$tmp"
done

mv -- "$tmp" "$INI_PATH"
trap - EXIT
info "Updated: $INI_PATH (backup: $bak)"

if (( ! NO_RECREATE )); then
  have distrobox || die "distrobox not found on host"
  info "Recreating via distrobox assemble create --replace (ini dir: $INI_DIR)"
  xsh "cd $(printf %q "$INI_DIR") && distrobox assemble create --replace --file $(printf %q "$INI_BASE") ${ONLY_NAME:+--name $(printf %q "$ONLY_NAME")}"
fi

info "Done."
