import matplotlib.pyplot as plt
import csv
import numpy as np
import yfinance as yf
import datetime
import pandas as pd
import statsmodels.tsa.stattools as ts
from scipy.stats import linregress
import warnings
warnings.filterwarnings("ignore")

sp_tickers = []

with open("sp500_companies.csv", "r") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        sp_tickers.append(row[1])
sp_tickers.pop(0)

#testing dates
data = yf.download(sp_tickers, start="2021-01-01", end="2023-01-01")['Close']
#backtesting dates
backtest_data = yf.download(sp_tickers, start="2023-01-01", end="2025-02-05")['Close']

#MA = data.rolling(200).mean()
#ma = data.rolling(50).mean()
#ma50 = ma.iloc[49:]
#ma200 = MA.iloc[199:]
hedge_ratios = []

def corr(data):
    """Grabs the highest correlated stock pairs from data"""
    data1 = pd.DataFrame(data)
    returns = data1.pct_change()
    corr_matrix = returns.corr()
    high_corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)): 
            corr_value = corr_matrix.iloc[i, j]
            if 0.85 < corr_value < 0.95:
                high_corr_pairs.append((
                    corr_matrix.columns[i],
                    corr_matrix.columns[j],
                    corr_value))
    high_corr_df = pd.DataFrame(
        high_corr_pairs,
        columns=["Stock 1", "Stock 2", "Correlation"])
    return high_corr_df

def plot_pairs(s1, s2):
    """Plots pairs and diffrence from pairs"""
    plt.figure(figsize=(12, 6))
    plt.plot(data[s1])
    plt.plot(data[s2])
    plt.show()
    plt.figure(figsize=(12, 6))
    plt.plot(data[s1] - data[s2])
    plt.show()

def adf_test(p1, p2, data):
    """ADF test and returns if p < 0.05"""
    s1 = data[p1]
    s2 = data[p2]
    df = pd.concat([s1, s2], axis=1).dropna()
    df.columns = ["s1", "s2"]
    result = linregress(df["s1"], df["s2"])
    residuals = df["s1"] - result.slope * df["s2"]
    adf = ts.adfuller(residuals.values)
    if adf[1] < 0.05:
        return (adf[1], residuals.values, result.slope)
    else:
        return None

def residual(p1, p2, data, ratio):
    """Returns diffrence of two stocks with its hedge ratio"""
    s1 = data[p1]
    s2 = data[p2]
    df = pd.concat([s1, s2], axis=1).dropna()
    df.columns = ["s1", "s2"]
    residuals = df["s1"] - ratio * df["s2"]
    return (residuals.values)

def result(high_corr_df, data):
    """takes in dataframe with 2 stocks and returns a list of stock pairs which passed ADF test"""
    picked = []
    for i in range(len(high_corr_df)):
        picked.append(((high_corr_df["Stock 1"][i]), (high_corr_df["Stock 2"][i]), (float(high_corr_df["Correlation"][i]))))
    results = []
    for i in range(len(picked)):
        if (adf_test(picked[i][0], picked[i][1], data)) is not None:
            hedge_ratios.append(adf_test(picked[i][0], picked[i][1], data)[2])
            results.append((picked[i][0], picked[i][1], adf_test(picked[i][0], picked[i][1], data)[1]))
    return results

def z_score(data, plots = False):
    """Plots the z-score of data, highlights points at the mean, and points beyond 1 STD"""
    crossed = []
    above_1 = []
    below_n1 = []

    for i in range(len(data)):
        d = data[i][2]
        df_zscore = (d - d.mean())/d.std()
        close = []
        above = []
        below = []

        for j in range(len(df_zscore)):
            if df_zscore[j] > 1:
                above.append(j)
            if df_zscore[j] < -1:
                below.append(j)   
            if j != 0:
                if df_zscore[j-1] * df_zscore[j] < 0:
                    close.append(j)

        if plots == True:
            plt.figure(figsize=(12, 6))
            plt.plot(df_zscore, label = "Z-Score of the spread")
            plt.scatter(close, df_zscore[close], color = "black", label = "Exit Position")
            plt.scatter(above, df_zscore[above], color = "green", marker='*', label = "Enter Position")
            plt.scatter(below, df_zscore[below], color = "green", marker='*', label = "Enter Position")
            plt.axhline(df_zscore.mean(), color = "black", linestyle='--')
            plt.axhline(1, color = "red")
            plt.axhline(-1, color = "red")
            plt.title("Z-Score from the spread of " + data[i][0] + " and " + data[i][1])
            plt.ylabel("Number of STD from mean")
            plt.xlabel("Number of days")
            plt.legend()
            plt.show()

        crossed.append(close)
        above_1.append(above)
        below_n1.append(below)
    return(crossed, above_1, below_n1)

raw = result(corr(data), data)
#MA50 = result(corr(ma50), data)
#MA200 = result(corr(ma200), data)

#backtest#########################################################################################

backtest_stocks = []
for i in range(len(raw)):
    backtest_stocks.append(((raw[i][0], raw[i][1])))

backtest = []
for i in range(len(backtest_stocks)):
    backtest.append(residual(backtest_stocks[i][0], backtest_stocks[i][1], backtest_data, hedge_ratios[i]))

backtest_raw = []
for i in range(len(raw)):
    backtest_raw.append((raw[i][0], raw[i][1], backtest[i]))

#Replace False to True to see plots
z_score(backtest_raw, False)
