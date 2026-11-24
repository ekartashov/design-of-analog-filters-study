# Prompt for Claude — translate the LAM maturità paper to English

Attach/paste the file `LAM_Design_dei_filtri_analogici.tex` (the full source), then send:

```
You are translating my Italian "lavoro di maturità" thesis (LaTeX, ~3350 lines, attached)
into English. Output the COMPLETE translated .tex file. This is a translation task, NOT a
refactoring task: change only the human-readable Italian text and the two switches listed
below. Leave every other byte exactly as-is — do not reflow, reorder, "improve", or
reformat any LaTeX code, and do not drop anything (footnotes, todos, commented lines).

The paper: a design of an EMG (electromyography) sensor board + analog filters, written
2022 in first person. Register: natural, technically precise academic English; keep the
author's voice and sentence structure close to the original rather than rewriting it.

TRANSLATE:
- All prose, section titles, abstract, title page text, captions/subcaptions, footnotes,
  \todo{...} contents, table cell text.
- Legend entries inside pgfplots axes, e.g. "Canale 1" -> "Channel 1".
- These exact strings:
    title={Sorgenti Maggiori}  -> title={Key Sources}
    title={Sorgenti Minori}    -> title={Secondary Sources}
    title={Sorgenti Dati}      -> title={Data Sources}
    title={Sorgenti Immagini}  -> title={Image Sources}
    title={Sorgenti Datasheet} -> title={Datasheet Sources}
- In prose, convert Italian decimal commas to decimal points (e.g. "0,5 V" -> "0.5 V"),
  but NOT inside CSV data, math mode, or numeric options.
- Italian accent escapes (\`{e}, \'{e}, \`{a}, …) will mostly just disappear in English.

DO NOT TOUCH (keep byte-identical):
- The preamble, except these TWO lines:
    \usepackage[italian]{babel}   ->   \usepackage[english]{babel}
    the document title text on the title page (translate "Design dei filtri analogici"
    as "Design of Analog Filters")
- The custom command \parenciteit (defined in the preamble) — keep the name everywhere,
  translate only its bracket prenote text, e.g. \parenciteit{p2, Sezione 3} -> \parenciteit{p2, Section 3}.
- All \label, \ref, \autoref, \cref, \cite, \parencite, \footcite arguments; keywords=
  values; CSV/file paths (e.g. datasets/result/gr1.csv); image paths; \jobname stuff.
- Everything inside \begin{tikzpicture}...\end{tikzpicture}, axis options, \addplot
  options, and any \node{...} that contains circuit labels (V, R, C, U, numbers) — but
  DO translate \node text that is Italian prose.
- Everything inside \begin{lstlisting} or listings code blocks (Arduino/C code).
- Inline math $...$ unchanged (translate only Italian words inside \text{...}/\mathrm
  if any).
- LaTeX comments (%) — keep them in Italian, they are author notes.

CONSISTENCY GLOSSARY (use exactly these terms):
scheda madre -> main board
scheda sensore -> sensor board
lavoro di maturità -> maturità thesis (keep the word maturità, italicized)
filtrazione / filtro -> filtering / filter
risposta in frequenza -> frequency response
diagramma di Bode -> Bode plot
amplificatore strumentazione (INA) -> instrumentation amplifier (INA)
tensione -> voltage (use "tension" only for mechanical contexts, rare here)
corrente -> current
retroazione -> feedback
disturbo / rumore -> interference / noise
campionamento -> sampling
digitalizzazione -> digitization
soglia -> threshold
realimentazione -> power supply
predispositivo -> preamplifier stage
muscolo -> muscle
segnale misurato -> measured signal

OUTPUT FORMAT:
The file is long. Output it in sequential parts, each starting with a line
"=== PART n ===" and ending mid-stream is fine; I will say "continue" until you print
"=== END ===". Inside parts, emit raw LaTeX (no markdown fences around the whole part).
Before PART 1, print a 5-line checklist of what you will NOT touch, and after END list
any spots where the Italian was ambiguous, as "% TRANSLATOR NOTE:" lines inserted at
those spots in the file itself.
```

## Workflow tips

1. Feed the `.tex` + prompt in one message (file is ~3350 lines / fits easily in context).
2. Answer "continue" until `=== END ===`.
3. Paste the stitched result into a NEW file `LAM_Design_dei_filtri_analogici_EN.tex` —
   never overwrite the Italian original.
4. Hand it back to me and I'll compile it in `devbox_lam_latex` (`latexmk -lualatex
   -shell-escape` after changing `@default_files`), fix any breakage, and reuse the
   figure cache so the EN build is fast.
