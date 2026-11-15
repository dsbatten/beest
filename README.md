# BEEST 2

Bitcoin network emissions tracker by Daniel Batten: gross and net emissions, flare-gas mitigation, hashrate and price, refreshed daily from public sources.

- `index.html`: the live chart, from 1 December 2025
- `history.html`: the same chain back to September 2019
- `methodology.html` / `methodology.md`: every input, calculation and assumption, with sources
- `series.json`, `history.json`: the data the charts draw, rebuilt each morning by the workflow in `.github/workflows/refresh.yml`
- `build_series.py`, `build_history.py`, `hashrate_feed.py`: the builders; `sources/`: the BEEST 1 and CBECI tables they read
