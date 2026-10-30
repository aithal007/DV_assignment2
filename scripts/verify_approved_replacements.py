"""Independent numerical and integration checks for the approved replacements."""
from pathlib import Path
import csv,json,statistics,math
R=Path(__file__).resolve().parents[1]
def ranks(values):
 ordered=sorted(enumerate(values),key=lambda z:z[1]);result=[0.]*len(values);start=0
 while start<len(ordered):
  end=start+1
  while end<len(ordered) and ordered[end][1]==ordered[start][1]:end+=1
  for idx,_ in ordered[start:end]:result[idx]=(start+1+end)/2
  start=end
 return result
rows=json.loads((R/'data/infovis_countries.json').read_text());a={r['code']:r for r in rows if r['year']==2015};b={r['code']:r for r in rows if r['year']==2020};codes=sorted(a.keys()&b.keys());assert len(codes)==175
y='internet_users_share_pct';keys={'Fixed broadband':'broadband_subs_per100','Landlines':'telephone_lines_per100','Mobile':'mobile_subs_per100'}
with (R/'output/proposals_20261026/fig7_association_values.csv').open() as stream:
 for row in csv.DictReader(stream):
  key=keys[row['measure']]
  for name,delta in [('levels',False),('gains',True)]:
   xv=[b[c][key]-(a[c][key] if delta else 0) for c in codes];yv=[b[c][y]-(a[c][y] if delta else 0) for c in codes];rho=statistics.correlation(ranks(xv),ranks(yv));assert math.isclose(rho,float(row[name]),abs_tol=1e-12)
with (R/'data/internet_panel_2000_2020.csv').open() as stream:
 panel={}
 for row in csv.DictReader(stream):panel.setdefault(row['code'],{})[int(row['year'])]=float(row[y])
assert len(panel)==159 and all(len(v)==21 for v in panel.values());ordered=sorted(panel,key=lambda c:(panel[c][2000],c));cohorts=[ordered[i*53:(i+1)*53] for i in range(3)];assert len(set(sum(cohorts,[])))==159
with (R/'output/proposals_20261026/fig10_cohort_summary.csv').open() as stream:
 for members,row in zip(cohorts,csv.DictReader(stream)):
  for year in [2000,2020]:assert math.isclose(statistics.median(panel[c][year] for c in members),float(row[f'median_{year}']),abs_tol=1e-12)
  q=statistics.quantiles([panel[c][2020] for c in members],n=4,method='inclusive');assert math.isclose(q[0],float(row['q25_2020']),abs_tol=1e-12) and math.isclose(q[2],float(row['q75_2020']),abs_tol=1e-12)
with (R/'output/internet_revision/pcp_gentle_values.csv').open() as stream:
 for row in csv.DictReader(stream):
  c=row['code']
  for key in [y,*keys.values()]:assert math.isclose(float(row[key]),b[c][key],abs_tol=1e-12)
manifest=json.loads((R/'data/current_figure_manifest.json').read_text(encoding='utf-8'));selected={f['figure']:f for f in manifest}
assert selected[5]['extension_key']=='gentle_pcp' and selected[7]['extension_key']=='association_audit' and selected[10]['extension_key']=='fixed_initial_cohorts'
assert selected[4]['extension_key']=='paired_change_pcp'
change_fields=[y,*keys.values()]
with (R/'output/pcp_changes/paired_changes.csv').open() as stream:
 changes=list(csv.DictReader(stream))
assert len(changes)==175 and len({r['code'] for r in changes})==175
for row in changes:
 for key in change_fields:assert math.isclose(float(row[key]),b[row['code']][key]-a[row['code']][key],abs_tol=1e-12)
chosen=[r for r in changes if 20<=float(r[y])<=30];assert len(chosen)==39
embedded=(R/'output/pcp_changes/data.js').read_text(encoding='utf-8')
js_rows=json.loads(embedded.removeprefix('const records=').removesuffix(';'))
for row in js_rows:
 for key in change_fields:assert math.isclose(row[key],b[row['code']][key]-a[row['code']][key],abs_tol=1e-9)
new_browser=json.loads((R/'output/pcp_changes/browser_validation.json').read_text())
assert new_browser['status']=='PASS' and all(new_browser[k] for k in ['pointer_brushing','reordering','hover','toggle','reset'])
report=(R/'REPORT.md').read_text(encoding='utf-8');assert '53.8 percentage points' in report and 'fixed starting groups' in report and 'These rows add a sequence to the milestone counts' not in report
browser=json.loads((R/'output/infovis_audit_20261026/interactions.json').read_text());assert browser['parallel_coordinates']['axis_values_unchanged'] and browser['parallel_coordinates']['hover_values_checked'] and not browser['errors']
result=dict(status='PASS',independent_spearman_checks=6,fixed_cohort_countries=159,group_sizes=[53]*3,endpoint_medians_checked=6,endpoint_quartiles_checked=6,pcp_country_values_checked=700,change_pcp_values_checked=700,change_pcp_selected=39,approved_figures=[4,5,7,10],browser_interactions='PASS')
(R/'output/approved_replacements_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
