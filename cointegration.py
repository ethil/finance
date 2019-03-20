# Get cointegration properties on multiple stocks
import itertools as iter
import datetime as dt
import portfolio as pf
import csv
import coint_test
import yahoo
from math import factorial


# period
window = int(input("How many years of history: "))
end_date = dt.datetime.now().date()
start_date = dt.datetime(dt.datetime.now().year-window, dt.datetime.now().month, dt.datetime.now().day).date()

# instruments
tickers = [];
xyz = None

while (xyz != ""):
    xyz = input("Please enter a valid ticker symbol (leave blank to finish): ")
    try:
        tickers.append(xyz)
    except:
        if xyz != "":
            print(xyz + " is not okay. Try again.")

tickers = tickers[:-1]
len = len(tickers)
print(tickers)
print('{} tickers were given.\n'.format(len))

if len > 2:
    components = int(input('How many stocks in a single cointegration (2,3,4)? ')) # pairs triplets quadruplets
else:
    components = 2


# the real stuff
if len > components: # if there are more than 1 combination possible
    print('Then, there will be {} cointegration tests.\n'.format(factorial(len)/(factorial(len-components)*factorial(components))))
    bucket = list(iter.combinations(tickers, components))

    for x in bucket:
        weights1, weights2, port1, port2 = coint_test.test(yahoo.stocks(x, start_date, end_date), x)
        hurst, vratio, hl = pf.mrev(port1)
        # save simple results to file
        with open('cointegrations.csv', mode='a') as triplets:
            triplets = csv.writer(triplets, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            triplets.writerow([hurst.round(3), hl.round(1), x, weights1])

        print('\n')

else:
    weights1, weights2, port1, port2 = coint_test.test(yahoo.stocks(tickers, start_date, end_date), tickers)
    hurst, vratio, hl = pf.mrev(port1)
    print('\n')
    pf.plot(port1)
