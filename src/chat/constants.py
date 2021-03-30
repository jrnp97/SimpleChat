""" Module to define constants values to use on app """

STOCK_SERVICE_URL = ('https://stooq.com/q/l/?s={stock_code}&'
                     'f=sd2t2ohlcv&h&'
                     'e=csv')
STOCK_MESSAGE_RGX = r'\/stock=(?P<stock_code>\.+)'
