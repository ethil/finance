# Use command line arguments to obtain results

import sys
import datetime as dt
import bond_functions as b


jolly = float(sys.argv[1])
maturity = sys.argv[2]
coupon = float(sys.argv[3])
frequency = int(sys.argv[4])

# need for a numerical time to maturity in years
#maturity = float(maturity)
time_to_maturity = dt.datetime.strptime(maturity, "%d-%m-%Y") - dt.datetime.now()
maturity = (time_to_maturity / dt.timedelta(minutes=1)) / 525960 # minutes in a year

if jolly < 1:
    # need for an input rate in continuous terms
    ask = input('Yield expressed in Nominal/compounded/continuous terms? ')
    if ask == 'continuous':
        rate = jolly
    elif ask == 'compounded':
        rate = b.continuous(jolly,frequency)
    else:
        rate = b.continuous(jolly,1)
    # done!
    price = b.BondPrice(rate, maturity, coupon, frequency)
    clean = price - b.BondAccrued(maturity, coupon, frequency)
    print('Bond price should be:   {:.3f}'.format(clean))
    print('Its cost (dirty price): {:.3f}'.format(price))
else:
    # usually the clean price is the one quoted
    ask = input('Clean price? (Y/n) ')
    if ask == 'n':
        price = jolly
    else:
        price = jolly + b.BondAccrued(maturity, coupon, frequency)
    rate = b.BondYield(price, maturity, coupon, frequency)
    print('The implied YTM is: {:.4f} (nominal)'.format(b.nominal(rate, 1000)))

# using a continuous rate as input
par = b.BondPar(rate, maturity, coupon, frequency)
D = b.BondDuration(price, rate, maturity, coupon, frequency)
up, dn = b.BondDV01(price, rate, maturity, coupon, frequency)
print('Par yield (coupon): {:.2f}'.format(par))
print('Bond duration is:   {:.2f} years'.format(D))
print('10 bps will move the bond by either {:.3f} or +{:.3f}\n'.format(up, dn))
