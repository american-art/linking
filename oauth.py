from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
from pprint import pprint
from config import *
from requests import ConnectionError

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return server+"callback/facebook"

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            access_token_url='https://graph.facebook.com/oauth/access_token',
            authorize_url='https://graph.facebook.com/oauth/authorize',
            base_url='https://graph.facebook.com/v2.7'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
        
    def custom_decoder(self, payload):
        return json.loads(payload.decode('utf-8'))

    def callback(self):
        if 'code' not in request.args:
            return None, None, None

        data={'code': request.args['code'],'grant_type': 'authorization_code','redirect_uri': self.get_callback_url()}
        
        try:
            if sys.version_info[0] < 3:
                oauth_session = self.service.get_auth_session(data=data,decoder=json.loads)
            else:
                oauth_session = self.service.get_auth_session(data=data,decoder=self.custom_decoder)
            me = oauth_session.get('me?fields=id,email,name',params={'format': 'json'}).json()
        except ConnectionError:
            #print "Connection Error in getting data from Facebook\n"
            logging.info("Connection Error in getting data from Facebook\n")
            return (None, None, None)

        #print "Facebook OAuth returned : {}, {}, {} \n".format(me.get('id'),me.get('email'),me.get('name'))
        logging.info("Facebook OAuth returned : {}, {}, {} \n".format(me.get('id'), me.get('email'), me.get('name')))
        return (me.get('id'), me.get('email'), me.get('name'))
