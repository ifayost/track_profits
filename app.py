import base64
import datetime
import logging
import requests
import threading
import time

from flask import Flask
from io import BytesIO
from matplotlib.figure import Figure


FILE = './data.txt'
SAMPLE_TIME = 5
eth_sold = 0.10540447
txn_fee = 0.001421961427074638
dai = 399.139261634971299146

rate_ini = dai / (eth_sold - txn_fee)

def get_exchange_rates(currencies):
    response = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms={','.join(currencies)}")
    rate = {i.split(':')[0]: float(i.split(':')[1]) for i in response.text[2:-1].replace('"', '').split(',')}
    return rate

def profit(rate, fee):
    return ((dai / rate - fee) - eth_sold) * rate

def str2datetime(text):
    return datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')

def read(file):
    with open(file, 'r') as f:
        data = f.readlines()
        data = [
                (
                    str2datetime(i.split('|')[0]),
                    float(i.split('|')[1])
                ) for i in data
                ]
    return data

def append(file, data):
    date = str(data[0]).split('.')[0]
    current_profit = str(data[1])
    with open(file, 'a') as f:
        f.write(f'{date}|{current_profit}\n')

def get_row_data():
    current_time = datetime.datetime.now()
    rate = get_exchange_rates(['USD', 'EUR'])
    # Assuming the txn_fee for changing dai for eth will be the same
    current_profit = profit(rate['USD'], txn_fee)
    logging.info(f"Current profit: {current_profit}")
    return (current_time, current_profit)

def scrape_data(sample):
    while True:
        row = get_row_data()
        append(FILE, row)
        time.sleep(sample)

def plot(data):
    # Generate the figure **without using pyplot**.
    fig = Figure(dpi=100, figsize=(12, 6))
    ax = fig.subplots()
    ax.plot([row[0] for row in data], [row[1] for row in data])
    ax.grid(True)
    ax.set_ylabel('USD')
    ax.set_title('Profits')
    fig.autofmt_xdate(rotation=90)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

app = Flask(__name__)

@app.route('/')
def index():
    current_row = get_row_data()
    data = read(FILE)
    data.append(current_row)
    return plot(data)

if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    t = threading.Thread(target=scrape_data, args=(SAMPLE_TIME,))
    t.start()
    app.run()
