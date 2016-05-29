#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

from pcompile.tests.test_context import TestContext
from pcompile.harness import Environment
from yaml import load, Loader, Dumper


class TestExamples(unittest.TestCase):

    def setUp(self):

        tc = TestContext()
        self.env = tc.env
        self.models_base =  os.path.abspath(os.path.join(os.path.dirname(
                                            os.path.abspath(__file__)),
                                            '..', 'example', 'models'))

    def test_amplicon_library(self, run=False):
        if run:
            from pcompile.example.amplicon_library import step as amplicon_library
            cfgpath = os.path.join(self.models_base, 'amplicon_library.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            amplicon_library(env, reactions_config)

    def test_crosslink(self, run=False):
        if run:
            from pcompile.example.crosslink import step as crosslink
            cfgpath = os.path.join(self.models_base, 'crosslink.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            crosslink(env, reactions_config)

    def test_digestion(self, run=False):
        if run:
            from pcompile.example.digestion import step as digestion
            cfgpath = os.path.join(self.models_base, 'digestion.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            digestion(env, reactions_config)

    def test_hichicago(self, run=False):
        if run:
            from pcompile.example.hichicago import step as hichicago
            cfgpath = os.path.join(self.models_base, 'hichicago.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            hichicago(env, reactions_config)

    def test_jpeg(self, run=False):
        if run:
            from pcompile.example.jpeg import step as jpeg
            cfgpath = os.path.join(self.models_base, 'jpeg.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            jpeg(env, reactions_config)

    def test_ligation(self, run=False):
        if run:
            from pcompile.example.ligation import step as ligation
            cfgpath = os.path.join(self.models_base, 'ligation.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            ligation(env, reactions_config)

    def test_lysis(self, run=False):
        if run:
            from pcompile.example.lysis import step as lysis
            cfgpath = os.path.join(self.models_base, 'lysis.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            lysis(env, reactions_config)

    def test_pcr(self, run=False):
        if run:
            from pcompile.example.pcr import step as pcr
            cfgpath = os.path.join(self.models_base, 'pcr.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            pcr(env, reactions_config)

    def test_purification(self, run=True):
        if run:
            from pcompile.example.purification import step as purification
            cfgpath = os.path.join(self.models_base, 'purification.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            purification(env, reactions_config)

    def test_quantification(self, run=False):
        if run:
            from pcompile.example.quantification import step as quantification
            cfgpath = os.path.join(self.models_base, 'quantification.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            quantification(env, reactions_config)

    def test_reconstitute_chromatin(self, run=False):
        if run:
            from pcompile.example.reconstitute_chromatin import step as reconstitute_chromatin
            cfgpath = os.path.join(self.models_base, 'reconstitute_chromatin.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            reconstitute_chromatin(env, reactions_config)

    def test_reversal(self, run=False):
        if run:
            from pcompile.example.reversal import step as reversal
            cfgpath = os.path.join(self.models_base, 'reversal.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            reversal(env, reactions_config)

    def test_tas(self, run=False):
        if run:
            from pcompile.example.tas import step as tas
            cfgpath = os.path.join(self.models_base, 'tas.yml')
            reactions_config = load(open(cfgpath, 'r'), Loader=Loader)
            env = Environment(reactions_config)
            tas(env, reactions_config)



if __name__ == '__main__':

    unittest.main()



