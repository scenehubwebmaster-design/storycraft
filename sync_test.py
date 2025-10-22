from backend.main import app
from fastapi.testclient import TestClient
c = TestClient(app)
resp = c.post('/api/references/sync-from-disk')
print('STATUS', resp.status_code)
try:
    j = resp.json()
    print('imported', j.get('imported'))
    items = j.get('items') or []
    print('sample count', len(items))
    for it in items[:5]:
        print(it.get('ref_type'), it.get('key'))
except Exception as e:
    print('json err', e, resp.text[:1000])
