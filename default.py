import sys, xbmc, xbmcplugin, xbmcgui, xbmcaddon, json
from urllib import urlencode
from urllib2 import urlopen
from urlparse import parse_qs

API_URL='https://i.bbcredux.com'
formatMap = {'Original stream': 'ts',
			'Stripped stream': 'strip',
			'H264 large': 'h264_mp4_hi_v1.1',
			'H264 small': 'h264_mp4_lo_v1.0',
			'MP3': 'MP3_v1.0'}

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)

addon = xbmcaddon.Addon()
username = addon.getSetting('username')
password = addon.getSetting('password')
format = addon.getSetting('format')

def alert(message):
	xbmcgui.Dialog().ok('Error', message)

def login(username, password):
	data = json.loads(urlopen(url=API_URL+'/user/login?'+urlencode({'username': username, 'password': password})).read())
	if data['success']: return data['token']
	alert('Wrong username or password')
	sys.exit(-1)

def searchDialog():
	kb = xbmc.Keyboard('', 'Search for')
	kb.doModal()
	if not kb.isConfirmed(): return None;
	searchterm = kb.getText().strip()
	return searchterm

if mode is None:
	token = login(username, password)
	data = json.loads(urlopen(API_URL+'/asset/search?'+urlencode({'q': searchDialog(), 'titleonly': '1', 'token': token})).read())
	for item in data['results']['assets']:
		listItem = xbmcgui.ListItem(item['name']+' - '+item['description'])
		d = {'key': item['key'],
			'reference': item['reference'],
			'token': token,
			'mode': 'play'}
		xbmcplugin.addDirectoryItem(addon_handle, base_url+'?'+urlencode(d), listItem)
	xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0] == 'play':
	reference = args.get('reference', None)[0]
	key = args.get('key', None)[0]
	xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play(API_URL+'/asset/media/'+reference+'/'+key+'/'+formatMap[format]+'/file')
