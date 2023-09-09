
# lam: regularization lambda in Inner UCB Algorithm;
# C1: exploration phase constant C_{1}; hyperparameters optimized in luo_main.R
# C2: discretization constant C_{2};
# CU: UCB constant; nk = number of replications; 
lam = 0.1
#C1 = 1
C2 = 20
CU = 1/40
nk = nrepl ;


# epi: number of episodes; 
# ini: \alpha_{1}, initial episode length;
# T: horizon length;
# exl: record exploration phase lengths; dis: record discretization numbers;
ini = l0
T = TIME_HORIZON

start_num = ini
tmp_jump = start_num * 2 ^ (0:10)
epi_doubling = c(start_num)
for (i in 2:length(tmp_jump)){
  epi_doubling[i] = tmp_jump[i] + epi_doubling[i-1]
}
epi_doubling = epi_doubling[epi_doubling < TIME_HORIZON] 
epis = rep(0, TIME_HORIZON)
epis[ epi_doubling + 1 ] = 1
epis = cumsum(epis) + 1
epi = epis[length(epis)]

exl = rep(0,epi)
dis = rep(0,epi)


# pmax = p_{\max}, the optimal price upper bound; 
# B = B, the valuation upper bound;
pmax = 12
B = 12


# lsber: record average accumulative optimal revenues
# lser: record average ExUCB accumulative revenues
# llsber: record accumulative optimal revenues in each replication
# llser: record accumulative ExUCB revenues in each replication
# time_cost: record time consumption of each replication
lsber = rep(0,T)
lser = rep(0,T)
llsber = matrix(0,nk,T)
llser = matrix(0,nk,T)
repl_cumRev_real = matrix(0,nk,T)
time_cost = rep(0,nk)


# Replications begin
# ik = current iteration; jk = current seed
ik = 1
jk = 1
while (ik <= nk){
  t1 = Sys.time()
  jk = jk + 1
  # print current iteration
  print(paste("Current iteration:", ik))
  
  # bS: record optimal prices; 
  # ber: record one-period optimal revenues;
  # sber: record accumulative optimal revenues;
  bS = rep(0,T)
  ber = rep(0,T)
  sber = rep(0,T)
  
  # S: record prices set by ExUCB policy;
  # y: record binary outcomes of ExUCB policy;
  # r: record realized revenues of ExUCB policy;
  # er: record one-period revenues of ExUCB policy;
  # ser: record accumulative revenues of ExUCB policy;
  S = rep(0,T)
  y = rep(0,T)
  r = rep(0,T)
  er = rep(0,T)
  ser = rep(0,T)
  
  # x1: covariates; tthx: record true x_{t}^{\top}\theta_{0};
  # thx: record estimated x_{t}^{\top}\theta_{0};
  # x1 = matrix(runif(dm*T, -1/2, 1/2),T,dm)
  x1 = gen_x(T, dm, seed=NULL)
  tthx = as.vector(x1%*%theta0)
  thx = rep(0,T)
  
  
  cur_end = 0
  # Episode iteration begins
  # subT: episode length
  for (j in 1:epi){
    subT = ini*2^(j-1)
    
    # Exploration Phase
    explore_l = ceiling(C1*subT^beta)
    exl[j] = explore_l
    for (i in 1:explore_l){
      if (i + cur_end > T){break}
      S[i+cur_end] = runif(1,0,B)
      bS[i+cur_end] = maxi_true(cdf_true,cdf0,tthx[i+cur_end], name_flag)
      y[i+cur_end] = rbinom(1,1,1-cdf_true(cdf0, S[i+cur_end], tthx[i+cur_end]))
      r[i+cur_end] = S[i+cur_end]*y[i+cur_end]
      er[i+cur_end] = S[i+cur_end]*(1-cdf_true(cdf0, S[i+cur_end], tthx[i+cur_end]))
      ber[i+cur_end] = bS[i+cur_end]*(1-cdf_true(cdf0, bS[i+cur_end], tthx[i+cur_end]))
      if (i+cur_end == 1){
        ser[i+cur_end] = er[i+cur_end]
        sber[i+cur_end] = ber[i+cur_end]
      }
      else {
        ser[i+cur_end] = ser[i-1+cur_end]+er[i+cur_end]
        sber[i+cur_end] = sber[i-1+cur_end]+ber[i+cur_end]
      }
    }
    
    # Estimating true theta0
    dat = data.frame(X = x1[(cur_end+1):(cur_end+explore_l),], y = B*y[(cur_end+1):(cur_end+explore_l)])
    glmfit = glm(y~.,data = dat)
    thetahat2 = coef(glmfit)
    thetahat = thetahat2[-1]
    thetahat[is.na(thetahat)] = 0
    #thetahat.set[ik,j] = sum(abs(thetahat-theta0))
    
    
    # UCB Phase
    exploit_l = subT - explore_l
    intv = ceiling(C2*exploit_l^gam) + 1 # prevent 0 value (+1)
    dis[j] = intv
    for (i in (explore_l+1):subT){
      if (i + cur_end > T){break}
      thx[i+cur_end] = sum(thetahat*x1[i+cur_end,])
    }
    
    # Inner UCB Algorithm
    me0 = rep(0,intv)
    ti0 = rep(0,intv)
    u1 = pmax
    u2 = sum(abs(thetahat))
    u = u1 + 2*u2
    ku = u/intv
    
    for (i in (explore_l+1):subT){
      if (i + cur_end > T){break}
      beta_t = CU*max(1,((lam*intv)^(1/2)/pmax+sqrt(2*log(exploit_l)+intv*log((lam*intv+(i-1)*pmax^(2))/(lam*intv))))^(2))
      cx = thx[i+cur_end]
      dex1 = max( (-cx+u2+ku/2)%/%ku+1, 0)
      dex2 = (u1-cx+u2+ku/2)%/%ku
      num = max(dex2 - dex1 + 1, 1)
      rma = (2*dex1-1)*ku/2 - u2 + cx
      if (i == 1){
        bc = round(runif(1,0.5,num+0.5))
      }
      if (i > 1){
        me = me0[dex1:dex2]
        ti = ti0[dex1:dex2]
        if (sum(ti==0, na.rm=TRUE)>0){
          bc = round(runif(1,0.5,sum(ti==0, na.rm=TRUE)+0.5))
          bc = which(ti == 0)[bc]
          if (length(bc) == 0) bc = Inf
        }
        if (sum(ti==0, na.rm=TRUE)==0){
          inde = rep(0,num)
          for (i1 in 1:num){
            inde[i1] = ((i1-1)*ku+rma)*(me[i1]+sqrt(beta_t/(lam+ti[i1])))
          }
          bc = which(inde == max(inde))
          bc = bc[sample(length(bc))[1]]
          if (length(bc) == 0) bc = Inf
        }
      }
      S[i+cur_end] = (bc-1)*ku+rma
      bS[i+cur_end] = maxi_true(cdf_true,cdf0,tthx[i+cur_end], name_flag)
      y[i+cur_end] = rbinom(1,1,1-cdf_true(cdf0, S[i+cur_end], tthx[i+cur_end]))
      r[i+cur_end] = S[i+cur_end]*y[i+cur_end]
      me0[dex1-1+bc] = (me0[dex1-1+bc]*(lam+ti0[dex1-1+bc])+S[i+cur_end]*r[i+cur_end])/(lam+ti0[dex1-1+bc]+(S[i+cur_end])^(2))
      ti0[dex1-1+bc] = ti0[dex1-1+bc] + (S[i+cur_end])^(2)
      er[i+cur_end] = S[i+cur_end]*(1-cdf_true(cdf0, S[i+cur_end], tthx[i+cur_end]))
      if (is.nan(er[i+cur_end])){er[i+cur_end] = 0}
      ber[i+cur_end] = bS[i+cur_end]*(1-cdf_true(cdf0, bS[i+cur_end], tthx[i+cur_end]))
      ser[i+cur_end] = ser[i+cur_end-1]+er[i+cur_end]
      sber[i+cur_end] = sber[i+cur_end-1]+ber[i+cur_end]
    }
    cur_end = cur_end + subT
  }
  ik = ik + 1
  lser = lser + ser
  lsber = lsber + sber
  llser[ik-1,] = ser
  llsber[ik-1,] = sber
  cumRev_real = cumsum(r)
  repl_cumRev_real[ik-1, ] = cumRev_real
  t2 = Sys.time()
  time_cost[ik-1] = difftime(t2, t1, units = "mins")
  # print time consumption of current iteration
  print(paste("Time consumption in minutes:", time_cost[ik-1]))
}
# calculate accumulative regret in each replication
llreg = llsber - llser
lsber = lsber/nk
lser = lser/nk
# calculated average accumulative regret
reg = lsber - lser
print(time_cost)

write.csv(repl_cumRev_real, sprintf("%s/cumRev_ExUCBReal_luo_%s.csv", save_dir, name_flag), row.names=FALSE)
write.csv(llser, sprintf("%s/cumRev_ExUCB_luo_%s.csv", save_dir, name_flag), row.names=FALSE)
write.csv(llsber, sprintf("%s/cumRev_opt_luo_%s.csv", save_dir, name_flag), row.names=FALSE)

