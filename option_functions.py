# option formulas
#
# b = r-q stocks
# b = 0 futures
# b = 0, r = 0 futures considering margin
# b = r - r_f FX
#
from scipy.stats import norm
import numpy as np


def BSMcall(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S*np.exp((b-r)*T) * norm.cdf(d1) -X*np.exp(-r*T)*norm.cdf(d2)

def BSMput(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return -S*np.exp((b-r)*T) * norm.cdf(-d1) +X*np.exp(-r*T)*norm.cdf(-d2)

def BSMcalldelta(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    return np.exp((b-r)*T) * norm.cdf(d1)

def BSMputdelta(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    return np.exp((b-r)*T) * (norm.cdf(d1)-1)

def BSMcalltheta(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    x = - np.exp((b-r)*T) * S*norm.pdf(d1)*sigma*0.5/np.sqrt(T)
    y = - (b-r)*S*np.exp((b-r)*T)*norm.cdf(d1)
    z = - r*X*np.exp(-r*T)*norm.cdf(d2)
    return (x+y+z)/365.25

def BSMputtheta(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    x = - np.exp((b-r)*T) * S*norm.pdf(d1)*sigma*0.5/np.sqrt(T)
    y = + (b-r)*S*np.exp((b-r)*T)*norm.cdf(-d1)
    z = + r*X*np.exp(-r*T)*norm.cdf(-d2)
    return (x+y+z)/365.25

def BSMgamma(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    return np.exp((b-r)*T) * norm.pdf(d1)/(S*sigma*np.sqrt(T))

def BSMvega(X,T,S,sigma,q,r):
    b = r - q
    d1 = ( np.log(S/X) + (b+(sigma**2)/2)*T ) / (sigma*np.sqrt(T)) 
    return np.exp((b-r)*T) * S*norm.pdf(d1)*np.sqrt(T)

def BSMcallITM(X,T,S,sigma,q,r):
    b = r - q
    d2 = ( np.log(S/X) + (b-(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    return np.exp(-r*T)*norm.cdf(d2)

def BSMputITM(X,T,S,sigma,q,r):
    b = r - q
    d2 = ( np.log(S/X) + (b-(sigma**2)/2)*T ) / (sigma*np.sqrt(T))
    return np.exp(-r*T)*norm.cdf(-d2)

def BSMcallIV(mkt,X,T,S,q,r):
    sigma = 0.3
    model = BSMcall(X,T,S,sigma,q,r)
    v = BSMvega(X,T,S,sigma,q,r)
    while abs(mkt-model) > 0.001: # Newton-Raphson
        model = BSMcall(X,T,S,sigma,q,r)
        v = BSMvega(X,T,S,sigma,q,r)
        if v == 0:
            break
        sigma = sigma - (model-mkt) / v
    if v == 0: # bisect
        floor = 0
        ceil = 2 # max 200% IV
        while abs(mkt-model) > 0.001:
            sigma = (floor + ceil) / 2
            model = BSMcall(X,T,S,sigma,q,r)
            if model < mkt:
                floor = sigma
            else:
                ceil = sigma
    return sigma

def BSMputIV(mkt,X,T,S,q,r):
    sigma = 0.3
    model = BSMput(X,T,S,sigma,q,r)
    v = BSMvega(X,T,S,sigma,q,r)
    while abs(mkt-model) > 0.001:
        model = BSMput(X,T,S,sigma,q,r)
        v = BSMvega(X,T,S,sigma,q,r)
        if v == 0:
            break
        sigma = sigma - (model-mkt) / v
    if v == 0: # bisect
        floor = 0
        ceil = 2 # max 200% IV
        while abs(mkt-model) > 0.001:
            sigma = (floor + ceil) / 2
            model = BSMcall(X,T,S,sigma,q,r)
            if model < mkt:
                floor = sigma
            else:
                ceil = sigma
    return sigma
