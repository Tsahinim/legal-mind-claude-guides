# Builds the "Claude בתוך Excel" series (excel/) as self-contained pages for legalmind.co.il/guides/.
# Usage: py -3 scripts/site-sync/excel_series.py <path to LEGAL-MIND-AI checkout>
# Output: guides/claude-excel*.html + guides/xl/<files>. Re-run after every change in excel/.
# The pages must look exactly like the source: stylesheet and script are inlined, images and downloads
# are copied next to them, links between the series pages point to the site pages.
import html, os, re, shutil, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SITE = sys.argv[1]
GUIDES = os.path.join(SITE, 'guides')
FILE_DIR = 'xl'
BASE = 'https://www.legalmind.co.il/guides/'
GH = 'https://tsahinim.github.io/legal-mind-claude-guides/'

PAGES = [  # source, site file
    ('excel/index.html', 'claude-excel.html'),
    ('excel/guide-1/index.html', 'claude-excel-guide-1.html'),
    ('excel/guide-2/index.html', 'claude-excel-guide-2.html'),
    ('excel/guide-3/index.html', 'claude-excel-guide-3.html'),
    ('excel/bonus/index.html', 'claude-excel-bonus.html'),
]
LINKS = {src: dst for src, dst in PAGES}
URLS = {GH + 'excel/' + p: BASE + d for p, d in
        [('guide-1/', 'claude-excel-guide-1.html'), ('guide-2/', 'claude-excel-guide-2.html'),
         ('guide-3/', 'claude-excel-guide-3.html'), ('bonus/', 'claude-excel-bonus.html'), ('', 'claude-excel.html')]}
COPY_EXT = ('.js', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.pdf', '.xlsx', '.docx', '.zip')

os.makedirs(os.path.join(GUIDES, FILE_DIR), exist_ok=True)
copied = set()


def resolve(src_page, href):
    target = os.path.normpath(os.path.join(os.path.dirname(src_page), href.split('?')[0])).replace('\\', '/')
    if not os.path.splitext(target)[1]:
        target = target.rstrip('/') + '/index.html'
    return target


def copy_file(repo_path):
    # scripts keep their folder in the name (each guide has its own copy); everything else by file name
    name = repo_path.replace('/', '-') if repo_path.endswith('.js') else os.path.basename(repo_path)
    dst = os.path.join(GUIDES, FILE_DIR, name)
    srcf = os.path.join(REPO, repo_path)
    if not os.path.exists(dst) or open(dst, 'rb').read() != open(srcf, 'rb').read():
        shutil.copyfile(srcf, dst)
    copied.add(name)
    return f'{FILE_DIR}/{name}'


def build(src, dst):
    h = open(os.path.join(REPO, src), encoding='utf8').read()
    title = re.search(r'<title>(.*?)</title>', h, re.S).group(1).strip()
    desc_m = re.search(r'<meta name="description" content="([^"]*)">|<meta content="([^"]*)" name="description">', h)
    desc = html.unescape((desc_m.group(1) or desc_m.group(2))) if desc_m else title
    # stylesheet and script -> inline (each page uses its own copy, as on GitHub Pages)
    h = re.sub(r'<link rel="stylesheet" href="([^"]+)">',
               lambda m: '<style>\n' + open(os.path.join(REPO, resolve(src, m.group(1))), encoding='utf8').read() + '\n</style>', h)
    h = re.sub(r'<script src="([^"]+)"></script>',
               lambda m: '<script>\n' + open(os.path.join(REPO, resolve(src, m.group(1))), encoding='utf8').read() + '\n</script>', h)
    h = re.sub(r'src="[^"]*legal-mind-logo-tight\.png"', 'src="legal-mind-logo-tight.png"', h)
    for a in sorted(URLS, key=len, reverse=True):
        h = h.replace(a, URLS[a])

    def fix(m):
        attr, val = m.group(1), m.group(2)
        if re.match(r'^(https?:|mailto:|#|data:|xl/|legal-mind-logo-tight\.png)', val):
            return m.group(0)
        path, _, frag = val.partition('#')
        t = resolve(src, path)
        if t in LINKS:
            return f'{attr}="{LINKS[t] + ("#" + frag if frag else "")}"'
        if t.lower().endswith(COPY_EXT) and os.path.exists(os.path.join(REPO, t)):
            return f'{attr}="{copy_file(t)}"'
        return f'{attr}="{GH + os.path.dirname(t) + "/" if t.endswith("index.html") else GH + t}"'
    h = re.sub(r'(href|src)="([^"]+)"', fix, h)
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
    open(os.path.join(GUIDES, dst), 'w', encoding='utf8', newline='\n').write(h)
    return len(h)


for src, dst in PAGES:
    print(dst, build(src, dst))
for f in os.listdir(os.path.join(GUIDES, FILE_DIR)):      # drop files no longer referenced
    if f not in copied:
        os.remove(os.path.join(GUIDES, FILE_DIR, f))
print('files', len(copied))
