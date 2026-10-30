"""Refresh chart numeric caches from their existing embedded workbook cells.

The exporter writes Excel cell numbers and chart caches at slightly different
floating precision. Preserve the workbooks and formulas; synchronize only caches.
"""
from pathlib import Path,PurePosixPath
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as ET
import io,re,posixpath,json,math

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tmp/video_build/internet_weather_candidate.pptx'
DST=ROOT/'tmp/video_build/internet_weather_validated_candidate.pptx'
C='http://schemas.openxmlformats.org/drawingml/2006/chart'
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/package/2006/relationships'
O='http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def main():
    changes=[];replacement={}
    with ZipFile(SRC) as z:
        for chartname in z.namelist():
            if not re.fullmatch(r'ppt/charts/chart\d+\.xml',chartname):continue
            tree=ET.fromstring(z.read(chartname));ext=tree.find('.//{'+C+'}externalData')
            if ext is None:continue
            relpath=posixpath.join(posixpath.dirname(chartname),'_rels',posixpath.basename(chartname)+'.rels')
            rels=ET.fromstring(z.read(relpath));rid=ext.get('{'+O+'}id')
            target=next(r.get('Target') for r in rels if r.get('Id')==rid)
            bookname=posixpath.normpath(posixpath.join(posixpath.dirname(chartname),target))
            with ZipFile(io.BytesIO(z.read(bookname))) as wb:
                workbook=ET.fromstring(wb.read('xl/workbook.xml'));wbrels=ET.fromstring(wb.read('xl/_rels/workbook.xml.rels'))
                sheets={}
                for sheet in workbook.findall('.//{'+S+'}sheet'):
                    srid=sheet.get('{'+O+'}id');starget=next(r.get('Target') for r in wbrels if r.get('Id')==srid)
                    path=starget.lstrip('/') if starget.startswith('/') else posixpath.normpath(posixpath.join('xl',starget))
                    cells=ET.fromstring(wb.read(path))
                    sheets[sheet.get('name')]={c.get('r'):c.findtext('{'+S+'}v') for c in cells.findall('.//{'+S+'}c')}
                for ref in tree.findall('.//{'+C+'}numRef'):
                    formula=ref.findtext('{'+C+'}f');m=re.fullmatch(r"'?([^']+?)'?!\$([A-Z]+)\$(\d+):\$([A-Z]+)\$(\d+)",formula or '')
                    if not m:continue
                    sheet,col,start,col2,end=m.groups();assert col==col2
                    values=[sheets[sheet][f'{col}{i}'] for i in range(int(start),int(end)+1)]
                    points=ref.findall('.//{'+C+'}pt');assert len(points)==len(values)
                    for pt,new in zip(points,values):
                        v=pt.find('{'+C+'}v');old=v.text
                        assert math.isclose(float(old),float(new),rel_tol=1e-13,abs_tol=1e-13),(old,new)
                        if old!=new:changes.append(dict(chart=chartname,formula=formula,index=int(pt.get('idx')),old=old,new=new));v.text=new
            replacement[chartname]=ET.tostring(tree,encoding='UTF-8',xml_declaration=True,standalone=True)
        with ZipFile(DST,'w',ZIP_DEFLATED) as out:
            for info in z.infolist():out.writestr(info,replacement.get(info.filename,z.read(info.filename)))
    (ROOT/'presentation_source/internet_weather_ppt169_20261024/validation/chart_cache_sync.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
    print(f'Synchronized {len(changes)} numeric cache strings; embedded workbooks and formulas retained.')

if __name__=='__main__':main()
