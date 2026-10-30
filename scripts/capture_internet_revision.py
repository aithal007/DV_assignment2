"""Capture current browser renderings, retaining full-page interaction evidence."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import threading,subprocess
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/internet_revision';OUT.mkdir(exist_ok=True)
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    pages={
      'pcp_straight':'index.html?year=2020&bundle=0&matched=1&fixed=1',
      'pcp_focus':'index.html?year=2020&bundle=50&matched=1&fixed=1&focus=1',
      'treemap_root_region':'treemap.html?hierarchy=region',
      'treemap_root_adoption':'treemap.html?hierarchy=adoption',
      'treemap_zoom':'treemap.html?hierarchy=region&zoom=Asia',
    }
    try:
        for name,url in pages.items():
            target=OUT/f'{name}.png'
            result=subprocess.run([CHROME,'--headless=new','--disable-gpu','--no-first-run','--hide-scrollbars','--window-size=1600,1050','--virtual-time-budget=5000',f'--screenshot={target}',f'http://127.0.0.1:{server.server_port}/web/{url}&report=1'],capture_output=True,timeout=45)
            assert result.returncode==0 and target.exists(),result.stderr[-1000:]
            im=Image.open(target).convert('RGB');box=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
            if box:im.crop((max(0,box[0]-15),max(0,box[1]-15),min(im.width,box[2]+15),min(im.height,box[3]+15))).save(target)
            print(name,flush=True)
        target=OUT/'pcp_focus_full_ui.png'
        subprocess.run([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--window-size=1600,1400','--virtual-time-budget=5000',f'--screenshot={target}',f'http://127.0.0.1:{server.server_port}/web/index.html?year=2020&bundle=50&focus=1'],capture_output=True,timeout=45,check=True)
    finally:server.shutdown()
if __name__=='__main__':main()
