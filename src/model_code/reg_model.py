"""
Use the nonlinear regression model to estimate result vectors and 
covariance matrix

"""

# Define the regression model in all cases (IRRA, CRRA, DRRA).

def reg_testh(x, a, m, h_est):
    """
    Regression model including the coefficient h.
    
    Args:
        x (np.ndarray): 1d array of size (wealth, loadings, h)
        a (float64): coefficient being estimated
        m (float64): coefficient being estimated
        h_est (float64): coefficient for testing
        
    Returns:
        Formular
    """
    w = x[0]
    lam = x[1]
    
    return a * w + m * ( lam * (w ** h_est))

def reg_model(x, a, m):
    """
    Regression model with known parameter h.
    
    Args:
        x (np.ndarray): 1d array of size (wealth, loadings, h)
        a (float64): coefficient being estimated
        m (float64): coefficient being estimated
        
    Returns:
        Formular ormular
    
    """
    w = x[0]
    lam = x[1]
    h = x[2]
    
    return a * w + m * ( lam * (w ** h))

# Generate the data matrices we need.

def gen_xy(data, h_test):
    """
    Generate the data matrices for regression (X and y).
    
    Args:
        data (pd.DataFrame): complete table with wealth/premiums/claims
        h_test (int): h = h_test? interest in 1 
                      (saved in **values_in_interest.json**)
        
    Returns:
        ydata (dict): premiums/claims data
        xdata (np.ndarray): 2d array of size ((wealth, loadings, h), years)
        
    """
    data['loadings'] = (data['Premiums'] / data['Claims']) - 1
    data['h'] = h_test
    
    xdata = data[['Wealth', 'loadings', 'h']].values.T
    ydata = data[['Premiums', 'Claims']].to_dict('list')
    
    return ydata, xdata

