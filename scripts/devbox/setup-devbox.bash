#!/usr/bin/env bash
set -Eeuo pipefail

# Build the devbox base image (slow once), pin its digest into distrobox.ini,
# then recreate the distrobox container (fast afterwards).
# (Ported from the TIDES thesis devbox system.)

INI="${INI:-./distrobox.ini}"
NAME="${NAME:-devbox_lam_latex}"

# Container build inputs
CONTAINERFILE="${CONTAINERFILE:-./scripts/devbox/Containerfile.latex}"
CONTEXT_DIR="${CONTEXT_DIR:-.}"

# Optional: control base-image pull behaviour during build (always|missing|never)
PULL_POLICY="${PULL_POLICY:-always}"

mkdir -p .devbox_home

PULL_POLICY="$PULL_POLICY" \
  ./scripts/devbox/update-pin.bash \
    -f "$INI" \
    -n "$NAME" \
    --containerfile "$CONTAINERFILE" \
    --context "$CONTEXT_DIR"

echo "OK: $NAME ready."
