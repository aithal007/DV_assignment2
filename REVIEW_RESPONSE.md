# Final PDF review: corrections and verification

All 32 analytical figure sets are retained. The three browser UI appendix pages have been removed; the first-page dashboard link directs readers to the interactive views. Full screenshots remain in the UI evidence gallery. Changes are local; no GitHub publishing is performed.

| Review point | Correction / evidence |
|---|---|
| Draft contribution language and video duties | Replaced with a concise named task-responsibility table. Removed proposed-allocation instructions and all video duties from the PDF. Assigned responsibilities do not certify personal implementation; the external readiness audit retains that team check. |
| Repeated professor/perturbation wording | Advice is attributed once in Data and Preparation; P95 remains explicitly the team's choice. Repeated attribution is removed from the figure discussion and network UI. |
| Undefined online method review | Replaced with explicit package paths: output/network_revision/ and output/review_revision/layout_comparison.csv. |
| Figure 26 axes/top panel contradiction | The guide now states horizontal date, vertical longitude, and a reference map of the 30-45 N band. |
| Contour implementation | scripts/marching_squares.py independently implements the 16 configurations, linear interpolation, both saddle-center resolutions and missing-cell handling. Figure 20 overlays custom lines with ContourPy and explains line versus filled-band purposes. |
| Contour tests | 32 configuration/center checks pass; unordered real-grid segments match ContourPy serial at 25, 30, 35 and 40 C to 1e-8 degrees. Details are in output/review_revision/marching_squares_validation.json. Both methods omit partially masked quads in this controlled comparison. |
| UI evidence only through links | The first-page dashboard link opens the interactive node-link, PCP and treemap views. Original full-resolution captures and actual browser interaction receipts remain supplied in the submission. |
| Figure 22 unsupported sign-disagreement claim | Added the endpoint-difference panel and an explicit map of cells with opposite signs, alongside complete-month differences and sector distributions. |
| Figure 23 repeated 31.19 | Raw-cache recomputation gives western July 27 mean 31.1931686 C and July-wide mean 31.1920232 C. Both round to 31.19; the report now uses three decimals and explains the coincidence. |
| Figure 26 rain colorbar | Verified the maximum 95.2024 mm/day band mean: September 16, longitude 67.2667 W, two coastal cells with 94.10 and 96.30 mm/day. Colorbar labels are physical mm/day; only color spacing is square-root transformed. A support-count panel exposes the 1-60-cell range across longitudes. |
| Oceania labels | Verified the 2020 median is 53.7123%, rounded to 53.7%. Figures 15/16 are full-width and temporal label fonts are enlarged; the interpretation identifies the agreement with Figure 17. |
| Figure 29 rounding | Both overlay panel titles now use two decimal places, agreeing with the 1.75% interpretation. |
| Uzbekistan omitted | Figure 4 discusses its 28.3-point adoption gain and approximately +10.0 broadband, +7.1 landline, +28.6 mobile changes, contrasting it with Georgia and Brunei. |
| 179 versus 175-country cohorts | Concise reminders accompany the network/profile comparisons. 179 needs complete 2020 data; the 175-country matched cohort additionally needs complete 2015 data. |
| Figure 1 annotations and invisible edges | Moved the P95 summary clear of the curves, strengthened edge contrast, enlarged the layout area, colored nodes by region and sized them by retained degree. The live explorer now uses visible degree for node area too. |
| Layout comparison is descriptive only | Added reproducible proper straight-edge crossing counts: Spring 3,042; Spectral 3,371; Circular 98,598. Shared-endpoint contacts and collinear overlaps are excluded. Text discusses separation, compression and crossing/clutter costs while preserving the same graph. |
| Figure 3 tiny overview matrices / alphabetical detail | Replaced the unreadable miniature overview matrices with six aggregate community nodes and between-group counts. The enlarged individual adjacency detail is ordered by internal degree and labeled as a node-link/matrix hybrid inspired by NodeTrix. |
| Figure 27 speck-sized arrows | Replaced six small panels with a 2x2 comparison at two sampling densities (4/12 display-cell steps), larger arrows, physical keys and explicit same-length versus magnitude-proportional encodings. |
| Figure 28 radial labels overlap bars | Removed numeric labels from inside bars and supplied common ring values/outer limit outside the plots. Direction labels remain external. |
| Figure 20 low contrast | Custom colored threshold lines are drawn on a pale neutral base, with a separate high-contrast library overlay and filled-band comparison. |
| Figures 9/10 same title and missing area legend | The titles distinguish region versus adoption-band grouping. The visible legend states area = internet users and color = adoption share. Browser exports are recaptured from the working D3 implementation. |
| Mixed figure styles | New analytical exports share typography, white backgrounds and accent conventions. The network's region colors match its UI. Different palettes are retained where the assignment explicitly compares color mappings; UI captures remain complete application evidence. |
| Figure/text separation | Every PDF discussion heading and takeaway identifies its figure number. Captions now state a key measured finding beside the image; detailed discussion can still follow normal IEEE float placement. |
| Ceiling/saturation and absolute catch-up | Figures 8/11 discuss the 0-100 bound, reduced headroom and S-curve diffusion timing. The report distinguishes absolute percentage-point gaps from relative inequality. |
| Feature sensitivity omitted from Discussion | Discussion states the 0.338-0.512 leave-one-indicator-out Jaccard range and distinguishes metric sensitivity from small-noise stability. |
| Figure 26 fixed climate gradient dominates | The temperature panel now shows each longitude's departure from its own 92-day mean. It is named and cited as a Hovmoller-style diagram; this is not a long-term climate anomaly. |
| Figure 24 concentration depends on rain-day count | Text explicitly notes that few wet days can create high five-day shares without sustained spells. Total rain, eligible footprints and daily sequence remain separate information. |
| Figure 6 distance/color definitions differ | The caption and interpretation distinguish the three-infrastructure-indicator histogram distance from the four-indicator network pass/fail color. |
| Repetitive five-block prose and caveats | The PDF uses concise reading guides, evidence-based interpretation and one actionable takeaway. Full question/rationale guides remain in figures.html. Routine caveats are centralized in Scope and Limits; captions carry local key results. |
| Sequential-only color experiment | Figure 18 adds a meaningful zero-centered, own-cell period-mean departure and a turbo baseline while keeping same-field comparisons explicit. |
| Rain global/local experiment | Added output/review_revision/rain_global_local.png as a supplement, using the dates with minimum/maximum sampled spatial rain maxima. Fixed/daily limits and physical units are explicit. The required temporal comparison remains in Figure 19 and the scalar GIFs. |

## Optional suggestions not added to the core PDF

- Gephi ForceAtlas2 and replacing Spectral: the assignment permits Gephi **or** NetworkX. Three valid NetworkX layouts are retained with stronger quantitative comparison; no unused-tool screenshot is invented.
- Offline-population treemap / third hierarchy: two hierarchy remodels and optional partition comparison already satisfy the task. No independent population measure is supplied for a new offline-population claim; online-user areas remain labeled accurately.
- Streamlines: optional. The required quiver sampling-and-length alternative is implemented and improved.
- Full native-grid comparison: not claimed. Stride-six processing/display rationale and the resulting scope limit are explicit. No unperformed native-resolution equivalence test is presented as evidence.

## Verification files

- output/review_revision/facts.json: checked weather numbers and layout metrics.
- output/review_revision/marching_squares_validation.json: independent/library comparisons.
- output/review_revision/validation.json: review-specific numerical and PDF checks.
- output/infovis_audit_20261026/interactions.json: latest timestamped browser tests (the folder name is historical).
- evidence/submission_validation.json: final folder, numbered images, GIFs and local-link integrity.
