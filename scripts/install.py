"""Install this skill into Codex, refusing to overwrite existing installations."""
import argparse
import os
import shutil
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--destination",type=Path,default=Path(os.environ.get("CODEX_HOME",str(Path.home()/".codex")))/"skills"/"tech-news-ziyou-10s")
a=p.parse_args()
src=Path(__file__).resolve().parent.parent
if a.destination.exists():
    p.exit(1,"Destination exists. Back up or rename it first; no files were changed.\n")
dst=a.destination.resolve()
if dst==src or src in dst.parents:
    p.exit(1,"Destination must be outside this repository.\n")
shutil.copytree(src,dst,ignore=shutil.ignore_patterns(".git","output","__pycache__","*.zip"))
print("Installed:",dst)

