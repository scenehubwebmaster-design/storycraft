import re
import os

root = r"e:\storycraft"
frontend = os.path.join(root, 'frontend')
backend = os.path.join(root, 'backend')

api_paths = set()

# Walk frontend files
for dirpath, dirnames, filenames in os.walk(frontend):
    for fn in filenames:
        if not fn.endswith(('.js', '.jsx', '.ts', '.tsx', '.html')):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        for m in re.finditer(r"\$\{API_URL\}(/api[\w\-\/\?=,&%\._:]*)", text):
            api_paths.add(m.group(1))

# Normalize paths
norm_paths = sorted(api_paths)

# Search backend for route decorators
backend_files = []
for dirpath, dirnames, filenames in os.walk(backend):
    for fn in filenames:
        if fn.endswith('.py'):
            backend_files.append(os.path.join(dirpath, fn))

# Parse main.py to get router prefixes mapping (module name -> prefix)
router_prefixes = {}
main_py = os.path.join(backend, 'main.py')
if os.path.exists(main_py):
    with open(main_py, 'r', encoding='utf-8', errors='ignore') as f:
        main_txt = f.read()
    # match lines like: app.include_router(characters.router, prefix="/api/characters", tags=[...])
    for m in re.finditer(r"app\.include_router\(([^,\)]+)\.router\s*,\s*prefix\s*=\s*['\"]([^'\"]+)['\"]", main_txt):
        mod = m.group(1).strip()
        pref = m.group(2).strip()
        router_prefixes[pref] = mod

# Also scan individual router files for APIRouter(prefix=...) declarations
for bf in backend_files:
    try:
        with open(bf, 'r', encoding='utf-8', errors='ignore') as f:
            btxt = f.read()
    except Exception:
        continue
    for m in re.finditer(r"APIRouter\s*\(\s*prefix\s*=\s*['\"]([^'\"]+)['\"]", btxt):
        pref = m.group(1).strip()
        # map prefix to the backend file path (prefer explicit router file mapping)
        router_prefixes[pref] = os.path.relpath(bf, root)

report = []
for p in norm_paths:
    found = False
    matches = []
    # Strip query params for matching
    path_only = p.split('?')[0]

    # Identify which router prefix this path belongs to (if any)
    matched_prefix = None
    for pref in sorted(router_prefixes.keys(), key=lambda x: -len(x)):
        if path_only.startswith(pref):
            matched_prefix = pref
            break

    # Build list of candidate backend files to search
    candidate_files = backend_files
    if matched_prefix:
        # Map module name from prefix to file path if possible
        mod_name = router_prefixes.get(matched_prefix)
        if mod_name:
            # Try to resolve module to a file under backend/routers
            # common pattern: from .routers import characters -> file backend/routers/characters.py
            candidate = os.path.join(backend, 'routers', f"{mod_name}.py")
            if os.path.exists(candidate):
                candidate_files = [candidate]

    # Remove the router prefix for matching inside router files
    inner_path = path_only
    if matched_prefix:
        inner_path = '/' + path_only[len(matched_prefix):].lstrip('/')

    # Try matching inner_path with/without trailing slash
    tries = [inner_path, inner_path.rstrip('/') + '/', inner_path.rstrip('/')]

    for bf in candidate_files:
        try:
            with open(bf, 'r', encoding='utf-8', errors='ignore') as f:
                btxt = f.read()
        except Exception:
            continue
        for t in tries:
            if re.search(re.escape(t), btxt):
                found = True
                matches.append((bf, t))
        # Additional heuristic: if path starts with /api/generate/, backend file may declare prefix inside router
        if not found and path_only.startswith('/api/generate/'):
            alt = '/' + path_only[len('/api/generate/'):]
            for t in [alt, alt.rstrip('/') + '/', alt.rstrip('/')]:
                if re.search(re.escape(t), btxt):
                    found = True
                    matches.append((bf, t))
    report.append((p, found, matches))

# Print report
print('Found {} unique frontend API paths'.format(len(norm_paths)))
for p, found, matches in report:
    print('\nPATH:', p)
    print('  BACKEND MATCH:', 'YES' if found else 'NO')
    if matches:
        for bf, t in matches[:5]:
            print('   -', os.path.relpath(bf, root), 'matched', t)
    else:
        print('   - No matching backend file contains this exact substring')

# Summarize missing
missing = [p for p, found, m in report if not found]
print('\nMISSING IN BACKEND ({}):'.format(len(missing)))
for p in missing:
    print(' -', p)
