import argparse
import sys
import os
import time
from datetime import datetime



### tuning
savedir = "fan_expr"
repl0 = 1
repl1 = 5
istuning = 1
horizon = 30000
tuninghorizon = 3000
for dim in [5]:
    for baseline in ['twomode', 'tnorm2']:
        for cov in ['nocov', 'ph']:
            for xdist in ["unif", "t"]:
                name_flag = "tuning_dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s_repl%sto%s" % \
                    (dim, baseline, cov, xdist, tuninghorizon, repl0, repl1)
                log_save_name = savedir + "/log_" + name_flag
                err_save_name = savedir + "/err_" + name_flag
                print("nohup python fan_main_v8.py --repl0 %s --repl1 %s --dim %s --baseline %s --cov %s --xdist %s --horizon %s --savedir %s --istuning %s --tuninghorizon %s > %s.log 2> %s.err & \n" %
                      (repl0, repl1, dim, baseline, cov, xdist, horizon, savedir, istuning, tuninghorizon, log_save_name, err_save_name))

### after tuning
savedir = "fan_expr"
istuning = 0
horizon = 30000
tuninghorizon = 3000
for repl in range(1, 6):
    for dim in [5]:
        for baseline in ['twomode', 'tnorm2']:
            for cov in ['nocov', 'ph']:
                for xdist in ["unif", "t"]:
                    repl0 = repl
                    repl1 = repl
                    name_flag = "dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s_repl%sto%s" % \
                        (dim, baseline, cov, xdist, tuninghorizon, repl0, repl1)
                    log_save_name = savedir + "/log_" + name_flag
                    err_save_name = savedir + "/err_" + name_flag
                    print("nohup python fan_main_v8.py --repl0 %s --repl1 %s --dim %s --baseline %s --cov %s --xdist %s --horizon %s --tuninghorizon %s --savedir %s --istuning %s 1> %s.log 2> %s.err & \n" %
                          (repl0, repl1, dim, baseline, cov, xdist, horizon, tuninghorizon, savedir, istuning, log_save_name, err_save_name))
