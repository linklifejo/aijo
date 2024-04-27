codes = ['1','2']
dicts = {}
for code in codes:
    dicts[code] = {'qty':10+int(code),'price':100+int(code)}
# for code,value in dicts.items():
#     print(code,value['qty'],value['price'])
keys = dicts.keys()
for key in keys:
    print(dicts[key]['qty'],end='')
    print('  ',dicts[key]['price'])