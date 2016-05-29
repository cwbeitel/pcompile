#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pcompile.solution import Component, Solution, SolutionPlan, objective_function, walloc, compile_solution, compile_solutions
from pcompile.solutiondb import SolutionDB
from pcompile import ureg
from math import floor
from pcompile.tests.test_harness import TestContext
import json


class TestComponent(unittest.TestCase):

    def test_init_from_dict(self):

        d = {'name':'1', 'concentration':1*ureg.microliter, 'classification':'1'}
        c = Component(**d)
        #assert c.to_dict() == d


class TestSolution(unittest.TestCase):

    def setUp(self):

        self.d = {'history':'1',
                  'name':'1',
                  'volume':1 * ureg.milliliter,
                  'components':[{'classification':{'CHEBI':'1234'},
                                'concentration':1 * ureg.micromolar},
                                {'classification':{'CHEBI':'5678'},
                                'concentration':2 * ureg.micromolar},
                                {'classification':{'CHEBI':'9123'},
                                'concentration':3 * ureg.micromolar}],
                  'other':{
                    'full_label':'1',
                    'components_string':'1'
                    },
                  'concentration': 1 * ureg.micromolar,
                  'classification':'1',
                  'container':{"ctype":"micro-1.5","location":"transcriptic:1234"},
                  'storage_temp':'1',
                  'comp_index':{}}

        self.d1 = {'history':'1',
                  'name':'1',
                  'volume':1 * ureg.milliliter,
                  'components':[{'classification':{'CHEBI':'1234'},
                                'concentration':1 * ureg.micromolar},
                                {'classification':{'CHEBI':'5678'},
                                'concentration':2 * ureg.micromolar},
                                {'classification':{'CHEBI':'9123'},
                                'concentration':3 * ureg.micromolar}],
                  'other':{
                    'full_label':'1',
                    'components_string':'1'
                    },
                  'concentration': 1 * ureg.micromolar,
                  'classification':'1',
                  'container':{"ctype":"micro-1.5","location":"transcriptic:1234"},
                  'storage_temp':'1',
                  'comp_index':{}}

        self.d2 = {'history':'1',
                  'name':'1',
                  'volume':1 * ureg.milliliter,
                  'components':[{'classification':{'CHEBI':'1234'},
                                'concentration':1 * ureg.molar},
                                {'classification':{'CHEBI':'5678'},
                                'concentration':2 * ureg.micromolar},
                                {'classification':{'CHEBI':'9123'},
                                'concentration':3 * ureg.micromolar}],
                  'other':{
                    'full_label':'1',
                    'components_string':'1'
                    },
                  'concentration': 1 * ureg.micromolar,
                  'classification':'1',
                  'container':{"ctype":"micro-1.5","location":"transcriptic:1234"},
                  'storage_temp':'1',
                  'comp_index':{}}

    def test_init_from_dict(self):

        s = Solution(components=[])
        image = Solution(**self.d).to_dict()
        assert image == self.d

    def test_build_component_index(self):

        s = Solution(**self.d)
        s.build_component_index()
        assert s.comp_index == {'CHEBI:1234': 0, 'CHEBI:9123': 2, 'CHEBI:5678': 1}

    def test_compatible(self):

        s = Solution(**self.d)

        s2 = Solution(components=[{'classification':{'CHEBI':'1234'},
                                   'concentration':1 * ureg.molar}],
                      container={"ctype":"micro-1.5"},
                      volume=1*ureg.milliliter)

        s3 = Solution(components=[{'classification':{'CHEBI':'1234'},
                                   'concentration':1 * ureg.units}],
                      container={"ctype":"micro-1.5"},
                      volume=1*ureg.milliliter)

        assert s.compatible(s2) == True
        assert s.compatible(s3) == False

    def test_add(self):

        s = Solution(**self.d)

        s2 = Solution(components=[{'classification':{'CHEBI':'1234'},
                                   'concentration':2 * ureg.micromolar}],
                      container={"ctype":"micro-1.5"},
                      volume=1*ureg.milliliter)

        s.add(s2, 10 * ureg.microliter)
        assert (s.components[0]['concentration'] - 1.01*ureg.micromolar) < 0.001*ureg.micromolar

        s3 = Solution(volume=1*ureg.liter)
        s3.add(s2, 10*ureg.microliter)

        #[{'concentration': <Quantity(1.0, 'micromolar')>, 'classification': {'CHEBI': '1234'}}]
        #[{'concentration': <Quantity(0.00099028530573, 'molar')>, 'classification': {'CHEBI': '1234'}}]

    def test_remove(self):
        s = Solution(**self.d)
        s.volume=10*ureg.microliter
        s.remove(1*ureg.microliter)
        assert s.volume == 9*ureg.microliter


    def test_dist(self):
        #A distance measure for comparing solution objects, specifically
        #for use in the non-constraint, component-only portion of solution
        #optimization.

        s1 = Solution(**self.d)
        s2 = Solution(**self.d1)
        s3 = Solution(**self.d2)

        # Coincidence, non-negativity
        assert s1.dist(s2) == 0
        assert s1.dist(s1) == 0
        s1.add(s1, 1*ureg.microliter)
        assert s1.dist(s2) < 0.00001
        s2.add(s3, 1 * ureg.microliter)
        assert s1.dist(s2) > 0

        # Symmetry
        assert (s1.dist(s2) - s2.dist(s1)) < 0.00001

        # Triangle inequality
        s3.add(s1, 10 * ureg.microliter)
        s3.add(s2, 10 * ureg.microliter)
        assert s3.dist(s2) <= s3.dist(s1) + s1.dist(s2)


'''
        # Translation invariance
        #s1 = Solution(**self.d)
        #s2 = Solution(**self.d)
        d1 = s1.dist_self_to_target(s2)
        s1.add(s3, 1 * ureg.microliter)
        s2.add(s3, 1 * ureg.microliter)
        print s1.dist_self_to_target(s2)
        print d1
        assert s1.dist_self_to_target(s2) == d1, 'Metric translation invariance violated.'
'''

        # Increases with additions
        # There's no guarantee it will be strictly increasing unless the solution does not
        # contain any of what's being added.


'''
    def test_ref(self):

        # Test whether we can generate a ref that works with autoprotocol
        # given a rosalind solution object with associated container data.

        tc = TestContext()
        s1 = Solution(container={'name':'sparkle', 'ctype':'micro-1.5', 'location':'transcriptic:1234'})
        s2 = Solution(container={'name':'dash', 'ctype':'micro-1.5', 'location':'transcriptic:5678'})

        tc.env.protocol.pipette([{'from': s1.ref(tc.env),
                               'to': s2.ref(tc.env),
                               'volume': '1:microliter'}])

        p = tc.env.protocol.as_dict()

        #print p

        assert p['instructions'] == [{'groups':
                                        [{'volume': '1:microliter',
                                          'to': 'dash/0',
                                          'from': 'sparkle/0'}],
                                      'op': 'pipette'}]
    '''


'''
class TestAllocation(unittest.TestCase):

    def test_simple_walloc(self):
        #Without the complication of an available container pool, allocate
        #the necessary wells.

        tc = TestContext()
        target_solution = Solution(volume=1*ureg.microliter)

        solution = walloc(tc.env, target_solution)
        assert solution.container is not None
        #assert 'location' in solution.container and solution.container['location'] is not None
'''

class TestSolutionPlan(unittest.TestCase):

    def setUp(self):

        self.rxn = {"meta": ["type:enzymatic",
                          "sensitivity:temperature,ph",
                          "amplifies:dna",
                          "named:pcr"],
                "params":
                    {"reagent_thaw_time": "10:minute",
                    "reagent_thaw_temp": "ambient",
                    "initial_temp": "94:celsius",
                    "initial_time": "120:second",
                    "extension_temp": "72:celsius",
                    "extension_time": "90:second",
                    "annealing_temp": "55:celsius",
                    "annealing_time": "60:second",
                    "melting_temp": "94:celsius",
                    "melting_time": "45:second",
                    "final_step_temp": "72:celsius",
                    "final_step_time": "600:second",
                    "hold_temp": "8:celsius",
                    "hold_time": "600:second",
                    "cycles": 30},
                "solution":
                    {"components":
                        [{"_reference": "primer_f",
                          "classification": {"CHEBI":"double-stranded_dna",
                                            "target":"515:16s",
                                            "orientation":"f"},
                          "concentration": 200*ureg.nanomolar},
                        {"_reference": "primer_r",
                         "classification": {"CHEBI":"double-stranded_dna",
                                            "target":"806:16s",
                                            "orientation":"r"},
                         "concentration": 200*ureg.nanomolar},
                        {
                         "_reference": "template_dna",
                         "concentration": 2*ureg.ng/ureg.microliter,
                         "_type": "user_specified",
                         "classification": {"CHEBI":"double-stranded_dna"}
                        },
                        {
                         "_reference": "pcr_master_mix",
                         "classification":{
                            "model": "11306-016",
                            "supplier": "invitrogen"
                            },
                         "concentration": 0.9*ureg.x
                        },
                        {"classification":{"CHEBI": "water"},
                        "concentration": 55*ureg.mol/ureg.liter,
                        "_ignore":True}
                        ],
                    "volume": 200*ureg.microliter},
                "constraints": ["glycerol:concentration:<:0.1:nM",
                                "ph:range:6.5:7.5",
                                ":auto_constraints"],
                "inputs":[
                  {"_reference":"template_dna",
                   "location":"ct177en2w6ggxv:transcriptic",
                    "name":"seadna_oct"
                  }
                  ]
                }

        self.target_solution = Solution(**self.rxn['solution'])
        self.input_solution_1 = Solution(**{"components":
                        [{"_reference": "primer_f",
                          "classification": {"CHEBI":"double-stranded_dna",
                                            "target":"515:16s",
                                            "orientation":"f"},
                          "concentration": 1000*ureg.nanomolar},
                        ],
                        "container":{"ctype":"micro-1.5",
                                     "location":"1234:transcriptic"},
                    "volume": 55*ureg.microliter})

        self.input_solution_2 = Solution(**{"components":
                        [{"_reference": "primer_r",
                         "classification": {"CHEBI":"double-stranded_dna",
                                            "target":"806:16s",
                                            "orientation":"r"},
                         "concentration": 1000*ureg.nanomolar}
                        ],
                        "container":{"ctype":"micro-1.5",
                                     "location":"456:transcriptic"},
                    "volume": 55*ureg.microliter})

        '''
        self.input_solution_3 = Solution(**{"components":
                        [{
                         "_reference": "template_dna",
                         "concentration": 4*ureg.nanograms/ureg.microliter,
                         "classification": {"CHEBI":"double-stranded_dna"}
                        }
                        ],
                        "container":{"ctype":"micro-1.5",
                                     "location":"789:transcriptic"},
                    "volume": 55*ureg.microliter})
        '''

        self.input_solution_4 = Solution(**{"components":
                        [{
                         "_reference": "pcr_master_mix",
                         "classification":{
                            "model": "11306-016",
                            "supplier": "invitrogen"
                            },
                         "concentration": 4*ureg.x
                        }
                        ],
                        "container":{"ctype":"micro-1.5",
                                     "location":"654:transcriptic"},
                    "volume": 55*ureg.microliter})

        self.diluent = Solution(**{"components":[
                                    {"classification":{"CHEBI": "water"},
                                    "concentration": 55*ureg.mol/ureg.liter,
                                    "_ignore_concentration":True}
                                    ],
                                    "container":{"ctype":"micro-1.5",
                                                 "location":"321:transcriptic"},
                                    "volume":200*ureg.microliter})

        self.diluent2 = Solution(**{"components":[
                                    {"classification":{"CHEBI": "water"},
                                    "concentration": 55*ureg.mol/ureg.liter,
                                    "_ignore_concentration":True}
                                    ],
                                    "container":{"ctype":"micro-1.5",
                                                 "location":"321:transcriptic"},
                                    "volume":200*ureg.microliter})

        self.sample = Solution(**{"components":[{
                         "classification": {"CHEBI":"double-stranded_dna"},
                         "concentration": 40 * ureg.nanograms/ureg.ul,
                        }],
                        "container":{"ctype":"micro-1.5",
                                     "location":"987:transcriptic"},
                        "volume":55*ureg.microliter})

        self.solution_set = [self.input_solution_1,
                             self.input_solution_2,
                             #self.input_solution_3,
                             self.input_solution_4,
                             self.sample,
                             self.diluent,
                             self.diluent2]


    '''
    def test_init(self):

        sp = SolutionPlan(target_solution=self.target_solution)
    '''

    def test_cluster_solutionset(self):

        import numpy as np
        #arr = np.array([[1,2,3],[1,2,3]])
        #print arr[np.where(arr == 1)]

        sp = SolutionPlan(target_solution=self.target_solution)
        sp.solutions = self.solution_set

        reps,  = sp.cluster_solutionset()

        #print reps[4].volume


    def test_objective_function(self):

        print 'the target concentrations are'
        print self.target_solution.components

        sp = SolutionPlan(target_solution=self.target_solution)
        sp.solutions = self.solution_set

        sp.solve()

        tc = TestContext()
        sp.compile(tc.env)

        print json.dumps(tc.env.protocol.as_dict(), indent=2)


    def test_compile(self):
        pass


    '''
    def test_compile_solution(self):

        env = TestContext().env
        rxn = env.reactions.get_current()

        rxn.solution.update_units()

        sset = compile_solutions(env=env,
                                 target_solution=rxn.solution,
                                 samples=rxn.inputs)
    '''


if __name__ == '__main__':

    unittest.main()



