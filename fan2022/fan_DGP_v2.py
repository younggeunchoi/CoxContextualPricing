import numpy as np
import scipy
from scipy.stats import truncnorm
 

# # Construct cdf0 F0 (cdf of the baseline error)
trun_min = 1 #trun = 15
trun_mid = 4
trun_max = 10


def cdf0_twomode(x):
    # x can be vector-valued input
    # y outputs cdf0(x) pointwise    
    y = np.ones_like(x, dtype='float')
    y[x <= trun_min] = 0
    y[(x > trun_min) & (x <= trun_mid)] = \
        0.5 * (x[(x > trun_min) & (x <= trun_mid)] - trun_min) / (trun_mid - trun_min)
    y[(x > trun_mid) & (x <= trun_max)] = \
        0.5 +  0.5 * ((x[(x > trun_mid) & (x <= trun_max)] - trun_mid) / (trun_max - trun_mid))
    return(y)
#cdf0_twomode(np.arange(0,11)) #ok


def cdf0_tnorm1(x, sd=0.1):
    trun_mid = 5.5
    p1 = truncnorm.cdf(x, a=trun_min, b=trun_max, \
      loc = (trun_min + trun_mid) / 2, scale=sd)
    p2 = truncnorm.cdf(x, a=trun_min, b=trun_max, \
      loc = (trun_mid + trun_max) / 2, scale=sd)
    return( 0.75*p1 + 0.25*p2 )
cdf0_tnorm2 = lambda x: cdf0_tnorm1(x, sd=0.5)
cdf0_tnorm1(np.arange(12))
cdf0_tnorm2(np.arange(12))



def gen_x_unif(n, d, seed=None):
    radius = 1/2
    # First generate random directions by normalizing the length of a
    # vector of random-normal values (these distribute evenly on ball).
    np.random.seed(seed)
    random_directions = np.random.normal(size=(n,d))
    random_directions /= np.sqrt(np.sum(random_directions**2, axis=1, keepdims=True))
    # Second generate a random radius with probability proportional to
    # the surface area of a ball with a given radius.
    random_radii = np.random.uniform(size=(n,1)) ** (1/d)
    # Return the list of random (direction & length) points.
    x = radius * (random_directions * random_radii)
    if (d == 1):
        x = x.reshape(-1)
    return x
# x = gen_x_unif(1000, 2)
# np.mean(x**2, axis=0) # ok


def gen_x_t(n, d, seed=None):
    radius = 1/2
    np.random.seed(seed)
    x = np.random.standard_t(df=3,\
        size=(n,d)) * radius / np.sqrt((d+2)*3)
    if d == 1:
        x = x.reshape(-1)
    return x
# x = gen_x_t(1000,2)
# np.mean(x**2, axis=0) #ok


def cdf_lin(cdf0, u, t):
    # cdf0: baseline cdf
    # u: input part
    # t: x^T theta part
    return( cdf0(u - t) )    

def cdf_ph(cdf0, u, t):
    # cdf0: baseline cdf
    # u: input part
    # t: x^T theta part
    return( 1 - np.array(1 - cdf0(u)) ** np.exp(t) )    


# Construct Optimal Price Function g that matches x^{\top}\theta_{0} to optimal price
def maxi_true(cdf_true, cdf0, t, name_flag="", low=trun_min - 1, upp=trun_max + 1):
    # tomi(x) = x * (1- F(x))
    def tomi(x):
        return(x * (1 - cdf_true(cdf0, x, t)))
    p_grid = np.arange(low, upp+0.01, 0.01)
    ind_max = np.argmax(tomi(p_grid))
    p_opt = p_grid[ind_max]
    #rev_opt = tomi(p_opt)
    #return(p_opt, rev_opt)
    return(p_opt)
