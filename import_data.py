import sys
import csv

#TODO check arg is given
# Input file is 1st arg
filename = sys.argv[1]
#Output file is 2nd arg
outfile = sys.argv[2]
#Set high and low age ranges in days
higherrange = 21
lowerrange = 6
#set low value period in days to calculate auto stop from
low_price = 20

#Arrays for required values
date_array = []
close_array = []
price_array = []
# eg 21 day avg
higher_array = []
# eg 6 day avg
lower_array = []
# eg 20 day low
lowprice_array = []

#TODO assumes the low_price will be less than the higherrange - build a check in 

#TODO check file exists
#Open and read file
datafile = csv.reader(open(filename), delimiter=",")

#first line is the header - pas over this
headerline = datafile.next()

#Loop through and build arrays
count = 0
data_count = 0
for Symbol, Date, Open, High, Low, Close, Volume in datafile:
    close_array.insert(count,Close) 
        
    #If we are above higher range - start adding to arrays - add 1 to account for header line 
    if count > higherrange + 1:

        #Add dates and closing prices
        date_array.insert(count,Date) 
        price_array.insert(count,Close) 

        #Get running higher range daily avg
        hstart_pos = count - higherrange
        higheravg = close_array[hstart_pos:count]
        _hsum = sum(float(hf) for hf in higheravg)
        _hlen = len(higheravg)
        higher_avg = _hsum / _hlen
        higher_array.insert(count, higher_avg)

        #Add lower range avg
        #calculate lower daily avg 
        lstart_pos = count - lowerrange
        loweravg = close_array[lstart_pos:count] 
        _lsum = sum(float(lf) for lf in loweravg)
        _llen = len(loweravg)
        lower_avg = _lsum / _llen 
        lower_array.insert(count, lower_avg)

        #Get the lowest price for the last low_price days - used to calculate auto stop
        pstart_pos = count - low_price
        lowpricelist = close_array[pstart_pos:count]
        _low = min(lowpricelist)
        lowprice_array.insert(count, _low)

        #Increment our data_count(er)
        data_count += 1

    #Increase the counter
    count += 1

#Count is number of records - loop through and write out
out_file = open(outfile, "w")
#Write a header 
out_file.write("Date,EOD_Price,low_day_avg,high_day_avg,low_day_price\n")

for i in range(data_count):
    outstr = str(date_array[i]) + "," + str(price_array[i]) + "," + str(lower_array[i]) + "," + str(higher_array[i]) + "," + str(lowprice_array[i] + "\n")
    out_file.write(outstr)
out_file.close()

