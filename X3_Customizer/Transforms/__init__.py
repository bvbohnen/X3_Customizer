
# Make all transform functions accessible.
# First import will grab everything, including misc functions.
from .T_Backgrounds import *
from .T_Director import *
from .T_Factories import *
from .T_Gates import *
from .T_Globals import *
from .T_Jobs import *
from .T_Missiles import *
from .T_Obj_Code import *
from .T_Scripts import *
from .T_Shields import *
from .T_Ships import *
from .T_Ships_Variants import *
from .T_Sounds import *
from .T_Universe import *
from .T_Wares import *
from .T_Weapons import *

#-Removed; individual transform names don't start with T_ like the files.
## Trim out non-transforms from the locals, to avoid excessive imports.
## This is not critical, but makes the module debug locals look cleaner
##  when triggering breakpoints.
## Could also consider putting an underscore on all such function names
##  to avoid accidental imports, but it may be cleaner to do it here.
## Loop over the names of vars in the globals dict.
## Underscore this iterator name to avoid it getting grabbed by * imports.
#for _object_name in list(globals().keys()):
#    # Remove everything that doesn't start with T_ or __ (to avoid removing
#    #  critical python stuff).
#    if not _object_name.startswith('__') and not _object_name.startswith('T_'):
#        del(globals()[_object_name])


# Special case: allow imports of the transforms to also capture some key
#  setup functions. For now, just Set_Path.
# This could be better organized, but is kept for compatability with
#  older versions.
from File_Manager.File_Manager import Set_Path
# Also make settings available, for a somewhat more scalable way to
#  apply custom settings without special functions.
from Common.Settings import Settings