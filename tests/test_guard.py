from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_site import ROOT, verify, validate_html

class RecoveryRegressionTests(unittest.TestCase):
    def test_cinematic_baseline_passes(self):
        verify(ROOT)
    def test_one_page_replacement_fails(self):
        with self.assertRaises(AssertionError):
            validate_html('<html><body><h1>Pegasus Private Network</h1></body></html>')
    def test_changed_registration_destination_fails(self):
        html = (ROOT / 'index.html').read_text().replace('name="request-access"', 'name="new-leads"')
        with self.assertRaises(AssertionError):
            validate_html(html)
    def test_removed_risk_disclosure_fails(self):
        html = (ROOT / 'index.html').read_text().replace('loss of principal', 'no losses')
        with self.assertRaises(AssertionError):
            validate_html(html)
    def test_missing_or_replaced_binary_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'assets', root / 'assets')
            for name in ('index.html', 'styles.css', 'script.js'):
                shutil.copy2(ROOT / name, root / name)
            video = root / 'assets/video/pegasus-hero-lite.mp4'
            video.write_bytes(b'not a video')
            with self.assertRaises(AssertionError):
                verify(root)
            video.unlink()
            with self.assertRaises(FileNotFoundError):
                verify(root)

if __name__ == '__main__':
    unittest.main()
