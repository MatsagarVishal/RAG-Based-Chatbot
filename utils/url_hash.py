from urllib.parse import urlparse


def generate_kb_id(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return domain.replace(".", "_")
