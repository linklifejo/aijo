import pandas as pd
'''코스피주식종목코드(kospi_code.mst) 정제 파이썬 파일'''

import urllib.request
import ssl
import zipfile
import os
import pandas as pd

base_dir = os.getcwd()

def kospi_master_download(base_dir, verbose=False):
    cwd = os.getcwd()
    if (verbose): print(f"current directory is {cwd}")
    ssl._create_default_https_context = ssl._create_unverified_context

    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
                               base_dir + "\\kospi_code.zip")

    os.chdir(base_dir)
    if (verbose): print(f"change directory to {base_dir}")
    kospi_zip = zipfile.ZipFile('kospi_code.zip')
    kospi_zip.extractall()

    kospi_zip.close()

    if os.path.exists("kospi_code.zip"):
        os.remove("kospi_code.zip")


def get_kospi_master_dataframe(base_dir):
    file_name = base_dir + "\\kospi_code.mst"
    tmp_fil1 = base_dir + "\\kospi_code_part1.tmp"
    tmp_fil2 = base_dir + "\\kospi_code_part2.tmp"

    wf1 = open(tmp_fil1, mode="w")
    wf2 = open(tmp_fil2, mode="w")

    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            rf1 = row[0:len(row) - 228]
            rf1_1 = rf1[0:9].rstrip().zfill(6)  # 단축코드를 6자리로 포맷
            rf1_2 = rf1[9:21].rstrip()
            rf1_3 = rf1[21:].strip()
            wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
            rf2 = row[-228:]
            wf2.write(rf2)

    wf1.close()
    wf2.close()

    part1_columns = ['단축코드', '표준코드', '한글명']
    df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')

    field_specs = [2, 1, 4, 4, 4,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 9, 5, 5, 1,
                   1, 1, 2, 1, 1,
                   1, 2, 2, 2, 3,
                   1, 3, 12, 12, 8,
                   15, 21, 2, 7, 1,
                   1, 1, 1, 1, 9,
                   9, 9, 5, 9, 8,
                   9, 3, 1, 1, 1
                   ]

    part2_columns = ['그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류',
                     '제조업', '저유동성', '지배구조지수종목', 'KOSPI200섹터업종', 'KOSPI100',
                     'KOSPI50', 'KRX', 'ETP', 'ELW발행', 'KRX100',
                     'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',
                     'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설',
                     'Non1', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',
                     'SRI', '기준가', '매매수량단위', '시간외수량단위', '거래정지',
                     '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',
                     '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',
                     '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',
                     '상장주수', '자본금', '결산월', '공모가', '우선주',
                     '공매도과열', '이상급등', 'KRX300', 'KOSPI', '매출액',
                     '영업이익', '경상이익', '당기순이익', 'ROE', '기준년월',
                     '시가총액', '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능'
                     ]

    df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)

    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

    # clean temporary file and dataframe
    del (df1)
    del (df2)
    os.remove(tmp_fil1)
    os.remove(tmp_fil2)
    
    df['마켓'] = 'KOSPI'  # '시장' 필드 추가 및 값 할당
    
    print("Done")

    return df


kospi_master_download(base_dir)
df = get_kospi_master_dataframe(base_dir) 

#df3 = df[df['KRX증권'] == 'Y']
df3 = df
df3[['단축코드', '한글명','관리종목','거래정지','증거금비율', '상장일자', '마켓']].to_excel('kospi_code_selected.xlsx', index=False)


base_dir = os.getcwd()

def kosdaq_master_download(base_dir, verbose=False):

    cwd = os.getcwd()
    if (verbose): print(f"current directory is {cwd}")
    ssl._create_default_https_context = ssl._create_unverified_context
    
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
                               base_dir + "\\kosdaq_code.zip")

    os.chdir(base_dir)
    if (verbose): print(f"change directory to {base_dir}")
    kosdaq_zip = zipfile.ZipFile('kosdaq_code.zip')
    kosdaq_zip.extractall()
    
    kosdaq_zip.close()

    if os.path.exists("kosdaq_code.zip"):
        os.remove("kosdaq_code.zip")

def get_kosdaq_master_dataframe(base_dir):
    file_name = base_dir + "\\kosdaq_code.mst"
    tmp_fil1 = base_dir + "\\kosdaq_code_part1.tmp"
    tmp_fil2 = base_dir + "\\kosdaq_code_part2.tmp"

    wf1 = open(tmp_fil1, mode="w")
    wf2 = open(tmp_fil2, mode="w")

    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            rf1 = row[0:len(row) - 222]
            rf1_1 = rf1[0:9].rstrip().zfill(6)  # 단축코드를 6자리로 포맷
            rf1_2 = rf1[9:21].rstrip()
            rf1_3 = rf1[21:].strip()
            wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
            rf2 = row[-222:]
            wf2.write(rf2)

    wf1.close()
    wf2.close()

    part1_columns = ['단축코드','표준코드','한글종목명']
    df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')

    field_specs = [2, 1,
                   4, 4, 4, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 9,
                   5, 5, 1, 1, 1,
                   2, 1, 1, 1, 2,
                   2, 2, 3, 1, 3,
                   12, 12, 8, 15, 21,
                   2, 7, 1, 1, 1,
                   1, 9, 9, 9, 5,
                   9, 8, 9, 3, 1,
                   1, 1
                   ]

    part2_columns = ['증권그룹구분코드','시가총액 규모 구분 코드 유가',
                     '지수업종 대분류 코드','지수 업종 중분류 코드','지수업종 소분류 코드','벤처기업 여부 (Y/N)',
                     '저유동성종목 여부','KRX 종목 여부','ETP 상품구분코드','KRX100 종목 여부 (Y/N)',
                     'KRX 자동차 여부','KRX 반도체 여부','KRX 바이오 여부','KRX 은행 여부','기업인수목적회사여부',
                     'KRX 에너지 화학 여부','KRX 철강 여부','단기과열종목구분코드','KRX 미디어 통신 여부',
                     'KRX 건설 여부','(코스닥)투자주의환기종목여부','KRX 증권 구분','KRX 선박 구분',
                     'KRX섹터지수 보험여부','KRX섹터지수 운송여부','KOSDAQ150지수여부 (Y,N)','주식 기준가',
                     '정규 시장 매매 수량 단위','시간외 시장 매매 수량 단위','거래정지 여부','정리매매 여부',
                     '관리 종목 여부','시장 경고 구분 코드','시장 경고위험 예고 여부','불성실 공시 여부',
                     '우회 상장 여부','락구분 코드','액면가 변경 구분 코드','증자 구분 코드','증거금 비율',
                     '신용주문 가능 여부','신용기간','전일 거래량','주식 액면가','주식 상장 일자','상장 주수(천)',
                     '자본금','결산 월','공모 가격','우선주 구분 코드','공매도과열종목여부','이상급등종목여부',
                     'KRX300 종목 여부 (Y/N)','매출액','영업이익','경상이익','단기순이익','ROE(자기자본이익률)',
                     '기준년월','전일기준 시가총액 (억)','그룹사 코드','회사신용한도초과여부','담보대출가능여부','대주가능여부'
                     ]

    df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)

    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

    # Clean temporary file and dataframe
    del (df1)
    del (df2)
    os.remove(tmp_fil1)
    os.remove(tmp_fil2)
    
    # Add '시장' column with 'kosdaq' value
    df['마켓'] = 'kosdaq'

    print("Done")

    return df

kosdaq_master_download(base_dir)
df = get_kosdaq_master_dataframe(base_dir)
df[['단축코드', '한글종목명','관리 종목 여부','거래정지 여부','증거금 비율', '주식 상장 일자', '마켓']].to_excel('kosdaq_code.xlsx', index=False)

file_path1 = 'kosdaq_code.xlsx'
file_path2 = 'kospi_code_selected.xlsx'
output_file_path = 'combined_excel.xlsx'

# Excel 파일 로드
df1 = pd.read_excel(file_path1)
df2 = pd.read_excel(file_path2)

# 업체코드가 숫자인 경우에만 필터링
df1_filtered = df1[df1['단축코드'].astype(str).str.isdigit() & (df1['관리 종목 여부'] == 'N') & (df1['거래정지 여부'] == 'N')].copy()  # .copy() 추가
df2_filtered = df2[df2['단축코드'].astype(str).str.isdigit() & (df2['관리종목'] == 'N') & (df2['거래정지'] == 'N')].copy()  # .copy() 추가

# 필드 이름 통일
df1_filtered.rename(columns={'단축코드': '종목코드', '한글종목명': '한글명', '관리 종목 여부': '관리종목', '거래정지 여부': '거래정지', '증거금 비율': '증거금비율', '주식 상장 일자': '상장일자'}, inplace=True)
df2_filtered.rename(columns={'단축코드': '종목코드', '한글명': '한글명', '관리종목': '관리종목', '거래정지': '거래정지', '증거금비율': '증거금비율', '상장일자': '상장일자'}, inplace=True)

# 상장일자를 'YYYY-MM-DD' 형식으로 변경
df1_filtered['상장일자'] = pd.to_datetime(df1_filtered['상장일자'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
df2_filtered['상장일자'] = pd.to_datetime(df2_filtered['상장일자'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

# 마켓 필드 추가
df1_filtered['마켓'] = 'kosdaq'
df2_filtered['마켓'] = 'kospi'

# 두 데이터프레임 수직 병합 (위에서 아래로 확장)
combined_df = pd.concat([df1_filtered, df2_filtered], ignore_index=True)

# 병합된 데이터프레임을 새 Excel 파일로 저장
combined_df.to_excel(output_file_path, index=False)

import sqlite3

# 엑셀 파일 경로 및 데이터베이스 파일 경로
excel_file_path = 'combined_excel.xlsx'
database_file_path = 'inet.db'

# Excel 파일에서 데이터프레임으로 데이터 읽기
df = pd.read_excel(excel_file_path)
df['종목코드'] = df['종목코드'].astype(str).str.zfill(6)
# 데이터프레임 열 이름을 영문으로 변경
df.rename(columns={
    '종목코드': 'code',
    '한글명': 'name',
    '관리종목': 'manage',
    '거래정지': 'stop',
    '증거금비율': 'buy_rate',
    '상장일자': 'ipo',
    '마켓': 'market'
}, inplace=True)
# SQLite 연결 및 커서 생성
conn = sqlite3.connect(database_file_path)
cur = conn.cursor()

# 테이블 생성 쿼리
create_table_query = '''
CREATE TABLE IF NOT EXISTS krxs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    name TEXT,
    manage TEXT, 
    stop TEXT,   
    buy_rate INTEGER,
    ipo TEXT,    
    market TEXT
);
'''

# 테이블 생성
cur.execute(create_table_query)

# 데이터프레임을 데이터베이스에 삽입
df.to_sql('krxs', conn, if_exists='replace', index=False)

# 커밋 및 연결 종료
conn.commit()
conn.close()
