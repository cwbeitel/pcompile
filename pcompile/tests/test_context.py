#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pcompile import ureg

import os
import json
import simplejson
from pcompile.harness import Environment
from pcompile.solution import Solution

class TestContext(object):
    '''
    Initialize an app run environment from a typical config specifying a
    series of reactions.
    '''

    def __init__(self):

        testdir = os.path.expanduser(os.path.join('~/.hyper', 'test'))
        json_path = os.path.join(testdir, 'proto_config.json')
        self.json_path = json_path
        os.system('mkdir -p ' + testdir)

        # This should be loaded from a file...

        with open(os.path.expanduser(json_path), 'w') as f:
            f.write(json.dumps({"reactions":
                [{"meta": ["type:enzymatic",
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
                          "concentration": "200:nanomolar"},
                        {"_reference": "primer_r",
                         "classification": {"CHEBI":"double-stranded_dna",
                                            "target":"806:16s",
                                            "orientation":"r"},
                         "concentration": "200:nanomolar"},
                        {
                         "_reference": "template_dna",
                         "concentration": "2:ng/microliter",
                         "_type": "user_specified",
                         "classification": {"CHEBI":"double-stranded_dna"}
                        },
                        {
                         "_reference": "pcr_master_mix",
                         "classification":{
                            "model": "11306-016",
                            "supplier": "invitrogen"
                            },
                         "concentration": "0.9:x"
                        },
                        {"classification":{"CHEBI": "water"},
                        "concentration": "55:mol/liter",
                        "_ignore":"True"}
                        ],
                    "volume": "55:microliter"},
                "constraints": ["glycerol:concentration:<:0.1:nM",
                                "ph:range:6.5:7.5",
                                ":auto_constraints"],
                "inputs":[
                  {"_reference":"template_dna",
                   "container":{"location":"ct177en2w6ggxv:transcriptic"},
                    "name":"seadna_oct"
                  }
                  ]
                }]
            }))


        self.reactions = simplejson.loads(open(json_path, 'r').read().decode("utf-8"))

        self.env = Environment(self.reactions)

        self.diluent = Solution(**{"components":[
                                    {"classification":{"CHEBI": "water"},
                                    "concentration": 55*ureg.mol/ureg.liter,
                                    "_ignore_concentration":True}
                                    ],
                                    "container":{"ctype":"micro-1.5",
                                                 "location":"321:transcriptic"},
                                    "volume":200*ureg.microliter})

        self.rxn2 = {"meta": ["type:enzymatic",
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
                  {"container":{
                      "location":"ct177en2w6ggxv:transcriptic"
                      },
                      "classification":"double-stranded_DNA"
                  }
                  ]
                }


        self.target_solution = Solution(**self.rxn2['solution'])
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
                         "concentration": 4 * ureg.x
                        }
                        ],
                        "container":{"ctype":"micro-1.5",
                                     "location":"654:transcriptic"},
                    "volume": 55 * ureg.microliter})

        self.diluent = Solution(**{"components":[
                                    {"classification":{"CHEBI": "water"},
                                    "concentration": 55 * ureg.mol/ureg.liter,
                                    "_ignore_concentration":True}
                                    ],
                                    "container":{"ctype":"micro-1.5",
                                                 "location":"321:transcriptic"},
                                    "volume":200 * ureg.microliter})

        self.diluent2 = Solution(**{"components":[
                                    {"classification":{"CHEBI": "water"},
                                    "concentration": 55 * ureg.mol/ureg.liter,
                                    "_ignore_concentration":True}
                                    ],
                                    "container":{"ctype":"micro-1.5",
                                                 "location":"321:transcriptic"},
                                    "volume":200 * ureg.microliter})

        self.sample = Solution(**{"components":[{
                         "classification": {"CHEBI":"double-stranded_dna"},
                         "concentration": 40 * ureg.nanograms/ureg.ul,
                        }],
                        "container":{"ctype":"micro-1.5",
                                     "location":"987:transcriptic"},
                        "volume":55 * ureg.microliter})

        self.solution_set = [self.input_solution_1,
                             self.input_solution_2,
                             #self.input_solution_3,
                             self.input_solution_4,
                             self.sample,
                             self.diluent,
                             self.diluent2]


class TestTestContext(unittest.TestCase):

    def test_test_context(self):
        tc = TestContext()


if __name__ == '__main__':
    unittest.main()




