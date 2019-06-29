# scrape yields
from bs4 import BeautifulSoup
#from scipy.optimize import curve_fit
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import pandas as pd
import bond_functions as bf
import requests, json, io, csv


# Nelson & Siegel + Svensson Model
model = lambda m: b[0] + b[1]*(1-np.exp(-m/b[4]))*b[4]/m + b[2]*((1-np.exp(-m/b[4]))*b[4]/m - np.exp(-m/b[4])) + b[3]*((1-np.exp(-m/b[5]))*b[5]/m - np.exp(-m/b[5]))
def nssm_err(b): # minimize this
    nssm = lambda m: b[0] + b[1]*(1-np.exp(-m/b[4]))*b[4]/m + b[2]*((1-np.exp(-m/b[4]))*b[4]/m - np.exp(-m/b[4])) + b[3]*((1-np.exp(-m/b[5]))*b[5]/m - np.exp(-m/b[5]))
    return sum( ( list(map(nssm, t)) - spot )**2 )


#U.S.A. Treasuries
#1m 2m 3m 6m 1y 2y 3y 5y 7y 10y 20y 30y
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
bei_us = (rate[12]-real) / (1+0.01*real)
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
t = ex
res = minimize(nssm_err, np.ones(6), method='L-BFGS-B', bounds=bnds, options={'ftol': 1e-12, 'disp': False})
b = res.x
yc_us = np.array(list(map(model, ex)))*100
print ('----------\nus dollar')
print ('LT rate: {:.2f}%\nST rate: {:.2f}%\nb/e inflation: {:.2f}%'.format(100*b[0], 100*(b[0]+b[1]), bei_us))

fig1, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, squeeze=True)
fig1.suptitle('Interest rate curve')
ax1.plot(ex, spot*100, color='lime', linestyle='-.', linewidth='0.7', label='linear')
ax1.plot(ex, yc_us, color='green', label='NSSM USD')
ax1.legend()
ax1.grid(True)

# Eurozone aaa-rated
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
bei_eu = ((fr5-fr5_r) / (1+fr5_r))*100
yc_eu = np.array(list(map(model, ex)))*100
print ('----------\neuro')
print ('LT rate: {:.2f}%\nST rate: {:.2f}%\nb/e inflation: {:.2f}%'.format(100*b[0], 100*(b[0]+b[1]), bei_eu))

ax2.plot(ex, yc_eu, color='xkcd:darkblue', label='NSSM EUR')
ax2.legend()
ax2.grid(True)


# Japan
rate = np.zeros(81)
page = requests.get("https://www.marketwatch.com/investing/bond/tmbmbjp-03m")
content = page.text
soup = BeautifulSoup(content, 'html.parser')
rate[0] = float( soup.find("span", attrs={"class":"value"}).decode_contents(formatter="html") )
page = requests.get("https://www.marketwatch.com/investing/bond/tmbmbjp-06m")
content = page.text
soup = BeautifulSoup(content, 'html.parser')
rate[1] = float( soup.find("span", attrs={"class":"value"}).decode_contents(formatter="html") )
page = requests.get('https://www.mof.go.jp/english/jgbs/reference/interest_rate/jgbcme.csv')
page.raise_for_status()
decoded_content = page.content.decode('utf-8')
cr = csv.reader(decoded_content.splitlines(), delimiter=',')
my_list = list(cr)[-1][1:]
numbers = [float(i) for i in my_list]
rate[2:4] = np.linspace(numbers[0],numbers[1],num=3)[:-1]
rate[4:6] = np.linspace(numbers[1],numbers[2],num=3)[:-1]
rate[6:8] = np.linspace(numbers[2],numbers[3],num=3)[:-1]
rate[8:10] = np.linspace(numbers[3],numbers[4],num=3)[:-1]
rate[10:12] = np.linspace(numbers[4],numbers[5],num=3)[:-1]
rate[12:14] = np.linspace(numbers[5],numbers[6],num=3)[:-1]
rate[14:16] = np.linspace(numbers[6],numbers[7],num=3)[:-1]
rate[16:18] = np.linspace(numbers[7],numbers[8],num=3)[:-1]
rate[18:20] = np.linspace(numbers[8],numbers[9],num=3)[:-1]
rate[20:30] = np.linspace(numbers[9],numbers[10],num=11)[:-1]
rate[30:40] = np.linspace(numbers[10],numbers[11],num=11)[:-1]
rate[40:50] = np.linspace(numbers[11],numbers[12],num=11)[:-1]
rate[50:60] = np.linspace(numbers[12],numbers[13],num=11)[:-1]
rate[60:81] = np.linspace(numbers[13],numbers[14],num=21)
#real = float(soupr.find_all('TC_5YEAR')[-1].decode_contents(formatter="lxml"))
bei_jp = 0.2#(rate[10]-real) / (1+0.01*real)
a = [0.25]
b = np.linspace(0.5, 40, num=80)
exj = a + list(b)
vector = pd.Series(rate[1:]).apply(lambda x: (x/200+1)**(-2)) # starting from the 6m rate
discount = vector**(b)
vector = np.cumsum(discount)
pv = np.zeros(78)
for x in range(0, 78):
    pv[x] = (vector[x+2]-discount[x+2]) * rate[x+3]/2
spot = rate
for x in range(3,81):
    spot[x] = ( ( (100+rate[x]/2)/(100-pv[x-3]) )**(0.5/b[x-3]) -1) *200
spot = spot/100
#cons = {'type':'ineq', 'fun': lambda x: x[0]+x[1]-1} # remember when rates were supposed to be positive?
bnds = ((None, None), (None, None), (None, None), (None, None), (0.01, None), (0.01, None))
t = exj
res = minimize(nssm_err, np.ones(6), method='L-BFGS-B', bounds=bnds, options={'ftol': 1e-12, 'disp': False})
b = res.x
yc_jp = np.array(list(map(model, ex)))*100
print ('----------\njapanese yen')
print ('LT rate: {:.2f}%\nST rate: {:.2f}%\nb/e inflation: {:.2f}%\n'.format(100*b[0], 100*(b[0]+b[1]), bei_jp))

ax3.plot(ex, yc_jp, color='red', label='NSSM JPY')
ax3.legend()
ax3.grid(True)
fig1.show()
fig1.savefig('treasuries.png', dpi=300, bbox_inches='tight')


# real curve
fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, squeeze=True)
fig.suptitle('Interest rate curve (real)')
ax1.plot(ex, yc_us-bei_us, color='green', label='NSSM USD')
ax1.legend()
ax1.grid(True)
ax2.plot(ex, yc_eu-bei_eu, color='xkcd:darkblue', label='NSSM EUR')
ax2.legend()
ax2.grid(True)
ax3.plot(ex, yc_jp-bei_jp, color='red', label='NSSM JPY')
ax3.legend()
ax3.grid(True)
fig.show()
fig.savefig('treasuries_real.png', dpi=300, bbox_inches='tight')
