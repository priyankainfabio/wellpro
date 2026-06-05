import base64
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import requests

root = Path('docs')
root.mkdir(parents=True, exist_ok=True)
assets_dir = root / 'assets'
assets_dir.mkdir(parents=True, exist_ok=True)

page_map = {
    'home.html': 'index.html',
    'about-us.html': os.path.join('about-us', 'index.html'),
    'contact-us.html': os.path.join('contact-us', 'index.html'),
    'diabetes-assist-program_index.html': os.path.join('diabetes-assist-program', 'index.html'),
    'wellness-protocol-basis.html': os.path.join('wellness-protocol-basis', 'index.html'),
    os.path.join('extra', 'advisory-board.html'): os.path.join('advisory-board', 'index.html'),
    os.path.join('extra', 'blog.html'): os.path.join('blog', 'index.html'),
    os.path.join('extra', 'cholesterol__index.html'): os.path.join('cholesterol', 'index', 'index.html'),
    os.path.join('extra', 'diabetes-assist-program__buy-now.html'): os.path.join('diabetes-assist-program', 'buy-now', 'index.html'),
    os.path.join('extra', 'diabetes-assist-program__diabetes-reversal.html'): os.path.join('diabetes-assist-program', 'diabetes-reversal', 'index.html'),
    os.path.join('extra', 'diabetes-reversal__index.html'): os.path.join('diabetes-reversal', 'index', 'index.html'),
    os.path.join('extra', 'doctor-assist.html'): os.path.join('doctor-assist', 'index.html'),
    os.path.join('extra', 'doctor-assist-registration__index.html'): os.path.join('doctor-assist-registration', 'index', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__cholesterol.html'): os.path.join('lifestyle-disorders', 'cholesterol', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__depression.html'): os.path.join('lifestyle-disorders', 'depression', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__diabetes.html'): os.path.join('lifestyle-disorders', 'diabetes', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__erectile-dysfunction.html'): os.path.join('lifestyle-disorders', 'erectile-dysfunction', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__immune-system.html'): os.path.join('lifestyle-disorders', 'immune-system', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__joint-pain.html'): os.path.join('lifestyle-disorders', 'joint-pain', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__thyroid.html'): os.path.join('lifestyle-disorders', 'thyroid', 'index.html'),
    os.path.join('extra', 'lifestyle-disorders__vegan-omega-oil.html'): os.path.join('lifestyle-disorders', 'vegan-omega-oil', 'index.html'),
    os.path.join('extra', 'pcod__index.html'): os.path.join('pcod', 'index', 'index.html'),
    os.path.join('extra', 'refund-and-exchange-policy.html'): os.path.join('refund-and-exchange-policy', 'index.html'),
    os.path.join('extra', 'soleus__index.html'): os.path.join('soleus', 'index', 'index.html'),
    os.path.join('extra', 'wellness-dietitian__registration.html'): os.path.join('wellness-dietitian', 'registration', 'index.html'),
    os.path.join('extra', 'wellpro.html'): os.path.join('wellpro', 'index.html'),
}

# Create page folders
for output_path in page_map.values():
    output_file = root / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

with open('mirror_raw/url_map.json', 'r', encoding='utf-8') as f:
    url_map = json.load(f)

# Use a more descriptive filename for Google Fonts CSS when available.
fonts_key = next((key for key in url_map if 'fonts.googleapis.com/css' in key), None)
if fonts_key:
    google_fonts_path = 'assets/css/google-fonts.css'
    old_path = url_map[fonts_key]
    if old_path != google_fonts_path:
        url_map[fonts_key] = google_fonts_path
        old_file = root / old_path
        new_file = root / google_fonts_path
        if old_file.exists():
            if new_file.exists() and old_file.read_bytes() == new_file.read_bytes():
                old_file.unlink()
            else:
                new_file.parent.mkdir(parents=True, exist_ok=True)
                old_file.replace(new_file)

# Add a normalized fallback map for app-sources URLs without query strings.
normalized_map = {}
for raw_url, local_path in url_map.items():
    if 'content.app-sources.com' in raw_url:
        parsed = re.sub(r'\?.*$', '', raw_url)
        if parsed != raw_url and parsed not in url_map:
            normalized_map[parsed] = local_path
url_map.update(normalized_map)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.265 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://wellpro.one/',
    'Connection': 'keep-alive',
}

REMOVE_PATTERNS = [
    'googletagmanager.com',
    'google-analytics.com',
    'doubleclick.net',
    'googleadservices.com',
    'googlesyndication.com',
    'convert.gocommercially.com',
    'apps.elfsight.com',
    'play.fabulousmedia.in',
    'youtube.com',
    'docs.google.com',
    'elfsight',
    'service-api.app-sources.com',
]

KEEP_PATTERNS = [
    'static.web-repository.com',
    'code.jquery.com',
    'cdn.jsdelivr.net',
    'cdnjs.cloudflare.com',
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'content.app-sources.com',
]


def normalize_app_sources_url(url: str) -> str:
    if url.startswith('//'):
        url = 'https:' + url
    parsed = urlparse(url)
    if 'content.app-sources.com' not in parsed.netloc:
        return url
    path = parsed.path
    if '/thumbnails/' in path:
        path = path.replace('/thumbnails/640x480/', '/uploads/')
        path = path.replace('/thumbnails/', '/uploads/')
    return urlunparse(parsed._replace(path=path, query=''))


def safe_filename(url: str, folder: Path) -> Path:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name:
        name = 'asset'
    name = re.sub(r'[^A-Za-z0-9._-]+', '-', name)
    if not Path(name).suffix:
        name += '.bin'
    return folder / name


def download_file(url: str, folder: Path) -> Path | None:
    if url.startswith('//'):
        url = 'https:' + url
    if any(pattern in url for pattern in REMOVE_PATTERNS):
        return None
    if not any(pattern in url for pattern in KEEP_PATTERNS):
        return None
    url = normalize_app_sources_url(url)
    target = safe_filename(url, folder)
    if target.exists():
        return target
    print('download', url, '->', target)
    try:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
    except requests.RequestException as exc:
        print('failed', url, exc)
        return None
    content_type = r.headers.get('content-type', '')
    if target.suffix == '.bin' and content_type:
        ext = {
            'text/css': '.css',
            'application/javascript': '.js',
            'text/javascript': '.js',
            'application/x-javascript': '.js',
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'font/woff2': '.woff2',
            'font/woff': '.woff',
            'font/ttf': '.ttf',
            'application/font-woff2': '.woff2',
        }.get(content_type.split(';', 1)[0].strip(), '')
        if ext:
            target = target.with_suffix(ext)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, 'wb') as f:
        f.write(r.content)
    return target


def download_missing_assets():
    found_urls = set()
    page_files = list(page_map.keys())
    pattern = re.compile(r'(?:href|src|content|data-slide)=(["\'])([^"\']+)(["\'])', flags=re.I)
    style_pattern = re.compile(r'url\((["\']?)([^"\')]+)(["\']?)\)', flags=re.I)

    for raw_name in page_files:
        raw_path = Path('mirror_raw') / raw_name
        text = raw_path.read_text(encoding='utf-8', errors='ignore')
        for match in pattern.finditer(text):
            url = match.group(2)
            if url.startswith('//'):
                url = 'https:' + url
            if url.startswith('http://'):
                url = 'https://' + url[len('http://'):]
            if url.rstrip('/') in ('https://content.app-sources.com', 'https://static.web-repository.com'):
                continue
            if any(p in url for p in REMOVE_PATTERNS):
                continue
            if any(p in url for p in KEEP_PATTERNS):
                found_urls.add(url)
        for match in style_pattern.finditer(text):
            url = match.group(2)
            if url.startswith('//'):
                url = 'https:' + url
            if url.startswith('http://'):
                url = 'https://' + url[len('http://'):]
            if url.rstrip('/') in ('https://content.app-sources.com', 'https://static.web-repository.com'):
                continue
            if any(p in url for p in REMOVE_PATTERNS):
                continue
            if any(p in url for p in KEEP_PATTERNS):
                found_urls.add(url)

    missing = []
    for url in sorted(found_urls):
        if url in url_map:
            continue
        noquery = re.sub(r'\?.*$', '', url)
        if noquery in url_map:
            continue
        normalized = normalize_app_sources_url(url)
        if normalized in url_map:
            continue
        missing.append(url)

    for url in missing:
        folder = assets_dir / 'images'
        if 'fonts.googleapis.com' in url or 'fonts.gstatic.com' in url:
            folder = assets_dir / 'fonts' if 'fonts.gstatic.com' in url else assets_dir / 'css'
        elif any(domain in url for domain in ['jquery.com', 'jsdelivr.net', 'cdnjs.cloudflare.com', 'static.web-repository.com']):
            folder = assets_dir / 'js' if url.endswith('.js') else assets_dir / 'css'
            if url.endswith('.css'):
                folder = assets_dir / 'css'
        target = download_file(url, folder)
        if target:
            url_map[url] = os.path.relpath(target, root).replace('\\', '/')
            noquery = re.sub(r'\?.*$', '', url)
            if noquery not in url_map:
                url_map[noquery] = os.path.relpath(target, root).replace('\\', '/')

    with open('mirror_raw/url_map.json', 'w', encoding='utf-8') as f:
        json.dump(url_map, f, indent=2)


download_missing_assets()

internal_pages = {
    'https://wellpro.one/diabetes-assist-program/index': '/diabetes-assist-program/',
    'https://wellpro.one/diabetes-assist-program': '/diabetes-assist-program/',
    'https://wellpro.one/wellness-protocol-basis': '/wellness-protocol-basis/',
    'https://wellpro.one/about-us': '/about-us/',
    'https://wellpro.one/contact-us': '/contact-us/',
    'https://wellpro.one/wellpro': '/',
    'https://wellpro.one/': '/',
    'https://wellpro.one': '/',
    'https://wellpro.one/advisory-board': '/advisory-board/',
    'https://wellpro.one/blog': '/blog/',
    'https://wellpro.one/cholesterol/index': '/cholesterol/index/',
    'https://wellpro.one/diabetes-assist-program/buy-now': '/diabetes-assist-program/buy-now/',
    'https://wellpro.one/diabetes-assist-program/diabetes-reversal': '/diabetes-assist-program/diabetes-reversal/',
    'https://wellpro.one/diabetes-reversal/index': '/diabetes-reversal/index/',
    'https://wellpro.one/doctor-assist': '/doctor-assist/',
    'https://wellpro.one/doctor-assist-registration/index': '/doctor-assist-registration/index/',
    'https://wellpro.one/lifestyle-disorders/cholesterol': '/lifestyle-disorders/cholesterol/',
    'https://wellpro.one/lifestyle-disorders/depression': '/lifestyle-disorders/depression/',
    'https://wellpro.one/lifestyle-disorders/diabetes': '/lifestyle-disorders/diabetes/',
    'https://wellpro.one/lifestyle-disorders/erectile-dysfunction': '/lifestyle-disorders/erectile-dysfunction/',
    'https://wellpro.one/lifestyle-disorders/immune-system': '/lifestyle-disorders/immune-system/',
    'https://wellpro.one/lifestyle-disorders/joint-pain': '/lifestyle-disorders/joint-pain/',
    'https://wellpro.one/lifestyle-disorders/thyroid': '/lifestyle-disorders/thyroid/',
    'https://wellpro.one/lifestyle-disorders/vegan-omega-oil': '/lifestyle-disorders/vegan-omega-oil/',
    'https://wellpro.one/pcod/index': '/pcod/index/',
    'https://wellpro.one/refund-and-exchange-policy': '/refund-and-exchange-policy/',
    'https://wellpro.one/soleus/index': '/soleus/index/',
    'https://wellpro.one/wellness-dietitian/registration': '/wellness-dietitian/registration/',
}

# Sort replacements by descending length to avoid partial substitutions.
all_url_replacements = sorted(
    list(url_map.items()) + list(internal_pages.items()),
    key=lambda item: len(item[0]),
    reverse=True,
)


def normalize_url(url: str) -> str:
    if url.startswith('//'):
        url = 'https:' + url
    if url.startswith('http://'):
        url = 'https://' + url[len('http://'):]
    return url


def get_local_path(url: str) -> str | None:
    url = normalize_url(url)
    if url in url_map:
        return '/' + url_map[url].replace('\\', '/')
    key = re.sub(r'\?.*$', '', url)
    if key in url_map:
        return '/' + url_map[key].replace('\\', '/')
    if 'content.app-sources.com' in key:
        alt = key.replace('/thumbnails/640x480/', '/uploads/')
        alt = alt.replace('/thumbnails/', '/uploads/')
        if alt in url_map:
            return '/' + url_map[alt].replace('\\', '/')
    if 'fonts.googleapis.com' in key:
        key = re.sub(r'\?.*$', '', key)
        if key in url_map:
            return '/' + url_map[key].replace('\\', '/')
    if url in internal_pages:
        return internal_pages[url]
    if 'static.web-repository.com' in key or 'cdn.jsdelivr.net' in key or 'cdnjs.cloudflare.com' in key:
        if key in url_map:
            return '/' + url_map[key].replace('\\', '/')
    if 'content.app-sources.com' in key and Path(urlparse(key).path).suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.svg'}:
        placeholder = root / 'assets' / 'images' / 'placeholder.png'
        if not placeholder.exists():
            placeholder.parent.mkdir(parents=True, exist_ok=True)
            placeholder.write_bytes(base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAusBRgYzx5kAAAAASUVORK5CYII='
            ))
        return '/' + str(placeholder.relative_to(root)).replace('\\', '/')
    return None


def rewrite_html_urls(html: str) -> str:
    def replace_attr(match: re.Match) -> str:
        attr, quote, value = match.group(1), match.group(2), match.group(3)
        local = get_local_path(value)
        if local:
            return f'{attr}={quote}{local}{quote}'
        return match.group(0)

    html = re.sub(r'(href|src|content|data-slide)=(["\'])([^"\']+)(["\'])', replace_attr, html)
    html = re.sub(r'url\((["\']?)([^"\')]+)(["\']?)\)',
                  lambda m: f'url({m.group(1)}{get_local_path(m.group(2)) or m.group(2)}{m.group(3)})', html)

    def replace_any_url(match: re.Match) -> str:
        url = match.group(0)
        local = get_local_path(url)
        return local or url

    html = re.sub(r'https?://[^"\'\s<>]+', replace_any_url, html)
    return html

remove_script_sources = [
    r'https?://apps\.elfsight\.com/[^"\']+',
    r'https?://play\.fabulousmedia\.in/[^"\']+',
    r'https?://convert\.gocommercially\.com/[^"\']+',
    r'https?://(www\.)?googletagmanager\.com/[^"\']+',
    r'https?://www\.google-analytics\.com/[^"\']+',
    r'https?://www\.youtube\.com/[^"\']+',
    r'https?://www\.facebook\.com/[^"\']+',
]

remove_iframe_sources = [
    r'https?://docs\.google\.com/[^"\']+',
    r'https?://www\.youtube\.com/[^"\']+',
    r'https?://youtube\.com/[^"\']+',
    r'https?://player\.vimeo\.com/[^"\']+',
]

script_block_patterns = [
    r'WebPlatform',
    r'dataLayer',
    r'gtag',
    r'Google Tag Manager',
    r'convert\.gocommercially',
    r'play\.fabulousmedia',
    r'service-api\.app-sources\.com',
    r'google-analytics\.com',
    r'googletagmanager\.com',
]

for raw_name, output_path in page_map.items():
    raw_path = Path('mirror_raw') / raw_name
    html = raw_path.read_text(encoding='utf-8', errors='ignore')

    # Remove external preload scripts and related link hints.
    html = re.sub(r'<link[^>]+rel="dns-prefetch"[^>]*>\s*', '', html, flags=re.I)
    html = re.sub(r'<link[^>]+rel="preconnect"[^>]*>\s*', '', html, flags=re.I)
    html = re.sub(r'<link[^>]+rel="preload"[^>]*as="script"[^>]*>\s*', '', html, flags=re.I)
    html = re.sub(r'rel="preload\s*stylesheet"', 'rel="stylesheet"', html, flags=re.I)
    html = re.sub(r'rel="preload"\s+as="style"', 'rel="stylesheet"', html, flags=re.I)
    html = re.sub(r'\s+as="style"', '', html, flags=re.I)

    # Remove external analytics, embeds, and platform scripts.
    for src_pattern in remove_script_sources:
        html = re.sub(rf'<script[^>]+src="{src_pattern}"[^>]*>\s*</script>\s*', '', html, flags=re.I)
    html = re.sub(r'<noscript[^>]*>[^<]*googletagmanager[^<]*</noscript>\s*', '', html, flags=re.I)
    html = re.sub(r'<iframe[^>]+src="(?:' + '|'.join(remove_iframe_sources) + r')"[^>]*>[\s\S]*?</iframe>\s*',
                  '<div class="offline-embed-placeholder">Embedded content removed for offline use.</div>',
                  html, flags=re.I)
    html = re.sub(r'<!--\s*Google Tag Manager[^>]*-->[\s\S]*?<!--\s*End Google Tag Manager[^>]*-->\s*', '', html,
                  flags=re.I)
    html = re.sub(r'<script[^>]*>[\s\S]*?(?:' + '|'.join(script_block_patterns) + r')[\s\S]*?</script>\s*', '', html,
                  flags=re.I)

    # Normalize protocol-relative URLs so mapped assets can be rewritten.
    html = re.sub(r'(["\'])//([^"\']+)(["\'])', r'\1https://\2\3', html)

    # Replace mapped URLs and internal paths with local references.
    html = rewrite_html_urls(html)

    # Fix any known root-relative internal page paths.
    html = html.replace('href="/about-us"', 'href="/about-us/"')
    html = html.replace('href="/contact-us"', 'href="/contact-us/"')
    html = html.replace('href="/wellness-protocol-basis"', 'href="/wellness-protocol-basis/"')
    html = html.replace('href="/diabetes-assist-program/index"', 'href="/diabetes-assist-program/"')
    html = html.replace('href="/diabetes-assist-program"', 'href="/diabetes-assist-program/"')

    # Remove remote app-sources and static resources metadata on body.
    html = re.sub(r'\sdata-resources="[^"]*"', '', html, flags=re.I)
    html = re.sub(r'\sdata-content="[^"]*"', '', html, flags=re.I)

    # Remove YouTube embed targets and Elfsight widgets from static pages.
    html = re.sub(r'\sdata-video="https?://[^"]+"', '', html, flags=re.I)
    html = re.sub(
        r'<div[^>]+class="[^"]*elfsight-app[^"]*"[^>]*>[\s\S]*?</div>',
        '<div class="offline-embed-placeholder">Embedded widget removed for offline use.</div>',
        html,
        flags=re.I,
    )
    html = re.sub(r'<script[^>]+src="/assets/js/hit\.js"[^>]*>[\s\S]*?</script>\s*', '', html, flags=re.I)

    # Rewrite any remaining clean internal roots.
    html = html.replace('href="https://wellpro.one/', 'href="/')
    html = html.replace('src="https://wellpro.one/', 'src="/')

    # Remove the platform runtime script from offline pages.
    html = re.sub(r'<script[^>]+src="/assets/js/platform\.client\.min\.js"[^>]*>\s*</script>\s*', '', html, flags=re.I)

    output_file = root / output_path
    output_file.write_text(html, encoding='utf-8')
    print('wrote', output_file)


# Save a simplified Vercel config for clean static hosting.
vercel_config = {
    'version': 2,
    'cleanUrls': True,
    'trailingSlash': True,
}
with open(root / 'vercel.json', 'w', encoding='utf-8') as f:
    json.dump(vercel_config, f, indent=2)

# Ensure GitHub Pages docs source works without Jekyll.
(root / '.nojekyll').write_text('', encoding='utf-8')

(readme := root / 'README.md').write_text(
    '# Wellpro Static Mirror\n\n'
    'This `docs/` folder contains the offline static site mirror of the original `wellpro.one` pages.\n\n'
    '## Deployment\n\n'
    '- Serve `docs/` as the site root.\n'
    '- GitHub Pages can use the `docs/` folder as the build source.\n'
    '- `vercel.json` enables clean URLs for Vercel static hosting.\n',
    encoding='utf-8'
)

# Persist any adjusted url_map for future use.
with open('mirror_raw/url_map.json', 'w', encoding='utf-8') as f:
    json.dump(url_map, f, indent=2)

print('build complete')
