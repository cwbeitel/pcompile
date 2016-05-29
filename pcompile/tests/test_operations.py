#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pcompile import ureg
from pcompile.tests.test_context import TestContext
from pcompile.solution import Solution

from pcompile.operations import pipette, mix, spin, inactivate, thermocycle, incubate, react, measure

class TestOperations(unittest.TestCase):

    def test_pipette(self, run=True):

        if run:

            from pcompile.operations import pipette

            tc = TestContext()
            solution = tc.input_solution_1
            vol = 1 * ureg.microliter
            dest_solution = tc.input_solution_2

            pipette(tc.env, solution, vol, dest_solution)


    def test_mix(self, run=False):

        if run:

            from pcompile.operations import mix

            tc = TestContext()
            solution = tc.env.reactions.get_current().solution

            mix(tc.env, solution)


    def test_spin(self, run=False):

        if run:

            from pcompile.operations import spin

            tc = TestContext()
            solution = tc.env.reactions.get_current().solution
            speed = ''
            duration = ''

            spin(tc.env, solution, speed, duration)

    def test_inactivate(self, run=False):

        if run:

            from pcompile.operations import inactivate

            tc = TestContext()
            solution = tc.env.reactions.get_current().solution
            itype = 'chemical'

            inactivate(tc.env, itype)

    def test_thermocycle(self, run=True):

        if run:

            from pcompile.operations import thermocycle

            tc = TestContext()
            rxn = tc.env.reactions.get_current()
            solution = tc.diluent

            thermocycle(tc.env, solution, rxn.params)

    def test_incubate(self, run=True):

        if run:

            from pcompile.operations import incubate

            tc = TestContext()
            solution = tc.diluent
            where = 'ambient'
            duration = 1*ureg.minute
            shaking = True

            incubate(tc.env, solution, where, duration, shaking)

    def test_react(self, run=True):

        if run:

            from pcompile.operations import react

            tc = TestContext()
            rxn = tc.env.reactions.get_current()
            target = rxn.solution
            incubation = []
            inactivation = {}
            inputs = rxn.inputs

            # So want to run this without actually doing the optimization...
            react(tc.env, target, incubation, inactivation, inputs)

    def test_measure(self, run=False):

        if run:

            from pcompile.operations import measure

            tc = TestContext()
            measurement_type = ''
            inputs = []

            measure(tc.env, measurement_type, inputs)

    def test_move(self, run=False):

        if run:

            from pcompile.operations import move

            move(env, s)

    def test_uncover(self, run=False):

        if run:

            from pcompile.operations import uncover

            uncover(env, s)

    def test_cover(self, run=False):

        if run:

            from pcompile.operations import cover

            cover(env, s)

    def test_unseal(self, run=False):

        if run:

            from pcompile.operations import unseal

            unseal(env, s)

    def test_seal(self, run=False):

        if run:

            from pcompile.operations import seal

            seal(env, s)

    def test_gel(self, run=False):

        if run:

            from pcompile.operations import gel

            gel(env, s)

    def test_fluorescence(self, run=False):

        if run:

            from pcompile.operations import fluorescence

            fluorescence(env, s)

    def test_luminescence(self, run=False):

        if run:

            from pcompile.operations import luminescence

            luminescence(env, s)

    def test_absorbance(self, run=False):

        if run:

            from pcompile.operations import absorbance

            absorbance(env, s)


if __name__ == '__main__':

    unittest.main()




