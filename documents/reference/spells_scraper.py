import os
import re
import time
import requests
import random
import logging
from bs4 import BeautifulSoup

BASE_URL = "https://5thsrd.org"
INDEX_URL = BASE_URL + "/spellcasting/spell_indexes/spells_by_name/"

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

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def slugify(name):
    """Convert spell name into safe filename slug."""
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

def fetch_page(session, url, retries=3, delay=1.0):
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
    soup = BeautifulSoup(html, 'html.parser')
    spells = []
    for li in soup.select('#page-content ul li'):
        a = li.find('a', href=True)
        if a:
            name = a.get_text().strip()
            href = a['href']
            if href.startswith('/'):
                full_url = BASE_URL + href
            else:
                full_url = BASE_URL + '/' + href
            spells.append((name, full_url))
    return spells

def html_table_to_md(table_tag):
    headers = [th.get_text().strip() for th in table_tag.select('thead th')]
    md = ["| " + " | ".join(headers) + " |",
          "|" + "|".join(["---"]*len(headers)) + "|"]
    for tr in table_tag.select('tbody tr'):
        vals = [td.get_text().strip() for td in tr.select('td')]
        md.append("| " + " | ".join(vals) + " |")
    return "\n".join(md)

def parse_spell(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Name
    h1 = soup.find('h1')
    data['name'] = h1.get_text().strip() if h1 else ''

    # Level & school: <p><em>2nd-level evocation</em></p>
    em = soup.select_one('#page-content > p em')
    data['level_school'] = em.get_text().strip() if em else ''

    # Then info block <p><strong>Casting Time:</strong> … <br> …</p>
    info_p = None
    if em:
        info_p = em.find_parent('p').find_next_sibling('p')
    if info_p:
        raw = info_p.decode_contents().split('<br>')
        for line in raw:
            text = BeautifulSoup(line, 'html.parser').get_text().strip()
            if text.startswith('Casting Time:'):
                data['casting_time'] = text.replace('Casting Time:','').strip()
            elif text.startswith('Range:'):
                data['range'] = text.replace('Range:','').strip()
            elif text.startswith('Components:'):
                data['components'] = text.replace('Components:','').strip()
            elif text.startswith('Duration:'):
                data['duration'] = text.replace('Duration:','').strip()

    # The description paragraphs & any tables
    desc_elements = []
    if info_p:
        for sibling in info_p.find_next_siblings():
            if sibling.name in ['h2','h3','h1']:
                break
            if sibling.name == 'p':
                desc_elements.append(sibling.get_text().strip())
            elif sibling.name == 'div' and sibling.select_one('table'):
                desc_elements.append(html_table_to_md(sibling.select_one('table')))
    data['description'] = "\n\n".join(desc_elements).strip()

    return data

def render_md(data):
    lines = []
    lines.append("<!-- Derived from 5thSRD — CC-BY 4.0 -->\n")
    lines.append(f"# {data.get('name','')}\n")
    if data.get('level_school'):
        lines.append(f"**Level & School.** {data['level_school']}\n")
    for field in ['casting_time','range','components','duration']:
        if data.get(field):
            pretty = field.replace('_',' ').title()
            lines.append(f"**{pretty}.** {data[field]}\n")
    if data.get('description'):
        lines.append("\n" + data['description'] + "\n")
    return "\n".join(lines)

def main(limit=None):
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    idx_html = fetch_page(session, INDEX_URL)
    if not idx_html:
        logging.error("Failed to fetch spells index. Exiting.")
        return

    spells = parse_index(idx_html)
    logging.info(f"Found {len(spells)} spells.")

    output_dir = "spells_md"
    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    fail_list = []

    for idx, (name, url) in enumerate(spells, start=1):
        if limit and success_count >= limit:
            break
        slug = slugify(name)
        filename = os.path.join(output_dir, slug + ".md")
        logging.info(f"[{idx}/{len(spells)}] Processing '{name}' → {url}")
        html = fetch_page(session, url)
        if not html:
            fail_list.append(name)
            continue
        try:
            data = parse_spell(html)
            md = render_md(data)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md)
            success_count += 1
        except Exception as e:
            logging.error(f"Error parsing spell '{name}': {e}")
            fail_list.append(name)
        time.sleep(random.uniform(0.8, 1.5))

    logging.info(f"Done. Success: {success_count}, Failed: {len(fail_list)}")
    if fail_list:
        logging.info("Failed spells:")
        for nm in fail_list:
            logging.info(f" - {nm}")

if __name__ == "__main__":
    main(limit=None)  # Remove limit or set to None to process all spells
