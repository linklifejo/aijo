import sqlite3

def connect_db():
    conn = sqlite3.connect('inet.db')
    # 외래 키 제약 조건 활성화
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def init_db():
    conn = connect_db()
    c = conn.cursor()
    # 외래 키 제약 조건 활성화
    c.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                trade_date TEXT,
                buy_price INTEGER,
                sell_price INTEGER,
                start_price   INTEGER,
                high_price   INTEGER,
                qty   INTEGER
                    );   
              ''')
    
    conn.commit()
    conn.close()
init_db()   