import importlib.util
import unittest
from pathlib import Path
s=importlib.util.spec_from_file_location("renderer",Path(__file__).resolve().parents[1]/"scripts/render.py")
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
class ConfigTest(unittest.TestCase):
    def config(self):
        return {"title":["标题","结论"],"rows":[["标签","内容"]]*5,"segments":[{"start":0,"end":2,"x":0,"y":0,"width":640,"height":359}]}
    def test_odd_height(self):
        m.check_config(self.config(),640,360,2)
    def test_bounds(self):
        c=self.config();c["segments"][0]["width"]=641
        with self.assertRaises(ValueError):m.check_config(c,640,360,2)
    def test_overlap(self):
        c=self.config();c["segments"]*=2
        with self.assertRaises(ValueError):m.check_config(c,640,360,2)
    def test_ass_injection(self):
        c=self.config();c["title"][0]="{bad}"
        with self.assertRaises(ValueError):m.check_config(c,640,360,2)
    def test_nonfinite(self):
        c=self.config();c["segments"][0]["end"]=float("nan")
        with self.assertRaises(ValueError):m.check_config(c,640,360,2)
if __name__=="__main__":unittest.main()

