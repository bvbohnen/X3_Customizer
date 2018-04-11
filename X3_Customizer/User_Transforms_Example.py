'''
Example for using the Customizer, setting a path to
the AP directory and running some simple transforms.
'''

# Import all transform functions.
from Transforms import *

Set_Path(
    # Set the path to the AP addon folder.
    path_to_addon_folder = r'D:\Steam\SteamApps\common\x3 terran conflict\addon',
    # Set the subfolder with the source files to be modified.
    source_folder = 'vanilla_source'
)

# Speed up interceptors by 50%.
Adjust_Ship_Speed(adjustment_factors_dict = {'SG_SH_M4' : 1.5})

# Increase frigate laser regeneration by 50%.
Adjust_Ship_Laser_Recharge(adjustment_factors_dict = {'SG_SH_M7': 1.5})

# Reduce OOS damage by 30%.
Adjust_Weapon_OOS_Damage(scaling_factor = 0.7)