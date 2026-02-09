This project implements a pairs trading strategy on S&P 500 stocks.
It finds highly correlated pairs, tests for cointegration (ADF test), builds a mean-reverting spread using a regression hedge ratio, and trades based on Z-score signals (enter at ±1, exit at zero).
Includes historical backtesting and signal plots.
Change the testing dates(line 21) and backtesting dates(line 23) to use this algorithm on diffrent dates.
At the last line switch z_score(backtest_raw, False) to z_score(backtest_raw, True) to see plots, and you must download sp500_companies.csv.
