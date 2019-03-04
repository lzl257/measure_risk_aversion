"""
Plot temporary and final data for illustration.

"""
import sys
import pandas as pd
import matplotlib.pyplot as plt

from bld.project_paths import project_paths_join as ppj

    
def save_final(data_name):
    """
    Generate the final premiums and claims table.
    Args:
        data_name (str): name of the table
    
    """
    fig = pd.read_csv(ppj('OUT_DATA', '{}.csv'.format(data_name)))
   
    plt.plot(fig['Year'], fig['Premiums'], linestyle='-', 
             marker='^', linewidth=1)
    plt.plot(fig['Year'], fig['Claims'], linestyle='-', 
             marker='.', linewidth=1)
    plt.xticks(fig['Year'].tolist(), rotation='vertical')
    plt.legend(loc='upper left')
    plt.savefig(ppj('OUT_FIGURES', 'fig_{}.png'.format(data_name)))
    plt.show()

 
if __name__ == '__main__':
    
    data_name = sys.argv[1]
    save_final(data_name)