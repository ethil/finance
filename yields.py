# scrape yields
from bs4 import BeautifulSoup
#from scipy.optimize import curve_fit
from scipy.optimize import minimize
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import pandas as pd
import bond_functions as bf
import requests, json, io


# Nelson & Siegel + Svensson Model
model = lambda m: b[0] + b[1]*(1-np.exp(-m/b[4]))*b[4]/m + b[2]*((1-np.exp(-m/b[4]))*b[4]/m - np.exp(-m/b[4])) + b[3]*((1-np.exp(-m/b[5]))*b[5]/m - np.exp(-m/b[5]))
def nssm_err(b): # minimize this
    nssm = lambda m: b[0] + b[1]*(1-np.exp(-m/b[4]))*b[4]/m + b[2]*((1-np.exp(-m/b[4]))*b[4]/m - np.exp(-m/b[4])) + b[3]*((1-np.exp(-m/b[5]))*b[5]/m - np.exp(-m/b[5]))
    return sum( ( list(map(nssm, ex)) - spot )**2 )


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
plt.plot(expiry, ge, color='xkcd:darkblue', label='LIBOR 3M FWD')
plt.yticks(np.arange(min(ge)-0.25-min(ge)%0.25, max(ge)+0.5-max(ge)%0.25, 0.25))
ax.xaxis.set_minor_locator(MultipleLocator(0.25))
ax.yaxis.set_minor_locator(MultipleLocator(0.125))
ax.yaxis.grid(which="minor", linestyle='--', linewidth=0.7)
plt.xlabel("years") 
plt.ylabel("interest rate") 
plt.legend()
plt.grid(True)
plt.show()
fig.savefig('eurodollars.png', dpi=300, bbox_inches='tight')


# U.S. Treasuries
# 1m 2m 3m 6m 1y 2y 3y 5y 7y 10y 20y 30y
rate = np.zeros(63)
#page = requests.get( 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/XmlView.aspx?data=yield' )
page = requests.get( 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Datasets/yield.xml' )
page.raise_for_status()
soup = BeautifulSoup(page.text, features='xml')
pager = requests.get( 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/XmlView.aspx?data=realyield' )
pager.raise_for_status()
soupr = BeautifulSoup(pager.text, features='xml')
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
real = float(soupr.find_all('TC_5YEAR')[-1].decode_contents(formatter="lxml"))
bei_us = (rate[12]-real) / (1+0.01*real)**5
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
#cons = {'type':'ineq', 'fun': lambda x: x[0]+x[1]-1} # remember when rates were supposed to be positive?
bnds = ((None, None), (None, None), (None, None), (None, None), (0.01, None), (0.01, None))
res = minimize(nssm_err, np.ones(6), method='L-BFGS-B', bounds=bnds, options={'ftol': 1e-12, 'disp': False})
b = res.x
yc_us = np.array(list(map(model, ex)))*100
print ('----------\nus dollar')
print ('LT rate: {:.2f}%\nST rate: {:.2f}%\nb/e inflation: {:.2f}%'.format(100*b[0], 100*(b[0]+b[1]), bei_us))

fig1, (ax1, ax2) = plt.subplots(2, sharex=True)
fig1.suptitle('Interest rate curve')
ax1.plot(ex, spot*100, color='lime', linestyle='-.', linewidth='0.7', label='linear')
ax1.plot(ex, yc_us, color='green', label='NSSM USD')
ax1.legend()
ax1.grid(True)

# EU aaa-rated
page = requests.get('https://sdw-wsrest.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A+G_N_C.SV_C_YM.?lastNObservations=1', headers={'Accept': 'text/csv'})
page.raise_for_status()
df = pd.read_csv(io.StringIO(page.text))
par = df['OBS_VALUE']
b = (list(par[:4]/100) + list(par[1081:1083]))
page = requests.get("https://www.boerse-stuttgart.de/en/products/bonds/stuttgart/a1hgez-frankreich-eo-inflindex-lkd-oat-201324/")
content = page.text
soup = BeautifulSoup(content, 'html.parser')
price1 = float( soup.find("span", attrs={"class":"js-bsg-live-data__field bsg-trend bsg-trend--table", "data-field":"PRICE", "data-type":"208"}).decode_contents(formatter="html") )
page = requests.get("https://www.boerse-stuttgart.de/en/products/bonds/stuttgart/a1zkfm-frankreich-eo-oat-201424/")
content = page.text
soup = BeautifulSoup(content, 'html.parser')
price2 = float( soup.find("span", attrs={"class":"js-bsg-live-data__field bsg-trend bsg-trend--table", "data-field":"PRICE", "data-type":"208"}).decode_contents(formatter="html") )
time_to_maturity = dt.datetime.strptime('25-07-2024', "%d-%m-%Y") - dt.datetime.now()
maturity = (time_to_maturity / dt.timedelta(days=1)) / 365.25 # minutes in a year
fr5_r = bf.BondYield(price1, maturity, 0.25, 1)
time_to_maturity = dt.datetime.strptime('25-11-2024', "%d-%m-%Y") - dt.datetime.now()
maturity = (time_to_maturity / dt.timedelta(days=1)) / 365.25 # minutes in a year
fr5 = bf.BondYield(price2 + bf.BondAccrued(maturity, 1.75, 1), maturity, 1.75, 1)
bei_eu = ((fr5-fr5_r) / (1+fr5_r)**5)*100
yc_eu = np.array(list(map(model, ex)))*100
print ('----------\neuro')
print ('LT rate: {:.2f}%\nST rate: {:.2f}%\nb/e inflation: {:.2f}%\n'.format(100*b[0], 100*(b[0]+b[1]), bei_eu))

ax2.plot(ex, yc_eu, color='xkcd:darkblue', label='NSSM EUR')
ax2.legend()
ax2.grid(True)
fig1.show()
fig1.savefig('treasuries.png', dpi=300, bbox_inches='tight')

# real curve
fig2, (ax1, ax2) = plt.subplots(2, sharex=True)
fig2.suptitle('Interest rate curve (real)')
ax1.plot(ex, yc_us-bei_us, color='green', label='NSSM USD')
ax1.legend()
ax1.grid(True)
ax2.plot(ex, yc_eu-bei_eu, color='xkcd:darkblue', label='NSSM EUR')
ax2.legend()
ax2.grid(True)
fig2.show()
fig2.savefig('treasuries_real.png', dpi=300, bbox_inches='tight')
