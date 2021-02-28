#!/usr/bin/python3
from threading import Thread
import sys
import json
from apscheduler.schedulers.background import BackgroundScheduler

from FinanceTickerAPIKit import ETradeSync

class FinanceTickerAPIKit(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.tickers = {}
        with open('config.json', 'r') as config:
                scheduler_config = json.load(config)['scheduler_config']
        self.scheduler = BackgroundScheduler(scheduler_config)
        self.etrade = ETradeSync(self.tickers)

        self.scheduler.add_job(self.renew, 'interval', minutes=115, id='renew_tokens')
        self.scheduler.print_jobs(out=sys.stdout)

    def renew(self):
        self.etrade.__renew_oath_token()

if __name__ == "__main__":
    m = FinanceTickerAPIKit()