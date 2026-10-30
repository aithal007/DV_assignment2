"""Approved report assets: lecture PCP comparison and an actual Marching Squares cell."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'output/internet_revision';ims=[Image.open(p/(x+'.png')).convert('RGB') for x in ['pcp_lecture_straight','pcp_lecture_bundled']]
 out=Image.new('RGB',(ims[0].width,sum(i.height for i in ims)+200),'white');d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',32);y=0
 for im,label in zip(ims,['A. Straight records: each line is a country; color shows region','B. Lecture-inspired bundling: axis density clusters joined by ribbons']):
  d.text((50,y+12),label,fill='#16354b',font=font);out.paste(im,(0,y+60));y+=im.height+100
 out.save(p/'pcp_lecture_comparison.png')
 z=np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz');t=z['tmmx'][4];level=35.
 found=False
 for i in range(t.shape[0]-1):
  for j in range(t.shape[1]-1):
   v=np.array([t[i,j],t[i,j+1],t[i+1,j+1],t[i+1,j]])
   if np.isfinite(v).all() and sum(v>=level) in (1,3) and v.max()-v.min()>1:
    found=True;break
  if found:break
 xy=np.array([[0,0],[1,0],[1,1],[0,1]]);cross=[]
 for k in range(4):
  a,b=k,(k+1)%4
  if (v[a]>=level)!=(v[b]>=level):cross.append(xy[a]+(level-v[a])/(v[b]-v[a])*(xy[b]-xy[a]))
 fig=plt.figure(figsize=(14,2.8));ax=fig.add_axes([.05,.17,.22,.7]);ax.plot([0,1,1,0,0],[0,0,1,1,0],color='#56677a');ax.scatter(xy[:,0],xy[:,1],color='#173f56');ax.plot(*np.array(cross).T,color='#d97722',lw=3)
 for (x,y),value in zip(xy,v):ax.annotate(f'{value:.2f} C',(x,y),xytext=(4,8),textcoords='offset points',fontsize=10)
 ax.set(xlim=(-.2,1.3),ylim=(-.2,1.3),aspect='equal');ax.axis('off');ax.set_title('One actual grid cell: 35 C crossing',fontsize=11)
 text=f'August 22, 2023 | grid row {i}, column {j}\nCompare each corner with 35 C. Two edges cross the threshold.\nOn a crossing edge: fraction = (35 - T1) / (T2 - T1).\nJoin the two interpolated crossings (orange). Repeat across the grid.\nThe contour follows the sampled grid; it does not add measurements.'
 fig.text(.34,.72,text,fontsize=12,va='top',linespacing=1.8);fig.savefig(p/'marching_cell.png',dpi=220,facecolor='white');plt.close(fig)
 original=Image.open(ROOT/'images/scivis/scivis_contour_experiments.png').convert('RGB');inset=Image.open(p/'marching_cell.png').convert('RGB');inset=inset.resize((original.width,round(inset.height*original.width/inset.width)))
 combined=Image.new('RGB',(original.width,original.height+inset.height),'white');combined.paste(original,(0,0));combined.paste(inset,(0,original.height));combined.save(p/'contours_worked.png')
 (p/'marching_cell_values.json').write_text(json.dumps(dict(date='2023-08-22',row=i,column=j,threshold=level,corners=v.tolist(),crossings=np.array(cross).tolist()),indent=2))
if __name__=='__main__':main()
