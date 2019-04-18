# get all bonds quotes from file
# calculate spot and forward yields
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import bond_functions as b

def find_nearest(df, value): # interpolate the yield a given time in the future (in years)
    array = np.asarray(df.Maturity)
    idx = (np.abs(array - value)).argmin()
    #return idx
    w1 = df.iloc[idx,:]
    if w1[0] < value:
        idx2 = idx + 1
        while df.iloc[idx2,0] == w1[0]:
            idx2 = idx2 + 1
    else:
        idx2 = idx - 1
        while df.iloc[idx2,0] == w1[0]:
            idx2 = idx2 - 1
    w2 = df.iloc[idx2,:]
    mid = ( np.abs(w2[0]-value)*w1[1] + np.abs(w1[0]-value)*w2[1] ) / np.abs(w2[0]-w1[0])
    return mid


# import
frequency = 2
quotes = pd.read_excel('bond_quotes.xlsx', sheet_name='quotes')
ask = input('Date of market quotes? (d-m-Y): ')

# get yields
time  = []
rates = []

for x in range(0, quotes.shape[0]):
    time_to_maturity = dt.datetime.strptime(quotes.Maturity[x], '%m/%d/%Y') - dt.datetime.strptime(ask, '%d-%m-%Y')
    maturity = (time_to_maturity / dt.timedelta(minutes=1)) / 525960 # minutes in a year
    price = quotes.Price[x] + b.BondAccrued(maturity, quotes.Coupon[x], frequency)
    rate = b.BondYield(price, maturity, quotes.Coupon[x], frequency)
    time.append(maturity)
    #rates.append(rate)
    rates.append(b.rosetta(rate, frequency, 'continuous', 'nominal'))

df = [time, rates]
data = {'Maturity': time,
        'Yield': rates
        }
df = pd.DataFrame(data,columns= ['Maturity', 'Yield'])
print(df.shape)

maturities = df.Maturity.unique()
time = []
rates = []
for x in maturities:
    time.append(x)
    tmp = df[df.Maturity==x]
    rates.append( np.median(tmp.Yield) )

df = [time, rates]
data = {'Maturity': time,
        'Yield': rates
        }
df = pd.DataFrame(data,columns= ['Maturity', 'Yield'])
print(df.shape)

print (find_nearest(df, 10))


yhat = savgol_filter(df.Yield, 33, 2) # window size , polynomial order
df['Smooth'] = yhat
# export
df.to_csv('export', sep='\t', encoding='utf-8')

# plot
plt.plot(df.Maturity,df.Yield)
plt.plot(df.Maturity,df.Smooth, color='red')
plt.ylabel('Yield')
plt.show()
