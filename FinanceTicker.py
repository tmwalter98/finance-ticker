#!/usr/bin/python3
import gi
import os
import time
from signal import pause
import threading

from tray_appindicator import TrayAppIndicator
from TickerSync import ETradeSync


APPINDICATOR_ID = 'Finance Ticker'


class FinanceTicker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.tickers = {}
        self.tray_indicator = TrayAppIndicator(APPINDICATOR_ID, self.tickers)
        self.tray_indicator.daemon = True
        
        self.etrade = ETradeSync(self.tickers)
        self.etrade.daemon = True

    def start(self):
        self.etrade.start()
        self.tray_indicator.start()
        pause()


if __name__ == "__main__":
    ft = FinanceTicker()
    ft.start()
    