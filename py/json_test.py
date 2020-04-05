#import json
import requests
import gzip

url = "https://datamine.cmegroup.com/cme/api/v1/download?fid=20170323-CRYPTOCURRENCY"
#filename = url.split("/")[-1]
filename = 'test.gz'
#with open(filename, "wb") as f:
#    r = requests.get(url, auth=('API_QUANTPEDIA', 'Jank0Hrask0'))
    
#    decompressed_file = gzip.GzipFile(fileobj=r)
#    f.write(decompressed_file.read())
r = requests.get(url, auth=('API_QUANTPEDIA', 'Jank0Hrask0'), stream=True)
    
if r.status_code == 200:
    with open(filename , 'wb') as f:
        f.write(r.raw.read())    
    
print('done')
