# Current recording script - network revision, 29 October 2026

14 slides; 6:30 raw, approximately 4:49 at 1.35x. The network scenes 2-3 now follow the instructor clarification: all pair scores, an explicit threshold and a recomputed NodeTrix example. The original six-neighbor and Cuba/Palestine examples are superseded. Other scenes and timings are retained. The PDF and final PowerPoint contain matching narration for this revision.

Record slide 2 with the similarity histogram and retained-edge count. Slide 3 uses a clearly labeled five-country excerpt of the 15-country group. Counts of 14 and 7 refer to the full group. For the browser network demonstration, show the default 797 pairs, move the threshold to zero for 15,931 pairs, then reset. GIFs remain embedded on slides 8 and 10. Use desktop PowerPoint Slide Show and preserve the dates and colour bars. Record actual JavaScript brushing for slides 4-5, as described in their actions. Human voice and browser footage still need recording.

## 1. What does the summary leave out?

Parikshith | 0:00-0:10

**Say:** What do averages and snapshots leave out? We examine Internet first, then Weather, following the evidence to a conclusion.

**Do:** State the main question. Explain that Internet finishes before Weather starts. Do not list every method.

**Source:** Current report: question and conclusions

## 2. Similarity needs a visible threshold

Parikshith | 0:10-0:35

**Say:** Madam confirmed that similarity networks are suitable. We now score all fifteen thousand nine hundred and thirty-one country pairs. This histogram shows their similarities. Our declared ninety-fifth-percentile threshold keeps seven hundred and ninety-seven links. Twelve countries have no pair above it, but remain in the data. The browser can show every pair or change the threshold.

**Do:** Point to the histogram and cutoff. State that the top five percent is a transparent starting view, not an optimal or significant threshold. Keep the retained-edge count and isolated-node count visible.

**Source:** Updated report Figure 1; data/network_threshold_audit.json; all-pair scores.

## 3. Groups still contain unequal relationships

Parikshith | 0:35-1:05

**Say:** NodeTrix now uses the filtered graph. Group five retains ninety-three of its one hundred and five possible pairs. This excerpt shows five of its fifteen countries. Afghanistan has fourteen links within the full group, while Angola has seven. Teal means above our similarity threshold; white means below it. A shared group label still hides different relationships. These links describe profiles, not physical cables.

**Do:** Read the five-country excerpt. Compare Afghanistan and Angola; state that 14 and 7 are degrees in the full 15-country group, not only in this excerpt. Explain the Angola-Burundi white cell. Do not count excerpt cells as the full 93 edges.

**Source:** Updated report Figure 3; output/network_revision/nodetrix_detail_matrix.csv and facts.json.

## 4. Does high internet use mean high fixed broadband?

Varshith | 1:05-1:35

**Say:** Does high internet use always come with high fixed broadband? One line follows the same country across four measurements. Each axis has its own scale. Read where the line crosses an axis, not the bend between axes. Faint lines keep the other countries visible. I select at least seventy percent internet use and at most five fixed-broadband subscriptions per hundred people.

**Do:** Show the four axes, then point at the two brush ranges. On the live browser page, apply Inspect high adoption / low broadband. Focus on one selected line; do not demonstrate unrelated controls yet.

**Source:** Report Fig. 4, 5

## 5. Six countries break the simple expectation

Varshith | 1:35-2:10

**Say:** Six of the one hundred and seventy-five matched countries meet both conditions. Their lines start high on internet use and cross low on fixed broadband. Cuba, Kuwait and South Africa are among them. I change the brush, then restore it, to demonstrate the selection. Fixed broadband alone therefore does not describe internet access. We cannot tell from this plot which connection each person uses.

**Do:** Record the real browser interaction from the slide link: apply the preset, move one brush slightly, then restore it. Keep six names and the 6-of-175 denominator visible. Return to the finding slide. Avoid a tour of every feature.

**Source:** Report Fig. 5

## 6. Progress does not mean everyone caught up

Sindhoor | 2:10-2:50

**Say:** Has progress closed the divide? These ridgelines follow the same countries at five dates. Moving right means higher internet use. Each curve shows the spread of countries; small ticks mark individual countries. Africa’s median rises from about zero to thirty-two percent, but its final curve remains wide. Europe moves right and reaches a much higher median. Progress is clear, yet differences remain within and between regions. Curve height is not a count of people.

**Do:** Read the 0–100 horizontal scale once. Trace Africa from 2000 to 2020; point at the wide final curve and the country ticks. Then compare Europe on the SAME scale. These are two labelled panels selected from report Fig. 16, not all regions.

**Source:** Report Fig. 16

## 7. Internet: three findings, one answer

Sindhoor | 2:50-3:15

**Say:** The internet evidence gives a connected answer. The matrix reveals different relationships inside one group. The selected profiles show high internet use with little fixed broadband. The ridgelines show progress with remaining gaps. A single adoption number cannot describe these differences. We need the relationships, other measurements and the spread of countries before saying the divide has closed.

**Do:** Use the three numbered evidence statements to recap the reasoning. Introduce no new figure. Pause before the Weather section.

**Source:** Report Fig. 3, 5, 16

## 8. Weather: can the same colour mislead us?

Parikshith | 3:15-3:45

**Say:** We now move to ninety-two days of United States weather. These animations show the same temperature fields. The left legend stays fixed, so a colour keeps its temperature meaning across dates. The right legend resets each day. Local variation becomes clearer, but the same colour can mean a different temperature. Watch that changing legend. We use fixed scales to compare dates fairly.

**Do:** Stay in desktop PowerPoint Slide Show. Let both embedded GIFs complete at least two 6.4-second loops. Point to each colour bar; do not open another animation window.

**Source:** Report Fig. 17, 18

## 9. A monthly total cannot tell us when rain fell

Parikshith | 3:45-4:20

**Say:** The left map shows September rainfall totals. The right map asks when that rain fell: what share arrived in the wettest five consecutive days? Bright areas have strongly concentrated rain. Across seventy-seven point six percent of the eligible area, at least half the monthly rain fell within five days. A monthly total therefore hides whether rain arrived steadily or in short bursts. Daily observations recover that timing.

**Do:** Read the monthly-total map on the left, then the wettest-five-day share on the right. Point to the 0–100% legend. State that 77.6% is eligible area, not a percentage of all rain. Eligible cells have September rainfall of at least 10 mm.

**Source:** Report Fig. 23

## 10. Contours let us follow temperature boundaries

Sindhoor | 4:20-4:45

**Say:** Each contour line follows equal temperature, while filled bands show ranges. As dates advance, we can follow those boundaries. Smaller intervals expose more detail but create more lines to read. We choose an interval that keeps the regional pattern visible. More detail is useful only when it helps answer the question.

**Do:** Let the embedded contour GIF complete two loops. Point to one boundary and its value on the legend. Explain why changing the interval changes detail; keep the same temperature field as the reference.

**Source:** Report Fig. 19

## 11. How often and how long are different questions

Sindhoor | 4:45-5:25

**Say:** The left map counts how often a place was both hot and dry. The right records its longest uninterrupted run. Hot means at least thirty-five degrees; dry means less than one millimetre of daily rain. Many qualifying days can be separated by breaks, so frequency cannot tell us persistence. The longest local run in this ninety-two-day window is sixty-seven days. Reading both maps separates repeated events from sustained conditions.

**Do:** Read the left frequency legend and the right run-length legend separately. Point to the southwest pattern and compare the maps; do not equate their colours because the units differ. The 67-day maximum is somewhere in the grid and is bounded by the study window.

**Source:** Report Fig. 30

## 12. Arrow length changes the pattern we notice

Varshith | 5:25-6:00

**Say:** Both maps use the same wind field and sampled locations. On the left, arrow length grows with speed, so slow winds can be hard to follow. Equal lengths on the right make directions clearer; colour still shows speed. Arrows point where air moves, after converting the source wind-from direction. The measurements stay the same. We choose the view according to whether we need speed differences or direction patterns.

**Do:** Compare the same western-US area in the two panels. Both retain every fourth sampled grid cell from the source experiment. Point first to short arrows and then to matching equal-length arrows. Use the retained common speed colour key.

**Source:** Report Fig. 26

## 13. What do averages and snapshots leave out?

Varshith | 6:00-6:24

**Say:** Our answer is that summaries leave out differences and time. For Internet, the group label and adoption number miss different country profiles and uneven progress. For Weather, monthly totals and event counts miss bursts and long uninterrupted spells. The strongest explanation therefore pairs the summary with the detail needed for the question, and draws its conclusion from that visible evidence.

**Do:** Connect each conclusion to the named evidence already shown. Introduce no new numbers or chart. Advance to credits after the final sentence.

**Source:** Report Fig. 3, 5, 16, 23, 30

## 14. Team Plot Twist

Silent closing card | 6:24-6:30

**Say:** [Silent closing hold]

**Do:** Hold for six seconds. End recording.

**Source:** Current report: question and conclusions
