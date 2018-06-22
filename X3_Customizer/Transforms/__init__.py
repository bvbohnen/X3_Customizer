'''
Subpackage with all transforms.
'''
# Make all transform functions accessible.
# First import will grab everything, including misc functions.
# TODO: name specific imports, for good form.
from .T_Backgrounds import *
from .T_Director import *
from .T_Factories import *
from .T_Gates import *
from .T_Globals import *
from .T_Jobs import *
from .T_Missiles import *
from .T_Scripts import *
from .T_Shields import *
from .T_Ships import *
from .T_Ships_Variants import *
from .T_Sounds import *
from .T_Universe import *
from .T_Wares import *

# Subpackages; can import all.
from .T_Obj_Code import *
from .T_Weapons import *
