import requests
from json import loads
import time

isin_ids = ['US0042391096',
'US00430M1018',
'US00434H1086',
'US0043371014',


]

output_path = 'figi/output.txt'

with open(output_path, 'a') as output_file:
    for isin in isin_ids:
        
        url = 'https://api.openfigi.com/v1/mapping'
        headers = {'Content-Type':'text/json', 'X-OPENFIGI-APIKEY':'a9ee5c1a-b853-48f1-94a7-bf5a3b07137f'}
        #headers = {'Content-Type':'text/json'}
        payload = '[{"idType":"ID_ISIN","idValue":"' + isin + '"}]'

        response = requests.post(url, data=payload, headers=headers)
        data = (response.content)
        entries = loads(data)
        if len(entries) != 0:
            if 'error' in entries[0]:   # error occured in json call. ''No identifier found.'
                print('---')
                output_file.write('---' + '\n')
            else:
                name = entries[0]['data'][0]['name']
                ticker = entries[0]['data'][0]['ticker']
                print(name + ': ' + ticker)
                output_file.write(str(ticker) + '\n')
        time.sleep(5)

print('! DONE !')
