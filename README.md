# The Samsung Odyssey G9 black screen

A guide for owners of a Samsung Odyssey G9 (C49G95T) or Odyssey Neo G9 (S49AG95) that lights up but shows no picture and no menu, and what is known about why it happens: the thermistor fix, where the thermistor is on each T-con board, the other faults behind the same symptom, and what Samsung has published.

- **Read it as a PDF:** <https://danieljbk.github.io/samsung-odyssey-g9-black-screen/report.pdf>
- **Read it as a web page:** <https://danieljbk.github.io/samsung-odyssey-g9-black-screen/>
- **Read the source:** [report.md](report.md)

Both links always show the latest version.

## Found a mistake?

Every claim in the report links to its source, and some of them will be wrong or out of date. Either:

- [open an issue](https://github.com/danieljbk/samsung-odyssey-g9-black-screen/issues/new) saying what is wrong and linking the post, video or document that shows it; or
- edit [report.md](report.md) here on GitHub (the pencil icon) and propose the change as a pull request.

When a change is merged, the PDF and the web page rebuild themselves within a few minutes.

Measurements are especially welcome: section 9 of the report describes the one that would settle what the thermistor input actually does.

## How it is built

`report.md` is the text. `figures/` holds the drawings; `make_charts.py` generates the outcome chart and the divider curve from the numbers it holds, and `data/removal-outcomes.csv` lists every post those outcome counts come from. `build_report.py` turns the text into `site/report.pdf` and `site/index.html` with pandoc and headless Chrome, and [the publish workflow](.github/workflows/publish.yml) runs both scripts and publishes `site/` on every change to `main`.

To build it yourself: install pandoc, poppler and Google Chrome, then run `python3 make_charts.py && python3 build_report.py`.

## Licence

The text, figures and data are licensed under [CC BY 4.0](LICENSE): you may share and adapt them with credit. The scripts are under the MIT licence, and the Inter font files in `assets/fonts/` under the [SIL Open Font License](assets/fonts/OFL.txt).
