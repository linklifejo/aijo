import asyncio
import aiosqlite
from datetime import datetime
import pandas as pd
import FinanceDataReader as fdr

# 비동기 I/O 작업을 위한 Semaphore 설정
sem = asyncio.Semaphore(1000)

async def fetch_range(start_id, end_id):
    async with aiosqlite.connect('inet.db') as db:
        async with db.execute('SELECT code, name FROM krxs WHERE id BETWEEN ? AND ?', (start_id, end_id)) as cursor:
            rows = await cursor.fetchall()
            return rows

async def data_reader_async(code, name, date):
    async with sem:  # 동시 실행을 제한
        data =  fdr.DataReader(code, date)
        data['Code'] = code
        data['Name'] = name
        return data

async def process_data_ranges(id_ranges):
    tasks = []
    for start_id, end_id in id_ranges:
        tasks.append(fetch_range(start_id, end_id))
    codes_results = await asyncio.gather(*tasks)

    # FinanceDataReader 작업 준비
    fdr_tasks = []
    date = datetime(2024, 3, 10).strftime('%Y-%m-%d')
    for codes in codes_results:
        for code, name in codes:
            fdr_tasks.append(data_reader_async(code, name, date))
    
    # 모든 FinanceDataReader 작업 실행
    data_results = await asyncio.gather(*fdr_tasks)
    return data_results

async def main():
    print(datetime.now())
    # ID 범위 리스트 세분화
    id_ranges = [(i, i + 249) for i in range(1, 2554, 250)]

    # 범위별 데이터 처리
    results = await process_data_ranges(id_ranges)
    all_df = pd.concat(results, ignore_index=True)
    print(all_df)
    print(datetime.now())

asyncio.run(main())
