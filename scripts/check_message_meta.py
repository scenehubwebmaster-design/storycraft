import sqlite3, json, os

db_path = r"e:\storycraft\storycraft.db"
if not os.path.exists(db_path):
    print('DB not found:', db_path)
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT meta FROM chat_messages WHERE id = 172')
    row = cur.fetchone()
    if not row:
        print('No row')
    else:
        meta = row[0]
        print('meta raw type:', type(meta))
        try:
            j = json.loads(meta)
            si = j.get('scene_image')
            if si:
                print('scene_image keys:', list(si.keys()))
                if 'image' in si:
                    print('image length:', len(si['image']) if si['image'] else 0)
                else:
                    print('no image in scene_image')
            else:
                print('no scene_image in meta')
        except Exception as e:
            print('failed to parse meta as json:', e)
    conn.close()
