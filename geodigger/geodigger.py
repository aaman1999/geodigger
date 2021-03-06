"""A base class to use for API geolocation data mining tools."""

import time
import pymongo
from Crypto.Hash import SHA256

class GeoDigger(object):
    def __init__(self, config, logfile):
        self.config = config
        self.mongodb = config['mongodb']
        self.logfile = open(logfile, "a+")
        # Override the namespace in your child class.
        self.namespace = "unknown"
        # Mongo connection setup
        if self.mongodb['port'] == '': self.mongodb['port'] = None
        conn = pymongo.Connection(self.mongodb['host'],
                self.mongodb['port'])
        db = conn[self.mongodb['database']]
        self.collection = db[self.mongodb['collection']]
        self.collection.create_index([('loc', pymongo.GEOSPHERE)])

    def save(self, userID, time, coordinates, text=''):
        """Write geolocation data to the Mongo database.
        Note: coordinates should be an ordered list in [longitude, latitude] format.
        """
        self.collection.insert({
                'userID': userID,
                'time': time,
                'loc': {
                    'type': 'Point',
                    'coordinates': coordinates,
                    },
                'source': self.namespace,
                'text': text,
                })

    def anonymizeUser(self, username):
        """Return a sanitized unique ID given a namespace and username.
        Uses SHA-256 (PyCrypto).
        """
        return SHA256.new('%s:%s' % (self.namespace,
                    username)).hexdigest()

    def log(self, message):
        self.logfile.write("[%s] %s\r\n" % (time.asctime(), message))
        self.logfile.flush()
