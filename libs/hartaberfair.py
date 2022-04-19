# -*- coding: utf-8 -*-
# Copyright 2022 WebEye
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import json
import sys
import urllib
import urllib.parse

from libs.database.database_api import DBAPI
from libs.kodion.addon import Addon
from libs.ardmediathek_api import ARDMediathekAPI
from libs.kodion.gui_manager import *
from libs.kodion.utils import Utils as kodionUtils
from libs.utils import utils
from libs.translations import *


class HardAberFair:

    def __init__(self):

        # -- Constants ----------------------------------------------
        self._ADDON_ID = 'plugin.video.hartaberfair'
        self._BASEURL = 'https://api.ardmediathek.de/page-gateway/widgets/daserste/asset' \
                        '/Y3JpZDovL3dkci5kZS9oYXJ0IGFiZXIgZmFpcg?pageNumber={pageNumber}&pageSize={' \
                        'pageSize}&embedded=true&seasoned=false&seasonNumber=&withAudiodescription=false' \
                        '&withOriginalWithSubtitle=false&withOriginalversion=false '

        # ADDONTHUMB = utils.translatePath('special://home/addons/' + ADDON_ID + '/resources/assets/icon.png')
        width = getScreenWidth()
        if width >= 2160:
            fanart = f'special://home/addons/{self._ADDON_ID}/resources/assets/2160p/fanart.jpg'
        elif width >= 1080:
            fanart = f'special://home/addons/{self._ADDON_ID}/resources/assets/1080p/fanart.jpg'
        else:
            fanart = f'special://home/addons/{self._ADDON_ID}/resources/assets/720p/fanart.jpg'

        self._FANART = kodionUtils.translatePath(fanart)
        self._POSTERWIDTH = int(width/3)

        self._DEFAULT_IMAGE_URL = ''

        self._guiManager = GuiManager(sys.argv[1], self._ADDON_ID, self._DEFAULT_IMAGE_URL, self._FANART)
        self._guiManager.setContent('movies')

        # -- Settings -----------------------------------------------
        addon = Addon(self._ADDON_ID)
        self._t = Translations(addon)
        self._quality_id = int(addon.getSetting('quality'))
        self._PAGESIZE = int(addon.getSetting('page_itemCount'))
        self._skip_itemPage = (addon.getSetting('skip_itemPage') == 'true')
        self._suppress_signLanguage = (addon.getSetting('suppress_signLanguage') == 'true')
        self._suppress_durationSeconds = int(addon.getSetting('suppress_duration'))

        self._db_enabled = (addon.getSetting('database_enabled') == 'true')
        self._db_config = None
        if self._db_enabled:
            self._db_config = {
                'host': addon.getSetting('db_host'),
                'port': int(addon.getSetting('db_port')),
                'username': addon.getSetting('db_username'),
                'password': addon.getSetting('db_password')
            }
        t = 0

    def setItemView(self, url, tag=None):

        tag = {
            'posterWidth': self._POSTERWIDTH,
            'quality': self._quality_id
        }

        API = ARDMediathekAPI(url, tag)
        item = API.getItem()
        if item is not None:
            title = item['title']

            infoLabels = {
                'Title': title,
                'Plot': item['plot'],
                'Date': item['broadcastedOn'],
                'Aired': item['broadcastedOn'],
                'Duration': item['duration']
            }

            self._guiManager.addItem(title=title, url=item['url'], poster=item['poster'], _type='video',
                                     infoLabels=infoLabels)

    def _isValidTeaser(self, teaser):
        if self._suppress_signLanguage and '(mit Gebärdensprache)' in teaser['title']:
            return False

        if self._suppress_durationSeconds > 0 and teaser['duration'] < self._suppress_durationSeconds:
            return False

        return True

    def addItemPage(self, teaser):
        title = teaser['title']
        duration, unit = utils.getDuration(int(teaser['duration']))
        duration = {
            'hours': duration + f' {self._t.getString(HOURS)}',
            'minutes': duration + f' {self._t.getString(MINUTES)}',
            'seconds': duration + f' {self._t.getString(SECONDS)}',
        }[unit]

        broadcastedOn = utils.getDateTime(teaser['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y, '
                                                                                                  '%H:%M:%S')
        availableTo = utils.getDateTime(teaser['availableTo'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y, '
                                                                                              '%H:%M:%S')
        plot = f'[B]{title}[/B]\n\n[B]{self._t.getString(DURATION)}[/B]: {duration}\n' \
               f'[B]{self._t.getString(BROADCASTEDON)}[/B]: {broadcastedOn}\n' \
               f'[B]{self._t.getString(AVAILABLETO)}[/B]: {availableTo} '

        infoLabels = {
            'Title': title,
            'Plot': str(plot),
            'Date': teaser['broadcastedOn'],
            'Aired': teaser['broadcastedOn'],
            'Duration': teaser['duration']
        }

        self._guiManager.addDirectory(title=title, poster=teaser['poster'], _type='Video',
                                      infoLabels=infoLabels, args=self.buildArgs('item', teaser['url']))

    def addClip(self, teaser):
        url = teaser['url']
        self.setItemView(url, None)

    def setHomeView(self, url, tag=None):

        if not self._db_enabled:
            API = ARDMediathekAPI(url, tag)
        else:
            tag['quality'] = self._quality_id
            tag['suppress_signLanguage'] = self._suppress_signLanguage
            tag['suppress_durationSeconds'] = self._suppress_durationSeconds
            API = DBAPI(self._db_config, tag)

        teasers = API.getTeaser()
        pagination = API.getPagination()

        if teasers is not None:
            for teaser in teasers:
                if self._isValidTeaser(teaser):
                    {
                        False: self.addItemPage,
                        True: self.addClip
                    }[self._skip_itemPage](teaser)

            if pagination is not None:
                pageNumber = int(pagination['pageNumber'])
                pageSize = int(pagination['pageSize'])
                totalElements = int(pagination['totalElements'])

                if totalElements > ((pageNumber + 1) * pageSize):
                    strPageNumber = str(pageNumber + 2)
                    tag = {
                        'pageNumber': pageNumber + 1,
                        'pageSize': self._PAGESIZE,
                        'posterWidth': self._POSTERWIDTH
                    }
                    self._guiManager.addDirectory(title=f'Page {strPageNumber}',
                                                  args=self.buildArgs('home', self._BASEURL, json.dumps(tag)))

    @staticmethod
    def get_query_args(s_args):
        args = urllib.parse.parse_qs(urllib.parse.urlparse(s_args).query)

        for key in args:
            args[key] = args[key][0]
        return args

    @staticmethod
    def buildArgs(method, url=None, tag=None):

        item = {
            'method': method,
        }

        if url is not None:
            item['url'] = url

        if tag is not None:
            item['tag'] = tag

        return item

    def DoSome(self):

        args = self.get_query_args(sys.argv[2])
        if args is None or args.__len__() == 0:
            tag = {
                'pageNumber': 0,
                'pageSize': self._PAGESIZE,
                'posterWidth': self._POSTERWIDTH
            }

            args = self.buildArgs('home', self._BASEURL, tag)

        method = args.get('method')
        url = args.get('url')
        tag = args.get('tag')

        if tag is not None and isinstance(tag, str):
            tag = json.loads(tag)

        {
            'home': self.setHomeView,
            'item': self.setItemView
        }[method](url, tag)

        # self._guiManager.addSortMethod(GuiManager.SORT_METHOD_NONE)
        # self._guiManager.addSortMethod(GuiManager.SORT_METHOD_DATE)
        self._guiManager.endOfDirectory()
