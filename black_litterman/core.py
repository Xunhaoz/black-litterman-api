from pypfopt import black_litterman, risk_models, BlackLittermanModel
from pypfopt import EfficientFrontier, objective_functions
import pandas as pd
import numpy as np


def cal_market_prior(prices: pd.DataFrame, market_prices: pd.DataFrame, mcaps: dict) -> dict:
    s = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
    delta = black_litterman.market_implied_risk_aversion(market_prices)
    market_prior = black_litterman.market_implied_prior_returns(mcaps, delta, s)
    return market_prior.to_dict()


def cal_black_litterman(prices, market_prices, mcaps, absolute_views, P, Q, omega, view_confidences):
    S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
    delta = black_litterman.market_implied_risk_aversion(market_prices)
    market_prior = black_litterman.market_implied_prior_returns(mcaps, delta, S)

    bl = BlackLittermanModel(
        S, pi=market_prior, absolute_views=absolute_views,
        Q=Q, P=P, omega=omega, view_confidences=view_confidences,
        risk_aversion=delta if type(omega)  is np.ndarray else 1
    )

    ret_bl = bl.bl_returns()
    S_bl = bl.bl_cov()

    return ret_bl, S_bl


def cal_profolio_allocation(ret_bl, S_bl):
    ef = EfficientFrontier(ret_bl, S_bl)
    ef.add_objective(objective_functions.L2_reg)
    ef.max_sharpe()
    weights = ef.clean_weights()
    return weights
