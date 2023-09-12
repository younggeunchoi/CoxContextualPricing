###################Function classes of kernels and their derivatives#################

import numpy as np

class Kernel:
    def __init__(self,v_i,y_t,n):
        self.v_i = np.array(v_i)
        self.y_t = np.array(y_t)
        # v_i and y_t should have the same length
        #global v_i
        #global y_t
        self.n = np.array(n)
        self.h = np.array(4*n**(-1/5))

    def sec_kernel_h(self,t):
        vec = self.kernel((self.v_i.reshape(-1,1) - np.array(t).reshape(1,-1) )/self.h)
        # vec: shape of (len of v_i, len of t)
        # return shape should be the same with the length of t
        return 1/(self.n*self.h) * np.sum(vec * self.y_t.reshape(-1,1), axis=0)
    
    def sec_kernel_f(self,t):
        vec = self.kernel((self.v_i.reshape(-1,1) - np.array(t).reshape(1,-1) )/self.h)
        return 1/(self.n*self.h) * np.sum(vec, axis=0)
    
    def sec_kernel_h1(self,t):
        vec = self.kernel2((self.v_i.reshape(-1,1) - np.array(t).reshape(1,-1) )/self.h)
        return -1/(self.n*self.h**2) * np.sum(vec * self.y_t.reshape(-1,1), axis=0)
    
    def sec_kernel_f1(self,t):
        vec=self.kernel2((self.v_i.reshape(-1,1) - np.array(t).reshape(1,-1) )/self.h)
        return -1/(self.n*self.h**2) * np.sum(vec, axis=0)
    
    def sec_kernel_h2(self,t):
        vec=self.kernel3((self.v_i.reshape(-1,1) - np.array(t).reshape(1,-1) )/self.h)
        return 1/(self.n*self.h**3) * np.sum(vec * self.y_t.reshape(-1,1), axis=0)
    def sec_kernel_f2(self,t):
        vec=self.kernel3((self.v_i.reshape(-1,1) - np.array(t).reshape(1,-1) )/self.h)
        return 1/(self.n*self.h**3) * np.sum(vec, axis=0)
    
    def kernel(self, x):
        return (1-x**2)**5*((abs(x)<=1)*1)

    def kernel2(self, x):
        return -5*(1-x**2)**4*2*x*((abs(x)<=1)*1)

    def kernel3(self, x):
        return -5*(1-x**2)**3*(2-18*x**2)*((abs(x)<=1)*1)
        
    def sec_kernel_whole1(self,t):
        return self.sec_kernel_h(t)/self.sec_kernel_f(t)

    # custom addition
    def cdf0_est(self,t):
        return 1 - self.sec_kernel_whole1(t)    
    def cdf_est(self, t, thetax):
        return self.cdf0_est(t - thetax)
    def maxi_est(self, thetax, low, upp):
        # tomi(x) = x * (1- F(x))
        def tomi(x):
            return(x * (1 - self.cdf_est(x, thetax)))
        p_grid = np.arange(low, upp+0.01, 0.01)
        #ind_max = np.argmax( [ tomi(p_grid[i]) for i in range(len(p_grid)) ]   )
        ind_max = np.argmax( tomi(p_grid) )
        p_opt = p_grid[ind_max]
        return(p_opt)
    
    def sec_kernel_whole2(self,t):
        return (self.sec_kernel_h1(t)*self.sec_kernel_f(t)-self.sec_kernel_h(t)*self.sec_kernel_f1(t))/self.sec_kernel_f(t)**2
    
    def sec_kernel_whole3(self,t):
        kh1=self.sec_kernel_h1(t)
        kf0=self.sec_kernel_f(t)
        kh0=self.sec_kernel_h(t)
        kf1=self.sec_kernel_f1(t)
        kh2=self.sec_kernel_h2(t)
        kf2=self.sec_kernel_f2(t)
        
        return ((kh1*kf0)**2-(kh0*kf1)**2-kh0*kh2*kf0**2+kh0**2*kf0*kf2)/(kh1*kf0-kh0*kf1)**2
    
    def phi(self,t,thetax):
        return t+self.sec_kernel_whole1(t)/self.sec_kernel_whole2(t)+thetax
    
    def phi_p(self,t): 
        return 1+self.sec_kernel_whole3(t)