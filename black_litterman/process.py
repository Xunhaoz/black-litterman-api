import yfinance as yf
import pandas as pd
import numpy as np
import json


def dict_to_csv(data: dict) -> str:
    for k, v in data.items():
        data[k] = [v]
    data = pd.DataFrame(data)
    data = data.to_csv(index=False)
    return data


def download_stock(tickers: list) -> str:
    stock_data = yf.download(tickers, period="max")
    stock_data = stock_data["Adj Close"]
    stock_data = stock_data.to_csv()
    return stock_data


def download_mcap(tickers: list) -> dict:
    mcaps = {}
    for t in tickers:
        stock = yf.Ticker(t)
        mcaps[t] = stock.info["marketCap"]

    return mcaps


def process(prices=None, market_prices=None, mcaps=None, absolute_views=None,
            PQ=None, intervals=None, view_confidences=None):
    omega = None
    P = None
    Q = None

    if prices is not None:
        prices = pd.read_csv(prices)
        prices.set_index("Date", inplace=True)

    if market_prices is not None:
        market_prices = pd.read_csv(market_prices)["Adj Close"]

    if mcaps is not None:
        mcaps = json.loads(mcaps.read())

    if absolute_views is not None:
        absolute_views = json.loads(absolute_views.read())

    if PQ is not None:
        PQ = json.loads(PQ.read())
        Q = np.array(PQ["Q"]).reshape(-1, 1)
        P = np.array(PQ["P"])

    if view_confidences is not None:
        view_confidences = json.loads(view_confidences.read())
        view_confidences = view_confidences["view_confidences"]
        omega = "idzorek"

    if intervals is not None:
        intervals = json.loads(intervals.read())
        intervals = intervals["intervals"]

        variances = []
        for lb, ub in intervals:
            sigma = (ub - lb) / 2
            variances.append(sigma ** 2)
        omega = np.diag(variances)

    return prices, market_prices, mcaps, absolute_views, P, Q, omega, view_confidences
