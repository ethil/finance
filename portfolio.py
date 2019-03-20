# Display portfolio statistics, including mean-reversion properties
import numpy as np
import matplotlib.pyplot as plt
import economethil as ee
from statsmodels.tsa.stattools import adfuller


def plot(port):

    m = np.mean(port)
    plt.plot(port)
    plt.plot([0, len(port)], [m, m], color='red', linestyle='dashed')
    plt.show()


def coint(port): # Johansen and ADF measure cointegration
    # ADF ... or variance ratio, both helps in stating a the mean reversion property of a time series
    adf = adfuller(port, maxlag=20, regression='c', autolag='AIC', store=False, regresults=False)
    print('--------------------------------------------------')
    print(adf)


def mrev(port): # Hurst, Vratio and Half-life measure mean-reversion

    low = min(port)
    if low <= 0:
        port += -low + 1
    lport = np.log(port)
    # Hurst
    hurst = ee.hurst(lport)
    vratio = ee.vratio(lport)
    # Half-Life
    hl = ee.halflife(port)

    return hurst, vratio, hl
