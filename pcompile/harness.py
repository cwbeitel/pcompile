#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson
import argparse
from yaml import load, Loader, Dumper
from pcompile.solutiondb import SolutionDB
from pcompile.solution import Solution
from autoprotocol.protocol import Protocol
from pcompile.items import Items
import click
from pcompile.helper import make_dottable_dict
from pymongo import MongoClient

def init_logging(name='roz'):

    import os
    import logging

    # from https://docs.python.org/2/howto/logging-cookbook.html

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join(os.path.expanduser('~'), '.hyper', 'general.log'))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


class Reaction(object):
    '''An individual reaction, which may be composed of multiple sub-reactions.
    '''

    def __init__(self, reactions=None, module=None, inputs=None, outputs=None,
                 solution=None, incubation=None, name=None, meta=None,
                 params=None, constraints=None):

        self.reactions = reactions
        self.module = module
        self.inputs = inputs
        self.outputs = outputs
        self.name = name
        self.solution = solution
        self.incubation = incubation
        self.meta = meta
        self.params = params
        self.constraints = constraints

        if (solution is not None) and not isinstance(solution, Solution):
            self.solution = Solution(**solution)
            #print self.solution.components
            if self.solution.components is not None:
                self.solution.update_units()

        if isinstance(reactions, list):

            names = set()

            for i,r in enumerate(reactions):

                assert 'name' in r, 'Each reaction must have a name.'
                assert r['name'] not in names, 'Found two reactions with the same name.'
                names.add(r['name'])
                self.reactions[i] = Reaction(**r)

        if params is not None:
            self.params = make_dottable_dict(params)

        if inputs is not None:
            if not isinstance(inputs, list):
                inputs = [inputs]
            for i, ipt in enumerate(inputs):
                assert isinstance(ipt, dict), 'Reaction object tried to load an input but was passed something other than a dict: ' + str(ipt)
                assert ('container' in ipt) and ('location' in ipt['container']), 'an input must have a container and location'

    def named(self, name):

        if isinstance(self.reactions, list):

            for i,r in enumerate(self.reactions):

                assert hasattr(r, 'name'), 'Found reaction without a name when looking for named reaction.'

                if r.name == name:

                    return r

        return None


# DEV
class RProtocol(Protocol):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = None
        self.description = None

    def step(self, name, description):
        if self.name is None:
            self.name = name
            self.description = description


class Environment(object):
    '''Store a structured set of objects that are needed at various times in
    the app.

    Note
    ----
    This object is primarily meant to be used without customization other than
    by specifying the protocol_config file.

    Example
    -------
    .. code-block:: python

        protocol_config = simplejson.loads(open(args.config, 'r').read().decode("utf-8"))
        from pcompile.app.environment import Environment
        env = Environment(protocol_config)
    '''

    def __init__(self,
                 protocol=Protocol(),
                 items=Items(),
                 db=SolutionDB(),
                 logger=init_logging(),
                 rprotocol=RProtocol()):

        self.protocol = protocol
        self.items = items
        self.db = db
        self.logger = logger
        self.rprotocol = rprotocol

    def lazy_ref(self, solution):

        solution_id = solution.container['location'].split(":")[1]
        ref = self.protocol.ref(solution_id,
                                cont_type=solution.container['ctype'],
                                storage="cold_20")
        return ref


def run(fn, args=None, log=True):
    '''Take configuration YAML file from the command line and run the given
    protocol.

    Example
    -------
    .. code-block:: unix

        python pcr.py pcr.yml
    '''

    from pcompile.helper import load_imports
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='YAML-formatted protocol configuration file')
    args = parser.parse_args(args)

    modelsdir = os.path.dirname(args.config) # for now assumes imports come from same dir
    cfg = load_imports(load(open(args.config, 'r'), Loader=Loader), modelsdir)

    # Run through the steps, building a graph of step relationships
    rxn = Reaction(**cfg)
    #env_graph = Environment()
    #fn(env_graph, rxn, compile_structure_only=True)

    # Compile, with awareness of overview graph
    env = Environment()
    #fn(env, rxn, graph=env_graph.graph)
    fn(env, rxn)

    protocol = env.protocol.as_dict()
    from copy import copy

    for i,ins in enumerate(protocol['instructions']):
        if i>0:
            if 'x-magnetic_separate' in protocol['instructions'][i-1]:
                cmd = copy(protocol['instructions'][i-1]['x-magnetic_separate'])
                ins['x-magnetic_separate'] = cmd
                del protocol['instructions'][i-1]

    result = simplejson.dumps(protocol, indent=2)
    if log:
        env.logger.info(result)

    # DEV
    protocol['name'] = env.rprotocol.name
    protocol['description'] = env.rprotocol.description
    from solutiondb import ReactionDB
    ReactionDB().update(protocol)

    outfile = os.path.join(os.environ['ROSALIND_EXAMPLE'], 'ap', env.rprotocol.name + '.ap.json')
    with open(outfile, 'w') as out:
        out.write(result)

    return result


def test_run(fn, args=None, log=True):
    pass



