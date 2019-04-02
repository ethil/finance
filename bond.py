# Use command line arguments to obtain results

import sys
import datetime as dt
import bond_functions as b

if len(sys.argv) < 5:
    sys.stderr.write('Usage: price or yield, maturity, annual coupon, frequency\n')
    sys.exit(1)

jolly = float(sys.argv[1])
maturity = sys.argv[2]
coupon = float(sys.argv[3])
frequency = int(sys.argv[4])

# need for a numerical time to maturity in years
#maturity = float(maturity)
time_to_maturity = dt.datetime.strptime(maturity, "%d-%m-%Y") - dt.datetime.now()
maturity = (time_to_maturity / dt.timedelta(minutes=1)) / 525960 # minutes in a year

if jolly < 1:
    # usually the yield is quoted in nominal terms
    ask = input('Yield expressed in nominal/compounded/continuous terms? ')
    if ask == 'continuous':
        rate = jolly
    else:
        rate = b.rosetta(jolly, frequency, ask, 'continuous')
    #
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
    #
    rate = b.BondYield(price, maturity, coupon, frequency)
    rateN = b.rosetta(rate, frequency, 'continuous', 'nominal')
    rateC = b.rosetta(rate, frequency, 'continuous', 'compounded')
    print('The implied YTM is: {:.5f} (nominal) {:.5f} (compounded) {:.5f} (continuous)'.format(rateN,rateC,rate))

# using a continuous rate as input
par = b.BondPar(rate, maturity, coupon, frequency)
D = b.BondDuration(price, rate, maturity, coupon, frequency)
up, dn = b.BondDV01(price, rate, maturity, coupon, frequency)
print('Par yield (coupon): {:.3f}'.format(par))
print('Bond duration is:   {:.2f} years'.format(D))
print('10 bps will move the bond by either {:.3f} or +{:.3f}\n'.format(up, dn))
