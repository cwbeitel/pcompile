# pcompile

A framework for building automated protocols.

## Cite this project (coming soon)

Beitel CW, ... , Eisen JA (2015) Pcompile: A compiler for robotic laboratory protocols. PeerJ ?? http://dx.doi.org/??/peerj.??

## Example

Pcompile is a framework for building molecular and cellular biology protocols in modular components that can be tested independently, combined, remixed, and optimized. Let's say you have an idea to test out a new protocol that you thought of over lunch (for measuring the cell co-localization of DNA). Here's how you would write it:

    def step(env, rxn):
        """Tag-associated sequencing (TAS)
        """
        s = lysis(env, rxn.lysis, rxn.inputs)
        s = digestion(env, rxn.digestion, s)
        s = ligation(env, rxn.ligation, s)
        s = reversal(env, rxn.reversal, s)
        s = purification(env, rxn.purification, s)
        s = library(env, rxn.library, s)

        return s

This is expressing a new series of reactions (itself a reaction), TAS, as a combination of multiple sub-reactions, each of which have been developed and validated previously. Unless otherwise specified, in a config file or with command-line options (or via a graphical UI, perhaps), these steps would run with their default parameters. And that's it! There's a lot going on in the background. For example, what reagents is it going to use? What plates? Where will it run? Etc. Also, you might need to debug it, might want to optimize it, or might wonder how you'll share it with others. More on that below.

## Design Philosophy

* Physical operations are distinct from the experimenter's intent behind exercising them.
* The expression of a protocol should cature the experimenter's intent as to how the protocol would perturb the state of the biological system (e.g. 'separating DNA from proteins' instead of 'wash->incubate->spin->etc.')
* Having a protocol specified in programmatic form or able to run on an automated lab platform doesn't make it re-usable unless you're always going to run it in isolation, always on the exact same kind of input.
* The protocol writing interface should be designed backward from the way molecular biologists and other scientists think about experiments.
* The final interface to writing and running protocols and doing molecular biology should allow experimenters to spend very little time on finding reagents, planning and performing experiments, debugging, etc. Your average graduate student or postdoc should be able to perform an experiment in a similar way as does their P.I., where much of the work is dispatched to a system (or employee) to do the work. The purpose is to enable a dramatic re-allocation of experimenter time away from tasks that can be automated, to the task of thinking of creative experiments to test interesting and important hypotheses.

## TODO

* Perhaps the most significant TODO is for the system to first build a graph of the operations to be performed, then to optimize the allocation of resources across that graph. After a friend explained to me how compilers work that seemed pretty obvious but the way I wrote it here optimizes each step in succession. So it doesn't currently make good global decisions about resource use.
* Also, this was my first attempt at a complex systems project and in the process of writing this I've learned a lot about the peril of tighly coupled code without good separation of concerns. Work on this would be significantly improved by starting over with a careful architecture plan before writing any code.

## LICENSE

Code is licensed under the BSD License, see LICENSE.

