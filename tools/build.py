"""Build only reviewed public host files; project sites stay in their own repos."""
import hashlib
import json
import os
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://kllollain-max.github.io/'
PUBLIC = ('index.html', '404.html', 'robots.txt', 'ads.txt', 'sitemap.xml', 'host-sitemap.xml', '.nojekyll')

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.meta = {}; self.links = []; self.scripts = []; self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta': self.meta[attrs.get('name', '')] = attrs.get('content', '')
        if tag == 'a': self.links.append(attrs.get('href', ''))
        if tag == 'script': self.scripts.append(attrs)

def build():
    source = (ROOT / 'index.html').read_text()
    page = Page(source)
    assert page.meta['google-adsense-account'] == 'ca-pub-3308170767665245'
    assert page.meta['naver-site-verification'] == '573a080f3a1917fae1389846b6cfe99a9450ed3c'
    assert not page.scripts, 'Host portal must not request ads or third-party scripts'
    assert page.links and all(link.startswith(('/careerpick/', '/supportpick/')) for link in page.links)
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    index = ET.fromstring((ROOT / 'sitemap.xml').read_bytes())
    expected = [BASE + 'host-sitemap.xml', BASE + 'careerpick/sitemap.xml', BASE + 'supportpick/sitemap.xml']
    assert index.tag == '{' + ns['s'] + '}sitemapindex'
    assert [node.text for node in index.findall('s:sitemap/s:loc', ns)] == expected
    urls = ET.fromstring((ROOT / 'host-sitemap.xml').read_bytes())
    assert [node.text for node in urls.findall('s:url/s:loc', ns)] == [BASE]
    robots = (ROOT / 'robots.txt').read_text()
    assert 'Disallow:' not in robots and all(url in robots for url in expected[1:])
    expected_ads = {
        'google.com, pub-3308170767665245, DIRECT, f08c47fec0942fa0',
        'google.com, pub-4206368432511517, DIRECT, f08c47fec0942fa0',
    }
    ads_lines = (ROOT / 'ads.txt').read_text().splitlines()
    assert len(ads_lines) == len(expected_ads) and set(ads_lines) == expected_ads, (
        'ads.txt must contain each approved publisher entry exactly once'
    )
    output = ROOT / '_site'
    if output.exists(): shutil.rmtree(output)
    output.mkdir()
    hashes = {}
    for name in PUBLIC:
        shutil.copyfile(ROOT / name, output / name)
        hashes[name] = hashlib.sha256((output / name).read_bytes()).hexdigest()
    manifest = {'sourceRevision': os.environ.get('GITHUB_SHA', 'local'), 'files': hashes,
                'projectSitesChanged': False, 'advertisingScripts': 0}
    (output / 'host-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    assert {p.name for p in output.iterdir()} == set(PUBLIC) | {'host-manifest.json'}
    print(json.dumps({'public_files': len(PUBLIC) + 1, 'sitemap_children': len(expected), 'advertising_scripts': 0}))

if __name__ == '__main__': build()
