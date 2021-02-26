import pyetrade
import json

class InterfaceAPIetrade:
    def __init__(self):
        # Obtained secrets from Etrade for Sandbox or Live
        self.config = {}
        self.accounts = None
        self.market = None
        try:
            with open('config.json', 'r') as config_file:
                self.config = json.load(config_file)
                self.config['default']
        except FileNotFoundError:
            # Use the printed URL to retrive Verification code
            print('API Key Required.')
            keypair = self.__add_keypair()
            self.config = {'keypairs': {keypair['name']: keypair}}
            self.config['default'] = keypair['name']
            self.save_config()
    
    def save_config(self):
        with open('config.json', 'w') as config_file:
                json.dump(self.config, config_file)
            
    
    def __add_keypair(self):
        name = input('Enter name for key, secret pair: ').strip()
        new_key = input('Enter key: ').strip()
        new_secret = input('Enter key secret: ').strip()
        keypair_dict = {'name':name, 'key':new_key, 'secret': new_secret}
        return self.__aquire_oauth_tokens(keypair_dict)

    # Using the EtradeOAuth object to retrive the URL to request tokens
    def __aquire_oauth_tokens(self, keypair_dict):
        oauth = pyetrade.ETradeOAuth(keypair_dict['key'], keypair_dict['secret'])
        print(oauth.get_request_token())
        # Use the printed URL to retrive Verification code
        verifier_code = input('Enter verification code: ')
        tokens = oauth.get_access_token(verifier_code)
        keypair_dict['oauth_token'] = tokens['oauth_token']
        keypair_dict['oauth_token_secret'] =  tokens['oauth_token_secret']
        return keypair_dict

    def getAccountInterface(self, keypair=None):
        if(keypair == None):
            kp_name = self.config['default']
        kp = self.config['keypairs']
        kp = kp[kp_name]
        key, secret, oauth_token, oauth_token_secret = kp['key'], kp['secret'], kp['oauth_token'], kp['oauth_token_secret']
        try:
            if(self.accounts == None):
                self.accounts = pyetrade.ETradeAccounts(key, secret, oauth_token, oauth_token_secret, dev=False)
        except:
            kp_name = self.config['kp_name'] = self.__aquire_oauth_tokens(kp)
            self.save_config()
        return self.accounts

    def getDefaultAccountIDKey(self):
        return self.config['keypairs'][self.config['default']]['defaultAccountIDKey']