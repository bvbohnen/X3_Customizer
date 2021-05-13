'''
Place to test individual transforms.
'''

# Import all transform functions.
from X3_Customizer import *

# Select if this is modifying vanilla or XRM or LU.
version = 'Vanilla'
#version = 'XRM'
#version = 'LU'
version = 'FL'


# Some convenience translation, to make easier if/else statements.
Vanilla = version == 'Vanilla'
XRM = version == 'XRM'
LU = version == 'LU'

if Vanilla:
    Set_Path(
        path_to_x3_folder = r'D:\Games\Steam\SteamApps\common\x3 terran conflict vanilla',
        #path_to_source_folder = 'vanilla_source'
    )
elif XRM:
    Set_Path(
        path_to_x3_folder = r'D:\Games\x3 terran conflict xrm',
        #path_to_addon_folder = r'C:\Base\x3 terran conflict xrm\addon',
        #path_to_source_folder = 'xrm_source'
        #path_to_output_folder = 'custom_output'
    )
elif LU:
    Set_Path(
        path_to_x3_folder = r'D:\Games\Steam\SteamApps\common\x3 terran conflict LU',
    )
elif version == 'FL':
    Set_Path(
        path_to_addon_folder = r'D:\Games\Steam\SteamApps\common\x3 terran conflict\addon2',
    )

# File cleanup; comment out to allow later tests to run.
if 0:
    Settings.skip_all_transforms = True
    
# Change settings to save as unpacked.
if 1:
    Settings.output_to_catalog = False

# Testing out catalog output.
#Settings.output_to_catalog = True
# Simple transform to trigger catalog write.
#Adjust_Ship_Speed(adjustment_factors_dict = {'SG_SH_M4' : 1.5})


# Experimental spacefly script ender.
# -Works.
#Kill_Spaceflies()
#Prevent_Accidental_Spacefly_Swarms()


# Experimental code to suppress complex connecting tubes.
# May address poor complex scaling issues (pending tests).
# Don't use; causes horrible framerates, and needs more exploration
#  into what's going on or if this is useful.
#Transforms.T_Obj_Code._Prevent_Complex_Connectors()

# Experimental code to try to find the complex related game slowdown.
#Remove_Complex_Related_Sector_Switch_Delay()

# Extract files for viewing, unchanged.
if 0:
    file_paths = [
        'L/x3story.obj'
        ]
    for path in file_paths:
        game_file = File_Manager.Load_File(path)
        # Treat as modified to force saving.
        game_file.modified = True
    # Change settings to save as unpacked.
    Settings.output_to_catalog = False

# Obj stuff.
if 0:
    pass

    #Adjust_Max_Seta(20)
    #Adjust_Max_Speedup_Rate(4)
    Preserve_Captured_Ship_Equipment()

    # These are broken in FL:
    #Remove_Complex_Related_Sector_Switch_Delay()
    #Allow_Valhalla_To_Jump_To_Gates()
    # Not for FL (uses tboarding instead).
    #Set_Max_Marines(
    #        tm_count      = 15,
    #        tp_count      = 60,
    #        m6_count      = 15,
    #        capital_count = 60,
    #        sirokos_count = 80,
    #    )
    # FL said to have a way to kill spaceflies through script instead.
    #Kill_Spaceflies()

    # These tentatively work in FL.
    #Adjust_Max_Speedup_Rate(4)
    #Stop_GoD_From_Removing_Stations()
    #Keep_TLs_Hired_When_Empty()
    #Prevent_Accidental_Spacefly_Swarms()
    #Disable_Combat_Music()
    #Remove_Combat_Beep()
    #Disable_Docking_Music()
    #Preserve_Captured_Ship_Equipment()
    #Prevent_Ship_Equipment_Damage()
    #Hide_Lasertowers_Outside_Radar()
    #Force_Infinite_Loop_Detection(operation_limit = 10000)
    #Remove_Factory_Build_Cutscene()
    #Stop_Events_From_Disabling_Seta(
    #        on_missile_launch = True,
    #        on_receiving_priority_message = True,
    #        on_collision_warning = True,
    #        on_frame_input = True,
    #    )
    #Disable_Asteroid_Respawn()