#
# A stationary price series means that the prices diffuses from its initial value
# more slowly than a geometric random walk.
# Tau is an arbitrary time lag
#
import numpy as np
import scipy.stats as stats


def hurst(p):  # p are log-prices

    lags = range(2, 20)
    variancetau = []
    tau = []

    for lag in lags:
        #  tau is the vector of lags
        tau.append(lag)
        # log returns
        pp = np.subtract(p[lag:], p[:-lag])
        # variance of log returns
        variancetau.append(np.var(pp))

    # we now have a set of tau or lags and a corresponding set of variances.
    # get the slope
    m = np.polyfit(np.log(tau), np.log(variancetau), 1)
    he = m[0] / 2  # polyfit returns the highest polynomial first..
    print('--------------------------------------------------')
    print('Hurst exponent: {:.3f}\n'.format(he))

    return he


def vratio(p):  # is the hurst exponent really 0.5 := RW ? (high pvalue)

    lags = range(2, 5)
    test = []
    n = len(p)

    for tau in lags:

        pp = np.subtract(p[tau:], p[:-tau])
        numerator = np.var(pp)
        pq = np.subtract(p[1:], p[:-1])
        denominator = tau * np.var(pq)
        adj = 2*(2*tau-1)*(tau-1) / (3*tau*n)
        test.append((numerator / denominator - 1) / np.sqrt(adj))

    pvalue = 2 * stats.norm.cdf(-np.abs(test))  # two sided tast
    print('Variance Ratio Test p-values:\n', pvalue.round(3))

    return pvalue


def beta(x,y): # variables in rows

    m = np.cov(y,x,rowvar=True) # covariances
    s = np.diag(m) # variances
    n = y.shape[0]
    X = np.vstack([np.ones(n), x]).T

    b = np.dot( np.linalg.inv( np.dot(X.T,X) ), np.dot(X.T,y.reshape(n, 1)) )
    b = b.reshape(1, b.shape[0])
    se = np.sqrt( np.diag( np.dot( s[0], np.linalg.inv( np.dot(X.T,X) ) ) ) )
    pvalue = 2 * stats.norm.cdf(-np.abs(b/se))
    print('--------------------------------------------------')
    print('Beta:\n', b.round(3))
    print('p-value\n', pvalue.round(3))

    return b, pvalue


def halflife(y):
    y = np.array(y)
    ylag = y[:-1]
    y = y[1:]
    b, se = beta(ylag, y)
    hl = -np.log(2) / (b[0][1] - 1)
    print('--------------------------------------------------')
    print('Half-life: {:.1f}\n'.format(hl))

    return hl
