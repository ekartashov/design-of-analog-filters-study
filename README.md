# Design of Analog Filters

**The analog front-end of a surface-EMG (muscle) sensor — designed, simulated, built and measured.**
Maturità thesis (independent research paper of the Swiss Gymnasium), *Liceo cantonale di Lugano 1*, school year **2021/2022**.

## 📄 Read the paper

| Edition | PDF | |
|---|---|---|
| 🇬🇧 **English** | [`…_EN_optimized.pdf`](LAM/LAM_Design_dei_filtri_analogici/LAM_Design_dei_filtri_analogici_EN_optimized.pdf) | **recommended entry point** |
| 🇮🇹 **Italiano** | [`…_2022-optimized.pdf`](LAM/LAM_Design_dei_filtri_analogici/LAM_Design_dei_filtri_analogici_2022-optimized.pdf) | **the original** |
| 🇷🇺 **Русский** | [`…_RU_optimized.pdf`](LAM/LAM_Design_dei_filtri_analogici/LAM_Design_dei_filtri_analogici_RU_optimized.pdf) | translation |

> **On languages.** The paper was written and submitted in **Italian**; that is the original. The English and Russian editions are complete 2026 re-translations of the same text and figures (AI-assisted, human-revised; interpretation spots are flagged in the sources as `% TRANSLATOR NOTE:` comments). Cite the Italian original.

> **On the context.** This was completed as a **maturità paper for the Gymnasium** (high-school leaving qualification) during the 2021/2022 school year at the Cantonal Lyceum of Lugano (Liceo cantonale di Lugano 1, Switzerland). It was an entirely self-directed project: **no university studies and no related formal courses had informed it** — the filter theory, the circuit design and the measurement methodology were studied independently for this work.

## What this project is

A from-scratch development of the analog signal chain of an electromyographic sensor — the weak muscle signal picked up by skin electrodes, conditioned and digitized:

- **Theory built up from first principles** in the paper: systems, transfer functions, poles/zeros, Bode plots, passive and active filter stages (Butterworth, Chebyshev, Bessel), op-amp circuits, noise/EMI, discretization, ADC resolution
- **Full hardware**: 3 custom PCBs (sensor board, electrode board, power-source board) designed in KiCad, built as photographed prototypes
- **Real measurements**: 8-channel recordings of hand-muscle contractions, with amplitude/height adjustability demonstrated and FFT gesture analysis — including a 66 MB raw acquisition dataset
- **81 pages, 121 natively-drawn plots** (pgfplots — Bode/transient/pole-zero figures compiled from the same CSVs as the measurements), 74 sources

## Repository layout

```
LAM/LAM_Design_dei_filtri_analogici/    the paper: .tex sources, .bib, media/, datasets/, and the 3 optimized PDFs
LAM/secondary/                          working material: filter-design notes, sensor-board diagram, FFT notebooks
kicad/emg_sensor_board/                 hardware project: 3 PCBs + schematics, 3D renders, sim notes, BOM
scripts/devbox/  distrobox.ini          reproducible TeX toolchain (podman + distrobox, image pinned by digest)
notes/                                  provenance and translation-workflow notes
```

## Building the paper

The toolchain is containerized (LuaLaTeX + biber + TeX Live 2025 in a Debian devbox):

```bash
./scripts/devbox/setup-devbox.bash            # build image + create the box (once; requires podman)
distrobox enter devbox_lam_latex -- bash -c '
  cd LAM/LAM_Design_dei_filtri_analogici && latexmk -lualatex -shell-escape'
```

Figures are TikZ-externalized into `cache/` (gitignored) — a cold build renders all ~120 of them once, incremental rebuilds then take minutes. The PDFs committed here are Ghostscript-optimized (~19 MB each, visually lossless); unoptimized builds are ~150 MB and are left out of the repo.

**Rebuilding the smaller documents.** The standalone working notes under `LAM/secondary/` (each folder is a tiny LaTeX document: the 8-channel plot sheet `plots/Standalone.tex`, `Q_Factor/`, `Analogue_filter_design/`, `Circuit/SensorBoard_circuit_diagram.tex`) and the KiCad print plot are *build outputs* and are not committed — regenerate them with `latexmk -lualatex -shell-escape <name>.tex` in the devbox, or re-export the plot from the KiCad project. The PDFs that **are** committed under `media/` (Maple exports, Ideasheets, PCB crops, TI app-notes) are *inputs*: the Maple worksheets did not survive, so those ten Maple PDFs are irreplaceable. The `guide/Order_*.pdf` is a JLC order record, kept as a document.

## Measurement datasets

In `LAM/LAM_Design_dei_filtri_analogici/datasets/`:

| Folder | Contents |
|---|---|
| `cf_fft_hand_muscles/` | 8-channel hand-contraction acquisitions (incl. per-session raw dumps and a 66 MB `data.txt`), FFT analysis notebook |
| `result/` | the three plotted measured signals (`gr1`–`gr3.csv` — the teal traces in Fig. 54) |
| `s_plot_example_data/`, `s_plot_log_example_data/` | filter-response datasets behind the Bode/transient plots |
| `ecg_example_data/` | ECG example recorded through the EMG sensor |

## License

© 2021–2026 Evgeny Kartashov — [CC BY 4.0](LICENSE.md). Third-party images (e.g. Arduino/ESP32 board photos, datasheet figures) keep their sources' licenses as credited in the paper's source lists.
