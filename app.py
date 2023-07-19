import logging
import datetime
from pathlib import Path

from black_litterman import process
from black_litterman import core

from flask import Flask, jsonify, request

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


@app.route("/profolio_allocation", methods=['POST'])
def profolio_allocation():
    try:
        logging.info("start profolio_allocation")
        prices = request.files.get("prices")
        market_prices = request.files.get("market_prices")
        mcaps = request.files.get("mcaps")
        absolute_views = request.files.get("absolute_views")
        PQ = request.files.get("PQ")
        intervals = request.files.get("intervals")
        view_confidences = request.files.get("view_confidences")

        prices, market_prices, mcaps, absolute_views, P, Q, omega, view_confidences = \
            process.process(prices, market_prices, mcaps, absolute_views, PQ, intervals, view_confidences)

        ret_bl, S_bl = core.cal_black_litterman(prices, market_prices, mcaps,
                                                absolute_views, P, Q, omega, view_confidences)

        weights = core.cal_profolio_allocation(ret_bl, S_bl)
        weights['status'] = '[success]'

        logging.info("profolio_allocation success")
        return jsonify(weights)
    except Exception as e:
        logging.info(e)
        return jsonify({'status': '[fail]'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
