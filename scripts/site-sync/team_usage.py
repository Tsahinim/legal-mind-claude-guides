# Builds the "מדריך על מנוי Team ב-Claude" series (team/) as self-contained pages for legalmind.co.il/guides/.
# Usage: py -3 scripts/site-sync/team_usage.py <path to LEGAL-MIND-AI checkout>
# Output: guides/claude-team-usage*.html + guides/tu/<hash>.<ext>. Re-run after every change in team/.
import base64, hashlib, html, os, re, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SITE = sys.argv[1]
GUIDES = os.path.join(SITE, 'guides')
IMG_DIR = 'tu'
BASE = 'https://www.legalmind.co.il/guides/'
GH = 'https://tsahinim.github.io/legal-mind-claude-guides/'

PAGES = [  # source, site file, relative depth of the source page
    ('team/index.html', 'claude-team-usage.html', 1),
    ('team/guide-1/index.html', 'claude-team-usage-guide-1.html', 2),
    ('team/guide-2/index.html', 'claude-team-usage-guide-2.html', 2),
    ('team/print/index.html', 'claude-team-usage-practice.html', 2),
]
LINKS = {  # source-relative targets (resolved to repo paths) -> site files
    'team/index.html': 'claude-team-usage.html',
    'team/guide-1/index.html': 'claude-team-usage-guide-1.html',
    'team/guide-2/index.html': 'claude-team-usage-guide-2.html',
    'team/print/index.html': 'claude-team-usage-practice.html',
}
URLS = {  # absolute URLs inside text (the companion prompt) -> site URLs
    GH + 'team/guide-1/': BASE + 'claude-team-usage-guide-1.html',
    GH + 'team/guide-2/': BASE + 'claude-team-usage-guide-2.html',
    GH + 'team/': BASE + 'claude-team-usage.html',
    GH + 'team-migration/': BASE + 'claude-team.html',
    'https://tsahinim.github.io/legal-mind-hub/netlify-deploy/guide-1.html': BASE + 'guide-1.html',
}

css = open(os.path.join(REPO, 'claude-code/assets/site.css'), encoding='utf8').read()
js = open(os.path.join(REPO, 'claude-code/assets/site.js'), encoding='utf8').read()
os.makedirs(os.path.join(GUIDES, IMG_DIR), exist_ok=True)
written_imgs = set()


def save_data_uri(m):
    mime, data = m.group(1), m.group(2)
    raw = base64.b64decode(data)
    ext = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp', 'image/gif': 'gif', 'image/svg+xml': 'svg'}[mime]
    name = f'{IMG_DIR}/{hashlib.sha1(raw).hexdigest()[:16]}.{ext}'
    if name not in written_imgs:
        path = os.path.join(GUIDES, name)
        if not os.path.exists(path) or open(path, 'rb').read() != raw:
            open(path, 'wb').write(raw)
        written_imgs.add(name)
    return name


def resolve(src_page, href):
    base = os.path.dirname(src_page)
    target = os.path.normpath(os.path.join(base, href)).replace('\\', '/')
    if not os.path.splitext(target)[1]:
        target += '/index.html'
    return target


def build(src, dst, depth):
    h = open(os.path.join(REPO, src), encoding='utf8').read()
    title = re.search(r'<title>(.*?)</title>', h, re.S).group(1).strip()
    desc_m = re.search(r'<meta content="([^"]*)" name="description">|<meta name="description" content="([^"]*)">', h)
    desc = (desc_m.group(1) or desc_m.group(2)) if desc_m else title
    # images: inline data URIs -> files
    h = re.sub(r'data:(image/[a-z+]+);base64,([A-Za-z0-9+/=]+)', save_data_uri, h)
    # stylesheet and script -> inline (site pages are self-contained)
    h = re.sub(r'<link[^>]*href="[^"]*claude-code/assets/site\.css[^"]*"[^>]*>', lambda m: '<style>\n' + css + '\n</style>', h)
    h = re.sub(r'<script src="[^"]*claude-code/assets/site\.js[^"]*"></script>', lambda m: '<script>\n' + js + '\n</script>', h)
    h = re.sub(r'src="[^"]*claude-code/assets/legal-mind-logo-tight\.png"', 'src="legal-mind-logo-tight.png"', h)
    # absolute URLs in text first (longest first)
    for a in sorted(URLS, key=len, reverse=True):
        h = h.replace(a, URLS[a])

    def fix_href(m):
        href = m.group(1)
        if re.match(r'^(https?:|mailto:|#|data:|tu/)', href):
            return m.group(0)
        path, _, frag = href.partition('#')
        t = resolve(src, path)
        if t in LINKS:
            return f'href="{LINKS[t] + ("#" + frag if frag else "")}"'
        # anything else in the source repo: point to the public GitHub Pages copy
        return f'href="{GH + os.path.dirname(t) + "/" if t.endswith("index.html") else GH + t}"'
    h = re.sub(r'href="([^"]+)"', fix_href, h)
    # head: canonical, icons, social tags
    url = BASE + dst
    head = (f'<link rel="canonical" href="{url}">\n'
            '<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">\n'
            '<link rel="icon" type="image/png" sizes="192x192" href="favicon-192.png">\n'
            '<link rel="apple-touch-icon" href="favicon-192.png">\n'
            '<meta property="og:type" content="article">\n<meta property="og:locale" content="he_IL">\n'
            '<meta property="og:site_name" content="Legal Mind">\n'
            f'<meta property="og:title" content="{html.escape(title)}">\n'
            f'<meta property="og:description" content="{html.escape(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{BASE}og-guides.jpg">\n'
            '<meta name="twitter:card" content="summary_large_image">\n')
    h = h.replace('</title>', '</title>\n' + head, 1)
    # no visual changes: the page must look exactly like the source
    open(os.path.join(GUIDES, dst), 'w', encoding='utf8', newline='\n').write(h)
    return len(h)


for src, dst, depth in PAGES:
    print(dst, build(src, dst, depth))
# remove images no longer referenced
for f in os.listdir(os.path.join(GUIDES, IMG_DIR)):
    if f'{IMG_DIR}/{f}' not in written_imgs:
        os.remove(os.path.join(GUIDES, IMG_DIR, f))
print('images', len(written_imgs))
