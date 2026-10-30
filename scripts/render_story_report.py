"""Render the current selected PDF for page-by-page visual inspection."""
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
pdf=fitz.open(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf')
out=ROOT/'tmp/story_report_final'
out.mkdir(parents=True,exist_ok=True)
for i,page in enumerate(pdf):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
    Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(out/f'page-{i+1:02}.png')
for start in range(0,len(pdf),6):
    sheet=Image.new('RGB',(1500,1480),'#dce3e9')
    draw=ImageDraw.Draw(sheet)
    for j in range(start,min(start+6,len(pdf))):
        im=ImageOps.contain(Image.open(out/f'page-{j+1:02}.png'),(490,705))
        x=((j-start)%3)*500;y=((j-start)//3)*740
        sheet.paste(im,(x,y+25));draw.text((x+10,y+5),f'Page {j+1}',fill='black')
    sheet.save(out/f'sheet-{start//6+1}.jpg')
text=''.join(p.get_text() for p in pdf)
assert 'python-Xutf8' not in text
print('Rendered latest',len(pdf),'pages')
print('Footer samples:',[pdf[i].get_text().strip().splitlines()[-1] for i in [0,15,len(pdf)-1]])
