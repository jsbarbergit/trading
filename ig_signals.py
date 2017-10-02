import json
import sys
import requests
import csv
from requests.auth import HTTPDigestAuth
from datetime import datetime, timedelta

# FX Markets to trade
fxmajmkts=['GBPUSD','EURUSD','USDJPY','EURGBP','AUDUSD','USDCAD','EURJPY','GBPEUR','USDCHF','EURCHF']

# Get Config
with open(sys.argv[1]) as config_file:
    config = json.load(config_file)

# Login
ig_url="https://api.ig.com/gateway/deal/session"
body = '{ "identifier": "' + config["user"] + '", "password": "' + config["pass"] + '", "encryptedPassword": null }'
response = requests.post(config["uri"], data=body,headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json; charset=UTF-8", "X-IG-API-KEY": config["key"], "Version": "2" })
accountId=str(response.json()['currentAccountId'])
accountType=str(response.json()['accountType'])
sec_token=response.headers['X-SECURITY-TOKEN']
cst=response.headers['CST']
print('LOGIN Response: ' + str(response))



# Get the data

# Forex markets are open 6 days a week(sun-fri), so we're looking for 21 days trading, which will be 
# e.g if 21 days is our long_avg,  21 days + 3 saturdays, so 24 days data needed to assess
long_avg=int(config['long_avg_days'])
short_avg=int(config['short_avg_days'])
limit_avg=int(config['limit_avg'])
data_days = int(config['days_of_data'])
# How many whole weeks included - we'll add this figure on for our saturday count (non trading day) - add 1 just in case of rounding down 
# may result in 1 extra data point being returned but no harm
nontradingdays=(long_avg / 7) + 1
# end date for data range is today
today=datetime.now().date()
# Calc the start date
# Also need to add 1 more historical point to be bale to calc yesterdays long(21) and short(6) day avgs
start_date=today - timedelta(days=(data_days))
print('Fetching data for ' + str(data_days) + ' days')

# API Lookup for data
for mkt in fxmajmkts:
  #Outputfile
  prices_file='results/' + mkt + "-" + str(today) + ".csv"
  prices_file_csv=open(prices_file, 'w+')
  prices_file_csv.write('Symbol,Date,Open,High,Low,Close,Volume\n')
  prices_file_csv.close()
  # Fetch data for given range
  prices_payload= {"resolution": "DAY", "from": str(start_date), "to": str(today), "pageSize": str(data_days)}        
  print('GET API Call Payload Data: ' + str(prices_payload))
  epic="CS.D." + mkt + ".TODAY.IP"
  prices_uri="https://api.ig.com/gateway/deal/prices/" + epic
  prices_headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json; charset=UTF-8", "X-IG-API-KEY": str(config["key"]), "Version": "3", "X-SECURITY-TOKEN": sec_token, "CST": cst }
  price_response = requests.get(prices_uri, params=prices_payload, headers=prices_headers)
  print(mkt + ' Price Lookup Response: ' + str(price_response) )

  # loop through returned dictionary and populate csv file for historical record
  prices_file_csv=open(prices_file, 'a')
  for p in range(len(price_response.json()['prices'])):
    pdate=price_response.json()['prices'][p]['snapshotTimeUTC']
    popen_ask=price_response.json()['prices'][p]['openPrice']['ask']
    popen_bid=price_response.json()['prices'][p]['openPrice']['bid']
    popen=(popen_ask + popen_bid) / 2.0
    peod_ask=price_response.json()['prices'][p]['closePrice']['ask']
    peod_bid=price_response.json()['prices'][p]['closePrice']['bid']
    peod=(peod_ask + peod_bid) / 2.0
    pdayhigh_ask=price_response.json()['prices'][p]['highPrice']['ask']
    pdayhigh_bid=price_response.json()['prices'][p]['highPrice']['ask']
    pdayhigh=(pdayhigh_ask + pdayhigh_bid) / 2.0
    pdaylow_ask=price_response.json()['prices'][p]['lowPrice']['ask']
    pdaylow_bid=price_response.json()['prices'][p]['lowPrice']['ask']
    pdaylow=(pdaylow_ask + pdaylow_bid) / 2.0
    pvolume=price_response.json()['prices'][p]['lastTradedVolume']
    output_line=(mkt + ',' + str(pdate) + ',' + str(popen) + ',' + str(pdayhigh) + ',' + str(pdaylow) + ',' + str(peod) + ',' + str(pvolume) +'\n')
    prices_file_csv.write(output_line)
  prices_file_csv.close()
  print('No. of pages: ' + str(price_response.json()['metadata']['pageData']['totalPages']))
  print('Page size: ' + str(price_response.json()['metadata']['pageData']['pageSize']))
  print('No. of prices: ' + str(len(price_response.json()['prices'] ) ))

# Analyze Data

# Run data through model
for mkt in fxmajmkts:
  # Arrays for required values
  date_array = []
  # Opening Price
  day_open_array = []
  # Closing Price
  eod_close_array = []
  # Daily High Price
  daily_high_array = []
  # Daily Low Price
  daily_low_array = []

  prices_file='results/' + mkt + "-" + str(today) + ".csv"
  prices_file_csv=csv.reader(open(prices_file), delimiter=",")

  # first line is the header - pass over this
  headerline = prices_file_csv.next()
  # Loop through and build arrays
  count = 0
  for Symbol, Date, Open, High, Low, Close, Volume in prices_file_csv:
    # Add dates and closing prices
    date_array.insert(count,Date)
    day_open_array.insert(count,Open)
    eod_close_array.insert(count,Close)
    daily_high_array.insert(count, High)
    daily_low_array.insert(count,Low)
    # Increase counter
    count =+ 1

  # Store period high and low values
  # We have more data points than for required period (to calc previous long/short term avgs)
  # Only need data points for currnet period
  period_high_price = max(daily_high_array[(data_days - int(config['long_avg_days'])):len(daily_high_array)])
  period_low_price = min(daily_low_array[(data_days - int(config['short_avg_days'])):len(daily_low_array)])

  # Get yesterdays period avgs
  # need to offset by 1 day so - length of array -1
  y_eod_long_sum = sum(float(yles) for yles in eod_close_array[((len(eod_close_array) - int(config['long_avg_days'])) - 1):len(eod_close_array) - 1])
  y_long_period_price_avg = y_eod_long_sum / int(config['long_avg_days'])
  y_eod_short_sum = sum(float(yles) for yles in eod_close_array[((len(eod_close_array) - int(config['short_avg_days'])) - 1):len(eod_close_array) - 1])
  y_short_period_price_avg = y_eod_short_sum / int(config['short_avg_days'])
  #print('MKT: ' + mkt + ' Yesterdays longterm avg: ' + str(y_long_period_price_avg) + ' and shortterm avg: ' + str(y_short_period_price_avg))

  # Get todays period avgs, eg 21 day avg and 6 day avg
  eod_long_sum = sum(float(yles) for yles in eod_close_array[((len(eod_close_array) - int(config['long_avg_days']))):len(eod_close_array)])
  long_period_price_avg = eod_long_sum / int(config['long_avg_days'])
  eod_short_sum = sum(float(yles) for yles in eod_close_array[((len(eod_close_array) - int(config['short_avg_days']))):len(eod_close_array)])
  short_period_price_avg = eod_short_sum / int(config['short_avg_days'])
  #print('MKT: ' + mkt + ' Todays longterm avg: ' + str(long_period_price_avg) + ' and shortterm avg: ' + str(short_period_price_avg))

  # Check for Buy signal - is todays short term (eg 6days) avg > long term (eg 21days)
  if short_period_price_avg  > long_period_price_avg:
    # Only a signal if yesterday, this hadn't crossed over already
    if y_short_period_price_avg  <= y_long_period_price_avg:
      print('BUY Signal for ' + mkt + ' ' 
        + str(config['short_avg_days']) + ' day avg price (' + str(short_period_price_avg) + ') was greater than '
        + str(config['long_avg_days']) + ' day avg price (' + str(long_period_price_avg) + ').')
      print('Latest EOD price: ' + str(eod_close_array[data_days]))
      print('If you are currently SHORT ' + mkt + ' then recommend you close the trade')
    else:
      nosignal = 1
  # Check for Sell signal - is todays short term avg < long term avg
  elif short_period_price_avg  > long_period_price_avg:  
    # Only if this wasnt true yesterday
    if y_short_period_price_avg  >= y_long_period_price_avg:
      print('SELL Signal for ' + mkt + ' ' 
        + str(config['short_avg_days']) + ' day avg price (' + str(short_period_price_avg) + ') was lower than '
        + str(config['long_avg_days']) + ' day avg price (' + str(long_period_price_avg) + ').')
      print('Latest EOD price: ' + str(eod_close_array[data_days]))
      print('If you are currently LONG ' + mkt + ' then recommend you close the trade')
    else:
      nosignal = 1
  
  # No signal - log it
  if nosignal > 0:
    print('No signals for ' + mkt)

# Logout
logout_uri="https://api.ig.com/gateway/deal/session"
logout_headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json; charset=UTF-8", "X-IG-API-KEY": str(config["key"]), "Version": "1", "X-SECURITY-TOKEN": sec_token, "CST": cst, "_method": "DELETE", "IG-ACCOUNT-ID": accountId, "IG-ACCOUNT-TYPE": accountType }
logout_response = requests.get(logout_uri, headers=logout_headers, data={})
print('LOGOUT Response: ' + str(logout_response))
