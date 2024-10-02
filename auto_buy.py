import os
import time
import random
from datetime import datetime, timedelta
import requests
from coinbase.rest import RESTClient
import json
from cryptography.fernet import Fernet
import logging

# Add this near the top of the file, after the imports
logging.basicConfig(level=logging.INFO)

# Add this near the top of the file, after the imports
PURCHASE_AMOUNT_USD = 2.0  # Set the default purchase amount to $2.00

# Initialize the Coinbase client
client = RESTClient(key_file='aj_api.json')

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

def get_coinbase_products():
    products = client.get_products()
    
    if isinstance(products, dict) and 'products' in products:
        products = products['products']
    
    usd_products = []
    for p in products:
        if isinstance(p, dict):
            if p.get('quote_currency_id') == 'USD':
                usd_products.append(p)
        elif hasattr(p, 'quote_currency_id'):
            if p.quote_currency_id == 'USD':
                usd_products.append(p)
        else:
            logging.warning(f"Unexpected product format: {p}")
    
    logging.info(f"Found {len(usd_products)} USD products")
    return usd_products

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

def select_random_coin(coins, products):
    # Choose a random coin without weighting
    coin = random.choice(coins)
    
    # Find the corresponding Coinbase product
    product = next((p for p in products if p['base_currency_id'].upper() == coin['symbol'].upper()), None)
    return coin, product

def get_payment_methods():
    payment_methods = client.list_payment_methods()
    
    if isinstance(payment_methods, dict) and 'payment_methods' in payment_methods:
        payment_methods = payment_methods['payment_methods']
        
    valid_methods = []

    for pm in payment_methods:
        if pm['id'] == 'b750b140-27c9-5a77-9d17-21ce3269800a':
            print('found it')
            print(pm)
            valid_methods.append(pm)
        '''logging.debug(f"Processing payment method: {json.dumps(pm, indent=2)}")
        if isinstance(pm, dict):
            if pm.get('type') in ['ach_bank_account', 'debit_card']:
                valid_methods.append(pm)
        elif hasattr(pm, 'type'):
            if pm.type in ['ach_bank_account', 'debit_card']:
                valid_methods.append(pm)
        elif pm['id'] =='b750b140-27c9-5a77-9d17-21ce3269800a':
            valid_methods.append(pm)
            print('found a valid method\n\n\n')
        else:
            logging.warning(f"Unexpected payment method format: {pm}")'''
    
    logging.debug(f"Found {len(valid_methods)} valid payment methods")
    print('\n\n\n')
    print(client.get_payment_method(valid_methods[0]['id']))
    return valid_methods

def buy_coin(product, amount_usd, payment_method):
    order = client.market_order_buy(
        client_order_id=f"{product['product_id']}-{amount_usd}-{time.time()}",
        product_id=product['product_id'],
        quote_size=str(amount_usd),
    )
    payment_method_type = payment_method['type'] if isinstance(payment_method, dict) else payment_method.type
    print(f"Bought ${amount_usd} worth of {product['base_currency_id']} using {payment_method_type}")
    print(order)
    return order

def main():
    last_purchase_time = get_last_purchase_time()
    if last_purchase_time is None or datetime.now() - last_purchase_time > timedelta(hours=24):
        coins = get_market_caps()
        logging.info(f"Retrieved {len(coins)} coins from market caps data")
        
        products = get_coinbase_products()
        logging.info(f"Retrieved {len(products)} products from Coinbase")
        
        # Filter coins that are available on Coinbase
        coinbase_symbols = set(p['base_currency_id'].upper() for p in products if 'base_currency_id' in p)
        
        logging.info(f"Found {len(coinbase_symbols)} unique Coinbase symbols")
        
        available_coins = [coin for coin in coins if coin['symbol'].upper() in coinbase_symbols]
        logging.info(f"Found {len(available_coins)} available coins")
        
        if not available_coins:
            print("No available coins to purchase.")
            return
        
        coin, product = select_random_coin(available_coins, products)
        '''print(coin)
        print('\n\n\n')
        print(product)'''
        logging.info(f"Selected coin: {coin['symbol']}")
        
        if product:
            # Get available payment methods
            payment_methods = get_payment_methods()
            if not payment_methods:
                print("No valid payment methods found. Please add a bank account or card to your Coinbase account.")
                return
            
            # Select the first available payment method (you can modify this to choose a specific one)
            selected_payment_method = payment_methods[0]
            
            # Use the PURCHASE_AMOUNT_USD variable instead of hardcoded value
            buy_coin(product, PURCHASE_AMOUNT_USD, selected_payment_method)
            save_current_time()
        else:
            print(f"Could not find a matching Coinbase product for {coin['symbol']}")
    else:
        print("Less than 24 hours since the last purchase.")

if __name__ == "__main__":
    main()