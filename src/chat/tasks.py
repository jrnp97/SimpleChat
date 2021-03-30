""" Module to define chat-bot related command processing """

from chatApp import celery_app as app

from chat.constants import STOCK_SERVICE_URL


@app.task
def stock_searching(stock_name, room_name):
    """ Task to perform stock info search """
