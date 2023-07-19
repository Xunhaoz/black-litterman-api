import json
import logging
import datetime
from pathlib import Path

from black_litterman import process
from black_litterman import core

import pandas as pd
from flask import Flask, jsonify, request, Response

log_name = Path('logs')
log_name.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO,
                    filename=log_name / datetime.datetime.now().strftime('%Y-%m-%d.logs'),
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if len(logging.getLogger().handlers) < 2:
    logging.getLogger().addHandler(logging.StreamHandler())

app = Flask(__name__, static_url_path='/assets', static_folder='./assets')


@app.route("/", methods=['GET', 'POST'])
def test():
    logging.info({'status': '[success]'})
    return jsonify({'status': '[success]'})


@app.route("/download_stock", methods=['POST'])
def download_stock():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'JSON data not provided'}), 400

    stock_names = data['stock names']
    stock_data = process.download_stock(stock_names)

    return Response(
        stock_data,
        mimetype='text/csv',
        headers={'Content-disposition': f'attachment; filename=price.csv'}
    )


@app.route("/download_mcap", methods=['POST'])
def download_mcap():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'JSON data not provided'}), 400

    stock_names = data['stock names']
    stock_data = process.download_mcap(stock_names)
    return jsonify(stock_data)


@app.route("/cal_market_prior", methods=['POST'])
def cal_market_prior():
    prices = request.files["prices"]
    market_prices = request.files["market_prices"]
    mcaps = request.files["mcaps"]

    prices = pd.read_csv(prices)
    prices.set_index("Date", inplace=True)
    market_prices = pd.read_csv(market_prices)["Adj Close"]
    mcaps = json.loads(mcaps.read())

    market_prior = core.cal_market_prior(prices, market_prices, mcaps)
    return jsonify(market_prior)


@app.route("/view_confident_template", methods=['POST'])
def view_confident_template():
    prices = request.files["prices"]

    prices = pd.read_csv(prices)
    prices.set_index("Date", inplace=True)

    view_and_confident_template = {
        "view": {column: 0.0 for column in prices.columns},
        "confident": {column: 0.5 for column in prices.columns},
        "P": [],
        "Q": [[], ],
        "note": "Q: Kx1 views vector, defaults to None. P: KxN picking matrix, defaults to None"
    }

    return jsonify(view_and_confident_template)


@app.route("/profolio_allocation", methods=['POST'])
def profolio_allocation():
    prices = request.files.get("prices")
    market_prices = request.files.get("market_prices")
    mcaps = request.files.get("mcaps")
    absolute_views = request.files.get("absolute_views")
    PQ = request.files.get("PQ")
    intervals = request.files.get("intervals")
    view_confidences = request.files.get("view_confidences")

    prices, market_prices, mcaps, absolute_views, P, Q, omega, view_confidences = \
        process.process(prices, market_prices, mcaps, absolute_views, PQ, intervals, view_confidences)
    # print(prices, market_prices, mcaps, absolute_views, P, Q, omega, view_confidences)
    # print(omega)

    ret_bl, S_bl = core.cal_black_litterman(prices, market_prices, mcaps, absolute_views, P, Q, omega, view_confidences)
    weights = core.cal_profolio_allocation(ret_bl, S_bl)

    return jsonify(weights)
    # return "OK"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
