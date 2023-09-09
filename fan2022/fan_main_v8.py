### ver 8 (2023-01-18)
## separate (T, t0) from l0
### ver 5 (2023-01-10)
## add "rwdReal" for tuning
### ver 4 (2023-01-08)
## added tuning
## it 
## changed the defintion of l_k1 (need the input of C1)

import argparse
import sys
import os
import time
import pandas as pd
from datetime import datetime


# Declare function to define command-line arguments
def readOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="The parsing commands lists.")
    parser.add_argument("-r", "--repl0", help="First replication index. Integer.")
    parser.add_argument("-R", "--repl1", help="Last replication index. Integer.")
    parser.add_argument("-d", "--dim", help="Covariate dimension. Integer.")
    parser.add_argument("-b", "--baseline", help="Baseline cdf (F0). twomode? or tnorm2?")
    parser.add_argument("-c", "--cov", help="Covariate effect. nocov? or ph?")
    parser.add_argument("-x", "--xdist", help="The distribution of x. unif? or t?")
    parser.add_argument("-T", "--horizon",
                        help="The number of total horizon. Integer. If istuning=0, then the total horizon of the main round. If istuning=1, it is a horizon for tuning.")
    parser.add_argument("-s", "--savedir", help="The name of saving directory?")
    parser.add_argument("-t", "--istuning", help="Will be this code for hyperparameter tuning? 0(no) 1(yes)")
    parser.add_argument("-0", "--tuninghorizon", help="The number of tuning horizon. Integer.")
    opts = parser.parse_args(args)
    return opts

# Call the function to read the argument values
try:
    opts = readOptions(sys.argv[1:])
except:
    print("no inputs detected. going with default options (test mode)...\n")
    class defaultOption(object):
        def __init__(self):
            self.repl0 = 1
            self.repl1 = 5
            self.dim = 1
            self.baseline = "twomode"
            self.cov = "ph"
            self.xdist = "unif"
            self.horizon = 30000
            self.savedir = 'test'
            self.istuning = True
            self.tuninghorizon = 3000
    opts = defaultOption()
opts.istuning = bool(int(opts.istuning))
    

base_dir = os.getcwd()

src_dir = base_dir
save_dir = base_dir
if (opts.savedir is not None):
    save_dir = base_dir + "/" + opts.savedir
os.makedirs(save_dir, exist_ok=True)

exec(open(src_dir + "/fan_DGP_v2.py").read())
exec(open(src_dir + "/fan_functions_v2.py").read())

########Basic simulation Setup,
repl0 = int(opts.repl0)
repl1 = int(opts.repl1)
B = 12       # maximum of the uniform sampling
# l_0 = int(opts.l0)    # the length of the first episode
# epi_num = int(opts.epinum)  # the number of episodes
#T = l_0*(2^(epi_num)-1) # the total horizon
if opts.istuning:
    T = int(opts.tuninghorizon)
if not opts.istuning:
    T = int(opts.horizon)


#C1_list = [1/4]
C1_list = [1/4, 1/2, 1, 2, 4]
#l_0_list = [256]
l_0_list = [64, 128, 256, 512, 1024]
hyperpara_list = [ (x, y) for x in C1_list for y in l_0_list ]
performance_list = np.zeros(len(hyperpara_list))

#################################################
############ assign simulation settings #########
#################################################
cdf0 = eval("cdf0_" + opts.baseline)
dm = int(opts.dim)
gen_x = eval("gen_x_" + opts.xdist)
if (opts.cov == "nocov"):
    cdf_true = cdf_lin
    theta0 = np.zeros(dm)
else: 
    cdf_true = eval("cdf_" + opts.cov)
    # dm = dimension; # theta0 = true \theta_{0}
    theta0 = np.ones(dm) * (4/np.sqrt(dm))


    
if opts.istuning:
    
    for tunInd in range(len(hyperpara_list)):
        print("Evaluating the %s-th hyperparameter...\n" % tunInd)
        assert repl0 != repl1, "If we want hyperparameter tuning using this code,\nI recommend not to parallelize by the replication number\n(i.e, if your replication number is 5, set repl0=1 and repl1=5)"
        C1, l_0 = hyperpara_list[tunInd]
        epi_num = int(np.ceil(np.log2( (T+1) / l_0 )))
        name_flag = "tunind_%s_dim_%s_cdf0_%s_cov_%s_xdist_%s_l0_%s_T_%s_repl%sto%s" % \
            (tunInd, dm, opts.baseline, opts.cov, opts.xdist, l_0, int(opts.tuninghorizon), opts.repl0, opts.repl1)
        save_name = name_flag 

        #### run!
        print(time.ctime())
        exec(open(src_dir + "/fan_simul_v7.py").read())
        print(time.ctime())
        
        performance_list[tunInd] = np.array(rwd_T_fanReal).mean(axis=0)[-1]  # cumulative regret at the last
   
    # save performance
    res_list = [ (x,y,z) for (x,y),z in zip(hyperpara_list, performance_list) ]
    result = pd.DataFrame(res_list, columns=["C1", "l0", "reward"])
    save_name = "tuningResult_dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s_repl%sto%s" % \
        (dm, opts.baseline, opts.cov, opts.xdist, int(opts.tuninghorizon), opts.repl0, opts.repl1)
    result.to_csv(save_dir + "/" + save_name + ".csv", na_rep='NaN', index = False)


if not opts.istuning:   
    # load best hyperapramer
    try:
        tuning_horizon = int(opts.tuninghorizon)
        tuning_repl0 = 1
        tuning_repl1 = 5
        load_name = "tuningResult_dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s_repl%sto%s" % \
            (dm, opts.baseline, opts.cov, opts.xdist, tuning_horizon, opts.repl0, opts.repl1)
        tuning_table = pd.read_csv(save_dir + "/" + load_name + ".csv")
        C1 = tuning_table['C1'][np.argmax(tuning_table.iloc[:,2])]
        l_0 = tuning_table['l0'][np.argmax(tuning_table.iloc[:, 2])]
    except:
        print("Warnings: tuning record does not exist. Going with C1=1 (Default)...")
        C1 = 1
        l_0 = 512
    
    epi_num = int(np.ceil(np.log2((T+1) / l_0)))
    name_flag = "dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s_repl%sto%s" % \
        (dm, opts.baseline, opts.cov, opts.xdist, opts.horizon, opts.repl0, opts.repl1)
    save_name = name_flag
    #### run!
    print(time.ctime())
    exec(open(src_dir + "/fan_simul_v7.py").read())
    print(time.ctime())

