#!/usr/bin/python3
from signal import pause
import threading

from SystemTrayIndicator import SystemTrayIndicator
from FinanceTickerAPIKit import ETradeSync


APPINDICATOR_ID = 'Finance Ticker'


class FinanceTicker(threading.Thread):
    def __init__(self, headless=True):
        threading.Thread.__init__(self)
        self.headless = headless
        self.daemon = True
        self.tickers = {}

        if not self.headless:
            self.tray_indicator = SystemTrayIndicator(APPINDICATOR_ID, self.tickers)
            self.tray_indicator.daemon = True
        
        self.etrade = ETradeSync(self.tickers)
        self.etrade.daemon = True

    def start(self):
        self.etrade.start()
        if not self.headless:
            self.tray_indicator.start()
        pause()


if __name__ == "__main__":
    ft = FinanceTicker(headless=False)
    ft.start()
