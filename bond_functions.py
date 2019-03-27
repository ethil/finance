# convertion between rates
# price and rate calculator
import numpy as np

#
def nominal(rate, frequency):
    if frequency > 999:
        y = np.exp(rate) - 1
    else:
        y = ( 1 + rate/frequency )**frequency - 1
    return y

def continuous(rate, frequency):
    if frequency > 1:
        rate = nominal(rate, frequency)
    return np.log( 1 + rate )

def compounded(rate, frequency):
    if frequency > 999:
        rate = nominal(rate,frequency)
    return (( 1 + rate )**( 1/frequency ) - 1 ) * frequency

#
def BondAccrued(maturity, coupon, frequency):
    return (1/frequency - maturity % frequency) * coupon/frequency

def BondPrice(rate, maturity, coupon, frequency): # time to maturity in years
    first = max(maturity % frequency, 1/frequency)
    timeline = np.linspace(first, maturity, int(np.floor(maturity*frequency)))
    discount = np.exp(- rate * timeline)
    cashflows = np.ones(len(timeline)) * coupon/frequency
    cashflows[-1] = cashflows[-1] + 100
    return np.dot( discount, cashflows )

def BondYield(price, maturity, coupon, frequency): # yield to maturity
    r1 = -0.1
    r2 = 0.25
    s = 0
    while(abs(price - s) > 0.001):
        rate = (r1+r2)/2
        s = BondPrice(rate, maturity, coupon, frequency)
        if s > price:
            r1 = rate
        else:
            r2 = rate
    return rate

def BondPar(rate, maturity, coupon, frequency): # par yield
    first = max(maturity % frequency, 1/frequency)
    timeline = np.linspace(first, maturity, int(np.floor(maturity*frequency)))
    discount = sum( np.exp(- rate * timeline) )
    return (100 * ( 1 - np.exp(- rate * maturity))) * frequency / discount

def BondDuration(price, rate, maturity, coupon, frequency): # time to maturity in years
    first = max(maturity % frequency, 1/frequency)
    timeline = np.linspace(first, maturity, int(np.floor(maturity*frequency)))
    discount = np.exp(- rate * timeline)
    cashflows = np.ones(len(timeline)) * coupon/frequency
    cashflows[-1] = cashflows[-1] + 100
    weights = [a*b for a,b in zip(discount,cashflows)]
    return np.dot( timeline, weights ) / price

def BondDV01(price, rate, maturity, coupon, frequency): # d.B = -B*D*d.y ~ but convexity
    up = BondPrice(rate+0.01, maturity, coupon, frequency) - price
    dn = BondPrice(rate-0.01, maturity, coupon, frequency) - price
    return up, dn
