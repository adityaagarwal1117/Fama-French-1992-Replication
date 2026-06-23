import pandas as pd
import numpy as np
import statsmodels.api as sm

# Reading the data
crsp_file = 'Your_Crsp_Price_File.csv'
comp_file = 'Your_Compustat_data.csv'

crsp = pd.read_csv(crsp_file)
comp = pd.read_csv(comp_file)

# Cleaning the CRSP Price data
crsp['date'] = pd.to_datetime(crsp['date'])
crsp = crsp[(crsp['SHRCD'].isin([10, 11])) & (crsp['EXCHCD'].isin([1, 2, 3]))]
crsp['ME'] = (crsp['PRC'].abs() * crsp['SHROUT']) / 1000
crsp['year'] = crsp['date'].dt.year
crsp['month'] = crsp['date'].dt.month
crsp['TICKER'] = crsp['TICKER'].astype(str).str.upper()
crsp['RET'] = pd.to_numeric(crsp['RET'], errors='coerce')

# Cleaning the compustat(Accounting) data
comp['datadate'] = pd.to_datetime(comp['datadate'])
comp['year'] = comp['datadate'].dt.year
comp['tic'] = comp['tic'].astype(str).str.upper()
comp['txditc'] = comp['txditc'].fillna(0)
comp['pstkrv'] = comp['pstkrv'].fillna(0)

#Calculating Book Equity
comp['BE'] = comp['seq'] + comp['txditc'] - comp['pstkrv']
comp = comp[comp['BE'] > 0]

# Preventing Look-Ahead Bias
dec_me = crsp[crsp['month'] == 12][['TICKER', 'year', 'ME']].copy()
dec_me.rename(columns={'ME': 'Dec_ME', 'year': 'match_year'}, inplace=True)

june_me = crsp[crsp['month'] == 6][['TICKER', 'year', 'ME']].copy()
june_me['match_year'] = june_me['year'] - 1
june_me.rename(columns={'ME': 'June_ME'}, inplace=True)


# Merging the Datasets & Calculating Book-to-Market
comp_be = comp[['tic', 'year', 'BE']].copy()
comp_be.rename(columns={'tic': 'TICKER', 'year': 'match_year'}, inplace=True)

merged = pd.merge(comp_be, dec_me, on=['TICKER', 'match_year'], how='inner')
merged = pd.merge(merged, june_me[['TICKER', 'match_year', 'June_ME', 'year']], on=['TICKER', 'match_year'],
                  how='inner')

merged['BM'] = merged['BE'] / merged['Dec_ME']
merged = merged[merged['BM'] > 0]

# Portfolio Sorting
merged['Size_Rank'] = merged.groupby('year')['June_ME'].transform(
    lambda x: pd.qcut(x, 10, labels=False, duplicates='drop'))
merged['BM_Rank'] = merged.groupby(['year', 'Size_Rank'])['BM'].transform(
    lambda x: pd.qcut(x, 10, labels=False, duplicates='drop'))

crsp_returns = crsp[['TICKER', 'date', 'year', 'month', 'RET', 'vwretd']].copy()
crsp_returns['port_year'] = np.where(crsp_returns['month'] <= 6, crsp_returns['year'] - 1, crsp_returns['year'])

final_data = pd.merge(crsp_returns, merged[['TICKER', 'year', 'June_ME', 'BM']],
                      left_on=['TICKER', 'port_year'], right_on=['TICKER', 'year'], how='inner')

final_data['log_ME'] = np.log(final_data['June_ME'])
final_data['log_BM'] = np.log(final_data['BM'])
final_data = final_data.dropna(subset=['RET', 'log_ME', 'log_BM'])

fm_results = []
for dt, month_data in final_data.groupby('date'):
    Y = month_data['RET']
    X = month_data[['log_ME', 'log_BM']]
    X = sm.add_constant(X)

    try:
        model = sm.OLS(Y, X).fit()
        fm_results.append(model.params)
    except:
        continue

# --- Fama-MacBeth Statistics Calculation ---
coefficients_df = pd.DataFrame(fm_results)
final_coefficients = coefficients_df.mean()

# Time-series standard error = standard deviation / sqrt(N)
N = len(coefficients_df)
std_errors = coefficients_df.std() / np.sqrt(N)
t_stats = final_coefficients / std_errors

results_summary = pd.DataFrame({
    'Coefficient': final_coefficients,
    't-stat': t_stats
})

print("--- Fama-MacBeth Cross-Sectional Regression Results ---")
print(f"Total Months Regressed: {N}")
print("-" * 55)
print(results_summary.round(4))