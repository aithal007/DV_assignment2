# Assignment 2: final three-part plan

Adopted responsibility allocation using the current **25-page, 30-figure report**, with the A1 member names and student IDs. The report now includes the allocation table. This assigns responsibility without certifying unconfirmed completed work. The video follows the continuous question-to-evidence story described in output/video_presentation/RECORDING_SCRIPT.md.

**Main question:** What do averages and snapshots hide about inequality, relationships and change over time?

## Three linked parts

| Part | Proposed person | Story role | Required Infovis work package | Required SciVis task |
|---|---|---|---|---|
| A: Patterns, profiles and trustworthy comparisons | Parikshith Aithal K V | Which patterns are supported by the data, and which impressions depend on how we draw or aggregate it? | Network: construction, three layouts, search/selection/filtering, country trajectories and profile interpretation. | Color mapping: continuous/discrete palettes, normalization, global/local extrema, global/local scalar GIFs. |
| B: The digital divide, trajectories and hidden persistence | Sindhoor Ganapathi Hegde | Does broad progress mean convergence, and what do averages hide about individual changes and persistent conditions? | Temporal methods: both horizon variations and both ridgeline variations, with their baselines, cohorts and density checks. | Contour mapping: Marching Squares-family tracing, lines/fills, interval comparison and contour GIF. |
| C: Infrastructure relationships, interactions and the final answer | Varshith M Gowda | Which relationships survive inspection across variables, country changes and joint conditions? | JavaScript browser methods: bundled parallel coordinates with brushing/reordering AND zoomable treemap with two hierarchy remodelings. | Quiver: spatial sampling, proportional versus equal arrow lengths, meteorological FROM to flow TO conversion and speed key. |


This follows the A1 structure: the first part establishes the patterns, the second tests whether progress closes the divide, and the third inspects infrastructure relationships and gives the qualified verdict. Weather supplies a separate case study of the same visualization question; no country-weather causal connection is asserted.

## Exact allocation: ten figure sets each

The current report remains in its reading order. These are responsibility and presentation sets, so figure numbers are intentionally nonconsecutive. Reordering or renumbering the PDF is unnecessary.

### Part A: Parikshith Aithal K V

**Question:** Which patterns are supported by the data, and which impressions depend on how we draw or aggregate it?

**Answer:** Similar adoption can accompany different infrastructure profiles. Fixed scales and complete daily coverage distinguish measured differences from drawing or sampling effects.

| Current figure | Topic |
|---|---|
| 1 | Same links, different network layouts. |
| 2 | Different country paths to higher internet use. |
| 3 | NodeTrix: look inside a country group. |
| 17 | How color choices change the view. |
| 18 | Fixed and daily color scales. |
| 20 | Monthly temperature maps. |
| 21 | Monthly change versus two selected dates. |
| 22 | Daily temperature and its spatial spread. |
| 23 | Monthly rain totals and five-day bursts. |
| 25 | Daily weather across longitude. |


**Principal evidence for a short explanation:** Figures 1-3 show layout effects, country paths and NodeTrix links; Figures 17-18 establish fair scalar comparisons; Figure 23 shows how monthly totals hide concentrated rainfall.

**Handoff:** The comparisons are now consistent. But has progress actually reduced inequality, and does an average describe the countries or places behind it?

### Part B: Sindhoor Ganapathi Hegde

**Question:** Does broad progress mean convergence, and what do averages hide about individual changes and persistent conditions?

**Answer:** Regional summaries hide country differences: 47% of measured 2020 variation lies within regions. Regional median shifts differ from typical individual gains. Event frequency differs from uninterrupted duration.

| Current figure | Topic |
|---|---|
| 10 | When countries first reach 50% and 75% internet use. |
| 11 | Country differences inside each region. |
| 12 | Regional change and individual country gains. |
| 13 | Country horizon plots. |
| 14 | Regional median horizon plots. |
| 15 | How the country distribution changed. |
| 16 | How distributions changed within regions. |
| 19 | Contour intervals and filled contours. |
| 24 | Where hot days are frequent. |
| 30 | How often conditions occur and how long they last. |


**Principal evidence for a short explanation:** Figures 10-12 connect timing to within-region variation and country gains; Figures 13-16 demonstrate the required temporal methods; Figure 30 distinguishes event counts from persistent runs.

**Handoff:** Progress is real but uneven, and a summary can conceal very different experiences. Which infrastructure relationships remain when we inspect the original measurements and their changes?

### Part C: Varshith M Gowda

**Question:** Which relationships survive inspection across variables, country changes and joint conditions?

**Answer:** The strong broadband/adoption association across country levels does not describe matched changes. User counts and adoption shares answer different questions. Individual weather conditions are more common than their exact joint overlap.

| Current figure | Topic |
|---|---|
| 4 | Six selected countries: straight parallel coordinates. |
| 5 | The same six countries with bundled lines. |
| 6 | Internet use, fixed broadband and mobile subscriptions. |
| 7 | Internet use rose while landlines fell. |
| 8 | Internet users grouped by region. |
| 9 | The same users grouped by adoption band. |
| 26 | Wind-arrow density and length. |
| 27 | Monthly wind-direction distributions. |
| 28 | Temperature, rain and wind on the same dates. |
| 29 | Separate frequencies and shared occurrence. |


**Principal evidence for a short explanation:** Figures 4-9 connect interactive methods to the infrastructure question; Figure 26 demonstrates the vector experiment; Figure 29 separates marginal prevalence from joint overlap.

**Handoff:** Final answer: averages hide heterogeneity, snapshots hide temporal order, and separate variables hide joint occurrence. Each conclusion depends on its stated units, cohort, scale and time support.

## Implementation boundaries and shared inputs

- A owns the network task and color-mapping task; B owns the complete temporal-method task and contour task; C owns both browser methods and the quiver task. This keeps each required task under one person.
- A prepares the shared scalar normalization conventions and global/local GIFs. B implements and explains contour tracing and the contour GIF. C implements and explains vector conversion and quiver rendering.
- Composite figures reuse those shared outputs. For Figure 20, A assembles monthly means while B owns the contour implementation. For Figure 28, C assembles the aligned composite using the existing scalar, contour and vector outputs. Reuse does not create joint ownership of the original required tasks.
- Shared preprocessing may cover country cohorts, region lookup, weather decoding, masks and units. A can coordinate integration and B numerical checks while C checks browser interactions, but every task owner must understand and verify their own implementation.
- Ten figures each balances the explanation load; it does not prove equal coding effort. C has two interactive browser methods, so shared preparation and final assembly should not all fall to C.

## Contribution record

The report now records this responsibility allocation in the A1 table format. Each person must implement their own distinct SciVis and Infovis tasks, and completed ownership must be recorded truthfully. Speaker order or reading existing code alone does not establish implementation ownership.

Source: supplied A2 brief, task list and specifications 1(f), 2 and 7-10. Final figure IDs are taken directly from `data/current_figure_manifest.json`.
## Current focused recording sequence

14 slides, six main analysis figures. Internet finishes on slide 7 at 3:15; Weather follows on slides 8–14. Internet speaker blocks: Parikshith (1–3), Varshith (4–5), Sindhoor (6–7). Weather blocks: Parikshith (8–9), Sindhoor (10–11), Varshith (12–14). Each block lasts 65 seconds, including the closing hold in the last block.

768 spoken words leave room to point, read the plot and show the brush. The authoritative [recording guide](output/video_presentation/RECORDING_SCRIPT.md) includes the narration and actions. GIFs play on slides 8 and 10. Full implementations and figure ownership in the report remain unchanged.
