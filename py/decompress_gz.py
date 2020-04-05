from gzip import decompress
from json import loads
from requests import get
from json import loads

files = [
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161231-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161230-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161229-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161228-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161227-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161226-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161225-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161224-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161223-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161222-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161221-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161220-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161219-CRYPTOCURRENCY',
'https://datamine.cmegroup.com/cme/api/v1/download?fid=20161218-CRYPTOCURRENCY'

]

output_path = 'btc/output.txt'

with open(output_path, 'a') as output_file:
    
    for url in files:
        print(url)
        filename = url.split("=")[-1].split('-')[0]
        filepath = 'btc/' + filename + '.txt'

        print('downloading...')
        response = get(url, auth=('API_QUANTPEDIA', 'Jank0Hrask0'))
        if response.status_code == 200:
            data = (response.content)
            json_contents_string = decompress(data)
            print('decompressing...')
            #print(json_contents_string)
            with open(filepath, 'wb') as f:
                f.write(json_contents_string)    


        print('Path >' + filepath)
        with open(filepath , 'r') as f:
            print('reading...')
            json_contents_string = f.read().split('\n')
            #print(json_contents_string)
            matched_line = [line for line in json_contents_string if filename+'-22:00:00' in line and 'BRTI' in line and 'SecurityDefinition' not in line][0]
            #print(matched_line)
            json = loads(matched_line)
            
            entires = json['mdEntries'][0]
            price = entires['mdEntryPx']
            output_file.write('\n' + filename + ';' + str(price))
            #print(filename)
            #print(price)
            #print(price)


print('done')

