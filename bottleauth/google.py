#!/usr/bin/env python
# -*- coding: utf-8 -*-'
import logging
from urlparse import urlparse

from bottleauth.exception import UserDenied, NegotiationError
from bottleauth.tornado.auth import GoogleMixin, HTTPRedirect


log = logging.getLogger('bottleauth.google')


class Google(object):
    def __init__(self, key, secret, callback_url,
                 scope='name,email,language,username'):
        self.settings = {
            'google_consumer_key': key,
            'google_consumer_secret': secret,
        }
        self.callback_url = callback_url
        self.scope = scope

    def redirect(self, environ):
        auth = GoogleMixin(environ, self.settings)
        ax_attrs = self.scope.split(',')
        try:
            auth.authenticate_redirect(
                callback_uri=self.callback_url,
                ax_attrs=ax_attrs)
        except HTTPRedirect, e:
            log.debug('Redirecting Google user to {0}'.format(e.url))
            return e.url
        return None

    def get_user(self, environ):
        auth = GoogleMixin(environ, self.settings)

        if auth.get_argument('error', None):
            log.debug('User denied attributes exchange')
            raise UserDenied()

        container = {}

        def get_user_callback(user):
            if not user:
                raise NegotiationError()

            container['attrs'] = user
            query_string = urlparse(user['claimed_id']).query
            params = dict(
                param.split('=') for param in query_string.split('&'))
            container['parsed'] = {
                'uid': params['id'],
                'email': user['email'],
                'username': None,
                'screen_name': user.get('first_name'),
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'language': user.get('locale'),
                'profile_url': None,
                'profile_image_small': None,
                'profile_image': None
            }

        auth.get_authenticated_user(get_user_callback)

        return container
