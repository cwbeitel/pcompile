#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.operations import react
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Digestion of DNA'''
    env.rprotocol.step('digestion', 'Digestion of DNA/proteins.')

    dig = rxn.reactions[0]
    s = react(env, dig.solution, dig.incubation, inputs)

    return s


if __name__ == '__main__':
    from pcompile.harness import run
    run(step)



