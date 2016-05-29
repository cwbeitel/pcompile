#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.example.lysis import step as lysis
from pcompile.example.digestion import step as digestion
from pcompile.example.ligation import step as ligation
from pcompile.example.reversal import step as reversal
from pcompile.example.purification import step as purification
from pcompile.example.amplicon_library import step as library
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Tag-associated sequencing (TAS)'''
    env.rprotocol.step('tas', 'Tag-associated sequencing (TAS)')

    lys, dig, lig, rev, pur, lib = rxn.reactions

    s = lysis(env, lys, inputs)
    s = digestion(env, dig, s)
    s = ligation(env, lig, s)
    s = reversal(env, rev, s)
    s = purification(env, pur, s)
    s = library(env, lib, s)

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)



