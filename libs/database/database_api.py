import mysql.connector
from libs.database.datalayer.dl_items import DL_items

class DBAPI:

    def __init__(self, db_config, tag):
        self._teaserCount = 0
        self._pageNumber = 0
        self._pageSize = 20
        self._posterWidth = 480
        self._quality_id = 3

        if tag is not None:
            if 'pageNumber' in tag:
                self._pageNumber = tag.get('pageNumber')
            if 'pageSize' in tag:
                self._pageSize = tag.get('pageSize')
            if 'posterWidth' in tag:
                self._posterWidth = tag.get('posterWidth')
            if 'quality' in tag:
                self._quality_id = tag.get('quality')
            if 'suppress_signLanguage' in tag:
                self._suppress_signLanguage = tag.get('suppress_signLanguage')
            if 'suppress_durationSeconds' in tag:
                self._suppress_durationSeconds = tag.get('suppress_durationSeconds')

        self._cnx = mysql.connector.Connect(**db_config)

    def __del__(self):
        self._cnx.close()

    def getTeaser(self):
        query = {
            'project': 'HARTABERFAIR',
            'quality': self._quality_id,
            'page': self._pageNumber + 1,
            'pageSize': self._pageSize,
            'posterWidth': self._posterWidth
        }

        if self._suppress_signLanguage:
            query['tag'] = 'None'

        if self._suppress_durationSeconds:
            query['minDuration'] = self._suppress_durationSeconds

        return DL_items.getItemView(self._cnx, query)

    def getPagination(self):
        query = {
            'project': 'HARTABERFAIR',
            'quality': self._quality_id
        }

        if self._suppress_signLanguage:
            query['tag'] = 'None'

        if self._suppress_durationSeconds:
            query['minDuration'] = self._suppress_durationSeconds

        item_count = DL_items.getCount(self._cnx, query)

        return {
            'pageNumber': self._pageNumber,
            'pageSize': self._pageSize,
            'totalElements': item_count
        }
