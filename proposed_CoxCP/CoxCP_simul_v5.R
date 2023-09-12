# episodic EG

require(icenReg)

## simulation setting
ini = unk.l0
PMIN = 0
PMAX = 12

dim = dm



## create p sequence for calculating p*
ngrid = 200
pseq = seq(from = PMIN, to = PMAX, length = ngrid)

## create stack variable for repl
opt_reg_iter_stack = matrix(NA, nrow = nrepl, TIME_HORIZON)
unk_reg_iter_stack = matrix(NA, nrow = nrepl, TIME_HORIZON)
unk_reg_iter_stack_div = matrix(NA, nrow = nrepl, TIME_HORIZON)

# oers : opt_expected_reward_stack
# uoers : unk_expected_reward_stack
# urrs : unk_real_reward_stack
oers = matrix(NA, nrow = nrepl, TIME_HORIZON)
uoers = matrix(NA, nrow = nrepl, TIME_HORIZON)
urrs = matrix(NA, nrow = nrepl, TIME_HORIZON)

func.Survival = function(pseq, theta, x_t){
  return(1 - cdf_true(cdf0, pseq, sum(x_t*theta)))
}

# create colname
unk_X_colname = list()
for (X_num in 1:dim){
  unk_X_colname = append(unk_X_colname,paste("X", X_num, sep = ""))
}


min.v <- function(x){  return(min(x,1-1e-8)) }

func.hazard.v = function(p_t){
  return(-log(1-unlist(lapply(cdf0(p_t), min.v))))
}


# likelihood function
beta.llk.v = function(theta, p, y, x){
  lk = sum( -y * func.hazard.v(p) * exp(x %*% theta) + (1-y) * log( 1 - unlist(lapply(exp(-func.hazard.v(p) * exp(x %*% theta)), min.v))) )
  return(-lk)
}


# gradient
beta.grad.v = function(theta, p, y, x){
  
  grad = apply( c(- y * func.hazard.v(p) * exp(x %*% theta)) * x + 
                  (1-y) * x * c((exp( -func.hazard.v(p) * exp(x %*% theta) + x %*% theta) * func.hazard.v(p) ) /( 1 - unlist(lapply(exp(-func.hazard.v(p) * exp(x %*% theta)), min.v)) )) , 2, sum)
  
  return(-grad)
}

# hessian
beta.hess.v = function(theta, p, y, x){
  
  if (dim == 1){sum_axis = 1}
  if (dim != 1){sum_axis = 2}
  outer.m = function(x){ return (x %o% x) }
  
  tmp1 = exp( -func.hazard.v(p) * exp(x %*% theta))
  tmp2 = exp(x %*% theta)
  hess = matrix(apply(c(-y * func.hazard.v(p) * tmp2) * t(apply(x, 1, outer.m)), sum_axis, sum) +
                  apply( c((1-y) * tmp1 * tmp2 * func.hazard.v(p) * (-func.hazard.v(p) * tmp2 + 1) * (1-tmp1)) * t(apply(x, 1, outer.m)), sum_axis, sum), nrow = dim)
  
  return(-hess)
}



for (iter in 1:nrepl){
  print(c('Current iteration: ', iter))
  
  # generate X
  X = gen_x(TIME_HORIZON, dm, seed=NULL) # matrix
  
  ## define episodes
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
  
  # stack varible for 1 iter
  opt_p_stack = opt_rew_stack = rep(NA, TIME_HORIZON) # optimal model stack
  unk_p_stack = unk_y_stack = unk_rew_stack = unk_rewreal_stack = rep(NA, TIME_HORIZON)  # unknown model stack

  # theta estimate stack for 1 iter
  unk_theta_stack = matrix(0, nrow = epi, ncol = dim)

  cur_end = 0
  cur_start = 1
  for (epis_curr in 1:epi){
    epis_num = sum(epis == epis_curr)
    print(sprintf("epis_curr: %s, epis_num : %s", epis_curr, epis_num))
    
    ## get price
    for (i in 1:epis_num){
      if (epis_curr == 1){
        unk_p_stack[i + cur_end] = runif(1,PMIN,PMAX)
        unk_y_stack[i + cur_end] = rbinom(1,1,1-cdf_true(cdf0, unk_p_stack[i+cur_end], sum(X[i + cur_end,]*theta0))) 
      } else {
        b_unk = rbinom(1,1, unk.alpha * 1/2**((epis_curr-1)/3))

        # unknown model
        if (b_unk == 1){
          unk_p_stack[i + cur_end] = runif(1,PMIN,PMAX)
          unk_y_stack[i + cur_end] = rbinom(1,1,1-cdf_true(cdf0, unk_p_stack[i+cur_end], sum(X[i + cur_end,]*theta0))) 
        } else{
          
          if (dim == 1) {newdat = data.frame(X[i + cur_end,])}
          if (dim != 1) {newdat = data.frame(matrix(X[i + cur_end,], nrow = 1))}
          
          colnames(newdat) = unk_X_colname
          
          tmp = X[i + cur_end] * unk_theta_stack[epis_curr - 1]
          if (covstr == "ph"){
            unk_expected_rewards = pseq * (1 - getFitEsts(ph_unk_fit, newdata = newdat, q = pseq))^exp(tmp)
          }
          if (covstr == "nocov"){
            unk_expected_rewards = pseq * (1 - getFitEsts(ph_unk_fit, newdata = newdat, q = pseq - tmp))
          }
          unk_p_stack[i + cur_end] = pseq[which.max(unk_expected_rewards)]
          unk_y_stack[i + cur_end] = rbinom(1,1,1-cdf_true(cdf0, unk_p_stack[i+cur_end], sum(X[i + cur_end,]*theta0))) 
        }
        
      }
      
      # optimal price
      opt_expected_rewards = pseq * func.Survival(pseq, theta0, X[i + cur_end,])
      opt_p_stack[i + cur_end] = pseq[which.max(opt_expected_rewards)]
      
      # expected reward
      unk_rewreal_stack[i + cur_end] = unk_p_stack[i + cur_end] * unk_y_stack[i + cur_end]
      opt_rew_stack[i + cur_end] = opt_p_stack[i + cur_end] * func.Survival(opt_p_stack[i + cur_end], theta0, X[i+cur_end,])
      unk_rew_stack[i + cur_end] = unk_p_stack[i + cur_end] * func.Survival(unk_p_stack[i + cur_end], theta0, X[i+cur_end,])
    } # end get p
    
    cur_end = cur_end + epis_num
    
    ## estimate theta
    
    # unknown model
    unk_l = ifelse(unk_y_stack[cur_start:cur_end], unk_p_stack[cur_start:cur_end], 0)
    unk_u = ifelse(!unk_y_stack[cur_start:cur_end], unk_p_stack[cur_start:cur_end], Inf)
    
    unk_data_cox = data.frame(l = unk_l, u = unk_u)
    X_data = data.frame(X[cur_start:cur_end,])
    colnames(X_data) = unk_X_colname
    unk_data_cox = cbind(unk_data_cox, X_data)
    
    ph_unk_fit = ic_sp(cbind(l,u) ~ . , data = unk_data_cox, model = 'ph')
    
    unk_theta_stack[epis_curr,] = matrix(ph_unk_fit$coef, nrow = 1)
    
    
    # set cur_start
    cur_start = cur_start + epis_num
    
  } # end 1 episode
  
  # stack value
  t = 1:TIME_HORIZON
  y1 = t^(2/3)

  unk_reg_iter_stack[iter,] = opt_rew_stack - unk_rew_stack
  unk_reg_iter_stack_div[iter,] = cumsum(opt_rew_stack - unk_rew_stack) / y1
  oers[iter, 1:TIME_HORIZON]  = opt_rew_stack
  uoers[iter, 1:TIME_HORIZON] = unk_rew_stack
  urrs[iter, 1:TIME_HORIZON] = unk_rewreal_stack

  cat("unknown model estimate: ", c(unk_theta_stack), "\n")
}

# save
if (tuning == FALSE){
  write.csv(oers, sprintf("%s/cumRev_unk_opt_coxph_%s.csv", save_dir, name_flag), row.names = FALSE)
  write.csv(uoers, sprintf("%s/cumRev_unk_coxph_%s.csv", save_dir, name_flag), row.names = FALSE)
}
if (tuning == TRUE){
  unk_rr_mean = rowMeans(apply(urrs, 1, cumsum)) # mean
  unk.cumRev_real = unk_rr_mean[length(unk_rr_mean)]
}

