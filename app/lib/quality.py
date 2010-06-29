class Quality:

    types = {
        0: {'name': '1080p'},
        1: {'name': '720p', 'default': True},
        2: {'name': 'dvdrip'},
        3: {'name': 'ts'},
        4: {'name': 'cam'}
    }

    def all(self):
        return self.types
