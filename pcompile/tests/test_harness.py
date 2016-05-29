#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import os
import json
import simplejson
from pcompile.harness import Environment, Reaction, Reactions, Config
from pcompile.tests.test_context import TestContext
from pcompile.solution import Solution

def hi(env):
    pass

class TestHarness(unittest.TestCase):

    def test_run(self):

        from pcompile.harness import run

        pth = os.path.expanduser(os.path.join('~/.hyper', 'test', 'proto_config.json'))

        res = run(hi, [pth], log=False)
        assert "refs" in res
        assert "instructions" in res


class TestEnvironment(unittest.TestCase):

    def test_init(self):

        tc = TestContext()

        assert hasattr(tc.env.reactions.reactions[0], 'meta')

    def test_lazy_ref(self):

        tc = TestContext()

        s = Solution(**{"container":{"location":"1234:transcriptic",
                                    "ctype":"96-pcr"}
                        }
                    )

        ref = tc.env.lazy_ref(s)


class TestReaction(unittest.TestCase):

    def test_init_reaction(self):

        tc = TestContext()

        rxn = Reaction(tc.reactions['reactions'][0])

    def test_init_reactions(self):

        tc = TestContext()

        rxns = Reactions(tc.reactions)
        assert len(rxns.reactions[0].solution.components) > 0

    def test_get_current_reaction(self):

        tc = TestContext()

        rxn = Reactions(tc.reactions).get_current()
        assert rxn.params.reagent_thaw_time == "10:minute"
        assert isinstance(rxn.solution.components, list)
        assert len(rxn.solution.components)>0

        rxn = tc.env.reactions.get_current()
        assert isinstance(rxn.solution.components, list)
        assert len(rxn.solution.components)>0

    def test_finished_current_reaction(self):

        tc = TestContext()

        # Why is there one more reaction when the TestContext is
        # created in the test function instead of outside of it?
        # For now, not necessary to know.

        #tc = TestContext()
        #print tc.env.reactions.reactions

        assert len(tc.env.reactions.reactions) == 1

        tc.env.reactions.finished_current()

        assert len(tc.env.reactions.reactions) == 0


class TestConfig(unittest.TestCase):

    #from pcompile.app.config import Config

    def test_init(self):

        c = Config()

    def test_save(self):
        pass



if __name__ == '__main__':
    unittest.main()



