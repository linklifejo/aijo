import asyncio
import aiosqlite
import pandas as pd
import os
import streamlit as st
import logging
import requests
from bs4 import BeautifulSoup
# Logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db_name = 'inet.db'

async def _removeDbFile(file_path, max_attempts=3, wait_seconds=1):
    for attempt in range(max_attempts):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"File {file_path} successfully removed.")
                break
        except PermissionError as e:
            logging.warning(f"Attempt {attempt + 1}: Unable to remove file {file_path}, waiting {wait_seconds} seconds before retrying...")
            await asyncio.sleep(wait_seconds)
    else:
        logging.error(f"Failed to remove file {file_path} after {max_attempts} attempts.")

async def _setupTables():

    try:
        async with aiosqlite.connect(db_name) as db: # 외부함수인 connect를 비동기함수로 사용한다
            await db.execute("PRAGMA foreign_keys = ON") 
            await db.executescript('''
                    CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT,
                    email_address TEXT NOT NULL UNIQUE,
                    phone_number TEXT,
                    department TEXT,
                    position TEXT,
                    hire_date DATE,
                    salary REAL,
                    employment_status TEXT,
                    date_of_birth TEXT,
                    address TEXT,
                    gender TEXT,
                    nationality TEXT,
                    emergency_contact_name TEXT,
                    emergency_contact_relationship TEXT,
                    emergency_contact_number TEXT,
                    description TEXT
                );
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT NOT NULL,               
                    first_name TEXT,
                    last_name TEXT,
                    email_address TEXT NOT NULL UNIQUE,
                    phone_number TEXT,
                    address TEXT,
                    city TEXT,
                    state_province TEXT,
                    postal_code TEXT,
                    country TEXT,
                    date_of_birth TEXT,  -- 날짜를 문자열로 저장
                    gender TEXT,
                    account_creation_date TEXT NOT NULL DEFAULT CURRENT_DATE,  -- 날짜를 문자열로 저장
                    last_purchase_date TEXT NOT NULL DEFAULT CURRENT_DATE,  -- 날짜를 문자열로 저장
                    customer_segment TEXT,
                    preferences TEXT,
                    loyalty_points INTEGER,
                    description TEXT
                );                                   
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    email_address TEXT NOT NULL UNIQUE,
                    phone_number TEXT,
                    address TEXT,
                    date_of_birth TEXT,
                    gender TEXT,
                    registration_date TEXT NOT NULL DEFAULT CURRENT_DATE,
                    membership_type TEXT,
                    membership_status TEXT NOT NULL,
                    last_login_date TEXT DEFAULT CURRENT_DATE,
                    profile_photo TEXT,
                    preferences TEXT,
                    notes TEXT,
                    description TEXT
                );
                CREATE TABLE IF NOT EXISTS apikeys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key_value TEXT NOT NULL UNIQUE,
                    member_id INTEGER NOT NULL DEFAULT 1,                       -- 'member_id'
                    status TEXT NOT NULL DEFAULT 'Active',       -- 'Active', 'Inactive', 'Revoked' 
                    description TEXT NOT NULL DEFAULT '회원관리자'
                );
                CREATE TABLE IF NOT EXISTS relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT NOT NULL,
                    assistant_id TEXT NOT NULL,   
                    thread_id  TEXT NOT NULL, 
                    apikey_id  TEXT NOT NULL,                                   
                    status TEXT NOT NULL DEFAULT 'Active',       -- 'Active', 'Inactive' 
                    description TEXT NOT NULL DEFAULT 'Chatting'      -- 'Chatting', 'Voice', 'Complex' 
                );
                CREATE TABLE IF NOT EXISTS assistants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assistant_id TEXT NOT NULL UNIQUE,
                    member_id INTEGER,
                    description TEXT,
                    apikey_id INTEGER, 
                    FOREIGN KEY (apikey_id)
                    REFERENCES apikeys(id)
                    ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS threads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        thread_id TEXT NOT NULL UNIQUE,
                        merber_id INTEGER,
                        description TEXT,
                        assistant_id INTEGER, 
                        FOREIGN KEY (assistant_id)
                        REFERENCES assistants(id)
                        ON DELETE CASCADE
                    );
                CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id TEXT NOT NULL UNIQUE,
                        name TEXT,           
                        description TEXT,
                        assistant_id INTEGER, 
                        FOREIGN KEY (assistant_id)
                        REFERENCES assistants(id)
                        ON DELETE CASCADE
                    );
                CREATE TABLE IF NOT EXISTS predicts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL UNIQUE,
                        name TEXT,      
                        predicted_date TEXT,                 
                        decision TEXT,
                        predicted_price INTEGER,
                        close_price   INTEGER,
                        percent       REAL                   
                    );
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    trade_date TEXT,
                    buy_price INTEGER,
                    sell_price INTEGER,
                    start_price   INTEGER,
                    high_price   INTEGER,
                    qty   INTEGER
                    );                                
            ''')
            await db.commit()
    except Exception as e:
        logging.error(f"Setup tables failed: {e}")
        raise

async def _insertData(table, data, unique_key_column=None):
    try:
        async with aiosqlite.connect(db_name) as db:
            await db.execute("PRAGMA foreign_keys = ON")        
            if unique_key_column and unique_key_column in data:
                query = f"SELECT COUNT(*) FROM {table} WHERE {unique_key_column} = ?"
                cursor = await db.execute(query, (data[unique_key_column],))
                count = await cursor.fetchone()
                if count[0] > 0:
                    logging.warning(f"Record already exists in {table} with {unique_key_column} = {data[unique_key_column]}. Skipping insert.")
                    return

            placeholders = ', '.join(['?'] * len(data))
            columns = ', '.join(data.keys())
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            await db.execute(sql, list(data.values()))
            await db.commit()
        logging.info(f"Data inserted successfully into {table}.")
    except aiosqlite.Error as e:
        logging.error(f"Error inserting data into {table}: {e}")
        raise

async def _updateData(table, data, condition_field, condition_value):
    try:
        async with aiosqlite.connect(db_name) as db:
            await db.execute("PRAGMA foreign_keys = ON")        
            setters = ', '.join([f"{key} = ?" for key in data.keys()])
            sql = f"UPDATE {table} SET {setters} WHERE {condition_field} = ?"
            await db.execute(sql, list(data.values()) + [condition_value])
            await db.commit()
        logging.info(f"Data in {table} updated successfully.")
    except aiosqlite.Error as e:
        logging.error(f"Error updating data in {table}: {e}")
        raise

async def _deleteData(table, condition_field, condition_value):
    try:
        async with aiosqlite.connect(db_name) as db:
            await db.execute("PRAGMA foreign_keys = ON")        
            sql = f"DELETE FROM {table} WHERE {condition_field} = ?"
            await db.execute(sql, (condition_value,))
            await db.commit()
        logging.info(f"Data deleted successfully from {table}.")
    except aiosqlite.Error as e:
        logging.error(f"Error deleting data from {table}: {e}")
        raise
async def _deleteAllData(table):
    try:
        async with aiosqlite.connect(db_name) as db:
            await db.execute("PRAGMA foreign_keys = ON")        
            sql = f"DELETE FROM {table}"
            await db.execute(sql)
            await db.commit()
        logging.info(f"Data deleted successfully from {table}.")
    except aiosqlite.Error as e:
        logging.error(f"Error deleting data from {table}: {e}")
        raise
async def _queryToDataframe(query, params=None):
    try:
        async with aiosqlite.connect(db_name) as db:
                
            if params is not None:
               cursor = await db.execute(query,params)
            else:
                cursor = await db.execute(query)
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    except aiosqlite.Error as e:
        logging.error(f"Error executing query: {e}")
        return pd.DataFrame()

async def _queryByField(table, field_name, field_value):
    try:
        query = f"SELECT * FROM {table} WHERE {field_name} = ?"
        async with aiosqlite.connect(db_name) as db:
            cursor = await db.execute(query, (field_value,))
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    except aiosqlite.Error as e:
        logging.error(f"Error querying {table} by {field_name}: {e}")
        return pd.DataFrame()
async def _queryIdRange(table, start_id, end_id):
    try:
        # IPO 날짜 문자열에서 날짜 부분을 추출하고, 이를 기준으로 60일이 지난 업체를 조회하는 쿼리
        query = f"""
            SELECT * 
            FROM {table} 
            WHERE id BETWEEN ? AND ?
            AND DATE(SUBSTR(ipo, 1, 10)) <= DATE('now', '-60 days')
        """
        async with aiosqlite.connect(db_name) as db:
            cursor = await db.execute(query, (start_id, end_id))
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    except aiosqlite.Error as e:
        logging.error(f"Error querying {table} with IPO date range and ID range {start_id} to {end_id}: {e}")
        return pd.DataFrame()

async def _queryJoin(table1, table2, join_condition, select_fields, where_clause=None, where_params=None):
    try:
        base_query = f"SELECT {', '.join(select_fields)} FROM {table1} JOIN {table2} ON {join_condition}"
        query = base_query + (f" WHERE {where_clause}" if where_clause else "")
        async with aiosqlite.connect(db_name) as db:
            cursor = await db.execute(query, where_params or [])
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    except aiosqlite.Error as e:
        logging.error(f"Error performing join query between {table1} and {table2}: {e}")
        return pd.DataFrame()
    
# 현재 이벤트 루프를 가져오거나 새로운 이벤트 루프를 생성하는 함수
def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

# 비동기 함수를 동기적으로 실행하기 위한 래퍼 함수
def run_async(coroutine):
    loop = get_or_create_eventloop()
    return loop.run_until_complete(coroutine)        

def removeDbFile(file_path, max_attempts=3, wait_seconds=1):
    run_async(_removeDbFile(file_path, max_attempts, wait_seconds))

def setupTables():
    run_async(_setupTables())

def insertData(table, data, unique_key_column=None):
    run_async(_insertData(table, data, unique_key_column))

def updateData(table, data, condition_field, condition_value):
    run_async(_updateData(table, data, condition_field, condition_value))

def deleteData(table, condition_field, condition_value):
    run_async(_deleteData(table, condition_field, condition_value))
def deleteAllData(table):
    run_async(_deleteAllData(table))
def queryToDataframe(query, params=None):
    return run_async(_queryToDataframe(query, params))

def queryByField(table, field_name, field_value):
    return run_async(_queryByField(table, field_name, field_value))
def queryIdRange(table, start_id, end_id):
    return run_async(_queryIdRange(table, start_id, end_id))

def queryJoin(table1, table2, join_condition, select_fields, where_clause=None, where_params=None):
    return run_async(_queryJoin(table1, table2, join_condition, select_fields, where_clause, where_params))

def codes():
    COST = 100  # 최소 단가
    VOLUME = 300000  # 최소 거래량
    results = []
    codes = []

    for chk in [0, 1]:  # 0은 코스피, 1은 코스닥
        url = f'https://finance.naver.com/sise/sise_rise.naver?sosok={chk}'
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            trs = soup.select('table.type_2 tr')
            del trs[0:2]  # 제목 행 제거
            
            for tr in trs:
                record = []
                tds = tr.find_all('td')
                for td in tds:
                    if td.select('a[href]'):
                        code = td.find('a').get('href').split('=')[-1].strip().replace(',', '')
                        name = td.get_text().strip().replace(',', '')
                        
                        record.append(code)  # 주식 코드
                        if name == '':
                            name = '없다'
                        record.append(name)  # 업체명
                    else:
                        data = td.get_text().strip().replace(',', '')
                        if data.isdigit():
                            record.append(int(data))
                        else:
                            record.append(data)
                if len(record) >= 7 and record[3] >= COST and record[6] >= VOLUME:
                    grade = record[5].replace('+','').replace('%','')
                    # 저장은 하고 있지만 코드만 사용 나중에 사용에 대한 고려
                    results.append({'code':record[1],'name':record[2],'price':record[3],'grade':float(grade),'volume':record[6],'stock': chk})  # 업체명과 시장 구분(0 또는 1) 추가
                    # print(f"{row['code']} {row['name']} {row['price']} {row['grade']} {row['volume']} {row['stock']}")
                    # codes.append(record[1])

                    

        else:
            print("Failed to retrieve data:", response.status_code)
    results.sort(key=lambda x: x['grade'], reverse=True)
    # 상위 10개 요소의 'code' 값만을 포함하는 새로운 리스트 생성
    codes = [result['code'] for result in results[:3]]
    return codes
# 비동기 함수 실행

def main():
    removeDbFile(db_name)
    setupTables()

    insertData('employees', {
    'first_name': 'Alice',
    'last_name': 'Smith',
    'email_address': 'alice.smith@example.com',
    'phone_number': '123-456-7890',
    'department': 'Engineering',
    'position': 'Software Engineer',
    'hire_date': '2023-01-01',
    'salary': 75000,
    'employment_status': 'Full-time',
    'date_of_birth': '1990-05-15',
    'address': '123 Main St, Anytown, USA',
    'gender': 'Female',
    'nationality': 'American',
    'emergency_contact_name': 'John Doe',
    'emergency_contact_relationship': 'Spouse',
    'emergency_contact_number': '098-765-4321'
    },"email_address")
    updateData('employees', {'department': 'Engineering'}, "email_address", 'alice.smith@example.com')
    # deleteData('employees', "email_address", 'alice.smith@example.com')
    employees_df = queryToDataframe("SELECT * FROM employees")
    print("\nEmployee Data:")
    print(employees_df)
    st.dataframe(employees_df, use_container_width=True)

    insertData('customers', {
    'customer_id': 'C001',
    'first_name': 'Bob',
    'last_name': 'Brown',
    'email_address': 'bob.brown@example.com',
    'phone_number': '987-654-3210',
    'address': '456 Secondary St, Anothertown, USA',
    'city': 'Anothertown',
    'state_province': 'Anystate',
    'postal_code': '12345',
    'country': 'USA',
    'date_of_birth': '1985-08-25',
    'gender': 'Male',
    'account_creation_date': '2023-02-01',
    'last_purchase_date': '2023-02-15',
    'customer_segment': 'Regular',
    'preferences': 'Tech Products',
    'loyalty_points': 500
    },"email_address")
    updateData('customers', {'city': 'New City'}, "customer_id", 'C001')
    # deleteData('customers', "customer_id", 'C001')
    customers_df = queryToDataframe("SELECT * FROM customers")
    print("\nCustomer Data:")
    print(customers_df)
    st.dataframe(customers_df, use_container_width=True)

    # Members 테이블 예시
    insertData('members', {
    'member_id': 'M001',
    'name': 'John Doe',  # 'username' 대신 'name'을 사용
    'password': 'securepassword',  # 실제 암호화된 값이어야 함
    'first_name': 'John',
    'last_name': 'Doe',
    'email_address': 'john.doe@example.com',
    'phone_number': '123-456-7890',
    'address': '123 Main St, Anytown, USA',
    'date_of_birth': '1990-01-01',
    'gender': 'Male',
    'registration_date': '2023-01-01',
    'membership_type': 'Premium',
    'membership_status': 'Active',
    'last_login_date': '2023-02-20',
    'profile_photo': 'path/to/photo.jpg',
    'preferences': 'News, Technology',
    'notes': 'Important member'
    },"email_address")
    updateData('members', {'email_address': 'john.doe@example.com'}, "member_id", 'M001')
    # deleteData('members', "member_id", 'M001')
    members_df = queryToDataframe("SELECT * FROM members")
    print("\nMember Data:")
    print(members_df)
    st.dataframe(members_df, use_container_width=True)

    # Api_keys 테이블 예시
    insertData('apikeys', {
    'api_key_value': 'apikey123456',
    'creation_date': '2023-01-01',
    'expiration_date': '2024-01-01',  # 만료 날짜 설정
    'owner_user_id': 1,  # 소유자 ID, 실제 사용자 ID에 맞게 설정해야 함
    'status': 'Active',  # API 키 상태
    'usage_limit': 1000,  # 사용 제한 설정, 필요에 따라 조정
    'usage_count': 0,  # 초기 사용 횟수는 0으로 시작
    'last_used_date': None,  # 처음에는 사용되지 않았으므로 None
    'permissions_scope': 'read,write',  # 권한 범위 설정
    'description_notes': 'API key for external service'  # API 키 설명
    },"api_key_value")
    updateData('apikeys', {'status': 'Inactive'}, "api_key_value", 'apikey123456')
    # deleteData('apikeys', "api_key_value", 'apikey123456')
    api_keys_df = queryToDataframe("SELECT * FROM apikeys")
    print("\nAPI Key Data:")
    print(api_keys_df)
    st.dataframe(api_keys_df, use_container_width=True)

    # Assistant 테이블 예시
    insertData('assistants', {
    'assistant_id': 'A001',
    'instruction': 'Create something amazing',
    'model': 'model_name',  # 사용할 모델의 이름 또는 식별자
    'apikey_id': 1,  # api_key 테이블에서 참조하는 apikey_id, 실제 값에 맞게 설정
    'file_id': 'file123',  # 관련 파일이나 자료의 식별자, 필요에 따라 설정
    'status': 'active',  # assistant의 현재 상태
    'description': 'Assistant for generating creative content'  # assistant에 대한 설명
    },"assistant_id")
    updateData('assistants', {'model': 'new_model'}, "assistant_id", 'A001')
    # deleteData('assistants', "assistant_id", 'A001')
    assistant_df = queryToDataframe("SELECT * FROM assistants")
    print("\nAssistant Data:")
    print(assistant_df)
    st.dataframe(assistant_df, use_container_width=True)

    # Thread 테이블 예시
    insertData('threads', {
    'thread_id': 'T001',
    'apikey_id': 1,  # API 키 ID, 실제 사용중인 API 키 ID에 맞게 설정해야 함
    'created_date': '2023-02-15',  # 스레드 생성 날짜
    'last_used_date': '2023-02-16',  # 스레드 마지막 사용 날짜, 필요에 따라 설정
    'status': 'Open',  # 스레드 상태, 예: 'Open', 'Closed', 'Resolved' 등
    'description': 'Detailed description of the urgent issue'  # 스레드에 대한 설명
    },"thread_id")
    updateData('threads', {'status': 'Resolved'}, "thread_id", 'T001')
    # deleteData('threads', "thread_id", 'T001')
    thread_df = queryToDataframe("SELECT * FROM threads")
    print("\nThread Data:")
    print(thread_df)
    st.dataframe(thread_df, use_container_width=True)

    # 조인 쿼리 실행 예시
    join_fields = [
        'e.first_name AS EmployeeFirstName', 
        'e.last_name AS EmployeeLastName', 
        'c.first_name AS CustomerFirstName', 
        'c.last_name AS CustomerLastName'
    ]
    join_condition = "e.id = c.id"
    where_clause = "e.first_name = ?"
    where_params = ['Alice']

    joined_df = queryJoin(
        table1='employees e', 
        table2='customers c', 
        join_condition=join_condition, 
        select_fields=join_fields, 
        where_clause=where_clause, 
        where_params=where_params
    )

    print("\nJoined Employee and Customer Data:")
    print(joined_df)
    # streamlit를 사용하는 경우
    st.dataframe(joined_df, use_container_width=True)

if __name__ == "__main__":
    main()