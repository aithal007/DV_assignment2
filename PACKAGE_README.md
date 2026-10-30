# A2 selected report and interactive JavaScript package

Extract this ZIP to a folder. Open output/pdf/DAS732_A2_Report_IEEE.pdf for the
27-page illustrated report (32 figures, with supporting checks in the companion gallery).

To run the browser visualizations, double-click START_VISUALIZATIONS.cmd on Windows,
or run `python run_visualizations.py` with Python 3. The launcher opens at
http://127.0.0.1:8765/web/home.html. Keep the server process running.
The browser app uses only the Python standard library server, local JavaScript,
vendored D3 v7 and the supplied JSON files; it needs no CDN or Python data packages.

Required JavaScript: web/app.js (parallel coordinates), web/treemap.js (zoomable
treemap), web/network.js (network explorer). See web/README.md for controls and the
interaction instructions. The PDF is static; the working pages and three GIFs
are separate evidence. On October 26, the browser audit exercised all three network
layouts, search/filtering, PCP bundling, pointer brushing, axis reordering, treemap
zoom/back and both hierarchies. Results are in output/infovis_audit_20261026/.

The editable LaTeX report and all 32 numbered PNGs are in report_latex/.
Compile DAS732_A2_Report.tex twice with pdfLaTeX. The gallery uses original
full-resolution images, with detailed readings, under output/quality_figures/.

The team's required video materials are in output/video_presentation/.
The current deck and script retain the same network default and numerical findings;
the latest report adds method-sensitivity diagnostics in output/network_revision/.
The human narration and final video still need recording.

To recreate numerical results, install requirements.txt, then run
`python -X utf8 scripts/reproduce_results.py` from the extracted folder.
Raw country extracts, the regional lookup, preprocessing source/audit and current
gridMET NPZ caches are included. The country builders use data/processed/,
prepared by scripts/preprocess_data.py, without needing an external A1 folder.
The cache-backed numerical pipeline does not need a network connection; absent
weather caches can be retrieved with --download-weather. PDF compilation requires
pdfLaTeX on PATH. Exact stages and processing rules are in WORKSPACE_README.md.
Browser screenshots remain supplied artifacts; recapture them with
node scripts/audit_infovis_interactions.mjs when Playwright and Edge are configured.
See web/README.md for the view states. Presentation regeneration requires a separate Node.js runtime for the artifact tools;
the numerical/report command does not rebuild the slide deck.

The prior-figure comparison gallery is at output/report_changes/index.html.
All omitted/replaced original plots and the previous PDF are supplied.

The report now includes the adopted three-person responsibility allocation in the
A1 contribution-table format. Each member has a distinct Infovis and SciVis task.
Actual implementation completion and individual AI disclosures require verification.
