# Analyze tastyworks' portfolio
import pandas as pd
import numpy as np
import yahoo_finance as yf
import option_functions as fz


# rearrage data
pf = pd.read_csv('positions.csv')
und = pf['Symbol'].copy() # remove warnings...
dte = pf['DTE'].copy()
x = pf.shape[0]

for i in range(0, x):
    dte[i] = int(pf.iloc[i]['DTE'][:-1]) # remove last letter "d"
    tmp = pf.iloc[i]['Symbol'].split(" ", 1)[0]

    if (pf.iloc[i]['Type'] == 'FUTURES_OPTION'):
        und[i] = tmp[2:4] + '=F' # su yahoo ticker presenti come ES=F per le /ES
    else:
    	und[i] = tmp

pf['Symbol'] = und
pf['DTE'] = dte
underlyings = np.unique(und)
print('\nList of current underlyings:')
print(underlyings)


# analysis
ticker = input('\nWhich one do you want to analyze? ') # servirebbe poter richiedere in caso di ticker non presente
price = yf.last(ticker)

fut = input('Is it a future? (y/N) ')
if fut == 'y':
    r = 0
    dividend = 0
else:
    r = yf.last('^IRX')/100 # risk-free
    dividend = yf.div_yield(ticker)

opz = pf.loc[pf['Symbol'] == ticker]
net = np.dot(opz['Mark'], abs(opz['Quantity']))
print('\n')
print(opz)
iv = mrk_new = np.arange(opz.shape[0], dtype=np.float)

for i in range(0, opz.shape[0]):
    if opz.iloc[i]['Call/Put'] == 'Call':
        iv[i] = fz.BSMcallIV(abs(opz.iloc[i]['Mark']), opz.iloc[i]['Strike Price'], opz.iloc[i]['DTE']/365.25, price, dividend, r)
    else:
        iv[i] = fz.BSMputIV(abs(opz.iloc[i]['Mark']), opz.iloc[i]['Strike Price'], opz.iloc[i]['DTE']/365.25, price, dividend, r)

#
tool = input('''\nGive me the change in the price of the underlying (percentage points),
how many days in the future (integer)\nand the change in the I.V. (percentage points):\ne.g. : -1 3 5\n''')
tool = tool.split(" ", 2)

p_new = price * (1 + float(tool[0])/100)
iv_new = iv + float(tool[2])/100

for i in range(0, opz.shape[0]):
    if opz.iloc[i]['Call/Put'] == 'Call':
        mrk_new[i] = fz.BSMcall(opz.iloc[i]['Strike Price'], (opz.iloc[i]['DTE']+int(tool[2]))/365.25, p_new, iv_new[i], dividend, r)
    else:
        mrk_new[i] = fz.BSMput(opz.iloc[i]['Strike Price'], (opz.iloc[i]['DTE']+int(tool[2]))/365.25, p_new, iv_new[i], dividend, r)

net_new = np.dot(mrk_new, opz['Quantity'])
print('\nPosition mark is {:.2f} and would move to {:.2f}\nPnL: ${:.2f}'.format(net,net_new,100*(net_new-net)))
