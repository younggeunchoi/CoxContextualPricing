# Semi-Parametric Contextual Pricing Algorithm using Cox Proportional Hazards Model

This repository provides the source codes to reproduce the main experiments of the ICML2023 accepted paper, 'Semi-Parametric Contextual Pricing Algorithm using Cox Proportional Hazards Model'. 

The codes are grouped into four directories: "proposed_CoxCP", "luo2022_ExUCB", "fan2022", and "shah2019_DEEPC", with the first two containing R files and the last two Python files. 
Below, we provide a brief explanation of the purpose and instructions for running each files.

###  1. "./proposed_CoxCP" directory (our proposed algorithm)

#### CoxCP_main_v5.R

This file conducts hyperparameter tuning across all combinations of baseline cdf $F_0$, choice of true parameter $\beta$, and distribution of $X_t$. The tuning results are then saved in a .csv file. Subsequently, it executes `CoxCP_simul_v5.R`, employing the optimal hyperparameter.

#### CoxCP_simul_v5.R

The reward used for hyperparameter tuning is stored in `urrs`. Both optimal expected reward and expected reward acquired via the proposed algorithm (CoxCP) are retained in `oers` and `uoers`, respectively. It then writes these results into .csv files.

#### Execution Guide:
 
Run the main R file: `CoxCP_main_v5.R`.


### 2. "./luo2022_ExUCB" directory

#### luo_main_v4.R

Analogous to 'CoxCP_main_v5.R', this file performs hyperparameter tuning for all combinations of baseline cdf $F_0$, choice of true parameter $\beta$, and distribution of $X_t$, saving the tuning result in a .csv file. Then, it executes `luo_simul_v4.R` using the optimal hyperparameter.

#### luo_simul_v4.R

This R script carries out the algorithm suggested by Luo et al.(2022).
It operates separately during the exploration and UCB phases. The cumulative reward used for hyperparameter tuning is saved in `repl_cumRev_real`. Optimal Expected cumulative reward and expected cumulative reward acquired via the ExUCB are stored in `llsber` and `llser`. These results are then written to .csv files.

#### luo_DGP_v2.R

This file contains the implementation of baseline cdfs $F_0$, choice of true parameter $\beta$, and the methods of generating $x_t$. Functions in this file are shared with CoxCP.


The options that can be selected for each argument and the meaning of each option are as follows.

- baseline cdfs $F_0$
  - `twomode`: baseline distribution $F_0$ is $\frac{1}{2} U[1,4] + \frac{1}{2} U[4,10]$. 
  - `tnorm2`: baseline distribution $F_0$ is $\frac{3}{4} TN(3.25, 0.5^2, 1, 10) + \frac{1}{4} TN(7.75, 0.5^2, 1, 10)$.
- choice of true parameter $\beta$
  - `nocov`: true parameter $\beta = 0_d$.
  - `ph`: true parameter $\beta = \frac{4}{\sqrt{d}}1_d$.
- distribution of $X_t$
  - `unif`: $X_t$ follows a uniform distribution on $d$-dimensional ball with radius $\frac{1}{2}$.
  - `t`: $X_t$ follows a multivariate $t$-distribution with the degree of freedom as 3 and the scale parameter as $\frac{1}{4 \cdot 3 (d + 2)}I_{d \times d}$.

#### Execution Guide:

Run the main R file: `luo_main_v4.R`.


### 3. "./fan2022" directory
   
#### fan_main_v8.py

This Python script parses a command line argument, considering inputs related to replication index, true parameter, baseline cdf, covariate effect, distribution of $X_t$, total horizons, tuning horizons, hyperparameter tuning necessity, and the name of the saving directory. 

After conducting the hyperparameter tuning process, similar to CoxCP, the script `fan_simul_v7.py` is executed with the optimal hyperparameters.


#### fan_scriptGenerate_v1.py

This script produces command-line executable scripts. It provides combinations of baseline cdf $F_0$, choice of true parameter $\beta$, and distribution of $X_t$. Selectable options are the same as those mentioned in `luo_DGP_v2.R`.

#### fan_simul_v7.py

This Python script carries out the algorithm suggested by Fan et al.(2022). It operates separately during the exploration and exploitation phases. The cumulative reward used for hyperparameter tuning is saved in `rwd_T_fanReal`. Optimal Expected cumulative reward and expeced cumulative reward acquired via the algorithm are stroed in `rwd_T_opt` and `rwd_T_fan`. These results are then written to 'cumRev_opt_fan_*.csv', 'cumRev_fan_fan_*.csv', and 'cumRev_fanReal_*.csv', respectively.


#### fan_functions_v2.py

This script includes a class encapsulating necessary kernel functions for baseline cdf estimation via kernel smoothing.

#### fan_DGP_v2.py

This Python file houses the implementation of baseline cdfs $F_0$, choice of true parameter $\beta$, and the methods of generating $x_t$.


#### Execution Guide:

Run the script below in the './fan2022' folder.

```
python fan_main_v8.py --repl0 1 --repl1 5 --dim 5 --baseline twomode --cov nocov --xdist unif --horizon 30000 --tuninghorizon 3000 --savedir fan_expr --istuning 0
```

**repl0** : replication index (start),  
**repl1** : replication index (end),   
**baseline** : type of baseline cdf,   
**cov** : choice of true parameter $\beta$,  
**xdist** : distribution of $X_t$,     
**horizon** : length of total horizons,   
**tuninghorizon** : length of tuning horizons,
**epinum** : number of episodes,
**savedir** : name of saving directory,   
**istuning** : tuning necessity. (0: no tuning, 1: tuning)

<br/>

### 4. "./shah2019_DEEPC" directory

#### shah_main_v5.py

This Python script parses a command line argument, considering inputs related to replication index, true parameter, baseline cdf, covariate effect, distribution of $X_t$, total horizons, tuning horizons, hyperparameter tuning necessity, the name of the saving directory, and degree of exploration gamma. 

After conducting the hyperparameter tuning process, similar to CoxCP, the script `shah_simul_v4.py` is executed with the optimal hyperparameters.


#### shah_scriptGenerate_v1.py

This script produces command-line executable scripts. It provides combinations of baseline cdf $F_0$, choice of true parameter $\beta$, and distribution of $X_t$. Selectable options are the same as those mentioned in `luo_DGP_v2.R`.

#### shah_simul_v4.py

This Python script carries out the algorithm suggested by Shah et al.(2019).
The cumulative reward used for hyperparameter tuning is saved in `rwd_T_shahReal`. Optimal Expected cumulative reward and expeced cumulative reward acquired via the algorithm are stroed in `rwd_T_opt` and `rwd_T_shah`. These results are then written to 'cumRev_opt_shah_*.csv', 'cumRev_shah_shah_*.csv', and 'cumRev_shahReal_*.csv', respectively.


#### Execution Guide:

Run the script below in the './shah2019_DEEPC' folder.

```
python shah_main_v5.py --repl0 1 --repl1 5 --dim 5 --baseline twomode --cov nocov --xdist unif --horizon 30000 --savedir shah_expr --istuning 1 --tuninghorizon 3000
```

**repl0** : replication index (start),
**repl1** : replication index (end),   
**baseline** : type of baseline cdf,  
**cov** : choice of true parameter $\beta$,  
**xdist** : distribution of x,    
**horizon** : number of total horizon,   
**savedir** : name of saving directory,   
**istuning** : tuning necessity. (0: no tuning, 1: tuning),
**tuninghorizon** : number of tuning horizon    




