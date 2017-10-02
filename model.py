import sys
import csv
#Input data file
infile = csv.reader(open(sys.argv[1]), delimiter=",")
#Data arrays
date_array = []
eodprice_array = []
lowavg_array = []
highavg_array = []
lowprice_array = []
#Skip 1 row - header
headerline=infile.next()
#Skip 2nd row - no previous value to compare against
firstdatarow=infile.next()
data_rows_count = 0
#Build data array - this can almost certainly be better
for Date,EOD_Price,low_day_avg,high_day_avg,low_day_price in infile:
    date_array.insert(data_rows_count, Date)
    eodprice_array.insert(data_rows_count, EOD_Price)
    lowavg_array.insert(data_rows_count, low_day_avg)
    highavg_array.insert(data_rows_count, high_day_avg)
    lowprice_array.insert(data_rows_count, low_day_price)
    data_rows_count += 1
#Record position
position='NONE'
trade_price=''
auto_stop=''
for i in range(data_rows_count): 
    #Check for BUY Signal
    #Was todays 6 day avg greater than the 21 day avg
    if lowavg_array[i] > highavg_array[i]:
        #Potential long signalbut only if this cross over occured today
        #Check against yesterday
        if lowavg_array[i-1] <= highavg_array[i-1]:
            print("We have a BUY signal on " + date_array[i] + " Price: " + eodprice_array[i] + " 20 Day Low: " + lowprice_array[i] + " Current Position: " + position)
            #If we have no position - BUY
            if position is 'NONE':
                position='LONG'
                #Record Buy Price and 20 day low(auto stop price)
                trade_price=eodprice_array[i]
                auto_stop=lowprice_array[i]
                print("\tBUYING - New Position: " + position + " Buy Price: " + trade_price + "  AutoStop: " + auto_stop)
            #If we are short - Sell
            #TODO - Is this correct? or do we hold our nerve?
            elif position is 'SHORT':
                position='NONE'
                #Calculate Result
                if eodprice_array[i] < trade_price:
                    result = "LOSS"
                else:
                    result = "WIN"
                print("\t Getting Out - Result: " + result + " - New Position: " + position)
            #Otherwise we already have a long position - do nothing
            #Should never get here so log for debug
            else:
                print("WELL SOMETHING SEEMS WRONG - We have a " + position + " already ???")
        #No significant events - stay as is unless auto stop hit
        else:
            if eodprice_array[i] <= auto_stop:
                #Do we have an open position?
                if position is not 'NONE':
                  #Oh Dear - we're out
                  position = 'NONE'
                  print("AUTO STOP. Buy Price: " + trade_price + " AutoStop: " + auto_stop + "     YOU LOSE :(")
            else:
                print("Retain " + position + " Position on " + date_array[i] + ' EOD Proce: ' + eodprice_array[i])

    #Check for SELL Signal
    elif lowavg_array[i] < highavg_array[i]:
        #Potential short signal if yesterday it crossed over today
        if lowavg_array[i-1] >= highavg_array[i-1]:
            print("We have a SELL signal on " + date_array[i] + " Price: " + eodprice_array[i] + " 20 Day Low: " + lowprice_array[i] + " Current Position: " + position)
            #Do we have any position on this market? If not short
            if position is 'NONE':
                position='SHORT'
                #Record Short Price and 20 day low for use as auto stop
                trade_price=eodprice_array[i]
                auto_stop=lowprice_array[i]
                print("\t SHORTING - New Position: " + position + " Short Price: " + trade_price + "  AutoStop: " + auto_stop)
            #Already short - so get the hell outta dodge
            elif position is 'LONG':
                position = 'NONE'
                #Calculate Result
                if eodprice_array[i] < trade_price:
                    result = "LOSS"
                else:
                    result = "WIN"
                print("\t Getting Out Result: " + result + " - New Position: " + position)
            #Hmmm shouldn't have got here
            else:
                print("WELL SOMETHING SEEMS WRONG - We have a " + position + " already ???")
        #No significant events - stay as is
        else:
            if eodprice_array[i] <= auto_stop:
                #Do we have an open position?
                if position is not 'NONE':
                  #Oh Dear - we're out
                  position = 'NONE'
                  print("AUTO STOP. Short Price: " + trade_price + " AutoStop: " + auto_stop + "     YOU LOSE :(")
            else:
                print("Retain " + position + " Position on " + date_array[i] + ' EOD Price: ' + eodprice_array[i])
    else:
        print("No signal for: " + date_array[i] + " Current Position: " + position)  
