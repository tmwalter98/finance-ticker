#!/usr/bin/python3
import gi
import os
import time
from signal import pause
from threading import Thread

from tray_ticker import TrayTicker
from etrade_api_interface import InterfaceAPIetrade

APPINDICATOR_ID = 'Finance Ticker'


class FinanceTicker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.tickers = {}
        self.etrade = InterfaceAPIetrade()
        self.accounts = self.etrade.getAccountInterface()
        self.update_etrade()
        
        self.tray_indicator = TrayTicker(APPINDICATOR_ID, self.tickers)

    def start(self):
        self.tray_indicator.start()

    def update_etrade(self):
        dict_mask = {
            'costPerShare': None,
            'daysGain': None,
            'daysGainPct': None,
            'pctOfPortfolio': None,
            'pricePaid': None,
            'quantity': None,
            'symbolDescription': None,
            'totalGain': None,
            'totalGainPct': None
            }
        account_portfolio = self.accounts.get_account_portfolio(self.etrade.getDefaultAccountIDKey(), resp_format='json')['PortfolioResponse']['AccountPortfolio'][0]

        for position in account_portfolio['Position']:
            extracted_p = dict_mask.copy()
            for k in extracted_p.keys():
                extracted_p[k] = position[k]
            self.tickers[extracted_p['symbolDescription']] = extracted_p        

if __name__ == "__main__":
    ft = FinanceTicker()
    ft.start()
    etrade = InterfaceAPIetrade()
    #main()
    pause()