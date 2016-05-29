#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pcompile import ureg
from pcompile.operations import react, relocate_volume
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''DNA Ligation'''
    env.rprotocol.step('ligation', 'DNA Ligation.')

    lig = rxn.reactions[0]

    s, t = relocate_volume(env, inputs, vol=5*ureg.microliter)
    s = react(env, lig.solution, lig.incubation, t)

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


