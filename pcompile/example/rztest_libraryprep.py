#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile import ureg
from pcompile.example.pcr import step as pcr
from pcompile.example.purification import step as purification
#from pcompile.example.quantification import step as quantification
from pcompile.helper import step_wrapper
from pcompile.operations import relocate_volume, gel

@step_wrapper
def step(env, rxn, inputs=None):
    '''Amplicon sequencing library prep from purified DNA.'''
    env.rprotocol.step('amplicon_library', 'Amplicon sequencing library prep from purified DNA.')

    amp, pur, quant = rxn.reactions

    s, t = relocate_volume(env, inputs, vol=5*ureg.microliter)
    s = pcr(env, amp, t)
    s = purification(env, pur, s)
    s = gel(env, s)
    s = quantification()

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


