import os
import time
import json
import requests
import random
from datetime import datetime, timedelta

# Replace these with your Coinbase API credentials
API_KEY = 'YOUR_COINBASE_API_KEY'
API_SECRET = 'YOUR_COINBASE_API_SECRET'

def get_last_purchase_time():
    if os.path.exists('time.txt'):
        with open('time.txt', 'r') as f:
            timestamp = f.read()
            return datetime.fromtimestamp(float(timestamp))
    else:
        return None

def save_current_time():
    with open('time.txt', 'w') as f:
        f.write(str(time.time()))

def get_coinbase_currencies():
    url = 'https://api.coinbase.com/v2/currencies'
    response = requests.get(url)
    data = response.json()
    currencies = data['data']
    return currencies

def get_market_caps():
    # Fetch market data from CoinGecko API
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
        'sparkline': 'false'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def select_random_coin(coins):
    total_market_cap = sum(coin['market_cap'] for coin in coins if coin['market_cap'])
    probabilities = [(coin['market_cap'] / total_market_cap) if coin['market_cap'] else 0 for coin in coins]
    coin = random.choices(coins, weights=probabilities, k=1)[0]
    return coin

def buy_coin(coin_id, amount_usd):
    # Implement the order creation using Coinbase API
    # This is a placeholder function
    print(f"Bought ${amount_usd} worth of {coin_id}")

def main():
    last_purchase_time = get_last_purchase_time()
    if last_purchase_time is None or datetime.now() - last_purchase_time > timedelta(hours=24):
        coins = get_market_caps()
        # Filter coins that are available on Coinbase
        coinbase_currencies = get_coinbase_currencies()
        coinbase_symbols = {c['id'].upper() for c in coinbase_currencies}
        available_coins = [coin for coin in coins if coin['symbol'].upper() in coinbase_symbols]
        if not available_coins:
            print("No available coins to purchase.")
            return
        coin = select_random_coin(available_coins)
        coin_id = coin['symbol'].upper()
        buy_coin(coin_id, 2)
        save_current_time()
    else:
        print("Less than 24 hours since the last purchase.")

if __name__ == "__main__":
    main()