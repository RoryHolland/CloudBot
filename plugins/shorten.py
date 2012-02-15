# # Lukeroge
from util import hook, http

try:
  from re import match
  from urllib2 import urlopen, Request, HTTPError
  from urllib import urlencode
  
except ImportError, e:
  raise Exception('Required module missing: %s' % e.args[0])
 
def tiny(url, user, apikey):
  try:
    params = urlencode({'longUrl': url, 'login': user, 'apiKey': apikey, 'format': 'json'})
    j = http.get_json("http://api.bit.ly/v3/shorten?%s" % params)
    if j['status_code'] == 200:
      return j['data']['url']
    raise Exception('%s'%j['status_txt'])
  except HTTPError, e:
    return "Invalid URL!"

@hook.command
def shorten(inp, bot = None):
  ".shorten <url> - Makes an j.mp/bit.ly shortlink to the url provided"
  api_user = bot.config.get("api_keys", {}).get("bitly_user", None)
  api_key = bot.config.get("api_keys", {}).get("bitly_api", None)
  if api_key is None:
      return "error: no api key set"
  return tiny(inp, api_user, api_key)
