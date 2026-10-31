"""Stable analysis IDs, narrative ordering, figure-reference remapping and sources."""
import re

SECTIONS=[
('Country relationships and paths',[1,2,3],'We establish how links are constructed, compare country histories and inspect relationships hidden inside a community.'),
('Profiles, changes and hierarchies',[4,5,31,6,7,8,9],'We connect paired changes and endpoint profiles, directly test almost equal adoption, then compare associations and user-count hierarchies.'),
('Progress, inequality and timing',[10,11,12,13,14,15,16],'Fixed country identities distinguish progress from catch-up; distributions and trajectories retain the differences behind regional summaries.'),
('Scalar fields and visual encodings',[17,18,19],'Controlled experiments hold measured weather fields fixed while varying palette, temporal normalization and contour representation.'),
('Weather across complete months and days',[20,21,22,23,24,25],'We restore all 92 dates to compare cooling, spatial spread, rainfall concentration, repeated heat and episode timing.'),
('Wind direction and magnitude',[26,27],'Quiver maps locate the flow; monthly direction distributions describe how often different winds occur.'),
('Coincidence, frequency and persistence',[28,29,30,32],'Aligned fields identify joint conditions, full-period counts establish occurrence, and the daily calendar explains why equal frequencies can have unequal run lengths.')]
ORDER=[aid for _,ids,_ in SECTIONS for aid in ids]
NUMBER={aid:i+1 for i,aid in enumerate(ORDER)}

REFERENCES=[
('J. T. Abatzoglou, "Development of gridded surface meteorological data for ecological applications and modelling," International Journal of Climatology, vol. 33, pp. 121-131, 2013. gridMET product and documentation.', 'https://www.climatologylab.org/gridmet.html'),
('Our World in Data, "Internet" and underlying ITU/World Bank indicator metadata. The report uses the preserved A1 extracts, not a newly downloaded release.', 'https://ourworldindata.org/internet'),
('A. A. Hagberg, D. A. Schult and P. J. Swart, "Exploring network structure, dynamics, and function using NetworkX," Proceedings of the 7th Python in Science Conference, pp. 11-15, 2008.', 'https://aric.hagberg.org/papers/hagberg-2008-exploring.pdf'),
('D3 contributors, "What is D3?" and hierarchy/treemap documentation. JavaScript library used for the browser visualizations.', 'https://d3js.org/what-is-d3'),
('M. Bastian, S. Heymann and M. Jacomy, "Gephi: An Open Source Software for Exploring and Manipulating Networks," ICWSM, 2009. Assignment-permitted alternative; not used in this implementation.', 'https://doi.org/10.1609/icwsm.v3i1.13937'),
('ContourPy contributors, "Algorithm description," serial marching-squares/sweep contour generation and interpolation documentation.', 'https://contourpy.readthedocs.io/en/stable/description.html'),
('Matplotlib contributors, "Choosing Colormaps in Matplotlib," sequential and diverging palette guidance.', 'https://matplotlib.org/stable/users/explain/colors/colormaps.html'),
('N. Henry, J.-D. Fekete and M. J. McGuffin, "NodeTrix: A Hybrid Visualization of Social Networks," IEEE TVCG, vol. 13, no. 6, pp. 1302-1309, 2007.', 'https://www.dgp.toronto.edu/~mjmcguff/research/nodetrix/nodetrix.pdf'),
('NOAA National Centers for Environmental Information, "Assessing the U.S. Climate in July 2023," 2023. Independent context for the Southwest heat episode in the selected year.', 'https://www.ncei.noaa.gov/news/national-climate-202307'),
('J. Heinrich et al., "Evaluation of a Bundling Technique for Parallel Coordinates," 2011. Inspiration for the explicit-group, axis-preserving browser curves.', 'https://arxiv.org/abs/1109.6073')]

def remap(text):
    def replace(m):
        prefix,a,b=m.groups();a=NUMBER.get(int(a),int(a))
        return prefix+' '+str(a)+('-'+str(NUMBER.get(int(b),int(b))) if b else '')
    return re.sub(r'\b(Figures?|Figs?\.)\s+(\d+)(?:[-–](\d+))?',replace,text)

def normalize(figures):
    out=[]
    for f in figures:
        f=dict(f);aid=f.get('analysis_id',f['figure']);f['analysis_id']=aid;f['figure']=aid
        if aid<=30:out.append(f)
    return sorted(out,key=lambda f:f['analysis_id'])

def arrange(figures,editorial):
    by={f.get('analysis_id',f['figure']):f for f in figures}
    result=[]
    for aid in ORDER:
        f=by[aid];n=NUMBER[aid];f.update(analysis_id=aid,figure=n,number=n)
        f['explanation']=[remap(x) for x in f['explanation']]
        f.setdefault('caption',f['title'])
        for key in ['caption','detailed_interpretation']:f[key]=remap(f[key])
        f['live_links']=[dict(label=a,url=b) for a,b in editorial.links(aid,n)]
        result.append(f)
    return result
