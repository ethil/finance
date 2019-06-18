# scrape yields
from bs4 import BeautifulSoup
#from scipy.optimize import curve_fit
from scipy.optimize import minimize
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import pandas as pd
import requests, json


# Eurodollars / LIBOR
# keep 20 quaterly expirations, approx. 5 years
cme = 'https://www.cmegroup.com/CmeWS/mvc/Quotes/FutureContracts/XCME/G?quoteCodes=GEU9,GEZ9,GEH0,GEM0,GEU0,GEZ0,GEH1,GEM1,GEU1,GEZ1,GEH2,GEM2,GEU2,GEZ2,GEH3,GEM3,GEU3,GEZ3,GEH4,GEM4'
response = requests.get(cme)
json_loaded = json.loads(response.text)
response.raise_for_status()
ge = np.zeros(20)
expiry = np.linspace(0, 4.75, num=20)
time_to_maturity = dt.datetime.strptime('18-09-2019', "%d-%m-%Y") - dt.datetime.now() # update the first expiry once a quarter
maturity = (time_to_maturity / dt.timedelta(days=1)) / 365.25
expiry = expiry + maturity
for x in range(0, 20):
    ge[x] = 100 - float( json_loaded['quotes'][x]['last'] )

fig, ax = plt.subplots()
plt.plot(expiry, ge, color='b', label='LIBOR 3M FWD')
plt.yticks(np.arange(min(ge)-min(ge)%0.25, max(ge)+0.25-max(ge)%0.25, 0.25))
ax.xaxis.set_minor_locator(MultipleLocator(0.25))
ax.yaxis.set_minor_locator(MultipleLocator(0.125))
ax.yaxis.grid(which="minor", linestyle='--', linewidth=0.7)
plt.legend()
plt.grid(True)
plt.show()
fig.savefig('eurodollars.png', dpi=300, bbox_inches='tight')


# U.S. Treasuries
# 1m 2m 3m 6m 1y 2y 3y 5y 7y 10y 20y 30y
rate = np.zeros(63)
page = requests.get( 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/XmlView.aspx?data=yield' )
page.raise_for_status()
soup = BeautifulSoup(page.text, features='xml')
#print (soup.prettify())
rate[0] = soup.find_all('BC_1MONTH')[-1].decode_contents(formatter="lxml")
rate[1] = soup.find_all('BC_2MONTH')[-1].decode_contents(formatter="lxml")
rate[2] = soup.find_all('BC_3MONTH')[-1].decode_contents(formatter="lxml")
rate[3] = soup.find_all('BC_6MONTH')[-1].decode_contents(formatter="lxml")
rate[4] = soup.find_all('BC_1YEAR')[-1].decode_contents(formatter="lxml")
rate[6] = soup.find_all('BC_2YEAR')[-1].decode_contents(formatter="lxml")
rate[8] = soup.find_all('BC_3YEAR')[-1].decode_contents(formatter="lxml")
rate[12] = soup.find_all('BC_5YEAR')[-1].decode_contents(formatter="lxml")
rate[16] = soup.find_all('BC_7YEAR')[-1].decode_contents(formatter="lxml")
rate[22] = soup.find_all('BC_10YEAR')[-1].decode_contents(formatter="lxml")
rate[42] = soup.find_all('BC_20YEAR')[-1].decode_contents(formatter="lxml")
rate[62] = soup.find_all('BC_30YEAR')[-1].decode_contents(formatter="lxml")
rate[5] = np.linspace(rate[4],rate[6],num=3)[1:-1]
rate[7] = np.linspace(rate[6],rate[8],num=3)[1:-1]
rate[9:12] = np.linspace(rate[8],rate[12],num=5)[1:-1]
rate[13:16] = np.linspace(rate[12],rate[16],num=5)[1:-1]
rate[17:22] = np.linspace(rate[16],rate[22],num=7)[1:-1]
rate[23:42] = np.linspace(rate[22],rate[42],num=21)[1:-1]
rate[43:62] = np.linspace(rate[42],rate[62],num=21)[1:-1]

a = [1/12, 2/12, 0.25]
b = np.linspace(0.5, 30, num=60)
ex = a + list(b)
vector = pd.Series(rate[3:]).apply(lambda x: (x/200+1)**(-2)) # starting from the 6m rate
discount = vector**(b)
vector = np.cumsum(discount)
pv = np.zeros(58)
for x in range(0, 58):
    pv[x] = (vector[x+2]-discount[x+2]) * rate[x+5]/2
spot = rate
for x in range(5,63):
    spot[x] = ( ( (100+rate[x]/2)/(100-pv[x-5]) )**(0.5/b[x-3]) -1) *200
spot = spot/100

fig1 = plt.figure()
plt.plot(ex, spot*100, color='g', linestyle='-.', linewidth='0.7', label='linear')


def nssm_err(b):
    nssm = lambda m: b[0] + b[1]*(1-np.exp(-m/b[4]))*b[4]/m + b[2]*((1-np.exp(-m/b[4]))*b[4]/m - np.exp(-m/b[4])) + b[3]*((1-np.exp(-m/b[5]))*b[5]/m - np.exp(-m/b[5]))
    return sum( ( list(map(nssm, ex)) - spot )**2 )

bnds = ((None, None), (None, None), (None, None), (None, None), (0.01, None), (0.01, None))
#cons = {'type':'ineq', 'fun': lambda x: x[0]+x[1]-1}
res = minimize(nssm_err, np.ones(6), method='L-BFGS-B', bounds=bnds, options={'ftol': 1e-12, 'disp': False})
print (res.x)
print (res.message)
b = res.x
model = lambda m: b[0] + b[1]*(1-np.exp(-m/b[4]))*b[4]/m + b[2]*((1-np.exp(-m/b[4]))*b[4]/m - np.exp(-m/b[4])) + b[3]*((1-np.exp(-m/b[5]))*b[5]/m - np.exp(-m/b[5]))

plt.plot(ex, np.array(list(map(model, ex)))*100, color='r', label='NSSM')
plt.legend()
plt.grid(True)
plt.show()
fig1.savefig('treasuries.png', dpi=300, bbox_inches='tight')
