from datetime import datetime
import shutil
import os

ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
dst = f'tools/backups/storycraft.db.backup.{ts}'
os.makedirs('tools/backups', exist_ok=True)
shutil.copy('storycraft.db', dst)
print(f'Backup created: {dst}')
