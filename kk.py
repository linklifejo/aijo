import asyncio
import random

async def evaluate_stock():
    # 임의의 시간동안 "계산"을 시뮬레이션합니다.
    await asyncio.sleep(random.uniform(0.5, 2.0))  # 비동기로 대기
    sell = random.choice([True, False])  # 임의로 매도 결정을 합니다.
    return sell

async def main():
    # 세 개의 주식에 대해 매도 여부를 비동기적으로 평가
    tasks = [evaluate_stock() for _ in range(3)]
    
    results = await asyncio.gather(*tasks)  # 모든 비동기 작업을 동시에 실행하고 결과를 모읍니다.
    
    for result in results:
        print('Sell' if result else 'Hold')

# 비동기 메인 함수를 실행
asyncio.run(main())

# 종목선정은 한종목만 선택한다.
# 종목선정 기준은 시가대비 현재가 격차가 가장 큰것
# 
# 거래원칙은 분할매수/분할매도 이다. 
#  분할매수는 매수가능금액의 1%로 한다.
#  분할매도는 매수량(보유량)의 10%/50%로 한다.
#  trades테이블에 종목이 미존재하면 매수 이다
#  trades테이블에 종목이 존재하면 매수/매도 이다
#
#  매수원칙
#  선정된 종목은 시장가 1% 매수한다(테이블에 미존재시).
#  매수는 현재가가 매수가 대비 1% 적은 경우 시장가 1% 매수한다.
#
#  매도원칙
#  현재가가 매수가 대비 1% 큰 경우는 보유량의 10%를 시장가 매도한다.
#  매매수가능금액이 50%이고, 현재가가 매수가 대비 1% 작은 경우는 보유량의 50%를 시장가 매도한다.

