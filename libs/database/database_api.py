class DBAPI:

    def __init__(self, db_config, tag):
        self._db_config = db_config
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

    def getTeaser(self):
        pass
    # SELECT * FROM (
    #
    # SELECT ROW_NUMBER() OVER (ORDER BY broadcastOn_date DESC) AS rowNumber, viewItems.*
    #     FROM viewItems
    #     WHERE project = 'HARTABERFAIR'
    #
    # ) AS t
    # WHERE t.rowNumber BETWEEN 1 AND 20;



    def getPagination(self):
        pass