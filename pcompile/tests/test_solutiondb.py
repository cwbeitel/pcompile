#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from pcompile.solutiondb import SolutionDB
from pcompile.solution import Solution
import os
import json
from pcompile.tests.test_harness import TestContext

class TestSolutionDB(unittest.TestCase):

    def setUp(self):
        '''Create a new collection containing known entries against which the
        following tests can be performed.
        '''

        '''
        testdir = os.path.expanduser(os.path.join('~/.hyper', 'test'))
        json_path = os.path.join(testdir, 'test.solutiondb.json')
        self.json_path = json_path
        os.system('mkdir -p ' + testdir)

        with open(os.path.expanduser(json_path), 'w') as f:
            f.write(json.dumps({'name': {
                'name': 'dna',
                'concentration': '5:uM'
            }}))
        '''

        # Start a mongod process running on a separate thread,

        # Verify that the collection being created for the purposes of testing
        # is one that does not already exist on the users' system and thus
        # could be damaged by over-writing.
        #sdb = SolutionDB(db_json=json_path, collection='test')

        pass

    def test_connect_and_find(self):

        #sdb = SolutionDB()
        #print sdb.db.find_one()

        pass

    def test_verify(self):

        # TODO: Create a json file that can be used to initialize a test DB
        #self.sdb.verify()
        pass

    def test_find_solution_set(self):
        '''
        .. note:
            In order to make this test general and usable by everyone,
            there should be the means to create a new database and populate it
            with known elements, just for the purpose of solutiondb testing.
            For now, just the database I have on disk will be used instead of
            creating and destroying collections automatically.
        '''

        # Set up the input
        tc = TestContext()
        comps = tc.env.reactions.get_current().solution.components

        '''
        for c in comps.values():

            print c.as_dict()
        '''

        #comps = [{'_reference': 'primer_f', 'classification': {'CHEBI': 'double-stranded_dna', 'target': '515:16s', 'orientation': 'f'}, '_target_concentration': '200:nanomolar'},
        #         {'_reference': 'primer_r', 'classification': {'CHEBI': 'double-stranded_dna', 'target': '806:16s', 'orientation': 'r'}, '_target_concentration': '200:nanomolar'},
        #         {'_type': 'user_specified', '_reference': 'template_dna', 'classification': {'CHEBI': 'double-stranded_dna'}, '_target_concentration': '2:ng/microliter'},
        #         {'_reference': 'pcr_master_mix', 'classification': {'supplier': 'invitrogen', 'model': '11306-016'}, '_target_concentration': '1:x'}]

        solution_hits = tc.env.db.find_solution_set(comps)

        for h in solution_hits:

            assert isinstance(h, Solution)
            assert len(h.components) > 0
            print h.components['_reference']

        # The result should be a dict of Solution objects.
        #for s in solution_hits.values():

        #    assert isinstance(s, Solution)

    def tearDown(self):
        '''Delete the test collection.
        '''
        pass


if __name__ == '__main__':

    unittest.main()



