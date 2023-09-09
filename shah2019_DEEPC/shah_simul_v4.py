#### ver 4
## as-was: the number of grid grows with T^{d/4}
## to-be: the number of grid set by 3000^{d/4} (for scalability of the algorithm. If T >=10000, the algorithm become intractiable)

import argparse
import sys
import os
import time
import pandas as pd
from datetime import datetime

z_supp_len = trun_max - trun_min + 2       
# assuming supp(F0) = [1,10] and will set search region [0, 11]
# trun_max,trun_min should have been defined in DGP.py
theta_supp_len = np.sum(np.abs(theta0)) * 2  # assuming param space is [0, 2*theta0]^d

reg_T = []  # record 'nrepl' times
rwd_T_shah = []
rwd_T_shahReal = []
rwd_T_opt = []

### repl start
for repl in range(repl0, repl1+1):

    # within-replication rewards and regrets
    print("Simulating scenario %s with repl %s..." % (name_flag, repl))
    print(time.ctime())
    reg = []  # for every time, record all the regret
    rwd_shah = []
    rwd_shahReal = []
    rwd_opt = []

    # sample all the covariates
    #X = np.random.uniform(low=-1/2, high=1/2, size=(n, d))
    X = gen_x(n, d, seed=None)

    # needed quantities for the procedures
    # k = np.ceil((n)**(1/4)) # the len of each partition
    k = np.ceil((3000)**(1/4))  
    a = np.arange(k)
    if d == 1:
        B = np.vstack(np.meshgrid(a, a)).reshape(2, -1).T
    elif d == 2:
        B = np.vstack(np.meshgrid(a, a, a)).reshape(3, -1).T
    elif d == 3:
        B = np.vstack(np.meshgrid(a, a, a, a)).reshape(4, -1).T
    elif d == 4:
        B = np.vstack(np.meshgrid(a, a, a, a, a)).reshape(5, -1).T
    elif d == 5:
        B = np.vstack(np.meshgrid(a, a, a, a, a, a)).reshape(6, -1).T
    elif d == 0:
        B = np.vstack(np.meshgrid(a, np.zeros(int(k)))).reshape(2, -1).T
    else:
        print('ERROR: only d=1 or d=2 are allowed')
    #B[:,0] : the partition of the support of z
    #B[:,1] or the remaining columns : the partition of the support of theta
    B = B*1/k
    B[:, 0] = B[:, 0] * z_supp_len
    B[:, 1:(B.shape[1])] = B[:, 1:(B.shape[1])] * theta_supp_len

    # arms
    m = int(k**(d+1))
    # Initializing Ta (#times arm played) and Sa (#rewards) for each arm
    Ta = np.zeros(m)
    Sa = np.zeros(m)
    # Initializing estimates and confidence bounds for arms
    mu = np.zeros(m)
    l = np.zeros(m)
    u = np.ones(m)

    # Inititalizing set of active arms. 1 imples active, 0 implies inactive
    A = np.ones(m)

    Pmin = np.zeros(m)
    Pmax = np.zeros(m)

    # Implementing Bandit AE algo
    for t in range(n):

        # Compute price range for each active arm. For Pmin, use right boundry for dimension
        # with negative X-entry, and left otherwise
        for j in np.nditer(np.nonzero(A)):
            Pmin[j] = B[j, 0] * \
                np.exp(np.dot(X[t], B[j, 1:d+1] + (X[t] < 0)*(theta_supp_len/k)))
            Pmax[j] = (B[j, 0] + z_supp_len/k) * \
                np.exp(np.dot(X[t], B[j, 1:d+1] + (X[t] > 0)*(theta_supp_len/k)))

        # play one of the active prixes at random, observe reward
        # proposed price
        pt = np.random.uniform(np.amin(Pmin[A > 0]), np.amax(Pmax[A > 0]))
        pt = np.array(pt)

        # optimal price and optimal revenue
        theta_x = np.dot(theta0, X[t])
        ptstar = maxi_true(cdf_true, cdf0, theta_x, name_flag=name_flag)
        rev_opt = ptstar * (1 - cdf_true(cdf0, ptstar, theta_x))

        # reward from the proposed policy
        yt = np.random.binomial(1, 1 - cdf_true(cdf0, pt, theta_x))
        rt = yt*pt  # realized revenue
        rev_shah = pt * (1 - cdf_true(cdf0, pt, theta_x))  # expected revenue

        # save rewards
        rev_diff = rev_opt - rev_shah
        rwd_opt.append(rev_opt)
        rwd_shah.append(rev_shah)
        rwd_shahReal.append(rt)
        reg.append(rev_diff)  # exploitation
        np.savetxt(save_dir + "/rwd_opt_shah_%s.csv" %
                   save_name, rwd_opt, delimiter=",")
        np.savetxt(save_dir + "/rwd_shah_shah_%s.csv" %
                   save_name, rwd_shah, delimiter=",")
        np.savetxt(save_dir + "/rwd_shahReal_shah_%s.csv" %
                   save_name, rwd_shahReal, delimiter=",")


        # Update arm's statistical variables
        A_temp = A.copy()
        for at in np.nditer(np.nonzero(A)):
            if pt > Pmin[at] and pt < Pmax[at]:
                Ta[at] = Ta[at] + 1
                Sa[at] = Sa[at] + rt
                mu[at] = Sa[at]/Ta[at]
                # l[at] = mu[at] - np.sqrt(gamma*np.log(n)/Ta[at])
                # u[at] = mu[at] + np.sqrt(gamma*np.log(n)/Ta[at])
                l[at] = mu[at] - np.sqrt(gamma/Ta[at])
                u[at] = mu[at] + np.sqrt(gamma/Ta[at])

                # Eliminate arms
                if u[at] < np.max(np.multiply(A, l)):  # Eliminate this arms if l to low
                    A[at] = 0
                A[u < l[at]*A] = 0  # Eliminate other arms with low u
        if (sum(A != 0) == 0):
            A = A_temp.copy()  # if supp(A) becomes zero unexpectedly, then neglict this step
            print("Warning: active set became empty at time %s. wiil maintain the current active set..." % t)
        
        if t % 1000 == 0:
            print(t)
    # for a fixed T, we need to do this for renpl times
    reg_T.append(np.cumsum(reg))
    rwd_T_opt.append(np.cumsum(rwd_opt))
    rwd_T_shah.append(np.cumsum(rwd_shah))
    rwd_T_shahReal.append(np.cumsum(rwd_shahReal))

    np.savetxt(save_dir + "/cumRev_opt_shah_%s.csv" % save_name,
               np.array(rwd_T_opt), delimiter=",")
    np.savetxt(save_dir + "/cumRev_shah_shah_%s.csv" % save_name,
               np.array(rwd_T_shah), delimiter=",")
    np.savetxt(save_dir + "/cumRev_shahReal_shah_%s.csv" % save_name,
               np.array(rwd_T_shahReal), delimiter=",")
