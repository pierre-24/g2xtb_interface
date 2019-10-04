import tempfile
import ctypes
from ctypes import cdll, Structure, c_double, c_int, c_bool, POINTER, c_char_p
import numpy as np
import os

c_int_p = POINTER(c_int)
c_bool_p = POINTER(c_bool)
c_double_p = POINTER(c_double)


# define options structure:
class SCC_options(Structure):
    _fields_ = [
        ('prlevel', c_int),
        ('parallel', c_int),
        ('acc', c_double),
        ('etemp', c_double),
        ('grad', c_bool),
        ('restart', c_bool),
        ('maxiter', c_int),
        ('solvent', ctypes.c_char * 20)
    ]


class XTBError(Exception):
    pass


class XTB:
    def __init__(self, accuracy: float = 1.0, temperature: float = 300.0, print_level: int = 2):

        self.accuracy = accuracy
        self.temperature = temperature
        self.print_level = print_level

        self.lib = None
        self.callback = None

        self._load_lib()
        self._setup()

    def _load_lib(self) -> None:
        """Load the xtb library"""
        try:
            self.lib = cdll.LoadLibrary('libxtb.so')
        except OSError as e:
            raise XTBError('error while loading libxtb.so: {}'.format(e))

    def _setup(self):
        """Setup the callback"""

        raise NotImplementedError()

    def compute(self, atoms_type: np.ndarray, atoms: np.ndarray, charge: int = 0, **kwargs):
        """Compute"""

        raise NotImplementedError()


class GNF2(XTB):

    def _setup(self):
        self.lib.GFN2_calculation.argtypes = [
            c_int_p,  # natoms
            c_int_p,  # attyp
            c_double_p,  # charge
            c_double_p,  # coords
            POINTER(SCC_options),  # opt
            c_char_p,  # output
            c_double_p,  # energy
            c_double_p,  # grad
            c_double_p,  # dipole
            c_double_p,  # q
            c_double_p,  # dipm
            c_double_p,  # qp
            c_double_p  # wbo
        ]

        self.callback = self.lib.GFN2_calculation

    def compute(self, atoms_type: np.ndarray, coordinates: np.ndarray, charge: int = 0, **kwargs) -> dict:
        """Compute with GFN2

        ``kwargs`` may be:

        + ``max_iteration``
        + ``solvent``
        """

        # get options
        max_iterations = kwargs.get('max_iterations', 250)
        solvent = kwargs.get('solvent', 'none')

        # check coordinates
        number_of_atoms = atoms_type.shape[0]

        atoms_type = np.array(atoms_type, dtype=np.int32)  # use int32

        if len(coordinates.shape) == 1:
            if coordinates.shape[0] / 3 != number_of_atoms:
                raise XTBError('atoms_type and coordinates does not match')
        else:
            if coordinates.shape[0] != number_of_atoms:
                raise XTBError('atoms_type and coordinates does not match')

            coordinates = coordinates.flatten(order='F')

        # create output variables (! use Fortran order)
        energy = c_double(.0)
        dipole = np.zeros(3)
        charges = np.zeros(number_of_atoms)
        gradient = np.zeros((3, number_of_atoms), order='F')
        dipoles = np.zeros((3, number_of_atoms), order='F')
        quadrupoles = np.zeros((6, number_of_atoms), order='F')
        wiberg = np.zeros((number_of_atoms, number_of_atoms), order='F')

        # create options
        options = SCC_options(
            c_int(self.print_level),
            c_int(0),
            c_double(self.accuracy),
            c_double(self.temperature),
            c_bool(True),  # gradient
            c_bool(False),
            c_int(max_iterations),
            solvent.encode('utf-8')
        )

        # compute
        fd, path = tempfile.mkstemp()

        status = self.callback(
            c_int(number_of_atoms),
            atoms_type.ctypes.data_as(c_int_p),
            c_double(charge),
            coordinates.ctypes.data_as(c_double_p),
            options,
            path.encode('utf-8'),
            c_double_p(energy),
            gradient.ctypes.data_as(c_double_p),
            dipole.ctypes.data_as(c_double_p),
            charges.ctypes.data_as(c_double_p),
            dipoles.ctypes.data_as(c_double_p),
            quadrupoles.ctypes.data_as(c_double_p),
            wiberg.ctypes.data_as(c_double_p)
        )

        if status != 0:
            raise XTBError('error while running XTB (status is {})'.format(status))

        with open(path) as f:
            output = f.read()

        os.close(fd)
        os.remove(path)

        # store output(s)
        return {
            'output': output,
            'energy': energy.value,
            'charges': charges,
            'dipole': dipole,
            'dipoles': dipoles,
            'gradient': -gradient.T,
            'quadrupole': quadrupoles,
            'wbo': wiberg
        }
