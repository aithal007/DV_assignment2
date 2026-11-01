# Infovis requirements check — October 26, 2026

All three Infovis task groups are implemented. The static report includes all required plot forms; working browser pages supply the interactions.

| Required method | Report evidence | Implementation |
|---|---|---|
| NetworkX node-link with at least three layouts and interaction | Fig. 1, page 2: Spring, Spectral, Circular | `scripts/build_infovis_data.py`; `web/network.html`, `web/network.js` |
| JavaScript parallel coordinates with bundling and interaction | Figs. 4–5, page 5 | `web/index.html`, `web/app.js`: bundling, brushing, axis reordering |
| JavaScript zoomable treemap | Figs. 8–9, pages 8–9: region-first and adoption-first | `web/treemap.html`, `web/treemap.js`: zoom, Back, hierarchy switch |
| Python horizon plots | Figs. 13–14, page 12: country and regional median views | `scripts/build_temporal_figures.py`: `build_horizons` |
| Python ridgeline plots | Figs. 15–16, pages 13–14: selected-year distributions and regional panels | `scripts/build_temporal_figures.py`: `build_ridges` |

`interactions.json` records successful browser-control tests with no runtime errors. The network retained 179 countries and 590 links across three layouts; the filter reduced visible links to 52. The PCP preset selected the six expected countries from 175, and both a pointer brush and an axis-heading click changed the view. Treemap zoom/Back worked; both root hierarchies retained 4,521,767,530 users.

Run the browser apps with `python run_visualizations.py` from the submitted folder. Start at `http://127.0.0.1:8765/web/home.html`.

The short 14-slide video intentionally selects six main analysis figures. Treemap, horizon and the full three-layout comparison remain in the report and code rather than being explained in the main video. No report plot was removed in this text revision. This audit establishes implementation and tested controls; it does not predict a grade.
