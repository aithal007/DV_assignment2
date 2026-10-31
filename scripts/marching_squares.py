"""Independent 16-case marching squares with linear edge interpolation.

Corner bits follow grid indices (i,j), (i,j+1), (i+1,j+1), (i+1,j):
BL, BR, TR, TL for increasing y. Both coordinate directions work.
Values exactly at the level are below. Ambiguous saddles
use the arithmetic corner mean, matching ContourPy serial with linear
z interpolation, quad_as_tri=False and corner_mask=False.
"""
import numpy as np

CASES={0:[],1:[(3,0)],2:[(0,1)],3:[(3,1)],4:[(1,2)],
       6:[(0,2)],7:[(3,2)],8:[(2,3)],9:[(0,2)],11:[(1,2)],
       12:[(3,1)],13:[(0,1)],14:[(3,0)],15:[]}
EDGES=((0,1),(1,2),(2,3),(3,0))

def cell_segments(xy,values,level):
    values=np.asarray(values,dtype=float)
    if not np.isfinite(values).all():return []
    case=sum((int(v>level)<<k) for k,v in enumerate(values))
    if case==5:pairs=[(0,1),(2,3)] if values.mean()>level else [(3,0),(1,2)]
    elif case==10:pairs=[(3,0),(1,2)] if values.mean()>level else [(0,1),(2,3)]
    else:pairs=CASES[case]
    def crossing(edge):
        a,b=EDGES[edge];fraction=(level-values[a])/(values[b]-values[a])
        return xy[a]+fraction*(xy[b]-xy[a])
    return [np.array([crossing(a),crossing(b)]) for a,b in pairs if np.linalg.norm(crossing(a)-crossing(b))>1e-12]

def segments(x,y,z,level):
    x,y,z=np.asarray(x),np.asarray(y),np.asarray(z)
    if z.shape!=(len(y),len(x)):raise ValueError('Grid shape does not match coordinates')
    answer=[]
    for i in range(len(y)-1):
        for j in range(len(x)-1):
            v=z[[i,i,i+1,i+1],[j,j+1,j+1,j]]
            xy=np.array([[x[j],y[i]],[x[j+1],y[i]],[x[j+1],y[i+1]],[x[j],y[i+1]]])
            answer.extend(cell_segments(xy,v,level))
    return np.array(answer).reshape(-1,2,2)

def canonical(lines,decimals=8):
    result=set()
    for line in lines:
        for a,b in zip(line[:-1],line[1:]):
            if np.linalg.norm(a-b)>1e-12:result.add(tuple(sorted((tuple(np.round(a,decimals)),tuple(np.round(b,decimals))))))
    return result

def validate(x,y,z,levels):
    import contourpy
    xy=np.array([[0.,0.],[1.,0.],[1.,1.],[0.,1.]])
    count=0
    # Test all configurations and both saddle-center resolutions.
    for case in range(16):
        for magnitude in [.5,2.]:
            values=np.array([magnitude if case&(1<<k) else -1. for k in range(4)])
            grid=values[[0,1,3,2]].reshape(2,2)
            ours=cell_segments(xy,values,0)
            ref=contourpy.contour_generator(x=[0.,1.],y=[0.,1.],z=grid,name='serial',corner_mask=False).lines(0)
            assert canonical(ours)==canonical(ref),(case,magnitude)
            count+=1
    comparisons=[]
    generator=contourpy.contour_generator(x=x,y=y,z=np.ma.masked_invalid(z),name='serial',corner_mask=False)
    for level in levels:
        ours=segments(x,y,z,level);a=canonical(ours);b=canonical(generator.lines(level))
        assert a==b,(level,len(a-b),len(b-a))
        comparisons.append(dict(level_C=float(level),segments=len(a),identical_quantized_segments=True))
    assert not len(segments([0,1],[0,1],np.full((2,2),np.nan),0))
    return dict(status='PASS',synthetic_case_checks=count,masked_cells_skipped=True,coordinate_tolerance_degrees=1e-8,real_grid=comparisons)
