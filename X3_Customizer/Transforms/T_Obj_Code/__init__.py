'''
Obj file edits, broken out due to length.
'''
from .Seta import Adjust_Max_Seta
from .Seta import Adjust_Max_Speedup_Rate
from .Seta import Stop_Events_From_Disabling_Seta

from .Spaceflies import Kill_Spaceflies
from .Spaceflies import Prevent_Accidental_Spacefly_Swarms

from .Misc import Set_Max_Marines
from .Misc import Disable_Combat_Music
from .Misc import Stop_GoD_From_Removing_Stations
from .Misc import Disable_Asteroid_Respawn
from .Misc import Allow_Valhalla_To_Jump_To_Gates
from .Misc import Remove_Factory_Build_Cutscene
from .Misc import Keep_TLs_Hired_When_Empty
from .Misc import Disable_Docking_Music
from .Misc import _Disable_Friendly_Fire
from .Misc import Preserve_Captured_Ship_Equipment

from .Complex import _Prevent_Complex_Connectors
from .Complex import Remove_Complex_Related_Sector_Switch_Delay

# Fill in the default documentation category for the transforms.
# Use a dict copy, since this adds new locals.
for _attr_name, _attr in dict(locals()).items():
    if hasattr(_attr, '_category'):
        _attr._category = 'Obj_Code'
