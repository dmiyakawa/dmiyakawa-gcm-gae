# -*- coding=utf-8 -*-
#
#   Copyright [2013] Daisuke Miyakawa
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import datetime
import jinja2
import json
import logging
import os
import urllib
import urllib2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb

from secret import CLIENT_ID
from secret import CLIENT_SECRET
from secret import REFRESH_TOKEN
from secret import ALLOWED_EMAIL

LOCAL_DEV = os.environ['SERVER_SOFTWARE'].startswith('Development')
JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'])


class AccessToken(ndb.Model):
  access_token = ndb.StringProperty(indexed=False)
  token_type = ndb.StringProperty(indexed=False)
  expires_in = ndb.IntegerProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)

  def is_effective(self):
    utcnow = datetime.datetime.utcnow()
    logging.debug('date: {}, expires_in: {}, utc_now: {}'
                  .format(self.date, self.expires_in, utcnow))
    return self.date + datetime.timedelta(seconds=self.expires_in) > utcnow
  pass


class Channel(ndb.Model):
  date = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
  pass


def get_world_ancestor_key():
  '''
  Key for id-s that must be unique world wide.
  '''
  return ndb.Key('ListName', 'debug')


def simple_sanitize(raw_string):
  return (raw_string.replace('<', '').replace('>', '')
          .replace('"', '').replace("'",''))

def is_appropriate_user(user):
  return LOCAL_DEV or user.email() == ALLOWED_EMAIL


def render_message(title, message):
  template_file = '/templates/message.tmpl'
  template = JINJA_ENVIRONMENT.get_template(template_file)  
  return template.render({'title': title, message: 'message'})


class RegisterChannelId(webapp2.RequestHandler):
  def get(self, channel_id):
    logging.debug('RegisterChannelId: ' + channel_id)
    self.response.headers.add_header('content-type',
                                     'application/json',
                                     charset='utf-8')

    user = users.get_current_user()
    if not user:
      result = json.dumps({'result': 'failure',
                           'message': 'Not logged in'})
      self.response.out.write(result)
      return

    if not is_appropriate_user(user):
      result = json.dumps({'result': 'failure',
                           'message': 'Inappropriate user'})
      self.response.out.write(result)
      return

    channel = Channel.get_by_id(id=channel_id,
                                parent=get_world_ancestor_key())
    if channel:
      logging.debug('channel exists (id: {})'.format(channel.key.id()))
      result = json.dumps({'result': 'failure',
                           'message': 'Already registered'})
      self.response.out.write(result)
      return

    channel = Channel(id=channel_id, parent=get_world_ancestor_key())
    channel.put()

    result = json.dumps({'result': 'success'})
    self.response.out.write(result)
    pass
  pass


class SendMessage(webapp2.RequestHandler):
  def get(self):
    self.response.headers.add_header('content-type',
                                     'application/json',
                                     charset='utf-8')
    user = users.get_current_user()
    if not user:
      result = json.dumps({'result': 'failure',
                           'message': 'Not logged in'})
      self.response.out.write(result)
      return
 
    if not is_appropriate_user(user):
      result = json.dumps({'result': 'failure',
                           'message': 'Inappropriate user'})
      self.response.out.write(result)
      return

    raw_channel_id = self.request.get('channel_id')
    channel_id = simple_sanitize(raw_channel_id)
    if len(channel_id) == 0:
      result = json.dumps({'result': 'failure',
                           'message': 'No channel_id provided'})
      self.response.out.write(result)
      pass

    raw_message = self.request.get('message')
    message = simple_sanitize(raw_message)

    if len(message) == 0:
      message = "(No message)"
      pass

    access_tokens = AccessToken.query().order(-AccessToken.date).fetch(1)
    if (len(access_tokens) == 0 or not access_tokens[0].is_effective()):
      logging.debug('Fetching AccessToken')
      url = 'https://accounts.google.com/o/oauth2/token'
      values = {'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'refresh_token': REFRESH_TOKEN,
                'grant_type': 'refresh_token'}
      data = urllib.urlencode(values)
      req = urllib2.Request(url, data)
      response = urllib2.urlopen(req)
      data = response.read()
      logging.debug('AccessToken result: ' + data)
      json_data = json.loads(data)
      if not json_data.has_key('access_token'):
        result = json.dumps({'result': 'error',
                             'message': 'Failed to fetch AccessToken'})
        self.response.out.write(result)
        return

      # TODO: remove old data ..
      access_token = AccessToken()
      access_token.access_token = json_data['access_token']
      access_token.token_type = json_data['token_type']
      access_token.expires_in = int(json_data['expires_in'])
      access_token.put()
    else:
      access_token = access_tokens[0]
      logging.debug('Access Token (id: {}) is effective.'
                    .format(access_token.key.id()))
      pass

    url = 'https://www.googleapis.com/gcm_for_chrome/v1/messages'
    data = {'channelId': channel_id,
            'subchannelId': '0',
            'payload': message}
    headers = {'Content-Type': 'application/json',
               'Authorization': '{} {}'.format(access_token.token_type,
                                access_token.access_token)}
    json_data = json.dumps(data)
    logging.debug('Send a message.'
                  ' access_token: {}, token_type: {}, json: {}'
                  .format(access_token.access_token,
                          access_token.token_type,
                          json_data))

    req = urllib2.Request(url, json_data, headers)
    logging.debug(req)
    try:
      response = urllib2.urlopen(req)
      logging.debug(response.read())
      result = json.dumps({'result': 'success'})
      self.response.out.write(result)
    except urllib2.HTTPError, e:
      logging.debug('Exception: {}'.format(e)) 
      result = json.dumps({'result': 'error',
                           'message': 'Exception: {}'.format(e)})
      self.response.out.write(result)
      pass
    pass
  pass


class Root(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    if not is_appropriate_user(user):
      self.response.write(render_message('Failure',
                                         'Not open to public. Sorry.'))
      return

    channels = Channel.query(ancestor=get_world_ancestor_key()).fetch()
    
    template_file = '/templates/root.tmpl'
    template = JINJA_ENVIRONMENT.get_template(template_file)
    self.response.write(template.render({'channels' : channels}))
    pass
  pass


app = webapp2.WSGIApplication([
    ('/RegisterChannelId/(.+)?', RegisterChannelId),
    ('/SendMessage', SendMessage),
    ('/', Root),
], debug=True)
