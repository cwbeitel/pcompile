#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helper import make_dottable_dict
from pcompile.helper import strip_internal, dict_to_str
from pcompile.solution import Solution


class SolutionDB(object):
    '''Object for managing interface with inventory database.

    Note
    ----
    The interface to this object should not change significantly over time.
    The way this object interfaces with the inventory database will likely
    change.

    Example
    -------
    .. code-block:: python
        s = SolutionDB()
        s.find()

    '''

    def __init__(self, collection='solutions',
                db_name='',
                port=53607,
                ip='',
                username='',
                password=''):

        import os
        import json
        from pymongo import MongoClient

        uri = 'mongodb://'+username+':'+password+'@'+ip+':'+str(port)+'/'+db_name+'?authMechanism=MONGODB-CR';

        self.db = MongoClient(uri)[db_name][collection]

        '''
        else:
            self.db = MongoClient(ip, port)[db_name][collection]
        '''

        self.username = username
        self.collection = collection
        self.port = port
        self.ip = ip
        self.db_name = db_name

    def find_solution_set(self, components, return_one=False, require_hit=False):

        print components

        from pcompile.helper import unserialize

        all_hits = {}

        filt = ['unknown', 'Unknown', 'unknown:micromolar', 'Unknown:micromolar', '?:x']
        # For now, it will ignore any hit with a concentration or component concentration
        # of one of the above types.

        for comp in components:

            query = dict_to_str(strip_internal(comp))
            classif = dict_to_str(strip_internal(comp))['classification']

            sol_query = {'classification': classif}
            comp_query = {'components': {'$elemMatch': {'classification': classif}}}
            query = {'$or':[sol_query,comp_query]}

            hits = self.db.find(query)

            for hit in hits:

                unique_identifier = hit['_id']

                if unique_identifier not in all_hits:

                    if hit['concentration'] not in filt:

                        f=0
                        #for hitcomp in hit['components']:
                        #    print hitcomp
                        #    if hitcomp['concentration'] in filt:
                        #        f=0

                        if f==0:
                            hit_stripped = strip_internal(hit)
                            all_hits[unique_identifier] = Solution(**hit_stripped)
                            print all_hits[unique_identifier].name
                            print all_hits[unique_identifier].components
                            all_hits[unique_identifier].update_units()

        if require_hit and (len(all_hits.values()) == 0):
            raise Exception('Did not find DB hit for query with require_hit enabled.')

        if (return_one) and (len(all_hits.values())>=1):
            return all_hits.values()[0]
        else:
            return all_hits.values()

    def find_by_location(self, location, return_one=True, require_hit=True):
        '''

        TODO: Deal with whether to have a return one flag or always return
        an array. To accept a solution as a query or to require a naked location.
        I prefer to be able to have as much of the logic that is repeated
        across different protocols handled by the underlying framework and thus
        favor find(solution, by="location") or find(solution, by="components")
        over location=sample['container']['location'];
        find_by_location(location)[0].

        '''

        print location

        hits = list(self.db.find({'container.location': location}))
        if len(hits) > 1:
            print 'Found more than one DB entry for location query.'
            print 'Theres probably something wrong with your database.'
        hit = hits[0]

        if require_hit and (len(hits) == 0):
            raise Exception('Did not find DB hit for query with require_hit enabled.')

        stripped = strip_internal(hit)
        s = Solution(**stripped)
        s.update_units() # Note - this will fail if the thing being passed in
        # has a dna concentration of unknown or string None...
        return s

# DEV
class ReactionDB(object):
    def __init__(self,
                 collection='protocols',
                 db_name='scilab-test',
                 port=27017,
                 ip="localhost"):

        import pymongo
        client = pymongo.MongoClient(ip, port)
        self.db = client[db_name][collection]

    def update(self, protocol):
        self.db.remove({'name':protocol['name']})
        self.db.insert({'name':protocol['name'], 'contents':protocol})




