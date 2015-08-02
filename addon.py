#!/usr/bin/env python
"""
Zoneminder XBMC addon
http://github.com/dankolbrs/plugin.video.zoneminder
"""

import sys, urllib, urllib2, re, os
import xbmcplugin, xbmcgui, xbmcaddon

from PIL import Image

from BeautifulSoup import BeautifulStoneSoup
import BeautifulSoup

__settings__ = xbmcaddon.Addon(id='plugin.video.zoneminder')
__language__ = __settings__.getLocalizedString


def clear_thumbnails():
    #clear all existing thumbnails
    thumbnails_dir = os.path.join(__settings__.getAddonInfo('path'),
            'resources',
            'thumbnails')
    for item in os.listdir(thumbnails_dir):
        os.remove(thumbnails_dir + "/" + item)

def get_monitors():
    #get the available monitors

    #clear existing thumbnails
    clear_thumbnails()

    #url of the zoneminder instance
    zone_url = str(__settings__.getSetting("zone_url"))

    #removing the /zm which is needed to call the CGI
    raw_url = zone_url.replace("/zm", "")

    #open the url, parse it for monitor names
    data = urllib2.urlopen(zone_url)
    console = BeautifulSoup.BeautifulSoup(data)
    monitor_list = []

    for row in console.findAll('td', {"class" : "colName"}):
        monitor_list.append(row.text)

    #loop through the found monitors, add them to the listing
    i = 0
    for item in monitor_list:
        i += 1

        thumbnails_dir = os.path.join(__settings__.getAddonInfo('path'),
                        'resources',
                        'thumbnails')


        single_image = urllib.urlretrieve(raw_url + "/cgi-bin-zm/nph-zms?mode=single&monitor=" + str(i),
                                            thumbnails_dir + "/" + "thumb" + str(i) + ".jpg")[0]

        #get a thumbnail of stream
        thumbnailImage = Image.open(single_image)
        thumbnailImage.thumbnail((250,250), Image.ANTIALIAS)
        thumbnailImage.save(single_image, 'JPEG', quality=90)

        fps = str(__settings__.getSetting("frames_per_second"))

        list_info = xbmcgui.ListItem(
            item,
            '',
            iconImage = single_image,
            thumbnailImage = single_image)
        list_info.setProperty('IsPlayable', 'true')
        list_info.setInfo(type='Video', infoLabels="info")
        xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url = "http://zoneminder.dankolb.net/cgi-bin-zm/nph-zms?mode=jpeg&monitor=" + str(i) + "&maxfps=" + fps,
            listitem = list_info,
            isFolder= False)
def get_params():
    """
    Retrieves the current existing parameters from XBMC.
    """
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


PARAMS = get_params()
URL = None
NAME = None
MODE = None
PAGE = None

try:
    URL = urllib.unquote_plus(PARAMS["url"])
except:
    pass
try:
    NAME = urllib.unquote_plus(PARAMS["name"])
except:
    pass
try:
    MODE = int(PARAMS["mode"])
except:
    pass
try:
    PAGE = int(PARAMS["page"])
except:
    PAGE = 0

if MODE == None or URL == None or len(URL) < 1:
    get_monitors()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
