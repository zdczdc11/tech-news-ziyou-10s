"""Create synthetic source footage and render a self-contained silent demo."""
import argparse
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--font",default="Microsoft YaHei")
args=p.parse_args()
out=root/"output"
out.mkdir(exist_ok=True)
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","testsrc2=size=1280x720:rate=24","-t","6","-c:v","libx264","-pix_fmt","yuv420p",str(out/"source.mp4")],check=True)
subprocess.run([sys.executable,str(root/"scripts/render.py"),"--source",str(out/"source.mp4"),"--config",str(root/"examples/news.json"),"--output",str(out/"demo.mp4"),"--silent","--font",args.font,"--overwrite"],check=True)

