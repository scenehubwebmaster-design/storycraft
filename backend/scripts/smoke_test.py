import requests

BASE = 'http://127.0.0.1:8000'

print('GET /api/worlds/')
try:
    r = requests.get(BASE + '/api/worlds/')
    print('status:', r.status_code)
    print('content-type:', r.headers.get('content-type'))
    print('body (truncated):', r.text[:1000])
except Exception as e:
    print('GET /api/worlds/ failed:', e)

print('\nPOST /api/generate/region/crop/ (world_id=1)')
try:
    payload = { 'world_id': 1, 'percent_bounds': { 'x1': 10, 'y1': 10, 'x2': 60, 'y2': 60 }, 'upscale': 1 }
    r = requests.post(BASE + '/api/generate/region/crop/', json=payload, timeout=20)
    print('status:', r.status_code)
    print('body (truncated):', r.text[:1000])
except Exception as e:
    print('POST crop failed:', e)
