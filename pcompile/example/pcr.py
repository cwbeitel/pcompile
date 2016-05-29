#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.solution import compile_solutions
from pcompile.operations import thermocycle, react, seal, unseal
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Automated polymerase chain reaction.'''
    env.rprotocol.step('pcr', 'Automated polymerase chain reaction')

    repcr = rxn.reactions[0]
    s = react(env, repcr.solution, repcr.incubation, inputs)
    #s = seal(env, s)
    s = thermocycle(env, s, repcr.params)
    #s = unseal(env, s)
    return s

if __name__ == '__main__':

    from pcompile.harness import run
    run(step)


