# LAM "Design dei filtri analogici" — build recipe
# Original (2022): lualatex with shell-escape + biber (biblatex).
# NOTE: box ships /etc/LatexMk with $pdf_mode=4 (xelatex) which beats this file —
# so build explicitly:  latexmk -lualatex -shell-escape
$pdf_mode = 5;                              # lualatex
$lualatex = 'lualatex -shell-escape -file-line-error -interaction=nonstopmode';
@default_files = ('LAM_Design_dei_filtri_analogici.tex');
# APA/biblatex + 121 externalised figures need several reruns to converge;
# the old value of 2 made latexmk quit with "needed too many passes".
$max_repeat = 6;
