### ver 7 (2023-01-18)
## ends at a specific decision round T

### ver 4 (2023-01-08)
## changed the defintion of l_k1 (need the input of C1)

###Import Packages########
import runpy
import random
import math
import numpy as np
from numpy.linalg import inv

import os
import time


reg_T=[] #record 'nrepl' times
rwd_T_fan = []
rwd_T_fanReal = []
rwd_T_opt = []


for repl in range(repl0, repl1+1):

    print("Simulating scenario %s with repl %s..." % (name_flag, repl))
    print(time.ctime())
    reg=[] #for every time, record all the regret
    rwd_fan=[]
    rwd_fanReal=[]
    rwd_opt=[]
    global_round_count = 0

    for k in range(epi_num):
        print("episode number = %s" % k)
        print(time.ctime())
        t=0
        l_k=l_0*2**k
        l_k1=math.floor(C1 * (l_k*dm)**(5/7))  # the length of forced exploration. C1 is a hyperparameter.
        v_i=[]
        # v_i_true=[]
        v_t=[]
        y_t=[]
        p_t_coll=[]
        X=np.zeros(dm,dtype=float) 
        X=X.reshape(1,-1) 
        while t < l_k:  # in-phase loop
            global_round_count = global_round_count + 1
            if t < l_k1:  #Exploration phase.
                #x = np.random.uniform(low=-0.5, high=0.5, size=dm)  
                x = gen_x(1, dm, seed=None).reshape(-1)
                X=np.concatenate((X, x.reshape(1,-1)))   # accumulate x's 
                theta_x = np.dot(theta0,x) 
                p_t= np.array(np.random.uniform(0,B))
                p_t_coll.append(p_t)
                y = np.random.binomial(1, 1 - cdf_true(cdf0, p_t, theta_x)) 
                y_t.append(y)

                op_price=maxi_true(cdf_true, cdf0, theta_x, name_flag=name_flag) 

                rev_opt = op_price * (1 - cdf_true(cdf0, op_price, theta_x))
                rev_fan = p_t * (1 - cdf_true(cdf0, p_t, theta_x))
                rev_diff = rev_opt - rev_fan

                rwd_opt.append(rev_opt)
                rwd_fan.append(rev_fan)
                rwd_fanReal.append(y * p_t)
                reg.append(rev_diff)
                np.savetxt(save_dir + "/rwd_opt_fan_%s.csv" % save_name, rwd_opt, delimiter=",")
                np.savetxt(save_dir + "/rwd_fan_fan_%s.csv" % save_name, rwd_fan, delimiter=",")
                np.savetxt(save_dir + "/rwd_fanReal_fan_%s.csv" % save_name, rwd_fanReal, delimiter=",")
                if t == l_k1 - 1: #Update Parameters theta and F
                    y_t=np.array(y_t)#vector of y_t
                    p_t_coll=np.array(p_t_coll)
                    X=X[1:] #matrix of X
                    one=np.ones(l_k1,dtype=int)
                    one=one.reshape(l_k1,1)
                    X_1=np.concatenate((one,X),axis=1)
                    theta1=np.dot(inv(np.dot(X_1.transpose(),X_1)),\
                                  np.dot(X_1.transpose(),B*y_t))
                    v_i=p_t_coll-np.dot(X_1,theta1).transpose()
                    ker=Kernel(v_i,y_t,l_k1) 
                    print('--explore--')
                    print(t)
                    print(time.ctime())
                    y_t = list(y_t)
                t=t+1

            else: #exploitation phase
                #x = np.random.uniform(low=-0.5, high=0.5, size=dm)  
                x = gen_x(1, dm, seed=None).reshape(-1)
                theta_x = np.dot(theta0,x) 
                op_price=maxi_true(cdf_true, cdf0, theta_x, name_flag=name_flag) 
                rev_opt = op_price * (1 - cdf_true(cdf0, op_price, theta_x))
                theta_est=theta1[0]+np.dot(theta1[1:],x)
                est_price = ker.maxi_est(theta_est, 0, B)   # p_t
                y = np.random.binomial(1, 1 - cdf_true(cdf0, est_price, theta_x)) 
                y_t.append(y)
                
                rev_fan = est_price * (1 - cdf_true(cdf0, est_price, theta_x))
                rev_diff = rev_opt - rev_fan
                rwd_opt.append(rev_opt)
                rwd_fan.append(rev_fan)
                rwd_fanReal.append(y * p_t)
                reg.append(rev_diff)#exploitation
                np.savetxt(save_dir + "/rwd_opt_fan_%s.csv" % save_name, rwd_opt, delimiter=",")
                np.savetxt(save_dir + "/rwd_fan_fan_%s.csv" % save_name, rwd_fan, delimiter=",")
                np.savetxt(save_dir + "/rwd_fanReal_fan_%s.csv" % save_name, rwd_fanReal, delimiter=",")
                if t == l_k-1:
                    print('--exploit--')
                    print(t)
                    print(time.ctime())
                t=t+1
            
            if global_round_count == T:
                break  # break from the inner loop
        
        if global_round_count == T:
            break  # break from the outer loop

    reg_T.append(np.cumsum(reg))#for a fixed T, we need to do this for 30 times
    rwd_T_opt.append(np.cumsum(rwd_opt))#for a fixed T, we need to do this for 30 times
    rwd_T_fan.append(np.cumsum(rwd_fan))
    rwd_T_fanReal.append(np.cumsum(rwd_fanReal))
    np.savetxt(save_dir + "/cumRev_opt_fan_%s.csv" % save_name, \
               np.array(rwd_T_opt), delimiter=",")
    np.savetxt(save_dir + "/cumRev_fan_fan_%s.csv" % save_name, \
               np.array(rwd_T_fan), delimiter=",")
    np.savetxt(save_dir + "/cumRev_fanReal_fan_%s.csv" % save_name, \
               np.array(rwd_T_fanReal), delimiter=",")
