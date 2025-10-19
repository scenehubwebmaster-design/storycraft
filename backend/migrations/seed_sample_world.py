import os
import sqlite3
import base64
from PIL import Image
from io import BytesIO

DB = os.path.join(os.path.dirname(__file__), '..', 'storycraft.db')
conn = sqlite3.connect(DB)
cur=conn.cursor()

# Create a small test image (100x80) with a colored gradient
img = Image.new('RGBA', (100,80), (255,255,255,255))
for x in range(100):
    for y in range(80):
        img.putpixel((x,y), (int(x*2.55), int(y*3.1875), 128, 255))
buf=BytesIO()
img.save(buf, format='PNG')
img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

# Insert sample world
cur.execute("INSERT INTO worlds (name, description, world_map, created_at, updated_at) VALUES (?,?,?,?,?)", (
    'Sample World', 'Automatically created sample world for tests', img_b64, '2025-10-19', '2025-10-19'
))
conn.commit()
print('Inserted sample world id', cur.lastrowid)
conn.close()
