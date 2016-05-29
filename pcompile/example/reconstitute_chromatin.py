#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.operations import react
from pcompile.helper import step_wrapper

@step_wrapper
def step(env, rxn, inputs=None):
    """In-vitro reconstituting of chromatin with Active Motif kit,
    Catalog No. 53500, protocol via http://www.activemotif.com/documents/134.pdf
    """

    '''
    1. Set water bath to 27°C. (transcriptic task)

    2. compile reaction 1, in order above.

    3.0 Gently vortex the samples.

    3.1 Centrifuge to collect material at the bottom of the
    microcentrifuge tube.

    3.2 Incubate on ice for 15 minutes.

    4. Add 64.3 µl of Low Salt Buffer to each reaction.

    5. compile reaction 2, in order above

    6.0 Gently vortex the samples.

    6.1 Briefly centrifuge to collect material at the bottom of the
    microcentrifuge tube.

    6.1 Incubate at 27°C for 4 hours. After incubation, the sample may be
    stored at 4°C for up to 2 days. Chromatin should not be frozen at this point.

    return s
    '''

    pass


if __name__ == '__main__':
    from pcompile.harness import run
    run(step)

'''
reconstitute.yml
----------------

- reaction 1 (in order)

              Positive Negative
    Component Control  Control Sample
    Recombinant h-NAP-1 1.4 µl – 1.4 µl
    HeLa Core Histones 1.8 µl – 1.8 µl
    High Salt Buffer 10 µl 10 µl 10 µl
    Low Salt Buffer – 3.2 µl –


- reaction 2 (in order)

    Component Control Control Sample
    Recombinant ACF Complex 2.5 µl – 2.5 µl
    Complete 10X ATP Regeneration System 10 µl 10 µl 10 µl
    Supercoiled DNA (control) 10 µl 10 µl –
    Sample DNA – – 1 µg
    Low Salt Buffer – 2.5 µl –
    dH2O – – to 100 µl
    Total Volume 100 µl 100 µl 100 µl

'''


