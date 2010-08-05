from app.core.db._tables import BasicTable
from sqlalchemy.orm import mapper

latestVersion = 0

class QualityTable(BasicTable):
    def __repr__(self):
        return BasicTable.__repr__(self) + self.name + str(self.version)

class QualityTemplateTable(BasicTable):
    def __repr__(self):
        return BasicTable.__repr__(self) + self.name + str(self.version)


def bootstrap(db):

    # movie quality table
    columns = [
        [['label', 's'], {}],
        [['order', 'i'], {}]
    ]
    qualityTable = db.getAutoIdTable('core_quality_quality', columns)
    mapper(QualityTable, qualityTable)

    # movie quality template table
    columns = [
        [['name', 's'], {}],
        [['order', 'i'], {}],
        [['wait_for', 'i'], {}],
        [['quality', 'i', 'core_movies_quality.id'], {}],
        [['mark_complete', 'i'], {}]
    ]
    qualityTemplateTable = db.getAutoIdTable('core_quality_template', columns)
    mapper(QualityTemplateTable, qualityTemplateTable)

    # movie quality table
    columns = [
        [['quality', 's'], {}],
        [['template', 'i'], {}]
    ]
    qualityTable = db.getAutoIdTable('core_quality_quality', columns)
    mapper(QualityTable, qualityTable)
