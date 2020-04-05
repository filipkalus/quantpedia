from requests import get
from json import loads
from datetime import datetime
from datetime import timedelta
import time

start_date = "20190102"
stop_date =  "20200101"

output_path = 'earnings/output.txt'

with open(output_path, 'a') as output_file:
    start = datetime.strptime(start_date, "%Y%m%d")
    stop = datetime.strptime(stop_date, "%Y%m%d")
    while start < stop:
        start = start + timedelta(days=1)
        date_str = start.strftime("%Y%m%d")

        # Parse data
        time.sleep(1.5)
        response = get('https://freeapi.earningscalendar.net/?date=' + date_str)
        if response.status_code == 200:
            data = (response.content)
            entires = loads(data)
            entries_str = ''
            if len(entires) != 0:
                print(start)
                for entry in entires:
                    entries_str += entry['ticker'] + ';'

                output_file.write(str(start) + '; ')
                output_file.write(entries_str + '\n')
            else:
                continue
print('DONE')


    
    
