from app.config.db import QualityTemplate, QualityTemplateType, Session as Db
from sqlalchemy.sql.expression import or_
import cherrypy
import logging

log = logging.getLogger(__name__)

class Qualities:

    types = {
        '1080p':    {'key': '1080p', 'minSize': 5000, 'order':1, 'label': '1080P', 'alternative': []},
        '720p':     {'key': '720p', 'minSize': 3500, 'order':2, 'label': '720P', 'alternative': []},
        'brrip':    {'key': 'brrip', 'minSize': 700, 'order':3, 'label': 'BR-Rip', 'alternative': ['bdrip']},
        'dvdr':     {'key': 'dvdr', 'minSize': 3000, 'order':4, 'label': 'DVD-R', 'alternative': []},
        'dvdrip':   {'key': 'dvdrip', 'minSize': 600, 'order':5, 'label': 'DVD-Rip', 'alternative': []},
        'scr':      {'key': 'scr', 'minSize': 600, 'order':6, 'label': 'Screener', 'alternative': ['dvdscr']},
        'r5':       {'key': 'r5', 'minSize': 600, 'order':7, 'label': 'R5', 'alternative': []},
        'tc':       {'key': 'tc', 'minSize': 600, 'order':8, 'label': 'TeleCine', 'alternative': ['telecine']},
        'ts':       {'key': 'ts', 'minSize': 600, 'order':9, 'label': 'TeleSync', 'alternative': ['telesync']},
        'cam':      {'key': 'cam', 'minSize': 600, 'order':10, 'label': 'Cam', 'alternative': []}
    }

    def default(self):
        return cherrypy.config.get('config').get('Quality', 'default')

    def conf(self, option):
        return cherrypy.config.get('config').get('Quality', option)

    def all(self, custom = None, enabled = None):
        q = Db.query(QualityTemplate).order_by(QualityTemplate.order)

        # Get only enabled
        if enabled:
            q = q.filter(~QualityTemplate.name.in_(self.conf('hide').split(',')))

        # Only show custom
        if custom != None:
            q = q.filter(QualityTemplate.custom == custom)

        return q.all()

    def getTypes(self):
        return sorted(self.types.items(), key = lambda type: type[1]['order'])

    def getTemplates(self):

        templates = []

        for template in self.all(custom = True):

            temp = {
                'id': template.id,
                'name': template.label,
                'waitFor': template.waitFor,
                'types': []
            }

            for type in template.types:
                temp['types'].append({
                    'id': type.id,
                    'type': type.type,
                    'markComplete': type.markComplete
                })
            templates.append(temp)

        return templates

    def saveTemplates(self, templates):
        log.debug('Saving Templates %s' % templates)

        # get all items
        delete = { 'templates': [], 'types': [] }
        for item in self.all(custom = True):
            delete['templates'].append(item.id)
            for type in item.types:
                delete['types'].append(type.id)

        for template in templates:

            # Don't delete
            try:
                delete['templates'].remove(int(template['id']))
            except (ValueError, TypeError):
                pass

            if int(template['id']) == 0:
                template['id'] = template['name']

            for type in template['types']:
                # Don't delete
                try:
                    delete['types'].remove(int(type['id']))
                except (ValueError, TypeError):
                    pass

            self.create(template['id'], template['name'], template['types'], waitFor = template['waitFor'])

        # remove all non used custom
        if delete['templates']:
            [Db.delete(x) for x in Db.query(QualityTemplate).filter(QualityTemplate.id.in_(delete['templates'])).all()]
            Db.flush()
        if delete['types']:
            [Db.delete(x) for x in Db.query(QualityTemplateType).filter(QualityTemplateType.id.in_(delete['types'])).all()]
            Db.flush()


    def getAlternatives(self, type):
        if self.types.get(type):
            return self.types.get(type).get('alternative')

        return []

    def create(self, name, label, types, waitFor = 0, custom = True, order = 0):

        newQ = QualityTemplate()
        exists = Db.query(QualityTemplate).filter(or_(QualityTemplate.name == name, QualityTemplate.id == name)).first()
        if not exists:
            log.info('Creating custom=%s quality: %s' % (custom, name))
            newQ.name = name
            newQ.label = label
            newQ.custom = custom
            newQ.waitFor = waitFor
            newQ.order = order
            Db.add(newQ)
            Db.flush()
            exists = Db.query(QualityTemplate).filter_by(name = name).first()
        else:
            log.debug('Updating custom=%s quality: %s' % (custom, name))
            exists.label = label
            exists.waitFor = waitFor
            Db.flush()

        nr = 1
        for type in types:

            # Update if needed
            newT = Db.query(QualityTemplateType).filter_by(quality = exists.id, type = type['type']).first()
            if not newT:
                newT = QualityTemplateType()

            newT.quality = exists.id
            newT.order = nr
            newT.type = type['type']
            newT.markComplete = type['markComplete']
            nr += 1
            Db.add(newT)
            Db.flush()

        return True

    def initDefaults(self):
        log.info('Creating default quality settings, if needed')

        for key, type in self.types.iteritems():
            self.create(key, type['label'], [{
                'type': key,
                'markComplete': True
            }], waitFor = 0, custom = False, order = type['order'])
