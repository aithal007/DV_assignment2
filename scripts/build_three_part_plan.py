"""Write a proposed A1-style allocation against the final thirty-figure manifest."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
FIGURES=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
PARTS=[
 dict(part='A',name='Parikshith Aithal K V',title='Patterns, profiles and trustworthy comparisons',
      question='Which patterns are supported by the data, and which impressions depend on how we draw or aggregate it?',
      infovis='Network: construction, three layouts, search/selection/filtering, country trajectories and profile interpretation.',
      scivis='Color mapping: continuous/discrete palettes, normalization, global/local extrema, global/local scalar GIFs.',
      ids=[1,2,3,17,18,20,21,22,23,25],
      finding='Similar adoption can accompany different infrastructure profiles. Fixed scales and complete daily coverage distinguish measured differences from drawing or sampling effects.',
      anchor='Figures 1-3 show layout effects, country paths and NodeTrix links; Figures 17-18 establish fair scalar comparisons; Figure 23 shows how monthly totals hide concentrated rainfall.',
      handoff='The comparisons are now consistent. But has progress actually reduced inequality, and does an average describe the countries or places behind it?'),
 dict(part='B',name='Sindhoor Ganapathi Hegde',title='The digital divide, trajectories and hidden persistence',
      question='Does broad progress mean convergence, and what do averages hide about individual changes and persistent conditions?',
      infovis='Temporal methods: both horizon variations and both ridgeline variations, with their baselines, cohorts and density checks.',
      scivis='Contour mapping: Marching Squares-family tracing, lines/fills, interval comparison and contour GIF.',
      ids=[10,11,12,13,14,15,16,19,24,30],
      finding='Regional summaries hide country differences: 47% of measured 2020 variation lies within regions. Regional median shifts differ from typical individual gains. Event frequency differs from uninterrupted duration.',
      anchor='Figures 10-12 connect timing to within-region variation and country gains; Figures 13-16 demonstrate the required temporal methods; Figure 30 distinguishes event counts from persistent runs.',
      handoff='Progress is real but uneven, and a summary can conceal very different experiences. Which infrastructure relationships remain when we inspect the original measurements and their changes?'),
 dict(part='C',name='Varshith M Gowda',title='Infrastructure relationships, interactions and the final answer',
      question='Which relationships survive inspection across variables, country changes and joint conditions?',
      infovis='JavaScript browser methods: bundled parallel coordinates with brushing/reordering AND zoomable treemap with two hierarchy remodelings.',
      scivis='Quiver: spatial sampling, proportional versus equal arrow lengths, meteorological FROM to flow TO conversion and speed key.',
      ids=[4,5,6,7,8,9,26,27,28,29],
      finding='The strong broadband/adoption association across country levels does not describe matched changes. User counts and adoption shares answer different questions. Individual weather conditions are more common than their exact joint overlap.',
      anchor='Figures 4-9 connect interactive methods to the infrastructure question; Figure 26 demonstrates the vector experiment; Figure 29 separates marginal prevalence from joint overlap.',
      handoff='Final answer: averages hide heterogeneity, snapshots hide temporal order, and separate variables hide joint occurrence. Each conclusion depends on its stated units, cohort, scale and time support.'),
]

def main():
    ids=[n for p in PARTS for n in p['ids']]
    assert sorted(ids)==list(range(1,31)) and len(set(ids))==30
    titles={f['figure']:f['title'] for f in FIGURES}
    text=['# Assignment 2: final three-part plan',
      'Adopted responsibility allocation using the current **20-page, 30-figure report**, with the A1 member names and student IDs. The report now includes the allocation table. This assigns responsibility without certifying unconfirmed completed work. The video follows the continuous question-to-evidence story described in output/video_presentation/RECORDING_SCRIPT.md.',
      '**Main question:** What do averages and snapshots hide about inequality, relationships and change over time?',
      '## Three linked parts',
      '| Part | Proposed person | Story role | Required Infovis work package | Required SciVis task |\n|---|---|---|---|---|']
    for p in PARTS:text.append(f"| {p['part']}: {p['title']} | {p['name']} | {p['question']} | {p['infovis']} | {p['scivis']} |")
    text+=['\nThis follows the A1 structure: the first part establishes the patterns, the second tests whether progress closes the divide, and the third inspects infrastructure relationships and gives the qualified verdict. Weather supplies a separate case study of the same visualization question; no country-weather causal connection is asserted.',
      '## Exact allocation: ten figure sets each',
      'The current report remains in its reading order. These are responsibility and presentation sets, so figure numbers are intentionally nonconsecutive. Reordering or renumbering the PDF is unnecessary.']
    for p in PARTS:
        text += [f"### Part {p['part']}: {p['name']}",f"**Question:** {p['question']}",f"**Answer:** {p['finding']}",
          '| Current figure | Topic |\n|---|---|']
        text.extend(f'| {n} | {titles[n]} |' for n in p['ids'])
        text += [f"\n**Principal evidence for a short explanation:** {p['anchor']}",f"**Handoff:** {p['handoff']}"]
    text+=['## Implementation boundaries and shared inputs',
      '- A owns the network task and color-mapping task; B owns the complete temporal-method task and contour task; C owns both browser methods and the quiver task. This keeps each required task under one person.\n- A prepares the shared scalar normalization conventions and global/local GIFs. B implements and explains contour tracing and the contour GIF. C implements and explains vector conversion and quiver rendering.\n- Composite figures reuse those shared outputs. For Figure 20, A assembles monthly means while B owns the contour implementation. For Figure 28, C assembles the aligned composite using the existing scalar, contour and vector outputs. Reuse does not create joint ownership of the original required tasks.\n- Shared preprocessing may cover country cohorts, region lookup, weather decoding, masks and units. A can coordinate integration and B numerical checks while C checks browser interactions, but every task owner must understand and verify their own implementation.\n- Ten figures each balances the explanation load; it does not prove equal coding effort. C has two interactive browser methods, so shared preparation and final assembly should not all fall to C.',
      '## Continuous video explanation',
      'The user requires a final video under five minutes. Record 6:30 total and export at 1.35x for approximately 4:49. Each member speaks for 2:10 across two appearances. The presentation has 17 slides, including the browser-demo reference frames and closing card.',
      '| Raw time | Speaker | Focus |\n|---|---|---|\n| 0:00-1:05 | A | Main question, network and country trajectories. |\n| 1:05-2:10 | B | Inequality, regional gains and temporal methods. |\n| 2:10-3:15 | C | JavaScript demonstration and levels versus changes. |\n| 3:15-4:20 | A | Weather scales and rainfall concentration. |\n| 4:20-5:25 | B | Contours and frequency versus persistence. |\n| 5:25-6:30 | C | Quiver, intersections, conclusion and closing card. |',
      'Use the full report for detailed method questions. A short explanation should feature a few decisive figures, while each person prepares all ten allocated figures. Keep live browser demonstrations ready rather than treating screenshots as interaction evidence.',
      '## Contribution record',
      'The report now records this responsibility allocation in the A1 table format. Each person must implement their own distinct SciVis and Infovis tasks, and completed ownership must be recorded truthfully. Speaker order or reading existing code alone does not establish implementation ownership.',
      'Source: supplied A2 brief, task list and specifications 1(f), 2 and 7-10. Final figure IDs are taken directly from `data/current_figure_manifest.json`.']
    rendered=text[0]
    for previous,current in zip(text,text[1:]):
        separator='\n' if previous.rstrip().endswith('|') and current.startswith('|') else '\n\n'
        rendered+=separator+current
    (ROOT/'PRESENTATION_PLAN.md').write_text(rendered,encoding='utf-8')
    (ROOT/'data/proposed_three_part_split.json').write_text(json.dumps(dict(status='adopted responsibility allocation; completed-work attribution requires verification',parts=PARTS),indent=2),encoding='utf-8')
    print('Saved three-part plan: 10 figures per person; all 30 allocated exactly once.')

if __name__=='__main__':main()
