# lavoro-di-maturita — LAM "Design dei filtri analogici" + EMG sensor board

Recovered **2026-11-24** from the Synology vault backup `homestead-2022`
(`/volume1/Backups/homestead-2022/mnt/bulk/home/darkcassini/…` — the old `/mnt/bulk` drive
content that lives inside that backup).

**What this is:** the *Lavoro Autonomo di Maturità* (LAM) — **"Design dei filtri analogici"**
(analog front-end filters for a surface-EMG sensor) — with the full KiCad hardware project
(3 PCBs), simulations, the EMG literature set, and Maple-related material.

## Layout

| Path | Content |
|---|---|
| `LAM/LAM_Design_dei_filtri_analogici/` | Final LaTeX paper: `.tex`, `.bib`, **155 MB final PDF** (+ 19 MB optimized), media (incl. Maple plots), datasets (`cf_fft_hand_muscles/data.txt` = 66 MB EMG measurements). **3 language versions:** `…analogici.tex` (IT original), `…_EN.tex` (English), `…_RU.tex` (Russian) — EN/RU machine-translated 2026 from the corrected IT source, `% TRANSLATOR NOTE:` comments mark interpretation spots |
| `LAM/LAM_Design_dei_filtri_analogici_old{,1}/` | Two earlier iterations of the paper (full sources) |
| `LAM/secondary/` | Working material: `Analogue_filter_design.tex`, `SensorBoard_circuit_diagram.tex`, Q-factor notes, reasoning process, Jupyter plots, plot generator |
| `kicad/emg_sensor_board/` | Main hardware project (ex-`05_emg_sensor_board`): `sensor_board_pcb`, `electrode_board_pcb`, `power_source_board_pcb` (KiCad 6 + plots + 3D render), `filter_sim`, `averager_sim` (KiCad schematic sims + `.wbk` WORKBENCH bode/transient notes), `main_board_software`, `guide/` (incl. JLC order PDF), `component_requirements.ods` |
| `kicad/emg_sensor/` | Earliest KiCad board draft (Nov 2021, incl. 8 auto-backup zips) |
| `papers/ScienceDirect_EMG_articles/` | 2019 *J. Electromyography & Kinesiology* set: **Tutorial: Surface-EMG detection in space and time**, needle-EMG myotonia paper, editorial board |
| `papers/phone_downloads/` | From the OnePlus 5T backup (May 2022): **EMG analysis.pdf**, **MapleFundamentalsGuide.pdf**, ADC-resolution note |
| `papers/sEMG-armband-archive.tar.gz` | sEMG armband archive (ex-flash-drive) |

> Maple note: no `.ml` worksheets survived — the Maple connection here is
> `MapleFundamentalsGuide.pdf` (phone download) and Maple-made plots inside the paper's `media/`.
> The Maplesoft *installer zips* (Windows, ~GBs) were left on the NAS under `Os-stuff/Software/windows/maplesoft_maple/`.

## Build (devbox, TIDES-style)

Containerized TeX Live (podman + distrobox, image pinned by digest in `distrobox.ini`):

```bash
./scripts/devbox/setup-devbox.bash                     # build image + create box (once)
distrobox enter devbox_lam_latex -- bash -c 'cd LAM/LAM_Design_dei_filtri_analogici && \
  latexmk -lualatex -shell-escape LAM_Design_dei_filtri_analogici_EN.tex'   # any of the 3 versions
```

Notes: the box ships `/etc/LatexMk` with `$pdf_mode=4`, so pass `-lualatex -shell-escape`
explicitly; 121 figures are tikz-externalized into `cache/` (parallel `make`) — first build
takes hours, later ones minutes. RU additionally needs `texlive-lang-cyrillic` (in
`Containerfile.latex`); xecyr must NOT be used under LuaLaTeX; babel-russian activates `"`,
so body text avoids straight double quotes.

## Technical note — why plain rsync to the vault failed (and the fix)

Two gotchas hit at once:

1. **Host alias vs IP:** `~/.ssh/config` binds `IdentityFile ~/.ssh/id_ed25519_synology-nas`
   (`IdentitiesOnly yes`) to `Host synology-nas` — connecting via the raw IP `192.168.1.71`
   doesn't match the pattern, so ssh offered no key → password prompt → rsync's
   non-interactive ssh dies with `Permission denied, please try again.`
2. **Synology's `rsync` PATH wrapper:** the bare `rsync` on the NAS is gated on the
   "rsync service" being enabled and refuses with a PAM-style `Permission denied`.
   The vault's own backup doc (`lostsecret-intel …/server-backup/README.md`) already
   prescribes the fix: **`--rsync-path=/bin/rsync`**.

Working recipe:

```bash
rsync -a --rsync-path=/bin/rsync \
  vault_main@synology-nas:/volume1/Backups/homestead-2022/mnt/bulk/home/darkcassini/Documents/School/LAM/ \
  ~/Projects/External/lavoro-di-maturita/LAM/
```
