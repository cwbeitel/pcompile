#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.operations import react
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Enzymatic cellular lysis.'''
    env.rprotocol.step('lysis', 'Enzymatic cellular lysis.')

    lys, prp = rxn.reactions

    s = react(env, lys.solution, lys.incubation, inputs)
    s = react(env, prp.solution, prp.incubation, s)

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


