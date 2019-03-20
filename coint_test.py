# Run cointegration test
import numpy as np
import johansen as j


def test(prices, tickers):

    # shares
    weights1 = j.johansen(prices, 0, 1)
    port1 = np.dot(prices, weights1.T)

    # portfolio weighting ~ worsen results
    log_returns = np.log(prices).diff()
    log_returns = log_returns[1:]
    weights2 = j.johansen(np.log(prices), 0, 1)
    port2 = np.dot(log_returns, weights2.T).cumsum()

    return weights1, weights2, port1, port2
