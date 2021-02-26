import pyetrade
import json
import time
from datetime import timedelta
from signal import pause
import threading
from signal import pause, signal, SIGINT

from .ETradeConfiguration import ETradeConfiguration

class ETradeSync(threading.Thread):
    def __init__(self, tickers):
        threading.Thread.__init__(self)
        signal(SIGINT, self.stop)
        self.etrade = ETradeConfiguration()
        self.tickers = tickers
    
    def stop(self, signal_received=None, frame=None):
        self.etrade.stop()
        exit(0)

    def start(self):
        self.thread = threading.Thread(target=self.update)
        self.thread.daemon = True
        self.thread.start()  
    
    def update(self):
        while True:
            self.update_positions()
            time.sleep(60*5)

    def update_positions(self):
        for accountIDKey in self.etrade.buildAccountIndex():
            account_portfolio = self.etrade.get_account_portfolio(accountIDKey)
            for account in account_portfolio:
                for position in account.get('Position'):
                    extracted_p = self.etrade.config['accountPortfolioMask'].copy()
                    for k in extracted_p.keys():
                        #print(json.dumps(position, indent=4))
                        extracted_p[k] = position[k]
                    self.tickers[extracted_p['symbolDescription']] = extracted_p
                    #print(json.dumps(self.tickers, indent=4))