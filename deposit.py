from cdp import *

Cdp.configure_from_json("keys/aj_cdp.json")

Cdp.


client.deposit(
    amount="10",
    currency="USD",
    payment_method="83562370-3e5c-51db-87da-752af5ab9559"
)   