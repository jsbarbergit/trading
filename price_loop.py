import sys
import json
from datetime import datetime, timedelta

price_file='prices.json'

price_data=json.loads(open(price_file).read())
#How many prices do we have
price_count=len(price_data['prices'])
print('No. of prices: ' + str(price_count))
print('first price data: ' + price_data['prices'][0]['snapshotTime'])
print('last price data: ' + price_data['prices'][price_count - 1]['snapshotTime'])



#Get the date 21 days ago
# Forex markets are open 6 days a week, so we're looking for 21 days trading, which will be 
# 21 days + 3 sundays, so 24
long_avg=21

nontradingdays=(long_avg / 7)



today=datetime.now().date()
start_date=today - timedelta(days=(long_avg + nontradingdays))




print('Today: ' + str(today))
print(str(long_avg) + ' trading days ago: ' + str(start_date))


fxmkts=['GBPUSD', 'GBPEUR']
count=0
for mkt in fxmkts:
    print('Mkt' + str(count) + ': ' +  mkt)
    count+=1


long_avg=21
for p in range(long_avg):
  print('p: ' + str(p))
