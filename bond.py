# Use command line arguments to obtain results

import sys
import bond_functions as b


jolly = float(sys.argv[1])
maturity = sys.argv[2]
coupon = float(sys.argv[3])
frequency = int(sys.argv[4])

# need for a numerical time to maturity in years
maturity = float(maturity)

if jolly < 1:
    # need for an input rate in continuous terms
    ask = input('Yield expressed in nominal/compounded/continuous terms? ')
    if ask == 'nominal':
        rate = b.continuous(jolly,1)
    elif ask == 'compounded':
        rate = b.continuous(jolly,frequency)
    else:
        rate = jolly
    price = b.BondPrice(rate, maturity, coupon, frequency)
    print('Price should be: {:.2f}'.format(price))
    print('The bond should cost (dirty price): {:.2f}\n'.format(price + b.BondAccrued(maturity, coupon, frequency)))
else:
    # usually the clean price is the one quoted
    ask = input('Clean price? (Y/n) ')
    if ask == 'n':
        price = jolly - b.BondAccrued(maturity, coupon, frequency)
    else:
        price = jolly
    rate = b.BondYield(price, maturity, coupon, frequency)
    rateN = b.nominal(rate, 1000)
    print('The implied YTM is: {:.4f} (continuous) or {:.4f} (nominal)'.format(rate, rateN))

D = b.BondDuration(price, rate, maturity, coupon, frequency)
up, dn = b.BondDV01(price, rate, maturity, coupon, frequency)
print('Bond duration is: {:.2f} years'.format(D))
print('100 bps will move the bond by either {:.2f} or +{:.2f}\n'.format(up, dn))
