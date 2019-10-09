"""Gaussian interface, mainly inspired by https://github.com/andersx/goptimizer/blob/master/goptimizer.py"""

import numpy as np
import fortranformat as ff


class GaussianException(Exception):
    pass


class Interface:
    """Interface between gaussian and other program"""

    @staticmethod
    def read(fp) -> dict:
        """Read the *.EIn file"""
        lines = fp.readlines()

        inf = lines[0].split()
        try:
            number_of_atoms, derivative, charge, spin = tuple(int(x) for x in inf)
        except ValueError as e:
            raise GaussianException(e)

        if derivative > 1:
            raise GaussianException('requested derivative ({}) is too large (maximum is 1)'.format(derivative))

        if len(lines) < number_of_atoms + 1:
            raise GaussianException('input is smaller than the number of atoms')

        output = {
            'number_of_atoms': number_of_atoms,
            'derivative_requested': derivative,
            'charge': charge,
            'spin': spin,
        }

        atoms_type = np.zeros(number_of_atoms, dtype=np.int32)
        coordinates = np.zeros((number_of_atoms, 3))
        for i in range(number_of_atoms):
            inf = lines[i + 1].split()
            atoms_type[i] = int(inf[0])
            coordinates[i] = list(float(x) for x in inf[1:4])

        output.update({'atoms_type': atoms_type, 'coordinates': coordinates})

        return output

    @staticmethod
    def write(fp,
              derivative_requested: int,
              energy: float,
              number_of_atoms: int,
              dipole: np.ndarray = None,
              gradient: np.ndarray = None,
              polarizability: np.ndarray = None,
              dipole_derivatives: np.ndarray = None) -> None:
        """Write the *.EOu file"""

        # Define output formats
        head_format = ff.FortranRecordWriter('4D20.12')
        body_format = ff.FortranRecordWriter('3D20.12')

        if dipole is None:
            dipole = np.zeros(3)

        fp.write(head_format.write([energy, *dipole]) + '\n')

        # gradient
        if derivative_requested > 0:
            if gradient is None:
                gradient = np.zeros((number_of_atoms, 3))

            for i in range(number_of_atoms):
                fp.write(body_format.write(gradient[i]) + '\n')

        # polarizability
        if polarizability is None:
            polarizability = np.zeros((2, 3))

        for i in range(2):
            fp.write(body_format.write(polarizability[i]) + '\n')

        # dipole derivatives
        if dipole_derivatives is None:
            dipole_derivatives = np.zeros((3 * number_of_atoms, 3))

        for i in range(3 * number_of_atoms):
            fp.write(body_format.write(dipole_derivatives[i]) + '\n')
