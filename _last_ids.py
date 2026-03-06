import requests,csv
from io import StringIO
url='https://docs.google.com/spreadsheets/d/e/2PACX-1vRrZEUcAFIiGmzFAjjdUVKWhDSLue_SvTQIxT4ZbhlvBa6yc4l4juAZn3HREfvO0VIv2ms98453VItI/pub?gid=0&single=true&output=tsv'
resp=requests.get(url,timeout=10)
resp.raise_for_status()
data=list(csv.reader(StringIO(resp.text),delimiter='\t'))
rows=[]
for i,row in enumerate(data[1:],start=1):
    ald = row[0].strip() if len(row)>0 else ''
    if ald:
        rows.append((i, ald, row[1] if len(row)>1 else ''))
# print last 3
for i,ald,name in rows[-3:]:
    print(i, ald, name)
