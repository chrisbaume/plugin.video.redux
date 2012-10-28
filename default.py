import cgi, sys, string, xbmc, xbmcplugin, xbmcgui, json, urllib, urllib2

def readParams(input):
  args = cgi.parse_qs(input[1:])
  params = {}
  params['thisplugin'] = args.get('thisplugin', [None])[0]
  params['username'] = args.get('username', [None])[0]
  params['password'] = args.get('password', [None])[0]
  params['diskref']  = args.get('diskref', [None])[0]
  return params

# removes duplicates from a list whilst preserving the order
def f7(seq):
  seen = set()
  seen_add = seen.add
  return [ x for x in seq if x not in seen and not seen_add(x)]

# sets up http basic auth
def login(username, password):
  auth_handler = urllib2.HTTPBasicAuthHandler()
  auth_handler.add_password(realm='Redux',
                          uri='http://devapi.bbcredux.com',
                          user=username,
                          passwd=password)
  opener = urllib2.build_opener(auth_handler)
  urllib2.install_opener(opener)

# process the given GET command
def process(query):
  req = urllib2.Request(url='http://devapi.bbcredux.com/'+query)
  req.add_header('Accept','application/json')
  try:
    res = urllib2.urlopen(req)
  except urllib2.HTTPError, e:
    message = 'HTTP Error '+str(e.code)
    if e.code == 401:
      message = 'Wrong username or password'
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('Error', message)
  return res

# pop up a dialog with a given message
def alert(message):
  dialog = xbmcgui.Dialog()
  ok = dialog.ok('Error', message)

# prompt user for search and return text
def searchDialog():
  kb = xbmc.Keyboard('', 'Search for')
  kb.doModal()
  if not kb.isConfirmed():
      return None;
  searchterm = kb.getText().strip()
  return searchterm

# convert seconds to hh:mm:ss
def seconds2duration(secs):
  mins = floor(secs/60)
  secs = secs - (mins*60)
  hours = floor(mins/60)
  mins = mins - (hours*60)
  return str(hours)+':'+str(mins)+':'+str(secs)

# grab plugin info
thisPlugin = int(sys.argv[1])
username = xbmcplugin.getSetting(thisPlugin,'username')
password = xbmcplugin.getSetting(thisPlugin,'password')

# if a programme has been selected
if sys.argv[2] is not '':

  alert('Reading params')
  params = readParams(sys.argv[2])
  alert('Done. Logging in.')
  login(params['username'], params['password'])
  alert('Done. Querying database.')
  res = process('programme/'+params['diskref'])
  alert('Done. Parsing JSON')
  jres = json.dump(json.loads(res.read()))
  alert('Done. Writing results')
  #sys.stderr.write(str(jres))

  #if '2m-mp4' in jres['media']:
    #alert('mp3')
  #  url = jres['media']['2m-mp4']['uri']
  #elif 'mp4-hi' in jres['media']:
    #alert('mp4-hi')
  #  url = jres['media']['mp4-hi']['uri']
  #elif 'mp4-lo' in jres['media']:
    #alert('mp4-lo')
  #  url = jres['media']['mp4-lo']['uri']
  #elif 'mp3' in jres['media']:
  #  url = jres['media']['mp3']['uri']
  #else:
    #alert('other')
  url = jres['media']['m2ts']['uri']
  sys.stderr.write('URL: '+url)
  alert('Done')
  #xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play(url)
  #xbmcplugin.endOfDirectory(int(params['thisplugin']))

# if a programme hasn't been selected
else:

  # login
  login(username, password)

  # Check username/password is correct
  process('user')

  # display seach dialog and process request
  searchText = searchDialog()
  searchText = string.replace(searchText, ' ', '+')
  res = process('search?q='+searchText)
  jres = json.loads(res.read())

  for item in jres['results']:
    listItem = xbmcgui.ListItem(item['title']+' ('+item['date']+')', item['description'])
    #if item['depiction'] is not None:
    #  listItem.setThumbnailImage(item['depiction'])
    d = {}
    d['diskref'] = item['diskref']
    d['username'] = username
    d['password'] = password
    d['thisplugin'] = thisPlugin
    params = urllib.urlencode(d, True)
    xbmcplugin.addDirectoryItem(thisPlugin, sys.argv[0]+'?'+params, listItem)
  xbmcplugin.endOfDirectory(thisPlugin)
