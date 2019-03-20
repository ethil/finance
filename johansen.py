# Johansen test for cointegration
from statsmodels.tsa.vector_ar.vecm import coint_johansen

# Parameters:
#
#     endog (array-like (nobs_tot x neqs)) – The data with presample.
#     det_order (int) –
#         -1 - no deterministic terms
#          0 - constant term
#          1 - linear trend
#     k_ar_diff (int, nonnegative) – Number of lagged differences in the model.
#


def johansen(endog, det_order, k_ar_diff):

    result = coint_johansen(endog, det_order, k_ar_diff)
    print('--------------------------------------------------')
    print('--> Trace Statistics')
    print('variable statistic Crit-90% Crit-95%  Crit-99%')
    for i in range(len(result.lr1)):
        print('r =', i, '\t', round(result.lr1[i], 4), result.cvt[i, 0], result.cvt[i, 1], result.cvt[i, 2])
    print('--------------------------------------------------')
    print('--> Eigen Statistics')
    print('variable statistic Crit-90% Crit-95%  Crit-99%')
    for i in range(len(result.lr2)):
        print('r =', i, '\t', round(result.lr2[i], 4), result.cvm[i, 0], result.cvm[i, 1], result.cvm[i, 2])
    print('--------------------------------------------------')
    print('eigenvectors:\n', result.evec)
    print('--------------------------------------------------')
    print('eigenvalues:\n', result.eig)

    return result.evec[:,0]
