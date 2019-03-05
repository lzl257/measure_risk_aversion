"""
Process the raw data to generate the tables we will use to..

implement the estimation.
"""

import numpy as np
import pandas as pd

from bld.project_paths import project_paths_join as ppj


# Prepare the original dataset.

raw_dict = {}
for dataset in 'pop_9314', 'pop_1517', 'gross_claims', 'gross_premiums', \
        'hhl_finworth', 'cpi_oecd', 'paper_table':
    raw_dict[dataset] = pd.read_csv(ppj('IN_DATA', '{}.csv'.format(dataset)))

earliest = min(np.unique(raw_dict['pop_9314']['TIME'].values))
before_miss_year = 2002


# Process the population data.

def pop_data():
    """
    Select the population data which we will use to calculate the per capita..

    based values.

    """
    pop_raw1 = raw_dict['pop_9314']
    pop_raw2 = raw_dict['pop_1517']

    pop_filoc = pop_raw1[pop_raw1['LOCATION'].str.contains('USA')]
    pop_filsb = pop_filoc[
        (pop_filoc['Subject'].str.contains('Population mid-year estimates Total')) &
        (pop_filoc['Subject'].str.contains('growth') == False)
    ].reset_index(drop=True)
    pop_tv = pop_filsb[['TIME', 'Value']]
    pop_tv['Value'] = pop_tv['Value'].apply(lambda x: x * 1000)
    pop_9314 = pop_tv.rename(columns={'TIME': 'Year', 'Value': 'Population'})

    pop_raw2['Value'] = pop_raw2['Value'].apply(lambda x: x * 1000)
    pop_1517 = pop_raw2.rename(columns={'TIME': 'Year', 'Value': 'Population'})

    final_pop = pd.merge(pop_9314, pop_1517, how='outer')

    return final_pop

# Process the premiums data.


def premiums_data():
    """
    Generate the premiums table.

    Returns:
        final_prem (pd.DataFrame)

    """
    prem_raw = raw_dict['gross_premiums']
    prem_fil = prem_raw[prem_raw['LOCATION'].str.contains('USA')]
    [['TIME', 'Value']]
    prem_fil['Value'] = prem_fil['Value'] * 1e6
    final_prem = prem_fil.rename(
        columns={'TIME': 'Year', 'Value': 'Premiums'}).reset_index(drop=True)

    return final_prem

# Process the claims data.


def _clam_fil():
    """
    Filter out the redundant claims data.

    Returns:
        known_clam (pd.DataFrame): claims table we have known

    """
    clam_raw = raw_dict['gross_claims']
    clam_fil = clam_raw[clam_raw['COU'].str.contains('USA') &
                        clam_raw['ITYP'].str.contains('TOT') &
                        clam_raw['OWN'].str.contains('TOT') &
                        clam_raw['Unit Code'].str.contains('USD') &
                        clam_raw['DB_RA'].str.contains('Total') &
                        clam_raw['Currency'].str.contains('US Dollars')
                        ][['Year', 'Value']].reset_index(drop=True)
    known_clam = clam_fil.rename(columns={'Value': 'Claims (mild)'})

    return known_clam


def _known_growth(clam_table):
    """
    Goal: use the mean annual growth rate we have known during the year..

    2002-2017 to roughly complement the missing values (1993-2001).

    Args:
        clam_table (pd.DataFrame): known clean gross claims table.

    Returns:
        mean_growth (float64)

    """
    growth_claims = []
    gclaims_list = clam_table['Claims (mild)'].tolist()
    for i in range(len(gclaims_list) - 1):
        growth_claims.append(
            (gclaims_list[i + 1] - gclaims_list[i]) / gclaims_list[i])

    outliers = [max(growth_claims), min(growth_claims)]

    for i in outliers:
        growth_claims.remove(i)

    mean_growth = np.mean(np.array(growth_claims))

    return mean_growth


def _guess_clam(clam_table, growth_mean):
    """
    Generate the guessed claims during the year 1993-2001.

    Args:
        clam_table (pd.DataFrame): known clean gross claims table

        growth_mean (float64): mean growth rate of claims during 2002-2017

    Returns:
        guess_claims (list): guessed results

    """
    guess_claims = []
    guess_claims.append(clam_table['Claims (mild)'].tolist()[0])

    for i in range(before_miss_year - earliest):
        guess_claims.append((guess_claims[i] / (1 + growth_mean)))

    guess_claims.reverse()
    guess_claims = guess_claims[:-1]

    return guess_claims


def _outlier_clam(clam_table, guessed_claims):
    """
    Generate the claims and premiums tables in dollars with claim outlier.

    Args:
        clam_table (pd.DataFrame): known clean gross claims table

        guessed_claims (list): guessed claims based on the known growth rate

    Returns:
        outlier_claims (pd.DataFrame): claims table with outlier

    """
    year_before = []

    for i in range(earliest, before_miss_year):
        year_before.append(i)

    clam_dict = {'Year': year_before, 'Claims (mild)': guessed_claims}
    clam_df = pd.DataFrame(clam_dict).round(2)

    only_claims = pd.merge(clam_df, clam_table, how='outer')

    only_claims['Claims'] = only_claims['Claims (mild)'] * 1e6
    only_claims = only_claims.drop(columns=['Claims (mild)'])

    only_prems = premiums_data()
    outlier_claims = pd.merge(only_claims, only_prems)

    return outlier_claims


def _merge_clam(clam_table, guessed_claims):
    """
    There is an outlier in the data (2011). The sharp rising of claims is..

    due to the serious earthquake in the U.S. in 2011. So we replace it by

    the mean of claims in 2010 and 2012. You can find the figure in the

    presentation sildes.

    Get rid of the outlier

    Args:
        clam_table (pd.DataFrame): known clean gross claims table

        guessed_claims (list): guessed claims based on the known growth rate

    Returns:
        final_claims (pd.DataFrame):
        final claims table after replacing the outlier

    """
    final_claims = _outlier_clam(clam_table, guessed_claims)
    adjust_claims = np.mean(final_claims[
        (final_claims['Year'] == 2010) | (final_claims['Year'] == 2012)
    ].iloc[:, 1].values)
    final_claims.iloc[18, 1] = adjust_claims

    return final_claims


def claims_data():
    """
    Generate the final claims data.

    Returns:
        final_table (pd.DataFrame)

    """
    known_table = _clam_fil()
    known_growth = _known_growth(known_table)
    guessed_table = _guess_clam(known_table, known_growth)
    final_table = _merge_clam(known_table, guessed_table)

    return final_table


# Process the net worth data.

def wealth_data():
    """
    Generate the net worth (per capita) table.

    Returns:
        final_weal (pd.DataFrame)

    """
    weal_raw = raw_dict['hhl_finworth']
    weal_fil = weal_raw[weal_raw['LOCATION'].str.contains('USA')]
    final_weal = weal_fil[['TIME', 'Value']].rename(
        columns={'TIME': 'Year', 'Value': 'Wealth'}).reset_index(drop=True)

    return final_weal


# Produce the table on a per capita basis.

def table_pc():
    """
    Generate the final table without price and moving-average adjustments.

    Returns:
        nonadj_pc (pd.DataFrame)
    """
    gross_premiums = premiums_data()
    gross_claims = claims_data()
    wealth = wealth_data()
    population = pop_data()

    gross_precl = pd.merge(gross_premiums, gross_claims)
    gross_table = pd.merge(gross_precl, population)

    for i in 'Premiums', 'Claims':
        gross_table[i] = gross_table['{}'.format(i)] / gross_table['Population']

    pc_table = gross_table[['Year', 'Premiums', 'Claims']]
    nonadj_pc = pd.merge(pc_table, wealth, how='outer')

    return nonadj_pc


# Recalculate the table using the constant 2015 dollars.

def _cpi_data():
    """Get the U.S. CPI data."""
    cpi_raw = raw_dict['cpi_oecd']
    cpi_fil = cpi_raw[cpi_raw['LOCATION'].str.contains('USA')][['TIME', 'Value']].reset_index(drop=True)
    final_cpi = cpi_fil.rename(columns={'TIME': 'Year', 'Value': 'CPI'})

    return final_cpi


def cpi_adjust(nonadj_table, cpi_table):
    """
    Use CPI data to recalculate the values in constant 2015 dollars, formula..

    is (e.g. 2004): money in 2004 * (CPI_2015 / CPI_2004)

    Arg:
        nonadj_table (pd.DataFrame): claims/premiums/wealth with inflation

        cpi_table (pd.DataFrame): CPI data of the U.S.

    Returns:
        final_constant (pd.DataFrame): adjusted table in constant 2015 dollars

    """
    mer_table = pd.merge(nonadj_table, cpi_table)

    temp_np = mer_table.iloc[:, 1:5].values
    n_year = temp_np.shape[0]
    for i in range(0, n_year):
        temp_np[i:i + 1, 0:3] = temp_np[i:i + 1, 0:3] * \
            (temp_np[n_year - 3:n_year - 2, 3] / temp_np[i:i + 1, 3])

    mer_table.iloc[:, 1:] = temp_np
    final_constant = mer_table.round(0).drop(columns=['CPI'])

    return final_constant


# Recalculate the values with five-year moving average method to overcome the
# problem of possible noise

def five_moving(nonadj_table, cpi_table):
    """
    Use five-moving average method to stabilize data.

    Arg:
        nonadj_table (pd.DataFrame): claims/premiums/wealth with inflation

        cpi_table (pd.DataFrame): CPI data of the U.S.

    Returns:
        stab (pd.DataFrame): our final dataset for estimation

    """
    nonstab = cpi_adjust(nonadj_table, cpi_table)
    nonstab_np = nonstab.iloc[:, 1:3].values
    n_year = nonstab_np.shape[0]

    for i in range(0, n_year - 4):
        nonstab_np[i + 2] = np.mean(nonstab_np[i:i + 5], axis=0)

    nonstab.iloc[2:23, 1:3] = nonstab_np[2:23]
    stab = nonstab.iloc[2:23].reset_index(drop=True).round(0)
    stab = stab[['Year', 'Wealth', 'Premiums', 'Claims']]

    return stab


# Output functions

def save_data(known_claim, guess_claim, nonadj_table, cpi_table):
    """
    Generate the final tables (including the table in original paper).

    Arg:
        known_claim (pd.DataFrame): known gross claims table

        guess_claim (pd.DataFrame):
        guessed claims based on the known growth rate

        nonadj_table (pd.DataFrame): claims/premiums/wealth with inflation

        cpi_table (pd.DataFrame): CPI data of the U.S.

    """
    known_claim = _clam_fil()
    growth_mean = _known_growth(known_claim)
    guess_claim = _guess_clam(known_claim, growth_mean)
    clam_olt = _outlier_clam(known_claim, guess_claim)
    clam_olt.to_csv(ppj('OUT_DATA', 'claims_outlier.csv'),
                    index=False, sep=',')

    cpi_adj = cpi_adjust(nonadj_table, cpi_table)
    cpi_adj.to_csv(ppj('OUT_DATA', 'cpi_adjust.csv'),
                   index=False, sep=',')

    stab = five_moving(nonadj_table, cpi_table)
    stab.to_csv(ppj('OUT_DATA', 'recent_table.csv'), index=False, sep=',')

    data_in_paper = raw_dict['paper_table']
    data_in_paper.to_csv(
        ppj('OUT_DATA', 'szpiro_table.csv'), index=False, sep=',')


# Export the data we need

if __name__ == '__main__':

    claim_known = _clam_fil()
    mean_growth = _known_growth(claim_known)
    claim_guess = _guess_clam(claim_known, mean_growth)
    no_cpi_adj = table_pc()
    cpi_table = _cpi_data()

    save_data(claim_known, claim_guess, no_cpi_adj, cpi_table)
