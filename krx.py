import asyncio
import aiosqlite
from datetime import datetime
import pandas as pd
import FinanceDataReader as fdr
import concurrent
from concurrent.futures import ThreadPoolExecutor

# 쓰레드 4개를 사용하며,각각 10개의 비동기를 실행함
sem = asyncio.Semaphore(10)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
async def fetch_range(start_id, end_id):
    async with aiosqlite.connect('inet.db') as db:
        async with db.execute('SELECT code, name FROM krxs WHERE id BETWEEN ? AND ?', (start_id, end_id)) as cursor:
            rows = await cursor.fetchall()
            return rows
        
async def data_reader_async(code, name, date):
    async with sem:  # 동시 실행을 제한
        loop = asyncio.get_running_loop()
        try:
            data = await loop.run_in_executor(executor, lambda: fdr.DataReader(code, date))
        except Exception as e:
            # 적절한 에러 처리
            print(f"Error fetching data: {e}")
            return None

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

async def main_asyn():
    print(datetime.now())
    # ID 범위 리스트 세분화
    id_ranges = [(i, i + 249) for i in range(1, 2554, 250)]

    # 범위별 데이터 처리
    results = await process_data_ranges(id_ranges)
    all_df = pd.concat(results, ignore_index=True)
    print(all_df)
    print(datetime.now())
def main():
    asyncio.run(main_asyn())
    executor.shutdown()
if __name__ == "__main__":
    main()
