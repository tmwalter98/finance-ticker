import pyetrade
import json
import os, tempfile
import time
import threading
from signal import signal, SIGINT

PERSISTENCE_PATH = os.path.join(tempfile.gettempdir(), 'finance-ticker')
API_KEY_PATH = os.path.join(PERSISTENCE_PATH, 'etrade.api_key',)
OAUTH_TOKENS_PATH = os.path.join(PERSISTENCE_PATH, 'etrade.oauth_tokens',)
OAUTH_EXPIRATION_AGE = 60 * 120

class ETradeSync(threading.Thread):
    def __init__(self, tickers):
        threading.Thread.__init__(self)
        self.daemon = True
        signal(SIGINT, self.stop)
    
        self.tickers = tickers
        self.account_index = {}
        self.ready = False
        
        self.key = None
        self.secret = None
        self.oauth_token = {'oauth_token': None, 'oauth_token_secret': None}

        self.access_manager = None
        self.etrade_accounts = None

        self.__secure_tempfile_dir()
        if not self.__load_keypair() == 0:
            self.__store_keypair()
        if not self.__load_token(self.key, self.secret) == 0:
            self.__aquire_oauth_token(self.key, self.secret)

        self.buildAccountIndex()

    def __secure_tempfile_dir(self):
        try:
            os.makedirs(PERSISTENCE_PATH)
        except IsADirectoryError:
            pass
        except:
            pass # Probably permissions error

        os.chmod(PERSISTENCE_PATH, 0o700)
        for root, dirs, files in os.walk(PERSISTENCE_PATH):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o600)
            for f in files:
                os.chmod(os.path.join(root, f), 0o600)

    def __load_token(self, key, secret):
        # Attempts to load tokens into instance objects
        # Returns failure code of 1 if
        # - Token file does not exist
        # - Token Expired
        # - Impropperly formatted JSON document
        # - Propperly formatted JSON document, but token keys not found
        try:
            # Checks if token is expired by checking last modification time
            # if expired, then delete file causing subsequent opening attempt to fail
            token_age = time.time() - os.path.getmtime(OAUTH_TOKENS_PATH)
            if token_age > OAUTH_EXPIRATION_AGE:
                os.remove(OAUTH_TOKENS_PATH)
            # Attemps to open, read JSON document into dict
            with open(OAUTH_TOKENS_PATH, 'r') as token_file:
                token = json.load(token_file)
            # If token keys exist and are not null, store them in instance object 
            if(token['oauth_token'] and token['oauth_token_secret']):
                self.oauth_token.update(token)

            self.access_manager = pyetrade.authorization.ETradeAccessManager(key,secret,token['oauth_token'],token['oauth_token_secret'])
            self.etrade_accounts = pyetrade.ETradeAccounts(key, secret, token['oauth_token'], token['oauth_token_secret'], dev=False)
            self.ready = True
        except:
            if os.path.exists(OAUTH_TOKENS_PATH):
                os.remove(OAUTH_TOKENS_PATH)
            return 1
        return 0

    def __aquire_oauth_token(self, key, secret):
        oauth = pyetrade.ETradeOAuth(key, secret)
        print(oauth.get_request_token())
        verification_code = input('Enter verification code: ')
        token = oauth.get_access_token(verification_code)
        with open(OAUTH_TOKENS_PATH, 'w') as token_file:
            json.dump(token, token_file)
        self.__load_token(key, secret)

    def renew_oath_token(self):
        os.utime(OAUTH_TOKENS_PATH, (time.time(), time.time()))
        self.access_manager.renew_access_token()

    def __load_keypair(self):
        try:
            with open(API_KEY_PATH, 'r') as keypair_file:
                keypair = json.load(keypair_file)
            self.key, self.secret = keypair['key'], keypair['secret']
        except PermissionError:
            return 1
        except FileNotFoundError:
            return 2
        return 0

    def __store_keypair(self, key=os.environ.get('ETRADE_API_KEY'), secret=os.environ.get('ETRADE_API_SECRET')):
        if(key == None):
            key = input('Enter key: ').strip()
        if(secret == None):
            secret = input('Enter key secret: ').strip()
        
        with open(API_KEY_PATH, 'w') as keystore:
            json.dump({'key':key, 'secret': secret}, keystore)
        self.key, self.secret = key, secret

    def buildAccountIndex(self):
        if not self.ready:
            return 1
        try:
            for account in self.etrade_accounts.list_accounts().get('AccountListResponse').get('Accounts').values():
                self.account_index[account['accountIdKey']] = account
        except:
            return 1
        return 0
        
    def get_account_portfolio(self, accountIDKey):
        if self.ready:
            return self.etrade_accounts.get_account_portfolio(accountIDKey, resp_format='json').get('PortfolioResponse').get('AccountPortfolio')
        else:
            return None

    def stop(self, signal_received=None, frame=None):
        self.__renew_oath_token()
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
        for accountIDKey in self.account_index:
            account_portfolio = self.get_account_portfolio(accountIDKey)
            for account in account_portfolio:
                for position in account.get('Position'):
                    self.tickers[position['symbolDescription']] = position
                    #print(json.dumps(self.tickers, indent=4))