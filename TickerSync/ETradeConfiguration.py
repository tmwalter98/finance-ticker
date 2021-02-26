import pyetrade
import json
import time
from datetime import timedelta, datetime
from signal import pause
from threading import Thread
from signal import pause, signal, SIGINT


class ETradeConfiguration():
    def __init__(self):
        self.config = {}
        self.accounts = {}
        self.etrade_accounts_objs = {}
        
        if(self.__load_config() == 1):
            self.config = { "keypairs": [ { "name": "template", "key": None, "secret": None, "oauth_token": None, "oauth_token_secret": None , 'oauth_token_expiration': None} ], "accountPortfolioMask": { "costPerShare": None, "daysGain": None, "daysGainPct": None, "pctOfPortfolio": None, "pricePaid": None, "quantity": None, "symbolDescription": None, "totalGain": None, "totalGainPct": None } }
            self.config['keypairs'] = []
            self.add_keypair()
            self.__save_config()
        self.__save_config()


    def stop(self, signal_received=None, frame=None):
        self.__save_config()
        exit(0)

    def __load_config(self):
        try:
            with open('config.json', 'r') as config_file:
                self.config = json.load(config_file)
                return 0
        except FileNotFoundError:
            # Use the printed URL to retrive Verification code
            print('No config file found.')
            return 1
    
    def __save_config(self):
        with open('config.json', 'w') as config_file:
            json.dump(self.config, config_file)

    def add_keypair(self, name='default', key='68e406b611cfe2f81493361d144f0433', secret='ccb32f01fe97fc3413c4c31a3700b88acd9de0d36d14d7445f8015f831669b57'):
    #def add_keypair(self, name=None, key=None, secret=None):
        if(name == None):
            name = input('Enter name for key, secret pair: ').strip()
        if(key == None):
            key = input('Enter key: ').strip()
        if(secret == None):
            secret = input('Enter key secret: ').strip()
        self.__aquire_oauth_tokens({'name':name, 'key':key, 'secret': secret})

    def refresh_oauth_tokens(self, keypair_name):
        self.__aquire_oauth_tokens(self.config.keypairs[keypair_name])

    # Using the EtradeOAuth object to retrive the URL to request tokens
    def __aquire_oauth_tokens(self, keypair):
        oauth = pyetrade.ETradeOAuth(keypair['key'], keypair['secret'])
        print(oauth.get_request_token())
        datetime_expiration = datetime.now() + timedelta(hours=2)

        # Use the printed URL to retrive Verification code
        verifier_code = input('Enter verification code: ')
        tokens = oauth.get_access_token(verifier_code)
        keypair.update({'oauth_token': tokens['oauth_token']})
        keypair.update({'oauth_token_secret': tokens['oauth_token_secret']})
        keypair.update({'oauth_token_expiration': datetime_expiration.timestamp()})
        print(json.dumps(self.config, indent=4))
        self.__save_config()

    def getKeyPairs(self):
        return self.config['keypairs']

    def buildAccountIndex(self):
        for kp in self.config['keypairs']:
            key, secret, oauth_token, oauth_token_secret = kp['key'], kp['secret'], kp['oauth_token'], kp['oauth_token_secret']
            if(True):
                etrade_accounts_obj = pyetrade.ETradeAccounts(key, secret, oauth_token, oauth_token_secret, dev=False)
                for account in etrade_accounts_obj.list_accounts().get('AccountListResponse').get('Accounts').values():
                    accountIdKey = account['accountIdKey']
                    self.accounts[accountIdKey] = account
                    self.etrade_accounts_objs[accountIdKey] = etrade_accounts_obj
        return self.accounts
        
    def get_account_portfolio(self, accountIDKey):
        return self.etrade_accounts_objs[accountIDKey].get_account_portfolio(accountIDKey, resp_format='json').get('PortfolioResponse').get('AccountPortfolio')