import mysql.connector

from libs.database.database_core import databaseCore


class DL_items:

    @staticmethod
    def getItemView(cnx, query):
        items = []
        innerWhereClause = 'project = %s'
        parameter = (query['project'], )
        if 'tag' in query:
            innerWhereClause += ' AND tag = %s'
            parameter += (query['tag'], )

        if 'minDuration' in query:
            innerWhereClause += ' AND duration > %s'
            parameter += (query['minDuration'], )

        if query['quality'] == 5:
            innerWhereClause += ' AND best_quality = 1'
        elif query['quality'] == 4:
            innerWhereClause += ' AND quality = %s'
            parameter += ('1080p',)
        elif query['quality'] == 3:
            innerWhereClause += ' AND quality = %s'
            parameter += ('720p',)
        elif query['quality'] == 2:
            innerWhereClause += ' AND quality = %s'
            parameter += ('540p',)
        elif query['quality'] == 1:
            innerWhereClause += ' AND quality = %s'
            parameter += ('360p',)
        elif query['quality'] == 0:
            innerWhereClause += ' AND quality = %s'
            parameter += ('270p',)

        minItem = (query['page'] - 1) * query['pageSize'] + 1
        maxItem = minItem + query['pageSize'] - 1
        parameter += (minItem, maxItem, )

        sQuery = f'    SELECT * FROM (' \
                 f'        SELECT ROW_NUMBER() OVER (ORDER BY broadcastOn_date DESC) AS rowNumber, viewItems.title' \
                 f'              ,viewItems.plot, viewItems.poster_url, viewItems.broadcastOn_date' \
                 f'              ,viewItems.availableTo_date, viewItems.duration, viewItems.quality, viewItems.hoster' \
                 f'              ,viewItems.url' \
                 f'            FROM viewItems' \
                 f'            WHERE {innerWhereClause}' \
                 f'    ) AS t' \
                 f'    WHERE t.rowNumber BETWEEN %s AND %s;'

        cursor = databaseCore.executeReader(cnx, sQuery, parameter)
        if cursor is not None:
            rows = cursor.fetchall()
            for row in rows:
                items.append({
                    'title': row[1],
                    'plot': row[2],
                    'poster': row[3].replace('{width}', str(query['posterWidth'])),
                    'broadcastedOn': row[4],
                    'availableTo': row[5],
                    'duration': row[6],
                    'quality': row[7],
                    'hoster': row[8],
                    'url': row[9]
                })

        cursor.close()

        return items

    @staticmethod
    def getCount(cnx, query):
        whereClause = 'project = %s'
        parameter = (query['project'],)
        if 'tag' in query:
            whereClause += ' AND tag = %s'
            parameter += (query['tag'],)

        if 'minDuration' in query:
            whereClause += ' AND duration > %s'
            parameter += (query['minDuration'],)

        if query['quality'] == 5:
            whereClause += ' AND best_quality = 1'
        elif query['quality'] == 4:
            whereClause += ' AND quality = %s'
            parameter += ('1080p',)
        elif query['quality'] == 3:
            whereClause += ' AND quality = %s'
            parameter += ('720p',)
        elif query['quality'] == 2:
            whereClause += ' AND quality = %s'
            parameter += ('540p',)
        elif query['quality'] == 1:
            whereClause += ' AND quality = %s'
            parameter += ('360p',)
        elif query['quality'] == 0:
            whereClause += ' AND quality = %s'
            parameter += ('270p',)

        sQuery = f'SELECT COUNT(*) FROM viewItems WHERE {whereClause};'

        return databaseCore.executeScalar(cnx, sQuery, parameter)


