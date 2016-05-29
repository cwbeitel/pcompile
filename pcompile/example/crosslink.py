#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.operations import react
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Crosslink DNA/proteins
    Notes: some things about this protocol could be changed to make it
    amenable to automation. It could also be performed as hybrid auto/nonauto.
    '''
    env.rprotocol.step('crosslink', 'Crosslink DNA/proteins.')

    pel, cro, que, fin = rxn.reactions

    # Pellet
    s = pellet(env, s, pel.pellet)
    s = wash(env, s, pel.wash)
    s = resuspend_to_od_target(env, s, pel.params.odtarget)
    # Perform serial dilution, measure OD, determine dilution for OD600:0.2

    # Crosslinking
    s = react(env, cro.solution, cro.incubation, inputs)

    # Quench
    s_1, s_2 = split(env, s)
    s_gly = react(env, que.solution, que.incubation, s_1)
    s_tris = react(env, que.solution, que.incubation, s_2)
    s = wash(env, s, que.wash, reps=2)

    # Wash, measure OD600
    s, m = measure(env, s, 'OD:600')
    m *= 8e8*ureg.cells/ureg.milliliter
    # ** Update sample cell concentrations **

    # Wash and resuspend to desired concentration
    # Split 1ml aliquots into 50ul aliquots?
    s = wash(env, s, wsh.wash)

    return s

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


