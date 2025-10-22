import os
import re
import time
import requests
import random
import logging
from bs4 import BeautifulSoup

BASE_URL = "https://5thsrd.org"
INDEX_URL = BASE_URL + "/gamemaster_rules/magic_item_indexes/items_by_name/"

# Expanded browser-style headers
DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/117.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': INDEX_URL,
}

# Setup logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def slugify(name):
    """Convert item name to a safe filename slug."""
    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return slug

def fetch_page(session, url, retries=3, delay=1.0):
    """Fetch page content with optional retry logic."""
    for attempt in range(retries):
        try:
            resp = session.get(url)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logging.warning(f"Fetch attempt {attempt+1}/{retries} failed for {url}: {e}")
            time.sleep(delay * (attempt+1))
    logging.error(f"Failed to fetch page after {retries} attempts: {url}")
    return None

def parse_index(html):
    """Parse the index of magic items and return list of (name, url)."""
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for li in soup.select('#page-content ul li'):
        a = li.find('a', href=True)
        if a:
            name = a.get_text().strip()
            href = a['href']
            if href.startswith('/'):
                full_url = BASE_URL + href
            else:
                full_url = BASE_URL + '/' + href
            items.append((name, full_url))
    return items

def html_table_to_md(table_tag):
    """Convert a BeautifulSoup <table> to Markdown table string."""
    md_lines = []
    # headers
    headers = [th.get_text().strip() for th in table_tag.select('thead th')]
    md_lines.append("| " + " | ".join(headers) + " |")
    md_lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    # rows
    for tr in table_tag.select('tbody tr'):
        vals = [td.get_text().strip() for td in tr.select('td')]
        md_lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(md_lines)

def parse_item(html):
    """Parse a magic-item page and return a dict of fields."""
    soup = BeautifulSoup(html, 'html.parser')
    data = {}
    # Name
    h1 = soup.find('h1')
    data['name'] = h1.get_text().strip() if h1 else ''
    # Category / Rarity line (in <p><em>…</em></p>)
    em = soup.select_one('#page-content > p em')
    data['category_line'] = em.get_text().strip() if em else ''
    # Description paragraphs & tables
    desc_elements = []
    if em:
        # Look at all following siblings until next heading (h2/h3) or end
        p = em.find_parent('p')
        for sibling in p.find_next_siblings():
            if sibling.name in ['h1','h2','h3']:
                break
            if sibling.name == 'p':
                desc_elements.append(sibling.get_text().strip())
            elif sibling.name == 'div' and sibling.select_one('table'):
                # get the table within
                table_md = html_table_to_md(sibling.select_one('table'))
                desc_elements.append(table_md)
    else:
        logging.warning(f"No category/em line found for item: {data.get('name')}")
    data['description'] = "\n\n".join(desc_elements).strip()
    # Additional sections? For simplicity we treat everything as description for now.
    return data

def render_md(data):
    """Render the data dict as Markdown text."""
    lines = []
    # Attribution header
    lines.append("<!-- This content derived from the SRD / 5thSRD site — licensed under CC-BY 4.0 -->\n")
    lines.append(f"# {data.get('name','')}\n")
    if data.get('category_line'):
        lines.append(f"**Category & Rarity.** {data['category_line']}\n")
    if data.get('description'):
        lines.append(data['description'] + "\n")
    return "\n".join(lines)

def main(limit=None):
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    idx_html = fetch_page(session, INDEX_URL)
    if not idx_html:
        logging.error("Failed to fetch the index page. Exiting.")
        return
    items = parse_index(idx_html)
    logging.info(f"Found {len(items)} magic items.")

    output_dir = "magic_items_md"
    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    fail_list = []

    for idx, (name, url) in enumerate(items, start=1):
        if limit and success_count >= limit:
            break
        slug = slugify(name)
        filename = os.path.join(output_dir, slug + ".md")
        logging.info(f"[{idx}/{len(items)}] Processing '{name}' → {url}")
        html = fetch_page(session, url)
        if not html:
            fail_list.append(name)
            continue
        try:
            data = parse_item(html)
            md_content = render_md(data)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)
            success_count += 1
        except Exception as e:
            logging.error(f"Error parsing item '{name}': {e}")
            fail_list.append(name)
        # polite delay
        time.sleep(random.uniform(0.8,1.5))

    logging.info(f"Done. Success: {success_count}, Failed: {len(fail_list)}")
    if fail_list:
        logging.info("Failed items:")
        for nm in fail_list:
            logging.info(f" - {nm}")

if __name__ == "__main__":
    main(limit=None)  # remove limit for full run
