import csv
import sqlite3

# CSV 파일 경로
csv_file_path = '코스피.csv'  # 코스피,코스닥 수정해서 두개를 수동으로 생성
market = csv_file_path.split('.')[0]

# SQLite 데이터베이스 파일 경로
sqlite_db_path = 'inet.db'

# SQLite 데이터베이스에 연결
conn = sqlite3.connect(sqlite_db_path)
cur = conn.cursor()

# 데이터베이스 테이블 생성 (이미 존재하지 않는 경우)
cur.execute('''
            CREATE TABLE IF NOT EXISTS krxs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL UNIQUE,
                    sector TEXT,
                    item TEXT,
                    ipo TEXT,
                    closing_month TEXT,
                    ceo TEXT,
                    homepage TEXT,
                    local TEXT,
                    market TEXT
                );
''')

# CSV 파일 열기 및 내용 읽기
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    
    # 첫 번째 줄은 헤더일 수 있으므로 건너뛰기
    next(csv_reader, None)
    
    # CSV 파일의 각 줄을 데이터베이스에 삽입
    for row in csv_reader:
        # 'row'의 첫 번째 항목이 아닌 두 번째 항목을 'name'으로 사용
        # 'row' 리스트의 나머지 항목도 필요에 따라 조정
        # 'code' 값을 6자리 문자열로 포매팅
        code = row[2].zfill(6)
        cur.execute('''
        INSERT INTO krxs (name, code, sector, item, ipo, closing_month, ceo, homepage, local, market)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row[1], code, row[3], row[4], row[5], row[6], row[7], row[8], row[9], market))

# 변경 사항을 데이터베이스에 커밋하고 연결 종료
conn.commit()
conn.close()
