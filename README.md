
X3 Customizer v2.04
------------------

This tool will read in source files from X3, perform transforms on them,
and write the results back out.  Transforms will often perform complex
or repetitive tasks succinctly, avoiding the need for hand editing of
source files.  Source files will generally support any prior modding.

This tool is written in Python, and tested on version 3.6.

Usage:
 * "X3_Customizer <user_transform_module.py>"
   - Runs the customizer using the provided module, located in this
     directory, to specify the path to the AP directory, the folder
     containing the source files to be modified, and the transforms
     to be run. See User_Transforms_Example.py for an example.
     Defaults to running 'User_Transforms.py' if an argument is 
     not provided.
 * "Make_Documentation.py"
   - Generates documentation for this project.

Setup:
  * Transforms will operate on source files which need to be set up
  prior to running this tool. Source files can be extracted using
  X2 Editor 2 if needed. Source files may be provided after any other 
  mods have been applied.

  * Source files need to be located in a folder underneath the 
  specified AP addon directory, and will have an internal folder
  structure matching that of the files in the normal addon directory.

  * Output files will be generated in the addon directory matching
  the folder structure in the source folder. Non-transformed files
  will generate output files. Files which do not have a name matching
  the requirement of any transform will be ignored and not copied.

  * Warning: Generated output will overwrite any existing files.

  Example directory:

    <path to X3 installation>
        addon
            source_folder
                maps
                    x3_universe.xml
                types
                    TBullets.txt
                    TLaser.txt
                    TShips.txt
                    TShips_backup.txt

   This will write to the following files, overwriting any
   existing ones:

    <path to X3 installation>
        addon
            maps
                x3_universe.xml
            types
                TBullets.txt
                TLaser.txt
                TShips.txt

Change Log:
 * 1.x :
   - Original project development for private use.
 * 2.0 :
   - Restructuring of project for general use, isolating individual
     transforms, separating out transform calls, adding robustness.
     Filling out documentation generation.
 * 2.01:
   - Added Convert_Beams_To_Bullets.
 * 2.02:
   - Added Adjust_Generic_Missions.
   - Added new arguments to Enhance_Mosquito_Missiles.
   - Adjusted default ignored weapons for Convert_Beams_To_Bullets.
 * 2.03:
   - Added Add_Ship_Life_Support.
   - Added Adjust_Shield_Regen.
   - Added Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio.
   - Added Standardize_Ship_Tunings.
   - New options added for Adjust_Weapon_DPS.
   - New option for Adjust_Ship_Hull to scale repair lasers as well.
   - Several weapon transforms now ignore repair lasers by default.
   - Command line call defaults to User_Transforms.py if a file not given.
 * 2.04:
   - Added Add_Ship_Equipment.
   - Added XRM_Standardize_Medusa_Vanguard.
   - Added Add_Ship_Variants, Add_Ship_Combat_Variants, Add_Ship_Trade_Variants.

Full documentation found in Documentation.md.

***

Setup methods:

  * Set_Path

***

Transform List:

 * Add_Ship_Combat_Variants
 * Add_Ship_Equipment
 * Add_Ship_Life_Support
 * Add_Ship_Trade_Variants
 * Add_Ship_Variants
 * Adjust_Beam_Weapon_Duration
 * Adjust_Beam_Weapon_Width
 * Adjust_Fade_Start_End_Gap
 * Adjust_Generic_Missions
 * Adjust_Global
 * Adjust_Job_Count
 * Adjust_Job_Respawn_Time
 * Adjust_Missile_Damage
 * Adjust_Missile_Hulls
 * Adjust_Missile_Range
 * Adjust_Missile_Speed
 * Adjust_Particle_Count
 * Adjust_Shield_Regen
 * Adjust_Ship_Hull
 * Adjust_Ship_Laser_Recharge
 * Adjust_Ship_Pricing
 * Adjust_Ship_Shield_Regen
 * Adjust_Ship_Shield_Slots
 * Adjust_Ship_Speed
 * Adjust_Strafe
 * Adjust_Weapon_DPS
 * Adjust_Weapon_Energy_Usage
 * Adjust_Weapon_Fire_Rate
 * Adjust_Weapon_OOS_Damage
 * Adjust_Weapon_Range
 * Adjust_Weapon_Shot_Speed
 * Boost_Truelight_Seeker_Shield_Reactor
 * Clear_Weapon_Flag
 * Color_Sector_Names
 * Convert_Beams_To_Bullets
 * Convert_Weapon_To_Ammo
 * Convert_Weapon_To_Energy
 * Convoys_made_of_race_ships
 * Enhance_Mosquito_Missiles
 * Fix_Pericles_Pricing
 * Remove_Stars_From_Foggy_Sectors
 * Remove_Weapon_Charge_Up
 * Remove_Weapon_Drain_Flag
 * Remove_Weapon_Shot_Sound
 * Replace_Weapon_Shot_Effects
 * Restore_Aldrin_rock
 * Restore_Heavy_Missile_Trail
 * Restore_Hub_Music
 * Restore_M148_Music
 * Restore_Vanilla_Tuning_Pricing
 * Set_Communication_Distance
 * Set_Complex_Connection_Distance
 * Set_Dock_Storage_Capacity
 * Set_Global
 * Set_Minimum_Fade_Distance
 * Set_Missile_Swarm_Count
 * Set_Ware_Pricing
 * Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio
 * Simplify_Engine_Trails
 * Standardize_Ship_Tunings
 * Standardize_Start_Plot_Overtunings
 * Standardize_Tunings
 * Swap_Standard_Gates_To_Terran_Gates
 * XRM_Standardize_Medusa_Vanguard

***

Example input file, User_Transforms_Example.py:

    '''
    Example for using the Customizer, setting a path to
    the AP directory and running some simple transforms.
    '''
    
    #Import all transform functions.
    from Transforms import *
    
    Set_Path(
        #Set the path to the AP addon folder.
        path_to_addon_folder = r'D:\Steam\SteamApps\common\x3 terran conflict\addon',
        #Set the subfolder with the source files to be modified.
        source_folder = 'vanilla_source'
    )
    
    #Speed up interceptors by 50%.
    Adjust_Ship_Speed(adjustment_factors_dict = {'SG_SH_M4' : 1.5})
    
    #Increase frigate laser regeneration by 50%.
    Adjust_Ship_Laser_Recharge(adjustment_factors_dict = {'SG_SH_M7': 1.5})
    
    #Reduce OOS damage by 30%.
    Adjust_Weapon_OOS_Damage(scaling_factor = 0.7)