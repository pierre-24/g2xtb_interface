#!/usr/bin/env python

import argparse
import sys

import g2xtb_interface
from g2xtb_interface import XTB, gaussian_interface


def main(prog_args):
    with open(prog_args.msgFile, 'w') as msg:
        print('running g2xtb_interface interface.py', file=msg)

        with open(prog_args.inputFile) as f:
            try:
                parameters = gaussian_interface.Interface.read(f)
            except gaussian_interface.GaussianException as e:
                print('error while loading gaussian input: {}'.format(e), file=msg)
                return 1

        if prog_args.verbose > 0:
            print('\nInput geometry (charge={})'.format(parameters['charge']), file=msg)
            print('---------------------------------------', file=msg)
            print('               Coordinates (Bohr)', file=msg)
            print('Z         X           Y           Z', file=msg)
            print('---------------------------------------', file=msg)
            for i in range(parameters['number_of_atoms']):
                print(
                    '{:<3} {: .8f} {: .8f} {: .8f}'.format(
                        parameters['atoms_type'][i], *parameters['coordinates'][i]), file=msg)
            print('---------------------------------------\n', file=msg)

        kwargs = {
            'solvent': args.solvent if args.solvent else 'none', 'max_iterations': args.max_iterations}

        try:
            r = XTB.GNF2(
                accuracy=prog_args.accuracy, temperature=prog_args.temperature, print_level=prog_args.verbose)
            output = r.compute(
                parameters['atoms_type'], parameters['coordinates'], charge=parameters['charge'], **kwargs)
        except XTB.XTBError as e:
            print('error while computing through xTB: {}'.format(e), file=msg)
            return 1

        print(output['output'], file=msg)

        if prog_args.verbose > 0 and parameters['derivative_requested'] > 0:
            print('\nOutput gradient', file=msg)
            print('----------------------------------------', file=msg)
            print('             Forces (Hartree/Bohr)', file=msg)
            print('           X           Y           Z', file=msg)
            print('----------------------------------------', file=msg)
            for i in range(parameters['number_of_atoms']):
                print(
                    '{:<4} {: .8f} {: .8f} {: .8f}'.format(
                        i, *output['gradient'][i]), file=msg)
            print('----------------------------------------\n', file=msg)

        with open(prog_args.outputFile, 'w') as f:
            try:
                gaussian_interface.Interface.write(
                    f,
                    parameters['derivative_requested'],
                    output['energy'],
                    parameters['number_of_atoms'],
                    dipole=output['dipole'],
                    gradient=output['gradient'])
            except gaussian_interface.GaussianException as e:
                print('error while writing gaussian output: {}'.format(e), file=msg)
                return 1

        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=g2xtb_interface.__doc__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + g2xtb_interface.__version__)

    parser.add_argument('-a', '--accuracy', type=float, default=1.0)
    parser.add_argument('-t', '--temperature', type=float, default=300.0)
    parser.add_argument('-V', '--verbose', type=int, default=1)
    parser.add_argument('-s', '--solvent', type=str)
    parser.add_argument('-M', '--max-iterations', type=int, default=250)

    # the six parameters of Gaussian external program (see http://gaussian.com/external/)
    parser.add_argument('layer')
    parser.add_argument('inputFile')
    parser.add_argument('outputFile')
    parser.add_argument('msgFile')
    parser.add_argument('fchkFile')
    parser.add_argument('matElFile')

    args = parser.parse_args()
    sys.exit(main(args))
