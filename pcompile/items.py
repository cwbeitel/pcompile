#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile import ureg
from math import floor
from numpy.random import random
from copy import copy


class NameRegistry(object):

    def __init__(self, names=set()):
        self.names=names
        assert isinstance(self.names, set)

    def new(self, tag=None):
        '''Generate a potentially unique name and check if its in the name
        registry. If not, return it. If so, keep generating names.'''

        max_iterations = 100
        i = 0

        while i < max_iterations:

            name = self.generate(tag)

            if name not in self.names:

                self.names.add(name)
                return name

            i += 1

        return None

    def generate(self, tag=None):
        if tag is None or len(tag) == 0:
            name = 'unlabeled_container_'
        else:
            name = str(tag) + "_"
        name += str(int(floor(random()*1e6)))
        return name


_PCR_96 = {'ctype':'96-pcr', 'children':[],
           'child_ctype':'96-pcr', 'free':True,
           'parent_only':True, 'children_free':96, 'name':None,
           'max_volume': 200 * ureg.microliter, 'container_ref':None,
           'well_ref':None}
_PCR_96_WELL = {'ctype':'96-pcr', 'parent_name':None, 'free':True,
                'max_volume':200 * ureg.microliter,
                'parent_index':None}
for i in range(0,96):
    well = copy(_PCR_96_WELL)
    well['parent_index'] = i
    _PCR_96['children'].append(well)

_MICRO_15 = {'ctype':'micro-1.5', 'children':[
                {'ctype':'96-pcr', 'parent_name':None, 'free':True,
                 'max_volume':200 * ureg.microliter,
                 'parent_index':0}
                 ],
             'name':'', 'child_ctype':'micro-1.5',
             'free':True, 'parent_only':True,
             'children_free':1,
             'max_volume':1500 * ureg.microliter,
             'container_ref':None,
             'well_ref':None}

_CONTAINERS = {'96-pcr': _PCR_96,
               'micro-1.5': _MICRO_15}

class Items(object):

    def __init__(self,
                 containers=[],
                 name_registry=NameRegistry()):

        self.containers = containers
        self.name_registry = name_registry

    def allocate(self, env, ctype):
        '''Find an instance of ctype in self.containers and return it.

        Note: This way of representing container relationships is wildly
        unecessary and will be updated to use the container > well > solution
        model in place of the current parent = container > child = well >
        solution model.
        '''

        for i,c in enumerate(self.containers):

            if c['ctype'] == ctype:

                #print 'found a container of the right ctype'
                #print c['free']

                if c['free']:

                    #print 'container is free'

                    if ('parent_only' not in c) or (not c['parent_only']):

                        #print 'is right ctype, is free, does not have children'

                        c['free'] = False
                        # Container ref should have already been created
                        c['well_ref'] = c['container_ref'].well(0)
                        return c

                    elif ('child_ctype' in c and c['child_ctype'] == ctype):

                        #print 'examining containers contained by parent'

                        for j,ch in enumerate(c['children']):

                            if ch['free']:

                                ch['free'] = False

                                # If this was the last well in the parent plate
                                if ch['parent_index'] == len(c['children']):

                                    c['free'] = False

                                ch['container_ref'] = c['container_ref']
                                ch['well_ref'] = ch['container_ref'].well(ch['parent_index'])

                                return ch


        #print 'couldnt allocate within existing items, allocatig a new container'

        # Didn't find a free container in the stack of existing containers,
        # let's try to allocate one.
        if ctype in _CONTAINERS.keys():

            new = copy(_CONTAINERS[ctype])
            name = self.name_registry.new()
            new['name'] = name

            ref = env.protocol.ref(name, cont_type=ctype, storage='cold_4')
            new['container_ref'] = ref

            self.containers.append(new)

            if ('parent_only' in new) and (new['parent_only'] is True):
                ch = new['children'][0]
                ch['free'] = False
                ch['container_ref'] = ref
                ch['well_ref'] = ref.well(0)
                return ch
            else:
                return new

        else:
            return None



class Container(object):
    #effectively this just imposes a particular
    #structure on a dict. nothing special about it otherwise.

    def __init__(self,
                 ctype=None,
                 location=None):

        self.ctype = ctype
        self.location = location

        self.max_volume = max_volume(ctype)


def max_volume(ctype):

    if ctype in _CONTAINERS.keys():
        return _CONTAINERS[ctype]['max_volume']
    else:
        return None


def min_container_type(vol):

    hit = None

    for c in _CONTAINERS.values():

        if c['max_volume'] > vol:

            if (hit is None) or (hit['max_volume'] > c['max_volume']):

                hit = c

    if hit is not None:

        return hit['ctype']

    else:

        return None





