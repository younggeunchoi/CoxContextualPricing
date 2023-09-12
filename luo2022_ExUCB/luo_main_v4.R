#setwd("~/_ICML2023_supplement/codes")

src_dir = paste0(getwd(), "/luo2022_ExUCB")
save_dir = paste0(getwd(), "/luo2022_ExUCB/result")
dir.create(save_dir, recursive = TRUE)

source( paste0(src_dir, "/luo_DGP_v2.R") )


nrepl = 5 ;

TH = 30000
TH_TUNING = 3000


CU = 1/40 

for (cdf0str in c("twomode", "tnorm2")) {
  for (covstr in c("ph", "nocov")) {
    for (xstr in c("unif","t")) {
      
      
      # set base parameters
      beta = 2/3 ; gam = 1/6 ;
      
      # set cdf0
      eval(parse(text=sprintf("cdf0 = cdf0_%s", cdf0str)))
      
      # set the model the effect of x
      dm = 5;
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
      hyperpara_list = expand.grid(C1=c(1/4, 1/2, 1, 2, 4), l0 = c(64, 128, 256, 512, 1024))
      performance_list = rep(0, nrow(hyperpara_list))
      TIME_HORIZON = TH_TUNING
      for (tunInd in 1:nrow(hyperpara_list)) {
        name_flag = sprintf("hyperpara_%s_dim_%s_cdf0_%s_cov_%s_xdist_%s", tunInd, dm, cdf0str, covstr, xstr)
        C1 = hyperpara_list[tunInd , "C1"]
        l0 = hyperpara_list[tunInd , "l0"]
        cat(sprintf("Evaluating the %s-th hyperparameter, C1=%s, l0=%s...\n", tunInd, C1, l0 ))
        print(Sys.time())
        source( paste0(src_dir, "/luo_simul_v4.R") )
        print(Sys.time())
        performance_list[tunInd] = colMeans(repl_cumRev_real, na.rm=T)[ncol(repl_cumRev_real)]
      }

      # save performance
      result = data.frame(hyperpara_list, reward = performance_list)
      save_name = sprintf("tuningResult_dim_%s_cdf0_%s_cov_%s_xdist_%s.csv", dm, cdf0str, covstr, xstr)
      write.csv(result, paste0(save_dir, "/", save_name), row.names=F)

      # load the optimal hyperparameter      
      tuning_table = read.csv(paste0(save_dir, "/", save_name), header=T)
      maxTunInd = which.max(tuning_table$reward)
      C1 = tuning_table$C1[maxTunInd]
      l0 = tuning_table$l0[maxTunInd]
      print("----------------\n")
      print(sprintf("Select (C1, l0): %s, %s\n", C1, l0))
      print("----------------\n")
      if (length(C1) == 0) {
        print("Warning: C1 not found. Run with default value C1 = 1\n")
        C1 = 1
      }
      if (length(l0) == 0) {
        l0= 512
        print("Warning: C1 not found. Run with default value CU = 1/40\n")
      }

      # run with the optimal hyperparameter
      TIME_HORIZON = TH
      name_flag = sprintf("dim_%s_cdf0_%s_cov_%s_xdist_%s", dm, cdf0str, covstr, xstr)
      print(name_flag)
      
      print(Sys.time())
      source( paste0(src_dir, "/luo_simul_v4.R") )
      print(Sys.time())
    }
  }
}
