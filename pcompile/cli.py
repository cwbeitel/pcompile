#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile.harness import run
import click

@click.group()
def cli():
    '''A general-purpose compiler for automated experiments.'''
    pass

@cli.command()
@click.option('-v', '--verbose', help='Print verbose logging.', default=False)
@click.option('--debug', help='Print debug information.', default=False)
def make(verbose, debug):
    '''Compile an automated protocol.'''
    from something import fn
    run(fn)

@cli.command()
def app():
    '''Launch the Rosalind UI.'''
    from pcompile.experimental.app.app import app #yikes..
    app.run(host='0.0.0.0', port=5000)

# ------------------
# Examples

@cli.group()
def examples():
    '''Run one of the core Rosalind protocol examples'''
    pass

@examples.command()
def amplicon_library():
    '''Amplicon sequencing library prep from purified DNA'''
    from pcompile.example.amplicon_library import step
    run(step)

@examples.command()
def crosslink():
    '''Crosslink DNA/proteins'''
    from pcompile.example.crosslink import step
    run(step)

@examples.command()
def digestion():
    '''Enzymatic digestion of DNA'''
    from pcompile.example.digestion import step
    run(step)

@examples.command()
def hichicago():
    '''Chromatin-reconstitution proximity ligation (Hi-Chicago)'''
    from pcompile.example.hichicago import step
    run(step)

@examples.command()
def jpeg():
    '''Pipette colored liquid into a plate to reproduce a jpeg'''
    from pcompile.example.jpeg import step
    run(step)

@examples.command()
def ligation():
    '''DNA ligation'''
    from pcompile.example.ligation import step
    run(step)

@examples.command()
def lysis():
    '''Enzymatic cellular lysis'''
    from pcompile.example.lysis import step
    run(step)

@examples.command()
def pcr():
    '''Polymerase chain reaction (PCR) amplification of DNA'''
    from pcompile.example.pcr import step
    run(step)

@examples.command()
def purification():
    '''Bead purification of DNA'''
    from pcompile.example.purification import step
    run(step)

@examples.command()
def quantification():
    '''Quantify DNA concentration'''
    from pcompile.example.quantification import step
    run(step)

@examples.command()
def reconstitute_chromatin():
    '''In-vitro reconstitution of chromatin'''
    from pcompile.example.reconstitute_chromatin import step
    run(step)

@examples.command()
def reversal():
    '''Reverse chromatin crosslinks'''
    from pcompile.example.reversal import step
    run(step)

@examples.command()
def tas():
    '''Tag-associated sequencing (TAS) library prep'''
    from pcompile.example.tas import step
    run(step)


