

require(truncnorm)  # for the truncated normal distribution
require(mvtnorm) # for multivariate normal and t distributions

# Construct cdf0 F0 (cdf of the baseline error)
trun_min = 1 #trun = 15
trun_mid = 4
trun_max = 10
cdf0_twomode = function(x){
  # x can be vector-valued input
  # y outputs cdf0(x) pointwise
  y = rep(1, length(x))
  y[x <= trun_min] = 0
  y[(x > trun_min) & (x <= trun_mid)] = 
    0.5 * (x[(x > trun_min) & (x <= trun_mid)] - trun_min) / (trun_mid - trun_min)
  y[(x > trun_mid) & (x <= trun_max)] = 
    0.5 +  0.5 * ((x[(x > trun_mid) & (x <= trun_max)] - trun_mid) / (trun_max - trun_mid))
  return(y)
}
# cdf0_twomode(0:11)

cdf0_tnorm1 = function(x, sd=0.1) {
  trun_mid = 5.5
  p1 = ptruncnorm(x, a = trun_min, b = trun_max, mean = (trun_min + trun_mid) / 2, sd = sd)
  p2 = ptruncnorm(x, a = trun_min, b = trun_max, mean = (trun_mid + trun_max) / 2, sd = sd)
  return( 0.75*p1 + 0.25*p2 )
}
cdf0_tnorm2 = function(x, sd=0.5) {
  return(cdf0_tnorm1(x, sd=0.5))
}



## generate covariate X
gen_x_unif= function(n, d, seed=NULL) {
  radius = 1/2
  set.seed(seed)
  # First generate random directions by normalizing the length of a
  # vector of random-normal values (these distribute evenly on ball).
  random_directions = matrix(rnorm(n*d), nrow=n, ncol=d)   # n by 1
  random_directions = random_directions / sqrt(rowSums(random_directions^2))
  # Second generate a random radius with probability proportional to
  # the surface area of a ball with a given radius.
  random_radii = runif(n)^(1/d)  # n by 1
  # Return the list of random (direction & length) points.
  return( radius * (random_directions * random_radii) )
}
#x = gen_x_unif(1000,1)
#mean(rowSums(x^2))
#plot(x) # ok
gen_x_t = function(n, d, seed=NULL) {
  radius = 1/2 # make the variances equal across unif, t
  set.seed(seed)
  x = rmvt(n=n, df=3, sigma=diag(d)*radius^2/(d+2) / 3) 
  return(x)
}
#x = gen_x_t(1000,1)
#mean(rowSums(x^2))
#plot(x) # ok


cdf_lin = function(cdf0, u, v) {
  # cdf0: baseline cdf
  # u: input part
  # v: x^T theta part
  return( cdf0(u - v) )
}
cdf_ph = function(cdf0, u, v) {
  # cdf0: baseline cdf
  # u: input part
  # v: x^T theta part
  return( 1 - (1 - cdf0(u))^(exp(v)) )
}

# Construct Optimal Price Function g that matches x^{\top}\theta_{0} to optimal price
maxi_true = function(cdf_true, cdf0, v, name_flag="", low=trun_min-1, upp=trun_max+1){
  # tomi(x) = x * (1- F0(x))^{exp(v)}, where v will be x^T \theta_0
  tomi = function(x) return(x * (1 - cdf_true(cdf0, x, v)))
  # may need a fine-grided initial value
  p_grid = seq(from=low, to=upp, length=100)
  ind_max = which.max(tomi(p_grid))
  rough_init = p_grid[ind_max]
  s = optim(par = rough_init, tomi, method = c("L-BFGS-B"), lower = low, upper = upp, control = list(fnscale = -1))
  y = s$par
  return(y) 
}
