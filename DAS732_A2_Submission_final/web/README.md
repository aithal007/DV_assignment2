# Interactive implementation and assessment guide

Run `python run_visualizations.py` from the submission root and use `http://127.0.0.1:8765/web/home.html`. Python serves local files; all JavaScript, D3 and data are supplied. There is no backend analysis service and no CDN dependency.

## Network: Figure 1

`network.html` / `network.js` draws positions computed in Python by NetworkX. Spring, Spectral and Circular preserve the same thresholded graph. The default P95 threshold is 0.5697629885414606: 797 of 15,931 pair scores, 179 countries and 12 isolates. Search India to inspect twelve default neighbors. Move the threshold to zero to show the complete pair graph. Use region and hide-isolate filters, pan/zoom and Reset. Layouts stay fixed during filtering; separate isolate rows are deliberate placement. These are telecom-profile similarities, not physical connections.

**Adjacency-matrix view.** The View control switches the same graph between node-link and an adjacency matrix, sharing threshold, region, isolate filter, search and country selection. A colored cell marks a retained pair (darker = higher similarity), gray is the excluded diagonal, and empty cells are measured scores below the cutoff, so every retained pair stays individually checkable. Matrix scan order switches between Region groups, visible degree and name; click a row label or cell to select that country; hover a cell for the measured pair score; scroll zooms. `?view=matrix&find=India` opens a sharing/audit link with the matrix view and a selected country.

## Parallel coordinates: Figures 4-5

`index.html` / `app.js` displays 175 matched country profiles. Compare bundling at 0% and 35%; values at each axis remain the source observations. Curves move toward explicit adoption-band centroid midpoints, constrained between measured endpoint values. They do not infer new country clusters.

Drag vertically on an axis to brush. Multiple brushes combine across axes; Clear brushes resets. Click an axis title, or press Enter when it has focus, to reorder axes. Change year/region/fixed-scale controls and hover country records. The focus button selects the six high-adoption/low-broadband countries. Status and details identify the displayed cohort and measured values.

`../output/pcp_changes/index.html` is the paired-change view: 2015-2020 differences are calculated within each of the same 175 countries. Brush gains, reorder axes, inspect countries and compare straight/bundled records. Zero is aligned; each measure has its own stated range.

## Treemap: Figures 9-10

`treemap.html` / `treemap.js` uses the same 184 country leaves and 4,521,767,530 included users in both remodels: Region -> country and Adoption band -> region -> country. Area encodes user count; country color encodes adoption share. Click a group to zoom, inspect the breadcrumb and Back control, and hover exact country values. Zoomed totals describe the visible subset. At the root, switching hierarchy must retain the same total.

The partition selector compares squarified and slice-and-dice layouts while preserving hierarchy, leaf values and the current zoom path. The partition changes rectangle geometry, not internet access measurements.

## Complete UI evidence

`../interactions.html` presents uncropped full-page screenshots with controls. Images are in `../images/gui/`. The actual Playwright audit uses real pointer brushing and axis-title clicks and checks measured-value invariance under bundling, all three layouts, search/threshold/reset, optional node filters, treemap zoom/back, both hierarchies and both partitions. Its latest timestamped receipt is `../output/infovis_audit_20261026/interactions.json`; the folder name is historical.

To recapture locally, install Playwright and Chromium as described in the root README, run `node scripts/audit_infovis_interactions.mjs`, then run `python -X utf8 scripts/submission_workflow.py --stage refresh`. Chart exports in the report are separate from these complete GUI screenshots.
