# Assignment 2: requirement-by-requirement audit

This audit checks all three pages of DAS732_T1-26-27_A2.pdf against the supplied report, source code, data and runtime evidence. Technical coverage is documented below. Dataset registration and actual personal implementation require team confirmation. No assessment score is predicted.

| Clause | Requirement | Status | Evidence |
|---|---|---|---|
| Task / SciVis | Python color, contour and quiver implementations | Covered | Figs. 18-20, 27; scripts/build_scivis.py. Four real gridMET fields; no synthetic weather values. |
| Task / GIFs | Scalar animations with 5-10 time instances | Covered | Three supplied GIFs, each with eight frames: fixed-scale temperature, daily-scale temperature and contours. images/scivis/. |
| Task / InfoVis i | NetworkX or Gephi; at least three layouts and interactions | Covered | NetworkX Spring, Spectral and Circular; Fig. 1. web/network.html supports layout switching, threshold, country search, selection, pan and zoom. |
| Task / InfoVis ii-a | JavaScript parallel coordinates with edge bundling and interaction | Covered | Figs. 4-5; web/app.js and output/pcp_changes/app.js. Bundling, real pointer brushing, axis ordering and country inspection are tested. Bundles use explicit adoption groups, not inferred clusters. |
| Task / InfoVis ii-b | JavaScript zoomable treemaps | Covered | Figs. 9-10; web/treemap.js. Zoom/back, breadcrumbs and two complete hierarchy remodels retain the same 184 country leaves. |
| Task / InfoVis iii | Python horizon and ridgeline visualizations | Covered | Figs. 14-17; scripts/build_temporal_figures.py. Two horizon variations and two ridgeline variations. |
| Data / SciVis | gridMET and a contiguous three-month interval | Covered | July 1-September 30, 2023. The 92-day cache and separate eight-date cache retain the selected gridMET variables and acquisition provenance. |
| Data / rationale | Explain both the period and temporal sampling choice | Covered | Data and preparation: summer-to-autumn heat/cooling/rain timing; documented 2023 Southwest heat context; uniform 13-day spacing with endpoints, contrasted with random gaps. Full-period claims use all 92 dates. |
| Data / registration | Team slice selected through the TAs form; first-come policy | Verify | The supplied files cannot prove registration or uniqueness in the TAs form. Team must confirm its registered slice. This is an administrative check, not a plot feature. |
| Data / NetCDF | Extract vs and th for wind; other variables for scalars | Covered | vs maps to wind_speed and th to wind_from_direction in build_scivis.py; tmmx maps to air_temperature and pr to precipitation_amount. Source masks/packing are decoded; source Kelvin converts once to Celsius. |
| Data / A1 | Build network, multivariate and hierarchy data from A1 | Covered | Three preserved OWID/ITU extracts in data/raw/. Preprocessing outer-joins on entity/code/year, excludes 823 aggregate rows and retains 12,564 country-year rows without imputation. |
| Data / instructor | Discuss network difficulty with instructor before deadline | Covered | User-supplied instructor reply approves a derived similarity network and advises distribution-based filtering. Report attributes guidance once; P95 is explicitly the team choice. The email itself is not published. |
| Spec. 1 / bundle | Submit report, images folder and codebase | Covered | DAS732_A2_Report.pdf; images/report/Fig1.png-Fig31.png; data/, scripts/, web/, requirements.txt and launcher. Submission is self-contained without a Git remote. |
| Spec. 1a | Captioned report images and image-specific inferences | Covered | All 31 figures sets have a key-result caption, concise reading guide, evidence-based interpretation and numbered action takeaway. Full question/rationale guides are included in figures.html; common caveats are centralized. |
| Spec. 1b | High-resolution assessment images with report indices | Covered | Numbered PNGs and available matching SVGs in images/report/. Raw plot exports also remain at their source paths for exact regeneration. |
| Spec. 1c | Titles, legends, axes and other necessary text | Covered | Rendered report and full-resolution exports reviewed. Units, thresholds, cohort/sample sizes and scale keys are included where relevant; non-Cartesian views use appropriate labels and legends. |
| Spec. 1d | Complete high-resolution GUI screenshots | Covered | Appendices A1-A3 embed complete high-resolution browser captures with controls. images/gui/ and interactions.html retain originals and extra states; the PNG charts are identified as analytical exports. |
| Spec. 1e | README for implementation | Covered | Root README contains a local launch route, dependencies, data preprocessing, transformations, staged reproduction and validation commands. web/README.md explains interactions. |
| Spec. 1f | Video demo is not required | Not required | The supplied PDF explicitly says a video demo is not required. Old slides, scripts and unrecorded video materials are excluded from the core submission. |
| Spec. 1g | Professional report; appropriate references encouraged | Covered | 27-page IEEE-style report, readable captions and eleven cited references including gridMET, OWID, NetworkX, D3, Gephi and ContourPy/Marching Squares. |
| Spec. 2 / workload | Each student implements at least one SciVis and one InfoVis task | Verify | The assigned responsibilities satisfy the domain rule: Parikshith network/PCP + color; Sindhoor horizon/ridgeline + contours; Varshith treemap + quiver. Actual independent implementation is a team attestation, not verified by counts. |
| Spec. 2a | Combined outcome proportional to team strength | Covered | All specified visualization families and experiments are included for the three-person team, plus supporting analyses addressing the main question. |
| Spec. 2b | Report clearly states contributions | Covered | Named task-responsibility table; Person A/B/C and video duties removed. Figure allocation is 12/10/10. Assigned responsibilities must match actual independent work. |
| Spec. 2c-d | No joint task ownership; no two students do the same task | Verify | The assigned type ownership is distinct and all 31 figures have one assigned name. Shared preprocessing and reuse of method outputs are separated from task ownership. Confirm that actual work matches this table. |
| Spec. 3 | Marching Squares and/or filled contours; explain rationale | Covered | Fig. 20; independent 16-case code, both saddle-center resolutions and missing-cell handling. All 32 case checks pass; real-grid segments match ContourPy at four levels. Lines/filled bands serve threshold/regional reading tasks. |
| Spec. 4 | Continuous/discrete/logarithmic mappings and palettes | Covered | Fig. 18 compares continuous/discrete sequential, linear/log rain, a turbo baseline and a meaningful zero-centered departure map. Fig. 22 uses diverging differences. Quantity changes and zero-rain handling are explicit. |
| Spec. 5 | Global versus local extrema across timesteps | Covered | Fig. 19 plus fixed/daily-scale GIFs; identical colors under different extrema can represent different temperatures. Global bounds cover the eight sampled fields, not every day in the interval. |
| Spec. 6a or 6b | Quiver sampling/length comparison OR streamline experiment | Covered | Option 6a: Fig. 27 compares 4/12 display-cell steps and speed-proportional versus same-length arrows. vs/th conversion, map bearing and 5 m/s key are explicit. Streamlines are optional and not implemented. |
| Spec. 7 | Node-link layouts; node filtering optional | Covered | Three layouts in Fig. 1 and the live UI. Optional region and hide-isolate node filters are implemented in addition to required edge-threshold interaction. |
| Spec. 8 | PCP must have axis reordering and/or brushing | Covered | Both are implemented and exercised through actual pointer/axis controls. Bundling changes paths while preserving measured values at the axes. |
| Spec. 9 | Treemap hierarchy remodels; spatial partition optional | Covered | Region -> country and adoption band -> region -> country. Optional squarified versus slice-and-dice selector preserves totals and hierarchy. Figs. 9-10 plus UI evidence. |
| Spec. 10 | At least two horizon and two ridgeline variations | Covered | Horizon: selected country series and regional medians (Figs. 14-15). Ridgeline: global yearly and regional yearly distributions (Figs. 16-17). Fixed cohorts and 0-100 scales avoid changing sample definitions. |
| Rubric / completeness | 4 points: all experiments and complete deliverables | Evidence mapped | Every compulsory experiment maps to a figure, implementation or GIF above. Folder integrity and local runtime links are checked; external registration and actual ownership remain separate checks. |
| Rubric / correctness | 8 points: valid inference for dataset space/time | Evidence mapped | Numerical verifiers recompute edges, distributions, paired changes, monthly weather, rainfall concentration and run lengths. Similarity is not a physical cable; observational associations are not causal claims. |
| Rubric / inferences | 8 points: useful complex inferences from visualization | Evidence mapped | 32 question/evidence/inference/takeaway sequences connect profiles, paired trajectories, within-group variation, full-month versus endpoint change, daily order and joint occurrence. |
| Rubric / data handling | 10 points: preprocessing and transformations | Evidence mapped | Separate preprocess_data.py; raw extracts, region lookup, cache metadata and SHA-256 audit. Missingness/cohort rules, masks, temperature units, wind convention, subsampling and area weights are documented. |

## Before submission

- Confirm the registered July-September 2023 slice in the TAs form.
- Confirm actual independent task ownership, and ensure that the assigned responsibility statement is accurate.
- The supplied assignment PDF does not require a video. Any later course announcement would need to be checked separately.

## Assessment weights

Completeness 4; correctness 8; quality of inferences 8; data handling 10. Total 30, scaled to 20.

No GitHub publishing or remote operations are needed for this folder.