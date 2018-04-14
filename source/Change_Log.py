'''
Change Log:
 * 1.x
   - Original project development for private use.
 * 2.0
   - Restructuring of project for general use, isolating individual
     transforms, separating out transform calls, adding robustness.
     Filling out documentation generation.
 * 2.01
   - Added Convert_Beams_To_Bullets.
 * 2.02
   - Added Adjust_Generic_Missions.
   - Added new arguments to Enhance_Mosquito_Missiles.
   - Adjusted default ignored weapons for Convert_Beams_To_Bullets.
 * 2.03
   - Added Add_Ship_Life_Support.
   - Added Adjust_Shield_Regen.
   - Added Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio.
   - Added Standardize_Ship_Tunings.
   - New options added for Adjust_Weapon_DPS.
   - New option for Adjust_Ship_Hull to scale repair lasers as well.
   - Several weapon transforms now ignore repair lasers by default.
   - Command line call defaults to User_Transforms.py if a file not given.
 * 2.04
   - Added Add_Ship_Equipment.
   - Added XRM_Standardize_Medusa_Vanguard.
   - Added Add_Ship_Variants, Add_Ship_Combat_Variants, Add_Ship_Trade_Variants.
 * 2.05
   - Updates to Add_Ship_Variants to refine is behavior and options.
   - Added in-game script for adding generated variants to shipyards.
   - XRM_Standardize_Medusa_Vanguard replaced with Patch_Ship_Variant_Inconsistencies.
 * 2.06
   - Updated scaling equation fitter to be more robust; functionality unchanged.
   - Update to Adjust_Missile_Damage to standardize the scaling function
     to support typical tuning paramaters.
   - Added Expand_Bomber_Missiles.
   - Added Add_Ship_Cross_Faction_Missiles.
   - Add_Ship_Boarding_Pod_Support.
   - Changed documentation generator to include more text in the readme file,
     and to categorize transforms.
 * 2.07
   - Minor tweak to Add_Ship_Variants, allowing selection of which variant will
     be set to 0 when an existing variant is used as a base ship.
   - Adjust_Missile_Damage has new parameters to scale missile ware volume
     and price in line with the damage adjustment.
 * 2.08
   - Added Adjust_Gate_Rings.
   - Removed Swap_Standard_Gates_To_Terran_Gates, which is replaced by an 
     option in the new transform.
 * 2.09
   - Added Add_Job_Ship_Variants.
   - Added Change_Ware_Size.
   - Tweaked Add_Ship_Variants to specify shield_conversion_ratios in args.
   - Unedited source files will now be copied to the main directory, in case
     a prior run did edit them and needs overwriting.
 * 2.10
   - New option added to Adjust_Gate_Rings, supporting a protrusionless ring.
   - Added Add_Script, generic transform to add pregenerated scripts.
   - Added Disable_OOS_War_Sector_Spawns.
   - Added Convert_Attack_To_Attack_Nearest.
   - Bugfix for when the first transform called does not have file dependencies.
   - Renames the script 'a.x3customizer.add.variants.to.shipyards.xml' to
     remove the 'a.' prefix.
 * 2.11
   - Minor fix to rename .pck files in the addon/types folder that interfere
     with customized files.
 * 2.12
   - Added Add_CLS_Software_To_More_Docks.
   - Added Remove_Khaak_Corvette_Spin.
   - Added option to Adjust_Ship_Laser_Recharge to adjust ship maximum
     laser energy as well.
   - Added cap on mosquito missile damage when adjusting damages, to avoid
     possible OOS combat usage.
   - Bugfix for transforms which adjust laser energy usage, to ensure the
     laser can store enough charge for at least one shot.
   - Bugfix for adjusting missile hulls, to add entries to globals when missing.
   - Bugfix for file reading which broke in recent python update.
   - Added patch support for editing files without doing full original source
     uploads. Disable_OOS_War_Sector_Spawns now uses a patch.
   - Added support for automatically filling in the source folder with any
     necessary scripts.
 * 2.13
   - Added Allow_CAG_Apprentices_To_Sell.
   - Added Increase_Escort_Engagement_Range.
   - Added Fix_OOS_Laser_Missile_Conflict.
 * 2.14
   - Bugfix for Add_CLS_Software_To_More_Docks.
 * 2.15
   - Added Change_Sector_Music.
 * 2.16
   - Added Complex_Cleaner_Bug_Fix.
   - Added Complex_Cleaner_Use_Small_Cube.
 * 2.17
   - Added Add_More_Factory_Sizes.
   - Added Remove_Ship_Variants.
   - Added Fleet_Interceptor_Bug_Fix.
   - Tweaked Adjust_Job_Count to support reducing counts to 0.
   - Switched Add_Ship_Variants to use a director script to update shipyards.
 * 2.18
   - Bug fixes for the director scripts, to ensure they work on new
     games and on terran/atf shipyards with cross-faction wares.
 * 2.19
   - Support added for editing .obj files containing game assembly code.
   - Added Adjust_Max_Seta.
   - Added Adjust_Max_Speedup_Rate.
   - Added Stop_Events_From_Disabling_Seta.
   - Added Set_Max_Marines.
 * 2.20
   - Added Disable_Combat_Music.
   - Added Remove_Sound.
   - Added Remove_Combat_Beep.
 * 2.21
   - Added Stop_GoD_From_Removing_Stations.
   - Added Disable_Asteroid_Respawn.
 * 2.22
   - Rewrite of much of the file loading system.
   - Added support for loading source files from cat/dat pairs, when the file
     is not found in the specified source folder.
   - Message log, as well as a log of files written, will now be written
     to a log folder customized by Set_Path.
 * 3.0
   - Major rewrite of the file handling system.
   - Can now load original data from loose files in the game directories
     as well as the user source folder and cat/dat pairs.
   - Normalized file creation in all transforms.
   - Added hashes to log of files written, to recognize when they
     change externally.
   - Added executable generation using pyinstaller.
   - Added alternative scaling functions to bypass scipy requirement,
     which otherwise bloats the exe.
 * 3.1
   - Bugfix for gate edits, adding an end-of-file newline that x3
     requires and was lost in the file system conversion.
   - Added Allow_Valhalla_To_Jump_To_Gates.
'''
# Note: changes moved here for organization, and to make them easier to
# break out during documentation generation.

def Get_Version():
    '''
    Returns the highest version number in the change log,
    as a float for easy comparisons.
    '''
    # Traverse the docstring, looking for ' *' lines, and keep recording
    #  strings as they are seen.
    version = ''
    for line in __doc__.splitlines():
        if not line.startswith(' *'):
            continue
        version = line.split('*')[1].strip()
    return float(version)