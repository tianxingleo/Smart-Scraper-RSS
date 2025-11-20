import sqlite3
import os

DB_PATH = "data/database.db"

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"[SKIP] Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(scrapeditem)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "ai_score" not in columns:
            print("Adding 'ai_score' column...")
            cursor.execute("ALTER TABLE scrapeditem ADD COLUMN ai_score INTEGER DEFAULT 0")
            
        if "risk_level" not in columns:
            print("Adding 'risk_level' column...")
            cursor.execute("ALTER TABLE scrapeditem ADD COLUMN risk_level VARCHAR DEFAULT 'Unknown'")
            
        conn.commit()
        print("[SUCCESS] Database migration completed.")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
