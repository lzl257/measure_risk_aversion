"""Draw the 3D criterion function."""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from pylab import meshgrid

from src.model_code.reg_model import gen_xy
from bld.project_paths import project_paths_join as ppj


def _cri_fun(a, m, h_test):
    """
    Criterion function, i.e. sum of squared error (premiums).

    Args:
        a (float64): coefficient being estimated

        m (float64): coefficient being estimated

        h_test (int): h = h_test? interest in 1
        (saved in **values_in_interest.json**)

    Returns:
        Function formular

    """
    data = pd.read_csv(ppj('OUT_DATA', 'szpiro_table.csv'))
    y, x = gen_xy(data, h_test)
    prems = np.array(y['Premiums'])

    w = x[0]
    lam = x[1]
    h = x[2]
    q = a * w + m * (lam * (w ** h))

    return np.sum((prems - q) ** 2)


def draw_cri():
    """Plot the 3D SSR in the range of (-0.01, 0.01) with grid of 0.001."""
    a_grid = np.arange(-0.01, 0.01, 0.001)
    m_grid = np.arange(-0.01, 0.01, 0.001)
    A, M = meshgrid(a_grid, m_grid)
    grid_num = A.shape[0]

    z = []
    for i in range(grid_num):
        for j in range(grid_num):
            z.append(_cri_fun(A[i, j], M[i, j], h_test))

    z = np.array(z).reshape((grid_num, grid_num))

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(A, M, z, rstride=1, cstride=1, cmap=cm.RdYlBu,
                           linewidth=0, antialiased=False)
    fig.colorbar(surf, shrink=0.5, aspect=4.5)
    plt.savefig(ppj('OUT_FIGURES', 'cri_fun_crra.png'))
    plt.show()


if __name__ == '__main__':

    spec = json.load(
        open(
            ppj('IN_MODEL_SPECS', 'values_in_interest.json'), encoding='utf-8')
    )
    h_test = spec['h_test']
    draw_cri()
