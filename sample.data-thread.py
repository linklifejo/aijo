import asyncio
import aiosqlite
import datetime
import pandas as pd
import FinanceDataReader as fdr
from concurrent.futures import ThreadPoolExecutor

async def fetch_range(start_id, end_id):
    async with aiosqlite.connect('inet.db') as db:
        async with db.execute('SELECT code, name FROM krxs WHERE id BETWEEN ? AND ?', (start_id, end_id)) as cursor:
            rows = await cursor.fetchall()
            return rows

def sync_data_reader(code, date):
    return fdr.DataReader(code, date)

async def data_reader_async(code, name, date):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=4) as executor:
        data = await loop.run_in_executor(executor, sync_data_reader, code, date)
    data['code'] = code
    data['name'] = name
    return data

async def main():
    print(datetime.datetime.now())
    # ID 범위 리스트
    id_ranges = [
        (1, 250), (251, 500), (501, 750), (751, 1000),
        (1001, 1250), (1251, 1500), (1501, 1750),
        (1751, 2000), (2001, 2250), (2251, 2500), (2501, 2553)
    ]

    # 데이터베이스 쿼리 태스크
    db_tasks = [fetch_range(start, end) for start, end in id_ranges]
    codes_results = await asyncio.gather(*db_tasks)

    # FinanceDataReader 호출 태스크
    date = datetime.datetime(2024, 3, 12).strftime('%Y-%m-%d')
    fdr_tasks = []
    for codes in codes_results:
        for code, name in codes:
            fdr_tasks.append(data_reader_async(code, name, date))

    # 모든 FinanceDataReader 태스크 실행
    data_results = await asyncio.gather(*fdr_tasks)

    # 최종 결과 처리
    all_df = pd.concat(data_results, axis=0, ignore_index=True)
    print(all_df)
    print(datetime.datetime.now())

asyncio.run(main())
# CHATGPT를 만든 OPEN AI회사에서 만든 인공지능API를 사용해서 프로그램을 개발중이고, 
# 90퍼정도 개발이 진행되고 있어, 한달에 200만원 정도들어가는데 다왔는데 돈을 구할방법이 없네, 
# 14일까지 150만원이 필요한데..2달 정도면 완성될듯한데..동생이 도와주면 안될까 부탁좀 할게
# 시간이 지나면 물론 투자도 받아야 하지만, 조심 스럽지만 Open ai 에 chats 스토어에 프로그램을 출시하면,
# 유튜브처럼 수익을 창출할수 있거든...투자한다고 생각하고 좀 도와주라, 정확하게 말하면 저돈은 카드값이야...`1``ㅊ`

