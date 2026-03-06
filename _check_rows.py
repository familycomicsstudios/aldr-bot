import requests,csv
from io import StringIO
url='https://docs.google.com/spreadsheets/d/e/2PACX-1vRrZEUcAFIiGmzFAjjdUVKWhDSLue_SvTQIxT4ZbhlvBa6yc4l4juAZn3HREfvO0VIv2ms98453VItI/pub?gid=0&single=true&output=tsv'
resp=requests.get(url,timeout=10)
resp.raise_for_status()
data=list(csv.reader(StringIO(resp.text),delimiter='\t'))
print('rows',len(data)-1)
for idx,row in enumerate(data[1:],start=1):
    pass
# print last 3
for i,row in enumerate(data[-3:],start=len(data)-3):
    name=row[1] if len(row)>1 else ''
    print(i+1, name)
