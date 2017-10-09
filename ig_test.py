import json
import sys
import requests
import csv
from requests.auth import HTTPDigestAuth
from datetime import datetime, timedelta

# FX Markets to trade
fxmajmkts=['GBPUSD','EURUSD','USDJPY','EURGBP','AUDUSD','USDCAD','EURJPY','GBPEUR','USDCHF','EURCHF']
fxminmkts=['GBPJPY','GBPCHF','CADJPY','GBPCAD','EURCAD','CHFJPY','CADCHF','GBPZAR','USDSGD','USDZAR','GBPSGD','SGDJPY','EURSGD','EURZAR']
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
#print('Fetching data for ' + str(data_days) + ' days')
# Flag or buy/sell signal
nosignal=0
#API Call Allowance - 500 per week
api_allowance=0



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

  #No Signal
  nosignal = 0

  prices_file='results/' + mkt + "-" + str(today) + ".csv"
  prices_file_csv=csv.reader(open(prices_file), delimiter=",")


  print('Checking mkt: '  + mkt )
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
  print('MKT: ' + mkt + ' Yesterdays longterm avg: ' + str(y_long_period_price_avg) + ' and shortterm avg: ' + str(y_short_period_price_avg))

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
      print('Latest EOD price: ' + str(len(eod_close_array)))
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
      print('Latest EOD price: ' + str(len(eod_close_array)))
      print('If you are currently LONG ' + mkt + ' then recommend you close the trade')
    else:
      nosignal = 1
  else:
    #No Signal
    nosignal = 1
  
  # No signal - log it
  if nosignal > 0:
    print('No signals for ' + mkt)
