'''
Functions related to mission director scripts.
'''
from .Bug_Fixes import Fix_Corporation_Troubles_Balance_Rollover
from .Bug_Fixes import Fix_Terran_Plot_Aimless_TPs
from .Bug_Fixes import Fix_Dual_Convoy_Invincible_Stations
from .Bug_Fixes import Fix_Reset_Invincible_Stations

from .Misc import Adjust_Generic_Missions
from .Misc import Disable_Generic_Missions
from .Misc import Convoys_made_of_race_ships

from .Support import Make_Director_Shell
from .Support import Generate_Director_Text_To_Update_Shipyards

from .Tunings import Standardize_Tunings
from .Tunings import Standardize_Start_Plot_Overtunings


# Fill in the default documentation category for the transforms.
# Use a dict copy, since this adds new locals.
for _attr_name, _attr in dict(locals()).items():
    if hasattr(_attr, '_category'):
        _attr._category = 'Director'
