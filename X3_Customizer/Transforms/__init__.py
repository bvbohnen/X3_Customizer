'''
Subpackage with all transforms.
'''
# Make all transform functions accessible.
# First import will grab everything, including misc functions.
# TODO: name specific imports, for good form.
from .T_Backgrounds import Set_Minimum_Fade_Distance
from .T_Backgrounds import Adjust_Fade_Start_End_Gap
from .T_Backgrounds import Adjust_Particle_Count
from .T_Backgrounds import Remove_Stars_From_Foggy_Sectors

from .T_Director import Adjust_Generic_Missions
from .T_Director import Disable_Generic_Missions
from .T_Director import Standardize_Tunings
from .T_Director import Convoys_made_of_race_ships
from .T_Director import Standardize_Start_Plot_Overtunings

from .T_Factories import Add_More_Factory_Sizes

from .T_Gates import Adjust_Gate_Rings

from .T_Globals import Set_Missile_Swarm_Count
from .T_Globals import Adjust_Missile_Hulls
from .T_Globals import Set_Communication_Distance
from .T_Globals import Set_Complex_Connection_Distance
from .T_Globals import Set_Dock_Storage_Capacity
from .T_Globals import Adjust_Strafe
from .T_Globals import Set_Global
from .T_Globals import Adjust_Global

from .T_Jobs import Adjust_Job_Count
from .T_Jobs import Adjust_Job_Respawn_Time
from .T_Jobs import Set_Job_Spawn_Locations
from .T_Jobs import Add_Job_Ship_Variants

from .T_Missiles import Adjust_Missile_Damage
from .T_Missiles import Enhance_Mosquito_Missiles
from .T_Missiles import Adjust_Missile_Speed
from .T_Missiles import Adjust_Missile_Range

from .T_Scripts import Disable_OOS_War_Sector_Spawns
from .T_Scripts import Allow_CAG_Apprentices_To_Sell
from .T_Scripts import Fix_OOS_Laser_Missile_Conflict
from .T_Scripts import Fleet_Interceptor_Bug_Fix
from .T_Scripts import Increase_Escort_Engagement_Range
from .T_Scripts import Convert_Attack_To_Attack_Nearest
from .T_Scripts import Add_CLS_Software_To_More_Docks
from .T_Scripts import Complex_Cleaner_Bug_Fix
from .T_Scripts import Complex_Cleaner_Use_Small_Cube

from .T_Shields import Adjust_Shield_Regen

from .T_Ships import Adjust_Ship_Hull
from .T_Ships import Adjust_Ship_Speed
from .T_Ships import Adjust_Ship_Laser_Recharge
from .T_Ships import Adjust_Ship_Pricing
from .T_Ships import Adjust_Ship_Shield_Regen
from .T_Ships import Adjust_Ship_Shield_Slots
from .T_Ships import Fix_Pericles_Pricing
from .T_Ships import Patch_Ship_Variant_Inconsistencies
from .T_Ships import Boost_Truelight_Seeker_Shield_Reactor
from .T_Ships import Simplify_Engine_Trails
from .T_Ships import Standardize_Ship_Tunings
from .T_Ships import Add_Ship_Equipment
from .T_Ships import Add_Ship_Life_Support
from .T_Ships import Expand_Bomber_Missiles
from .T_Ships import Add_Ship_Cross_Faction_Missiles
from .T_Ships import Add_Ship_Boarding_Pod_Support
from .T_Ships import Remove_Khaak_Corvette_Spin

from .T_Ships_Variants import Add_Ship_Combat_Variants
from .T_Ships_Variants import Add_Ship_Trade_Variants
from .T_Ships_Variants import Add_Ship_Variants
from .T_Ships_Variants import Remove_Ship_Variants

from .T_Sounds import Remove_Sound
from .T_Sounds import Remove_Combat_Beep

from .T_Universe import Color_Sector_Names
from .T_Universe import Restore_Aldrin_rock
from .T_Universe import Restore_Hub_Music
from .T_Universe import Restore_M148_Music
from .T_Universe import Change_Sector_Music

from .T_Wares import Restore_Vanilla_Tuning_Pricing
from .T_Wares import Set_Ware_Pricing
from .T_Wares import Change_Ware_Size

# Subpackages; these can import all since these already picked out
#  the individual transforms.
from .T_Obj_Code import *
from .T_Weapons import *
