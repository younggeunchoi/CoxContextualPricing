import argparse
import sys
import os
import time
from datetime import datetime


### 230120_expr3 - before tuning 
Tlist = [(3000, 30000)] # (tuninghorizon, horizon)
savedir = "shah_simul"
repl0 = 1
repl1 = 5
istuning = 1
dim = 5
for baseline in ['twomode', 'tnorm2']:
    for cov in ['nocov', 'ph']:
        for xdist in ["unif", "t"]:
            for (T0, T) in Tlist:
              name_flag = "cdf0_%s_cov_%s_T_%s_repl%sto%s" % \
                  (baseline, cov, T, repl0, repl1)
              log_save_name = savedir + "/log_" + name_flag
              err_save_name = savedir + "/err_" + name_flag
              print("nohup python shah_main_v5.py --repl0 %s --repl1 %s --dim %s --baseline %s --cov %s --xdist %s --horizon %s --savedir %s --istuning %s --tuninghorizon %s > %s.log 2> %s.err & \n" %
                    (repl0, repl1, dim, baseline, cov, xdist, T,  savedir, istuning, T0, log_save_name, err_save_name))


### 230120_expr3 - after tuning (done at 230125)
Tlist = [(3000, 30000)]
savedir = "shah_expr"
istuning = 0
dim = 5
for baseline in ['twomode', 'tnorm2']:
    for cov in ['nocov', 'ph']:
        for xdist in ["unif", "t"]:
            for (T0, T) in Tlist:
                for repl in range(1,6):
                    repl0 = repl
                    repl1 = repl
                    name_flag = "cdf0_%s_cov_%s_T_%s_repl%sto%s" % \
                        (baseline, cov, T, repl0, repl1)
                    log_save_name = savedir + "/log_" + name_flag
                    err_save_name = savedir + "/err_" + name_flag
                    print("nohup python shah_main_v5.py --repl0 %s --repl1 %s --dim %s --baseline %s --cov %s --xdist %s --horizon %s --savedir %s --istuning %s --tuninghorizon %s > %s.log 2> %s.err & \n" %
                            (repl0, repl1, dim, baseline, cov, xdist, T,  savedir, istuning, T0, log_save_name, err_save_name))

