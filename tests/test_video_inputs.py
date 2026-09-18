import json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from video import validate_job
class VideoInputTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'audio.wav').write_bytes(b'fixture');self.put([[],[]]);self.job=dict(duration=1,audio='audio.wav',mouth_events='mouths.json')
 def put(self,parts):(self.root/'mouths.json').write_text(json.dumps(parts))
 def test_no_private_scene_needed(self):validate_job(self.job,self.root)
 def test_missing_audio_fails_before_render(self):
  (self.root/'audio.wav').unlink()
  with self.assertRaises(FileNotFoundError):validate_job(self.job,self.root)
 def test_overlapping_mouth_events_rejected(self):
  self.put([[dict(start=0,end=.7,vowel='a'),dict(start=.5,end=1,vowel='o')],[]])
  with self.assertRaises(ValueError):validate_job(self.job,self.root)
 def test_abutting_boundary_float_roundoff_accepted(self):
  self.put([[dict(start=0,end=.7,vowel='a'),dict(start=.7-1e-15,end=1,vowel='o')],[]])
  validate_job(self.job,self.root)
 def test_odd_resolution_rejected(self):
  self.job['width']=1919
  with self.assertRaises(ValueError):validate_job(self.job,self.root)
if __name__=='__main__':unittest.main()
