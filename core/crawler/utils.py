from urllib.parse import urlparse, urljoin

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def clean_url(base_url, link):
    if not link:
        return None
    return urljoin(base_url, link)
