from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
from collections import deque


def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc


def clean_url(base_url, href):
    if not href:
        return None
    href = href.strip()
    if href.startswith(("#", "mailto:", "javascript:")):
        return None
    return urljoin(base_url, href)


def extract_visible_text(page):
    """
    Extract only visible text from rendered page
    """
    return page.evaluate(
        """() => {
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            let text = "";
            let node;
            while ((node = walker.nextNode())) {
                const parent = node.parentElement;
                if (!parent) continue;

                const style = window.getComputedStyle(parent);
                if (style.display === "none" || style.visibility === "hidden") continue;

                const value = node.textContent.trim();
                if (value) text += value + " ";
            }
            return text;
        }"""
    )


def crawl_website_playwright(
    start_url: str,
    max_pages: int = 50,
    max_depth: int = 2,
):
    """
    Optimized Playwright crawler
    - Single browser
    - Controlled parallel tabs (2)
    - Resource blocking
    - Fast DOM-based wait
    - Graceful failure
    """

    visited = set()
    queue = deque([(start_url, 0)])
    pages_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # 🚀 Block heavy resources
        context.route(
            "**/*",
            lambda route, request: (
                route.abort()
                if request.resource_type in {"image", "media", "font", "stylesheet"}
                else route.continue_()
            )
        )

        # ✅ Page pool (parallel tabs)
        page_pool = [context.new_page() for _ in range(2)]
        page_index = 0

        while queue and len(pages_data) < max_pages:
            url, depth = queue.popleft()

            if url in visited or depth > max_depth:
                continue

            page = page_pool[page_index % len(page_pool)]
            page_index += 1

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)

                # Small settle time for SPA hydration
                page.wait_for_timeout(700)

                text = extract_visible_text(page)

                # Skip junk / shell pages
                if len(text) < 400:
                    visited.add(url)
                    continue

                title = page.title() or ""

                pages_data.append(
                    {
                        "url": url,
                        "title": title,
                        "text": text,
                    }
                )

                visited.add(url)

                # Collect links for BFS
                if depth < max_depth:
                    links = page.evaluate(
                        """() => Array.from(document.querySelectorAll('a[href]'))
                            .map(a => a.getAttribute('href'))"""
                    )

                    for href in links:
                        full_url = clean_url(start_url, href)
                        if (
                            full_url
                            and full_url not in visited
                            and is_same_domain(start_url, full_url)
                        ):
                            queue.append((full_url, depth + 1))

            except Exception as e:
                print(f"[SKIP] {url} → {e}")
                visited.add(url)

        context.close()
        browser.close()

    return pages_data
