import sys, string, xbmc, xbmcplugin, xbmcgui, json, urllib2

def sendToXbmc(listing):
  global thisPlugin
  for item in listing:
    listItem = xbmcgui.ListItem(item)
    xbmcplugin.addDirectoryItem(thisPlugin,'',listItem)
  xbmcplugin.endOfDirectory(thisPlugin)

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

thisPlugin = int(sys.argv[1])
username = xbmcplugin.getSetting(thisPlugin,'username')
password = xbmcplugin.getSetting(thisPlugin,'password')
login(username, password)

# Check username/password is correct
process('user')

searchText = searchDialog()
searchText = string.replace(searchText, ' ', '+')
res = process('search?q='+searchText)
jres = json.loads(res.read())

for item in jres['results']:
  listItem = xbmcgui.ListItem(item['title']+' ('+item['date']+')')
  xbmcplugin.addDirectoryItem(thisPlugin,'',listItem)
xbmcplugin.endOfDirectory(thisPlugin)
