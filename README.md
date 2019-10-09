# `g2xtb_interface`

Interface between Gaussian and xTB for geometry optimization, using the `external` keyword.

For convenience, the interface is written in Python 3.
It only perform calculation with the GFN2 parametrization.

## Installation

1. Be sure to have a copy of [xTB](https://github.com/grimme-lab/xtb/) (in version 6.2) and Gaussian (tested with Gaussian 09 and 16). You will also need MKL (check with your system administrator, but version >= 2017 is required).
1. Clone this repository
2. Install the requirements: `numpy` and `fortranformat`, for example with pip: `pip3 install [--user] numpy fortranformat`. 

## Usage

Before running a calculation (so, in your job script if you use a cluster), make sure that you have python 3 in the `$PATH` (if you use a virtualenv or pipenv, make sure you `source` it).

You also need to include MKL (check with you system administrator) and xTB in `$LD_LIBRARY_PATH`: for the later, use

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:</path/to/you/xtb/directory>/lib/
```

(see the [current python xTB interface documentation](https://github.com/grimme-lab/xtb/blob/master/python/xtb.py) for more information).

Then, in the gaussian input, use

```text
#p opt external="/path/to/g2xtb_interface/interface.py"
```

as the input line (notice the quotes), and run gaussian normally.
It will use the xTB GFN2 parametrization to perform the optimization (GFN 1 and GFN 0 are not [yet?] available).

Note that you can set some options:

```text
  -a ACCURACY, --accuracy ACCURACY (default=1.0)
  -t TEMPERATURE, --temperature TEMPERATURE (default=300.0)
  -V VERBOSE, --verbose VERBOSE (default=1)
  -s SOLVENT, --solvent SOLVENT (default=none)
  -M MAX_ITERATIONS, --max-iterations MAX_ITERATIONS (default=250)
```

For example, to perform an optimization in water,

```text
#p opt external="/path/to/g2xtb_interface/interface.py -s h2o"
```

See [the examples](./examples/). It is also possible to use `External` in ONIOM, see the "Examples" section of the [`External` keyword](http://gaussian.com/external/).

## Links

For xTB:

+ [Current Python xTB interface](https://github.com/grimme-lab/xtb/blob/master/python/xtb.py).
+ [xTB API documentation](https://xtb-docs.readthedocs.io/en/latest/dev_interface.html).

For Gaussian:

+ The Gaussian 16 [`External` keyword](http://gaussian.com/external/) documentation for the interface.
+ [`goptimizer`](https://github.com/andersx/goptimizer), a simple example of what I'm trying to achieve.
+ [`garleek`](https://github.com/insilichem/garleek), a more complex example.