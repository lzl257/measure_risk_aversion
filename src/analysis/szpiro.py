"""
Obtain the regression results and generate reports for ``szpiro_table`` and 
``recent_table``. Furthermore save the crucial results to **bld/out/tables** to 
generate the table in **src/paper/research_paper.tex**.

"""
import sys
import json
import numpy as np
import pandas as pd

from scipy.stats.distributions import t
from scipy.optimize import curve_fit
from src.model_code.reg_model import gen_xy, reg_testh, reg_model
from bld.project_paths import project_paths_join as ppj


# Szpiro (1986)

def szp(testh_model, data_name, initial_test, h_test, level):
    """
    First check if h equals to unity (i.e. CRRA assumption satisfied).
    Function for reporting the regression reults using premiums and claims
    data respectively: estimators / t-values / R-square / relative risk aversion 
    and corresponding confidence bond. Reports are generated in **bld/out/analysis** 
    
    Args:
        testh_model (function): regression model for testing h
        data_name (str): name of tables (see **wscript** file)
        initial_test (list): initial vectors for estimating h
        h_test (int): h = h_test? interest in 1 
                      (saved in **values_in_interest.json.json**)
        level (float64): ((1 - level)*100)% is significant level.
    
    Returns:
        c (np.ndarray): 1d array of size (c_p, c_q)
        reg (list): regression results
        rep (dict): result dictionary for generating reports
    """
    c = []
    reg=[]
    rep={}
    data = pd.read_csv(ppj('OUT_DATA', '{}.csv'.format(data_name)))
    y, x = gen_xy(data, h_test)
    t_stat = t.ppf(1 - level / 2, 21 - 3)
    rep['htest'] = h_test
    rep['tstat'] = t_stat
    for key, data in y.items():
        popt_test, pcov_test = curve_fit(testh_model, x, np.array(data), initial_test, maxfev=2000)
        h_hat = popt_test[2]
        h_var = pcov_test[2,2]
        t_h0 = (h_hat - h_test) / np.sqrt(h_var)
        rep['{}_hhat'.format(key)] = h_hat
        rep['{}_th0'.format(key)] = t_h0
        if np.absolute(t_h0) < t_stat:
            popt, pcov = curve_fit(reg_model, x, np.array(data), maxfev=2000)
            a_hat = popt[0]
            m_hat = popt[1]
            sigma_a = pcov[0,0] ** 0.5
            sigma_m = pcov[1,1] ** 0.5
            
            # t-values of the estimated coefficient
            
            t_a = (a_hat / sigma_a).round(1)
            t_m = (m_hat / sigma_m).round(1)
            
            # R-sqaure
            
            predictions = np.array([testh_model(i, a_hat, m_hat, h_test) for i in x.T])
            residuals = predictions - np.array(data)
            Rsquare = 1 - np.var(residuals) / np.var(np.array(data))
            
            # Record regression results.
            
            reg.extend([a_hat, t_a, m_hat, t_m, Rsquare])
            
            rep['{}_ahat'.format(key)] = a_hat
            rep['{}_ta'.format(key)] = t_a
            rep['{}_mhat'.format(key)] = m_hat
            rep['{}_tm'.format(key)] = t_m
            rep['{}_RS'.format(key)] = Rsquare
            # Whther we can use the formula of c
            
            if h_test == 1:
                rra = - a_hat / m_hat
                lowerbound = - (a_hat + sigma_a) / (m_hat - sigma_m)
                upperbound = - (a_hat - sigma_a) / (m_hat + sigma_m)              
                c.append(rra)
            else:
                upperbound = lowerbound = rra = 'no values'
                c.append(np.nan)
            
            rep['{}_rra'.format(key)] = rra
            rep['{}_lb'.format(key)] = lowerbound
            rep['{}_ub'.format(key)] = upperbound
        
            
        else:
            
            c.append(np.nan)
            reg.extend([np.nan]*5)
            

    
    return np.array(c), reg, rep


def save_report(rep_dict, data_name, h_test, level):
    """
    Save the reports in text files.
    
    Args:
        rep_dict (dict): regression results to be reported.
        data_name (str): name of tables (see **wscript** file)
        h_test (int): h = h_test? interest in 1 
                      (saved in **values_in_interest.json.json**)
        level (float64): ((1 - level)*100)% is significant level.
        
    """
    data = pd.read_csv(ppj('OUT_DATA', '{}.csv'.format(data_name)))
    y, x = gen_xy(data, h_test)
    
    with open(ppj('OUT_ANALYSIS', 'report_{}.txt'.format(data_name)), 'w') as text:
        for key, data in y.items():
            if np.absolute(rep_dict['{}_th0'.format(key)]) < rep_dict['tstat']:
                text.write(
                            'For {} ({}):\n'
                            'h = {} is not significantly different from {}, '
                            'with t-value {}({}) given significant level {}%.\n'
                            '1st estimator is {} (t={})\n2nd estimator is {} (t={})\n'
                            'R^2 is {}\n'
                            'c_p = {}\n'
                            '{} <= c_p <= {} (confidence band)\n'
                            '\n'
                            .format(data_name, 
                                    key,
                                    rep_dict['{}_hhat'.format(key)], 
                                    rep_dict['htest'], 
                                    rep_dict['{}_th0'.format(key)].round(4), 
                                    rep_dict['tstat'].round(2), 
                                    int((1-level) * 100),
                                    rep_dict['{}_ahat'.format(key)].round(6), 
                                    rep_dict['{}_ta'.format(key)], 
                                    rep_dict['{}_mhat'.format(key)].round(6), 
                                    rep_dict['{}_tm'.format(key)],
                                    rep_dict['{}_RS'.format(key)],
                                    rep_dict['{}_rra'.format(key)],
                                    rep_dict['{}_lb'.format(key)], 
                                    rep_dict['{}_ub'.format(key)])
                            )
                            
            else:
                text.write(
                        'For {} ({}):\n'
                        'h = {} is likely not {} with the t-value {} ({})\n'
                        '\n'
                        .format(data_name, 
                                key,
                                rep_dict['{}_hhat'.format(key)], 
                                rep_dict['htest'], 
                                rep_dict['{}_th0'.format(key)].round(4), 
                                rep_dict['tstat'].round(2)
                                )
                        )


def save_reg(reg_list, data_name):
    """
    Save the regression results for premiums and claims data, respectively.
    
    Args:
        reg_list (list): a list consisting of the results of all regressions
        data_name (str): name of tables (see **wscript** file)
        
    """
    for idx in [0, 2, 5, 7]:
        reg_list[idx] = round(reg_list[idx], 6)
    for idx in [4, 9]:
        reg_list[idx] = round(reg_list[idx], 3)
        
    result_df = pd.DataFrame(reg_list, columns=['results']).T
    result_df.columns = ['a', 'ta', 'm', 'tm', 'Rsp', 'b', 'tb', 'n', 'tn', 'Rsq']
    result_df.index.name = 'type'
    dfs = np.split(result_df, [5], axis=1)
    reg_p = dfs[0].T.rename(columns={'results': 'Premiums Data'}).T
    reg_q = dfs[1].T.rename(columns={'results': 'Claims Data'}).T
    
    reg_p.to_csv(ppj('OUT_TABLES', '{}_prem_reg.csv'.format(data_name)), 
                 index=True, sep=',')
    reg_q.to_csv(ppj('OUT_TABLES', '{}_clam_reg.csv'.format(data_name)), 
                 index=True, sep=',')


if __name__ == "__main__":

    spec = json.load(open(ppj('IN_MODEL_SPECS', 'values_in_interest.json'), encoding='utf-8'))
    data_name = sys.argv[1]
    
    reg_results = szp(reg_testh, data_name, **spec)[1]
    rep = szp(reg_testh, data_name, **spec)[2]
    h_test = spec['h_test']
    level = spec['level']
    
    save_report(rep, data_name, h_test, level)
    save_reg(reg_results, data_name)
        

    