#### ver 5
## runs simul_v4.py instead of v3
#### ver 4
## separate before tuning and after tuning

import argparse
import sys
import os
import time
import pandas as pd
from datetime import datetime


# Declare function to define command-line arguments
def readOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="The parsing commands lists.")
    parser.add_argument(
        "-r", "--repl0", help="First replication index. Integer.")
    parser.add_argument(
        "-R", "--repl1", help="Last replication index. Integer.")
    parser.add_argument(
        "-d", "--dim", help="Covariate dimension. Integer.")
    parser.add_argument(
        "-b", "--baseline", help="Baseline cdf (F0). twomode? or tnorm?")
    parser.add_argument(
        "-c", "--cov", help="Covariate effect. nocov? or ph?")
    parser.add_argument(
        "-x", "--xdist", help="The distribution of x. unif? or t?")
    parser.add_argument(
        "-T", "--horizon", help="The number of total horizon. Integer.")
    parser.add_argument("-s", "--savedir",
                        help="The name of saving directory?")
    parser.add_argument(
        "-t", "--istuning", help="Will be this code for hyperparameter tuning? 0(no) 1(yes)")
    parser.add_argument(
        "-0", "--tuninghorizon", help="The number of tuning horizon. Integer.")
    parser.add_argument(
        "-g", "--gamma", help="The degree of exploration gamma (use this only if not tuning)")
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
            self.dim = 5
            self.baseline = "twomode"
            self.cov = "ph"
            self.xdist = "unif"
            self.horizon = 30000
            self.savedir = 'test'
            self.istuning = True
            self.tuninghorizon = 1000
            self.gamma = 3
    opts = defaultOption()
opts.istuning = bool(int(opts.istuning))


base_dir = os.getcwd()

src_dir = base_dir
save_dir = base_dir
if (opts.savedir is not None):
    save_dir = base_dir + "/" + opts.savedir
os.makedirs(save_dir, exist_ok=True)

exec(open("../fan2022/fan_DGP_v2.py").read())



########Basic simulation Setup,
repl0 = int(opts.repl0)
repl1 = int(opts.repl1)
# n denotes the number of total rounds in Shah et al. (2019)

hyperpara_list = np.array([(1/3)**2, 1/3, 1, 3, 3**2])  # candidates of gamma
performance_list = np.zeros_like(hyperpara_list)

#gamma = 3  # controls the degree of exploration

#################################################
############ assign simulation settings #########
#################################################
cdf0 = eval("cdf0_" + opts.baseline)
gen_x = eval("gen_x_" + opts.xdist)
d = int(opts.dim)   # the number of variables (context dimension)
if (opts.cov == "nocov"):
    cdf_true = cdf_lin
    theta0 = np.zeros(d)
else:
    cdf_true = eval("cdf_" + opts.cov)
    theta0 = np.ones(d) * (4/np.sqrt(d))

# if tuning is true, search for hyperparameter for T0 rounds
if opts.istuning:

    try:
        T0 = int(opts.tuninghorizon)
    except:
        assert False, "If want tuning, specify tuning horizon (T0)"

    n = T0
    for tunInd in range(len(hyperpara_list)):
        print("Evaluating the %s-th hyperparameter...\n" % tunInd)
        gamma = hyperpara_list[tunInd]
        name_flag = "tunind_%s_dim_%s_cdf0_%s_cov_%s_xdist_%s_T0_%s_repl%sto%s" % \
            (tunInd, opts.dim, opts.baseline, opts.cov, opts.xdist, T0,
             opts.repl0, opts.repl1)
        save_name = name_flag 

        #### run!
        print(time.ctime())
        exec(open(src_dir + "/shah_simul_v4.py").read())
        print(time.ctime())

        performance_list[tunInd] = np.array(rwd_T_shahReal).mean(
            axis=0)[-1]  # cumulative regret at the last

    # save performance
    result = pd.DataFrame(
        data={"hyperpara": hyperpara_list, "reward": performance_list})
    save_name = "tuningResult_dim_%s_cdf0_%s_cov_%s_xdist_%s_T0_%s_repl%sto%s.csv" % \
        (opts.dim, opts.baseline, opts.cov, opts.xdist, T0, opts.repl0, opts.repl1)
    result.to_csv(save_dir + "/" + save_name, na_rep='NaN', index=False)
    
    # load the performance (same file with above)
    tuning_table = pd.read_csv(save_dir + "/" + save_name)
    gamma = tuning_table['hyperpara'][np.argmax(tuning_table.iloc[:, 1])]
    print("----------------\n")
    print("Select gamma: %s\n" % gamma)
    print("----------------\n")

if not opts.istuning:
    try:
        T0 = int(opts.tuninghorizon)
        print("T0 input detected. Try finding tuning results..")
        load_name = "tuningResult_dim_%s_cdf0_%s_cov_%s_xdist_%s_T0_%s_repl%sto%s.csv" % \
            (opts.dim, opts.baseline, opts.cov,
             opts.xdist, T0, opts.repl0, opts.repl1)
        tuning_table = pd.read_csv(save_dir + "/" + load_name)
        gamma = tuning_table['hyperpara'][np.argmax(tuning_table.iloc[:, 1])]
    except:
        print("Warning: The file with T0 tuning does not exist. Going with specified gamma..\n") 
        try:
            gamma = int(opts.gamma)
        except:
            print("Warning: gamma didn't specified; set to default value")
            gamma = 3
            
    n = int(opts.horizon)
    name_flag = "dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s_repl%sto%s" % \
        (opts.dim, opts.baseline, opts.cov, opts.xdist, opts.horizon, opts.repl0, opts.repl1)
    save_name = name_flag  
    #### run!
    print(time.ctime())
    print("Running the main procedure with gamma=%s ..." % gamma)
    exec(open(src_dir + "/shah_simul_v4.py").read())
    print(time.ctime())
