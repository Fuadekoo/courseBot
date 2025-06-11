import sqlite3

def setup():
    conn = sqlite3.connect('botdata.db')
    cursor = conn.cursor()

    # Create a sample table like your channels
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        wdt_ID INTEGER PRIMARY KEY,
        chat_id INTEGER NOT NULL,
        name TEXT,
        subject TEXT,
        status TEXT
    )
    ''')

    # Insert dummy data (if you want)
    cursor.execute('''
    INSERT OR IGNORE INTO channels (wdt_ID, chat_id, name, subject, status)
    VALUES (10, 973677019, 'Darul-Kubra', 'Math', 'Active')
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup()
    print("Database and table created!")
