#!/usr/bin/env bash
# clean.sh — remove regenerable build junk from the paper directory.
#
# Only deletes things the repo already declares disposable (.gitignore) and
# that can be recreated by a rebuild (see README "Building the paper"):
#   - LaTeX/biber intermediates (*.aux, *.log, *.bbl, *.bcf, *.xdv, ...)
#   - latexmk strays from interrupted runs (*.auxlock, *SAVE-ERROR, *.bak)
#   - the ~150 MB unoptimised PDFs (regenerate with latexmk; the committed
#     *_optimized.pdf files are never touched)
#   --deep additionally removes cache/ (the tikz-externalised figures, ~500 MB;
#   next build is then cold: all ~35 figures re-render, ~1.5 h).
#
# Never touched: .tex/.bib sources, media/, datasets/, notes/, the three
# *_optimized.pdf deliverables and the irreplaceable 2022 original.
set -Eeuo pipefail
cd "$(dirname "$0")/.."

deep=0
[[ "${1:-}" == "--deep" ]] && deep=1
[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && { sed -n '2,15p' "$0"; exit 0; }

before=$(du -sb . | cut -f1)

# latexmk / biber / luaTeX intermediates (same list as .gitignore)
rm -f -- *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk \
          *.blg *.bcf *.run.xml *.synctex.gz *.xdv *.bbl \
          *.auxlock *SAVE-ERROR .latexmk

# unoptimised fresh-build PDFs (>100 MB, not publishable, rebuild in minutes
# from the warm figure cache)
rm -f -- LAM_Design_dei_filtri_analogici.pdf \
         LAM_Design_dei_filtri_analogici_EN.pdf \
         LAM_Design_dei_filtri_analogici_RU.pdf

# one-off leftovers
rm -f -- rebuild-2026-killed-partial.pdf.bak

if (( deep )); then
    rm -rf -- cache/
    echo "deep: removed cache/ (next build re-renders all figures)"
fi

after=$(du -sb . | cut -f1)
echo "freed: $(( (before - after) / 1048576 )) MB"
echo "remaining PDFs:"; ls -1 *.pdf 2>/dev/null | sed 's/^/  /' || true
