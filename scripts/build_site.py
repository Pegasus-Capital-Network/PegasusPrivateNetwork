"""Publish only the validated website, never repository instructions or tests."""
from pathlib import Path
import os
import re
import shutil
import subprocess
from verify_site import ROOT, verify

verify(ROOT)
out = ROOT / 'dist'
out.mkdir(exist_ok=True)
# Clear only this generated directory; source files and assets remain untouched.
for path in out.iterdir():
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
for name in ('index.html', 'styles.css', 'script.js'):
    shutil.copy2(ROOT / name, out / name)
shutil.copytree(ROOT / 'assets', out / 'assets')
commit = os.environ.get('COMMIT_REF') or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert re.fullmatch(r'[a-f0-9]{40}', commit), 'Expected a full Git commit SHA'
html = (out / 'index.html').read_text().replace('</head>', f'<meta name="ppn-commit" content="{commit}" /></head>')
(out / 'index.html').write_text(html)
print(f'Built validated website for {commit} into dist/')
