#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile import ureg
from pcompile.operations import react, incubate, mix, relocate_volume, dilute_dev, plate_off_mag_adapter
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    '''Bead purification of DNA using Agencourt AMPure XP magnetic beads.
    Adapted from https://www.beckmancoulter.com/wsrportal/techdocs?docname=B37419AA
    Presently the max volume for this step is set at 110 microliters.
    Important - a strong magnet should be used. The magnet should be on the side of
    the tube (?).
    '''
    env.rprotocol.step('purification', 'Bead purification of DNA using Agencourt AMPure XP magnetic beads..')

    bnd, wsh, elu = rxn.reactions
    bead_ratio = bnd.params.beadratio
    bead_frac = bead_ratio/(1 + bead_ratio)

    # ------- Binding to beads
    s, t = relocate_volume(env, inputs, vol=5*ureg.microliter)
    s = dilute_dev(env, t, bnd.params.beads, ratio=bead_ratio)
    s = mix(env, s, 10)
    s = incubate(env, s, bnd.params.premagtemp, bnd.params.premagtime)
    s = incubate(env, s, bnd.params.magtemp, bnd.params.magtime, mag=True)
    # ------------------------

    # -------- Ethanol wash
    # Remove non-bead volume and discard
    s, t = relocate_volume(env, s, fraction=1.0)
    s = dilute_dev(env, s, wsh.params.etoh, wsh.params.etohvol)
    s, t = relocate_volume(env, s, vol=wsh.params.etohvol)
    s = plate_off_mag_adapter(env, s)
    s = incubate(env, s, wsh.params.drytemp, wsh.params.drytime, mag=False)
    # ---------------------

    # --------- Re-suspension
    s = dilute_dev(env, s, elu.solution.components, elu.params.eluentvol)
    s = mix(env, s, 20)
    #s = incubate(env, s, elu.params.premagtemp, elu.params.premagtime, mag=False)
    s = incubate(env, s, elu.params.magtemp, elu.params.magtime, mag=True)
    # ------------------------

    s, t = relocate_volume(env, s, fraction=0.95)

    return t


if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


