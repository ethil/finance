# Eurodollars / LIBOR
from bs4 import BeautifulSoup
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
#import pandas as pd
import requests, json#, io


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
plt.plot(expiry, ge, color='green', label='LIBOR 3M FWD')
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
