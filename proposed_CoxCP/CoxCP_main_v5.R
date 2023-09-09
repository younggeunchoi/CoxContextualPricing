# set working directory to simulation_env folder
# (default : {~/_ICML2023_supplement/codes})
#setwd("~/_ICML2023_supplement/codes")

# set save directory (default : /{model_name}/{simulation_name})
src_dir = paste0(getwd(), "/proposed_CoxCP")
save_dir = paste0(getwd(), '/proposed_CoxCP/result')
dir.create(save_dir, recursive = TRUE)

source(paste0(getwd(), "/luo2022_ExUCB/luo_DGP_v2.R"))

nrepl = 5

EST_ITER = 3000
EST_EPS = 1e-5

TH = 30000
TH_TUNING = 3000

dm = 5


for (cdf0str in c("twomode", "tnorm2")) {
  for (covstr in c("ph", "nocov")) {
    for (xstr in c("unif", "t")) {
      
      # set base parameters

      # set cdf0
      eval(parse(text=sprintf("cdf0 = cdf0_%s", cdf0str)))
      
      # set the model the effect of x
      dm = dm;
      if (covstr != "nocov") {
        theta0 = rep(4/sqrt(dm),dm)
        eval(parse(text=sprintf("cdf_true = cdf_%s", covstr)))
      } else {
        theta0 = rep(0/dm,dm)
        eval(parse(text=sprintf("cdf_true = cdf_%s", "lin")))
      }
      
      # set the distribution of x
      gen_x = eval(parse(text=sprintf("gen_x = gen_x_%s", xstr)))
      
      # tuning
      hyperpara_list = expand.grid(alpha = 2^c(-4, -3, -2, -1, 0), l0 = c(64, 128, 256, 512, 1024))
      performance_list = data.frame(matrix(rep(0, nrow(hyperpara_list))))
      colnames(performance_list) = c("unk")
      TIME_HORIZON = TH_TUNING; tuning = TRUE;
      for (tunInd in 1:nrow(performance_list)) {
        name_flag = sprintf("hyperpara_%s_dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s", tunInd, dm, cdf0str, covstr, xstr, TIME_HORIZON)
        unk.alpha = hyperpara_list[tunInd, "alpha"]
        unk.l0    = hyperpara_list[tunInd, "l0"]
        cat(sprintf("Evaluating the %s-th hyperparameter, unk.alpha=%s,  unk.l0=%s", tunInd, unk.alpha, unk.l0))
        print(Sys.time())
        source( paste0(src_dir, "/CoxCP_simul_v5.R") )
        print(Sys.time())
        
        performance_list[tunInd] = unk.cumRev_real
      }
      
      # save performance
      save_name = sprintf("tuningResult_dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s.csv", dm, cdf0str, covstr, xstr, TIME_HORIZON)
      write.csv(performance_list, paste0(save_dir, "/", save_name), row.names=F)
      
      # load the optimal hyperparameter      
      tuning_table = read.csv(paste0(save_dir, "/", save_name), header=T)
      unk.maxTunInd = which.max(unlist(tuning_table[1]))
      unk.alpha = hyperpara_list[unk.maxTunInd,1]
      unk.l0 = hyperpara_list[unk.maxTunInd,2]
      print("----------------\n")
      print(sprintf("Select (unk.alpha, unk.lo): %s, %s\n", unk.alpha, unk.l0))
      print("----------------\n")
      
      if (length(unk.alpha) == 0) {
        print("Warning: unk.alpha not found. Run with default value alpha = 1\n")
        unk.alpha = 1
      }
      if (length(unk.l0) == 0) {
        print("Warning: unk.alpha not found. Run with default value alpha = 1\n")
        unk.l0 = 512
      }
      
      # run with the optimal hyperparameter
      TIME_HORIZON = TH; tuning = FALSE;
      name_flag = sprintf("dim_%s_cdf0_%s_cov_%s_xdist_%s_T_%s", dm, cdf0str, covstr, xstr, TIME_HORIZON)
      print(name_flag) 
      
      print(Sys.time())
      source( paste0(src_dir, "/CoxCP_simul_v5.R" ) )
      print(Sys.time())
    }
  }
}
