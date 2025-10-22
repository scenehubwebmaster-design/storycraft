import os
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://5thsrd.org"
INDEX_URL = BASE_URL + "/gamemaster_rules/monster_indexes/monsters_by_name/"

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
    'DNT': '1',  # Do Not Track
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    # Optionally you can add a Referer header
    'Referer': INDEX_URL,
}

def slugify(name):
    """Convert monster name to a safe filename slug."""
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

def fetch_page(session, url):
    """Fetch page content using given session and url, return html text."""
    resp = session.get(url)
    resp.raise_for_status()
    return resp.text

def parse_index(html):
    """Parse the index HTML and extract (name, url) pairs of monsters."""
    soup = BeautifulSoup(html, 'html.parser')
    monsters = []
    for li in soup.select('#page-content ul li'):
        a = li.find('a', href=True)
        if a:
            name = a.get_text().strip()
            href = a['href']
            if href.startswith('/'):
                full_url = BASE_URL + href
            else:
                full_url = BASE_URL + '/' + href
            monsters.append((name, full_url))
    return monsters

def parse_monster(html):
    """Parse a monster’s HTML page and extract data into a dictionary."""
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Name
    h1 = soup.find('h1')
    data['name'] = h1.get_text().strip() if h1 else ''

    # Size & Type (in <em> inside first <p>)
    em = soup.select_one('#page-content > p em')
    data['type_line'] = em.get_text().strip() if em else ''

    # Armor Class / Hit Points / Speed
    p_info = None
    if em:
        p_info = em.find_parent('p').find_next_sibling('p')
    if p_info:
        raw = p_info.decode_contents().split('<br>')
        for line in raw:
            text = BeautifulSoup(line, 'html.parser').get_text().strip()
            if text.startswith('Armor Class'):
                data['armor_class'] = text.replace('Armor Class','').strip()
            elif text.startswith('Hit Points'):
                data['hit_points'] = text.replace('Hit Points','').strip()
            elif text.startswith('Speed'):
                data['speed'] = text.replace('Speed','').strip()

    # Ability scores table
    table = soup.select_one('table.pure-table')
    if table:
        headers = [th.get_text().strip() for th in table.select('thead th')]
        values = [td.get_text().strip() for td in table.select('tbody tr td')]
        data['abilities'] = dict(zip(headers, values))

    # Saving Throws, Skills, Senses, Languages, Challenge
    if p_info:
        p_rest = p_info.find_next_sibling('p')
    else:
        p_rest = None
    if p_rest:
        raw = p_rest.decode_contents().split('<br>')
        for line in raw:
            text = BeautifulSoup(line, 'html.parser').get_text().strip()
            if text.startswith('Saving Throws'):
                data['saving_throws'] = text.replace('Saving Throws','').strip()
            elif text.startswith('Skills'):
                data['skills'] = text.replace('Skills','').strip()
            elif text.startswith('Senses'):
                data['senses'] = text.replace('Senses','').strip()
            elif text.startswith('Languages'):
                data['languages'] = text.replace('Languages','').strip()
            elif text.startswith('Challenge'):
                data['challenge'] = text.replace('Challenge','').strip()

    # Traits
    actions_h3 = soup.find('h3', id='actions')
    if actions_h3:
        sibling = actions_h3.find_previous_sibling('p')
        if sibling:
            trait_lines = sibling.decode_contents().split('<br>')
            traits = [BeautifulSoup(line, 'html.parser').get_text().strip() for line in trait_lines if line.strip()]
            data['traits'] = traits

    # Actions
    actions = []
    if actions_h3:
        p_actions = actions_h3.find_next_sibling('p')
        if p_actions:
            action_lines = p_actions.decode_contents().split('<br>')
            actions = [BeautifulSoup(line, 'html.parser').get_text().strip() for line in action_lines if line.strip()]
    data['actions'] = actions

    # Legendary Actions
    legendary = []
    leg_h3 = soup.find('h3', id='legendary-actions')
    if leg_h3:
        p_leg = leg_h3.find_next_sibling('p')
        if p_leg:
            leg_lines = p_leg.decode_contents().split('<br>')
            legendary = [BeautifulSoup(line, 'html.parser').get_text().strip() for line in leg_lines if line.strip()]
    data['legendary_actions'] = legendary

    return data

def render_md(data):
    """Render the collected monster data into a Markdown string."""
    lines = []
    lines.append(f"# {data.get('name','')}\n")

    if data.get('type_line'):
        lines.append(f"**Size & Type.** {data['type_line']}\n")
    if data.get('armor_class'):
        lines.append(f"**Armor Class.** {data['armor_class']}\n")
    if data.get('hit_points'):
        lines.append(f"**Hit Points.** {data['hit_points']}\n")
    if data.get('speed'):
        lines.append(f"**Speed.** {data['speed']}\n")

    if data.get('abilities'):
        headers = list(data['abilities'].keys())
        values = list(data['abilities'].values())
        lines.append("\n| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join(":----:" for _ in headers) + "|")
        lines.append("| " + " | ".join(values) + " |\n")

    for label in ['saving_throws', 'skills', 'senses', 'languages', 'challenge']:
        if data.get(label):
            pretty_label = label.replace('_',' ').title()
            lines.append(f"**{pretty_label}.** {data[label]}\n")

    if data.get('traits'):
        lines.append("## Traits\n")
        for t in data['traits']:
            lines.append(f"**{t}**\n")

    if data.get('actions'):
        lines.append("## Actions\n")
        for a in data['actions']:
            lines.append(f"**{a}**\n")

    if data.get('legendary_actions'):
        lines.append("## Legendary Actions\n")
        for la in data['legendary_actions']:
            lines.append(f"{la}\n")

    return "\n".join(lines)

def main(limit=None):
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    idx_html = fetch_page(session, INDEX_URL)
    monsters = parse_index(idx_html)
    print(f"Found {len(monsters)} monsters.")

    os.makedirs("monsters_md", exist_ok=True)

    count = 0
    for name, url in monsters:
        if limit and count >= limit:
            break
        slug = slugify(name)
        filename = os.path.join("monsters_md", slug + ".md")
        print(f"Processing {name} → {url}")
        try:
            html = fetch_page(session, url)
            data = parse_monster(html)
            md_content = render_md(data)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)
            count += 1
        except Exception as e:
            print(f"ERROR processing {name}: {e}")
        time.sleep(1)  # polite delay between requests

    print("Done.")

if __name__ == "__main__":
    main(limit=317)  # change or remove limit as needed
