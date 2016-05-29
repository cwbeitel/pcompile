#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.helper import step_wrapper
from pcompile.solution import walloc
import json
from pcompile.solution import Solution
from pcompile import ureg
import numpy as np
from pcompile.operations import pipette
from pcompile.helper import strip_internal
from pcompile.solution import SolutionPlan

@step_wrapper
def step(env, rxn, inputs=None):
    '''Pipette colored liquid into a plate to reproduce a jpeg'''
    env.rprotocol.step('jpeg', 'Pipette colored liquid into a plate to reproduce a jpeg.')

    jpg = rxn.reactions[0]
    template = jpg.solution

    red = Solution(components=[
            {"classification":{"color":"red"},"concentration":100*ureg.percent},
            {"classification":{"color":"green"},"concentration":0*ureg.percent},
            {"classification":{"color":"blue"},"concentration":0*ureg.percent},
            ], volume=5*ureg.milliliters, container={"location":"red"})
    green = Solution(components=[
            {"classification":{"color":"red"},"concentration":100*ureg.percent},
            {"classification":{"color":"green"},"concentration":0*ureg.percent},
            {"classification":{"color":"blue"},"concentration":0*ureg.percent},
            ], volume=5*ureg.milliliters, container={"location":"green"})
    blue = Solution(components=[
            {"classification":{"color":"red"},"concentration":100*ureg.percent},
            {"classification":{"color":"green"},"concentration":0*ureg.percent},
            {"classification":{"color":"blue"},"concentration":0*ureg.percent},
            ], volume=5*ureg.milliliters, container={"location":"blue"})
    water = Solution(components=[
            {"classification":{"color":"red"},"concentration":0*ureg.percent},
            {"classification":{"color":"green"},"concentration":0*ureg.percent},
            {"classification":{"color":"blue"},"concentration":0*ureg.percent},
            ], volume=5*ureg.milliliters, container={"location":"water"})

    with open(rxn.params.colorsfile, 'r') as f:
        colors = json.loads(f.read())['colors'] # colors as fractions, in json

    for c in colors:
        c = 100 * np.array(c, dtype=float)/255

        splan = SolutionPlan(target_solution=Solution(components=[
            {"classification":{"color":"red"},"concentration":c[0]*ureg.percent},
            {"classification":{"color":"green"},"concentration":c[1]*ureg.percent},
            {"classification":{"color":"blue"},"concentration":c[2]*ureg.percent},
            ], volume=150*ureg.microliter))

        splan.solutions = [red, green, blue, water]
        splan.solve()
        splan.compile(env)

        #c = np.array(c, dtype=float)
        #dest = walloc(env, template)
        #volumes = (c / 255.0) * template.volume
        #for source, vol in zip((red,green,blue), volumes):
        #    pipette(env, source, vol, dest)
        #pipette(env, water, (template.volume - sum(volumes)), dest)

    return 1

if __name__ == '__main__':
    from pcompile.harness import run
    run(step)


