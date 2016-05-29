e#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.operations import react, gel
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Perform gel electrophoresis
    '''

    env.rprotocol.step('gel', 'Perform gel electrophoresis.')

    gelrxn = rxn.reactions[0]
    s = gel(env, inputs, dataref="test_gel1234")

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


