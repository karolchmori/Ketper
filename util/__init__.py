import importlib

# Import submodules
from . import file
from . import create
from . import naming
from . import select
from . import intersection
from . import random
from . import rigging
from . import rendering

# Optionally, reload submodules to reflect any changes (useful in a development environment)
submodules = [file, create, naming, select, intersection, random, rigging, rendering]

for module in submodules:
    importlib.reload(module)
