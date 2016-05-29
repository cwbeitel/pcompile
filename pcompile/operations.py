#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile import ureg
from pcompile.helper import pint_to_str, to_pint, temp_to_where
from pcompile.solution import compile_solutions, Solution
from pcompile.harness import Environment
from pcompile.helper import strip_internal
from pcompile.solution import walloc

def get_wells(env, s):
    return list(set([si.ref(env) for si in s]))

def get_containers(env, s):
    return list(set([si.ref(env, rtype="container") for si in s]))

def operation_wrapper(fn):

    def wrapper(*args, **kwargs):

        kwargs.update(dict(zip(fn.func_code.co_varnames, args)))
        s = kwargs['s']
        env = kwargs['env']

        assert isinstance(env, Environment)

        if isinstance(s, list):
            #containers = set()
            for sol in s:
                if not isinstance(sol, Solution):
                    raise ValueError(operation_name + ' called on non-solution object')
                #containers.add(sol.ref(env))

        elif isinstance(s, Solution):
            #containers = [s.ref(env)]
            s = [s]
            kwargs['s'] = s

        else:
            raise ValueError('The solution parameter must be a Solution or set of Solutions')

        #kwargs['containers'] = containers

        ret = fn(**kwargs)

        if 's' in kwargs:
            kwargs.pop('s')
        if 'env' in kwargs:
            kwargs.pop('env')
        #if 'containers' in kwargs:
        #    kwargs.pop('containers')
        #if 'wells' in kwargs:
        #    kwargs.pop('wells')
        for sol in s:
            sol.update_history({"operation":fn.__name__, "args": kwargs})

        return ret

    return wrapper

@operation_wrapper
def plate_to_mag_adapter(env, s, duration, containers=None):
    if isinstance(duration, ureg.Quantity):
        duration = pint_to_str(duration)
    for c in get_containers(env, s):
        env.protocol.plate_to_mag_adapter(c, duration)
    return s

@operation_wrapper
def plate_off_mag_adapter(env, s, containers=None):
    for c in get_containers(env, s):
        env.protocol.plate_off_mag_adapter(c)
    return s

@operation_wrapper
def uncover(env, s, containers=None):
    for c in get_containers(env, s):
        env.protocol.uncover(c)
    return s

@operation_wrapper
def cover(env, s, containers=None):
    for c in get_containers(env, s):
        env.protocol.cover(c)
    return s

@operation_wrapper
def unseal(env, s, containers=None):
    for c in get_containers(env, s):
        env.protocol.unseal(c)
    return s

@operation_wrapper
def seal(env, s, containers=None):
    for c in get_containers(env, s):
        env.protocol.seal(c)
    return s

@operation_wrapper
def gel(env, s, volume="10:microliter", matrix="agarose(8,2.0%)", ladder="ladder1", duration="11:minute", dataref=None, wells=None):
    if dataref is None:
        from random import random
        dataref = "unlabeled_gel" + str(random()*10000)
    # TODO: auto selection of gel based on number of samples and expected size.
    env.protocol.gel_separate(get_wells(env, s),
                              #volume="10:microliter",
                              matrix="agarose(8,0.8%)",
                              ladder="ladder1",
                              duration="11:minute",
                              dataref=dataref)
    return s

@operation_wrapper
def fluorescence(env, s, containers=None):
    env.protocol.fluorescence(ref, get_wells(s), excitation, emission, dataref, flashes=25)
    return s

@operation_wrapper
def luminescence(env, s, containers=None):
    env.protocol.luminescence(ref, get_wells(s), dataref)
    return s

@operation_wrapper
def absorbance(env, s, containers=None):
    env.protocol.absorbance(container, get_wells(s), wavelength, dataref, flashes=25)
    return s

@operation_wrapper
def mix(env, s, count, containers=None):
    from pcompile.items import max_volume
    for solution in s:
        volume = pint_to_str(solution.volume)
        well = solution.ref(env)
        env.protocol.mix(well, volume=volume, repetitions=count)
    return s

@operation_wrapper
def spin(env, s, speed, duration, containers=None):
    s = seal(env, s)
    for c in get_containers(env, s):
        env.protocol.spin(c, acceleration, duration)
    return s

@operation_wrapper
def thermocycle(env, s, program, containers=None):
    '''Run a thermocycling program on a solution or solution set.
    '''

    formatted_program = [{
                            "cycles": 1,
                            "steps": [{
                                "duration": program.initial_time,
                                "temperature": program.initial_temp
                            }]
                        },
                        {
                            "cycles": program.cycles,
                            "steps": [{
                                "duration": program.melting_time,
                                "temperature": program.melting_temp
                            }, {
                                "duration": program.annealing_time,
                                "temperature": program.annealing_temp
                            }, {
                                "duration": program.extension_time,
                                "temperature": program.extension_temp
                            }]
                        },
                        {
                            "cycles": 1,
                            "steps": [{
                                "duration": program.final_step_time,
                                "temperature": program.final_step_temp
                            }, {
                                "duration": program.hold_time,
                                "temperature": program.hold_temp
                            }]
                        }]

    s = seal(env, s)

    for c in get_containers(env, s):
        env.protocol.thermocycle(c, groups=formatted_program, volume='10:microliter', dataref=None)

    s = unseal(env, s)

    return s

@operation_wrapper
def incubate(env, s, temperature, duration, shaking = False, containers=None, mag=False):

    incubate_temps = ['4:celsius', '-20:celsius', 'ambient']
    if temperature in incubate_temps:
        where = temp_to_where(temperature)
        if mag:
            assert where is 'ambient', 'Can only do magnetic incubation at ambient.'
            s = plate_to_mag_adapter(env, s, duration, containers=None)
            s = plate_off_mag_adapter(env, s, containers=None)
        else:
            for c in get_containers(env, s):
                env.protocol.incubate(c, where, duration, shaking=False)
    else:
        assert not mag, 'Cant perform magnetic incubation in thermocycler'
        program = [{"cycles": 1, "steps": [{
                        "duration": duration,
                        "temperature": temperature}]}]
        for c in get_containers(env, s):
            env.protocol.thermocycle(c, groups=program,
                                 volume='200:microliter', dataref=None)

    return s


def pipette(env, source_solution, vol, dest_solution):
    '''Transfer a specified volume from the source solution to the
    destination well, appending the pipette command to the protocol objects
    contained in env.protocol.'''

    assert isinstance(source_solution, Solution)
    assert isinstance(dest_solution, Solution)

    assert to_pint(vol) >= 0 * ureg.microliter

    if to_pint(vol) > 0 * ureg.microliter:

        dest_solution.add(source_solution, to_pint(vol))

        #print source_solution.container
        #print dest_solution.container

        src = source_solution.ref(env)
        assert src is not None
        dst = dest_solution.ref(env)
        assert dst is not None

        env.protocol.transfer(source_solution.ref(env),
                              dest_solution.ref(env),
                              pint_to_str(vol))

        dest_solution.update_history({"operation":"add",
                               "volume":vol,
                               "source_components":source_solution.components,
                               "source_container":source_solution.container})

        source_solution.update_history({"operation":"remove",
                                 "volume":vol,
                                 "target_container":dest_solution.container})


@operation_wrapper
def relocate_volume(env, s, vol=None, fraction=None, containers=None):
    '''The specified volume is taken from source and transferred to
    a newly allocated volume.
    TODO: extend to be able to handle cases where you're trying to pipette the
    supernatant off of a easily re-suspendable pellet.
    '''
    t = []
    for sol in s:
        if isinstance(fraction, float):
            assert hasattr(sol, 'volume'), 'Cant determine a fractional volume without knowing the volume of the source solution.'
            vol = sol.volume * fraction
        vol = to_pint(vol)
        target = walloc(env, Solution(volume=vol))
        pipette(env, sol, vol, target)
        t.append(target)
    return s, t


def dilute_dev(env, s, diluent, vol=None, ratio=None, mix_count=10, frac=None):
    '''
    When volume is specified, this is used. If ratio is specified and volume
    is not specified, the volume to use is computed as ratio*s.volume. If ratio
    and vol are not specified, but frac is specified, vol is computed as
    vol = frac * s.volume / (1 - frac)
    '''

    if isinstance(diluent, list):
        source = env.db.find_solution_set(diluent, return_one=True, require_hit=True)
    elif not isinstance(diluent, Solution):
        raise ValueError('dilute() parameter diluent must be either component list or Solution')

    for solution in s:
        assert isinstance(solution, Solution), 'target solutions for dilute() must be Solution objects'
        if ratio is not None:
            vol = solution.volume * ratio
        elif frac is not None:
            assert isinstance(frac, float), 'frac must be a float in the interval [0,1]'
            assert frac < 1, 'frac must be a float in the interval [0,1]'
            vol = frac * solution.volume / (1 - frac)
        else:
            assert vol is not None, 'Must specify either vol, ratio, or frac.'

        vol = to_pint(vol)
        pipette(env, source, vol, solution)

    #s = mix(env, s, mix_count)

    return s



def react(env, target=None, incubation=None, inputs=None, inactivation=None,
          config=None):
    '''Perform a generalized reaction, consisting of constructing a solution,
    incubating it according to any program of incubation, and constructing a
    secondary solution, any of the three of which may be left as identity
    transformations.

    Notes:
    ------
    - if target, incubation, or inactivation are specified in rxn as well as
        as a parameter, the parameter is given preference
    '''

    assert isinstance(target, Solution)

    s = compile_solutions(env=env,
                          target_solution=target,
                          samples=inputs)

    # extract containers for solution set
    #containers = set([si.ref(env) for si in s])
    #containers = get_containers(env, s)

    # Perform each incubation in the series
    if isinstance(incubation, list):
        for inc in incubation:

            s = incubate(env, s, inc['temp'], inc['time'])

            '''
            if True: # condition #:
                s = incubate(env, s, inc)

            elif True: # condition #:
                s = thermocycle(env, s, program)
            '''

    '''
    # Considering including an inactivation since this is part of many enzymatic
    # reactions.
    if isinstance(inactivation, dict) and ('type' in inactivation) and \
        ('args' in inactivation):

        if inactivation['type'] is 'temperature':

        elif inactivation['type']
        s = inactivate(inactivation)
    '''

    return s




