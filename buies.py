import model
import common
import requests
from bs4 import BeautifulSoup
def codes():
    COST = 100  #단가
    VOLUME = 2000000 #거래량
    url = 'https://finance.naver.com/sise/sise_rise.naver?sosok=1'


    response = requests.get(url)
    records = []
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html,'html.parser')
        trs = soup.select('table.type_2 tr')
        del trs[0:2]
        
        for tr in trs:
            record = []
            for td in tr.find_all('td'):
                if td.select('a[href]'):
                    code = td.find('a').get('href').split('=')[-1].strip().replace(',','')
                    record.append(code)  
                    name = td.get_text().strip().replace(',','')
                    record.append(name) 
                else:
                    data = td.get_text().strip().replace(',','')
                    if data.isdigit():
                        record.append(int(data))  
                    else:
                        record.append(data) 
            if len(record)>0:
                records.append(record)                 
                

    else : 
        print(response.status_code)
    result =[]
    codes = []

    for record in records:
        if len(record) > 1:
            if record[3] >= COST and record[6] >= VOLUME:
                result.append(record)
                codes.append(record[1])
    return codes

def code_write():
    x = []
    cs = []
    for code in codes():
        r = model.buy_and_sell(code)
        if r is not None:
            if r == '매수(Buy)':
                x.append(code)
    common.write_csv('buy.csv', x)
    data = common.read_csv('buy.csv')
    for code in data:
        cs.append(''.join(code))
    return cs
def code_read():
    cs = []
    data = common.read_csv('buy.csv')
    for code in data:
        cs.append(''.join(code))
    return cs
def main():
    code_write()
    for d in code_write():
        print(d)

if __name__ == '__main__':
    main()
