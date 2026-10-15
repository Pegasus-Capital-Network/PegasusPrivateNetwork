"""Verify the exact PR commit and all media on Netlify without submitting leads."""
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import URLError
from verify_site import CONTRACT, Page, validate_html
import hashlib
import json
import sys
import time

number, commit = sys.argv[1:3]
assert number.isdigit() and len(commit) == 40
base = f'https://deploy-preview-{number}--{CONTRACT["site_name"]}.netlify.app/'
def get(path):
    req = Request(base + path, headers={'Cache-Control': 'no-cache', 'User-Agent': 'Pegasus-preview-verification'})
    with urlopen(req, timeout=20) as response:
        assert response.status == 200
        return response.read()

# A previous preview can still be serving while Netlify builds the new commit.
for attempt in range(36):
    try:
        html = get('').decode()
        page = Page(html)
        if any(t == 'meta' and a.get('name') == 'ppn-commit' and a.get('content') == commit for t, a in page.tags):
            break
    except (URLError, TimeoutError):
        pass
    if attempt == 35:
        raise RuntimeError('No ready Netlify preview for the exact PR head; refusing a stale preview')
    time.sleep(10)
validate_html(html, served=True)
def check(item):
    path, expected = item
    assert hashlib.sha256(get(path)).hexdigest() == expected, f'Preview binary mismatch: {path}'
    return path
with ThreadPoolExecutor(max_workers=6) as pool:
    paths = list(pool.map(check, CONTRACT['assets'].items()))
for path in ('styles.css', 'script.js'):
    assert get(path), f'Empty asset: {path}'
print(json.dumps({'preview': base, 'commit': commit, 'media_verified': len(paths), 'form': 'request-access; no test lead sent'}, indent=2))
