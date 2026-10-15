"""Fail closed when the cinematic site, media, legal notices or form disappear."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / 'config/site-contract.json').read_text())

class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.text = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
    def handle_data(self, text):
        self.text.append(text)

def validate_html(html, served=False):
    page = Page(html)
    text = ' '.join(page.text)
    for section in CONTRACT['required_sections']:
        assert any(t == 'section' and a.get('id') == section for t, a in page.tags), f'Missing section: {section}'
    assert sum(t == 'section' for t, a in page.tags) >= 14, 'Cinematic page replaced or truncated'
    for project in CONTRACT['projects']:
        assert project in text, f'Missing project: {project}'
    for phrase in ('not an offer to sell', 'loss of principal', 'not a broker-dealer', 'does not guarantee returns', 'planned platform'):
        assert phrase in text, f'Missing disclosure: {phrase}'
    videos = [a for t, a in page.tags if t == 'video']
    assert videos and all(k in videos[0] for k in ('autoplay', 'muted', 'loop', 'playsinline')), 'Hero video contract changed'
    assert videos[0].get('poster') == 'assets/video/hero-poster.jpg', 'Missing hero poster'
    assert any(t == 'source' and a.get('src') == 'assets/video/pegasus-hero-lite.mp4' for t, a in page.tags), 'Missing drone video source'
    assert sum(t == 'img' for t, a in page.tags) >= 13, 'Photo gallery missing'
    forms = [a for t, a in page.tags if t == 'form']
    assert len(forms) == 1 and forms[0].get('name') == 'request-access', 'Existing Netlify form must be preserved'
    assert forms[0].get('method', '').upper() == 'POST' and forms[0].get('action', '/') == '/', 'Form endpoint changed'
    if not served:
        assert forms[0].get('data-netlify') == 'true', 'Netlify form detection missing'
    assert any(t == 'input' and a.get('name') == 'form-name' and a.get('value') == 'request-access' for t, a in page.tags), 'Form routing field missing'
    for name in ('name', 'email'):
        assert any(t == 'input' and a.get('name') == name and 'required' in a for t, a in page.tags), f'Required field missing: {name}'
    assert any(t == 'input' and a.get('name') == 'email' and a.get('type') == 'email' for t, a in page.tags), 'Email validation missing'
    for name in ('role', 'interest', 'message'):
        assert any(a.get('name') == name for t, a in page.tags), f'Original field removed: {name}'
    assert 'supabase' not in html.lower(), 'Do not add a second submission destination'
    assert any(t == 'link' and a.get('rel') == 'canonical' and a.get('href') == CONTRACT['production_url'] for t, a in page.tags), 'Production domain changed'
    return page

def verify(root):
    root = Path(root)
    page = validate_html((root / 'index.html').read_text())
    for path, digest in CONTRACT['assets'].items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, f'Protected binary changed: {path}'
    for tag, attrs in page.tags:
        for key in ('src', 'poster', 'href'):
            value = attrs.get(key, '')
            if value and not value.startswith(('#', 'https:', 'http:', 'mailto:', 'data:')):
                local = urlsplit(value).path
                path = (root / local).resolve()
                assert path.is_relative_to(root.resolve()) and path.is_file(), f'Missing local reference: {value}'
    print('PASS: cinematic content, legal notices, original form and all 14 protected media files')

if __name__ == '__main__':
    verify(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
