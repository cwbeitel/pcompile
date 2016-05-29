#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile import ureg
from pcompile.operations import react, relocate_volume
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Reverse chromatin crosslinks'''
    env.rprotocol.step('reversal', 'Reverse chromatin crosslinks')

    rna, pk = rxn.reactions

    s, t = relocate_volume(env, inputs, vol=5*ureg.microliter)
    s = react(env, rna.solution, rna.incubation, t)
    s = react(env, pk.solution, pk.incubation, s)

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)



