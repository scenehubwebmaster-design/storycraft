import sqlite3
import os

# Use the correct database path - parent directory
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storycraft.db'))
print(f"Checking database: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")
print(f"File size: {os.path.getsize(db_path) / (1024*1024):.2f} MB\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Check for user_settings specifically
if any(t[0] == 'user_settings' for t in tables):
    cursor.execute("SELECT * FROM user_settings LIMIT 1")
    row = cursor.fetchone()
    
    cursor.execute("PRAGMA table_info(user_settings)")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    
    print("\nuser_settings columns:")
    for col in col_names:
        print(f"  - {col}")
    
    if row:
        print("\nFirst user_settings row:")
        for i, col in enumerate(col_names):
            print(f"  {col}: {row[i]}")
else:
    print("\n❌ user_settings table NOT FOUND!")

conn.close()
