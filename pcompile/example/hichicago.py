#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.example.lysis import step as lysis
from pcompile.example.reconstitute_chromatin import step as reconstitute
from pcompile.example.crosslink import step as crosslink
from pcompile.example.digestion import step as digestion
from pcompile.example.ligation import step as ligation
from pcompile.example.reversal import step as reversal
from pcompile.example.purification import step as purification
from pcompile.example.amplicon_library import step as library
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Chromatin-reconstitution proximity ligation (Hi-Chicago)'''

    lys, rec, cro, dig, lig, rev, pur, lib = rxn.reactions

    # Extract HMW DNA
    s = lysis(env, lys, inputs)
    s = reconstitute(env, rec, s)
    s = crosslink(env, cro, s)
    s = digestion(env, dig, s)
    s = ligation(env, lig, s)
    s = reversal(env, rev, s)
    s = purification(env, pur, s)
    s = library(env, lib, s)

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


