# Use command line arguments to obtain results
#
# b = r-q stocks
# b = 0 futures
# b = 0, r = 0 futures considering margin
# b = r - r_f FX
#
import sys
import datetime as dt
import option_functions as opt

if len(sys.argv) < 7:
    sys.stderr.write('Usage: price or IV, strike, maturity, underlying, yield, risk-free\n')
    sys.exit(1)

jolly = float(sys.argv[1])
X = float(sys.argv[2])
maturity = sys.argv[3]
S = float(sys.argv[4])
q = float(sys.argv[5])
r = float(sys.argv[6])

# need for a numerical time to maturity in years
#T = float(maturity)
time_to_maturity = dt.datetime.strptime(maturity, "%d-%m-%Y") - dt.datetime.now()
T = (time_to_maturity / dt.timedelta(minutes=1)) / 525960 # minutes in a year
#
type = input('Call or put? (call/put) ')
ask = input('Find IV? (Y/n) ')
if ask == 'n':
    sigma = jolly
else:
    mkt = jolly
    if type == 'put':
        sigma = opt.BSMputIV(mkt,X,T,S,q,r)
    else:
        sigma = opt.BSMcallIV(mkt,X,T,S,q,r)

if type == 'put':
    price = opt.BSMput(X,T,S,sigma,q,r)
    delta = opt.BSMputdelta(X,T,S,sigma,q,r)
    theta = opt.BSMputtheta(X,T,S,sigma,q,r)
    itm   = opt.BSMputITM(X,T,S,sigma,q,r)
else:
    price = opt.BSMcall(X,T,S,sigma,q,r)
    delta = opt.BSMcalldelta(X,T,S,sigma,q,r)
    theta = opt.BSMcalltheta(X,T,S,sigma,q,r)
    itm   = opt.BSMcallITM(X,T,S,sigma,q,r)
gamma = opt.BSMgamma(X,T,S,sigma,q,r)
vega  = opt.BSMvega(X,T,S,sigma,q,r)
print('Price: {:.5f}\nDelta: {:.3f}\nGamma: {:.3f}\nTheta: {:.5f}\nVega:  {:.5f}'.format(price,delta,gamma,theta,vega/100))
print('Prob ITM: {:.1f}%\nImplied Vol: {:.1f}%'.format(itm*100,sigma*100))
