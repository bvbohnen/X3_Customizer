X3 Customizer 3.5.2
-----------------

This tool will read in source files from X3, modify on them based on user selected transforms, and write the results back to the game directory. Transforms will often perform complex or repetitive tasks succinctly, avoiding the need for hand editing of source files. Many transforms will also do analysis of game files, to intelligently select appropriate edits to perform.  Some transforms carry out binary code edits, allowing for options not found elsewhere.

Source files will generally support any prior modding. Nearly all transforms support input arguments to set parameters and adjust behavior, according to user preferences. Most transforms will work on an existing save.

This tool is written in Python, and tested on version 3.6. As of customizer version 3, an executable may be generated for users who do not wish to run the Python source code directly.

This tool is designed primarily for Albion Prelude v3.3. Most transforms will support prior or later versions of AP. TC is not supported currently due to some path assumptions.

When used alongside the X3 Plugin Manager, run X3 Customizer second, after the plugin manager is closed, since the plugin manager generates a TWareT.pck file when closed that doesn't capture changes in TWareT.txt.

Usage:

 * "Launch_X3_Customizer.bat [path to user_transform_module.py]"
   - Call from the command line.
   - Runs the customizer, using the provided python control module which will declare the path to the X3 directory and the transforms to be run.
   - Call with '-h' to see any additional arguments.
 * "source\X3_Customizer.py [path to user_transform_module.py]"
   - As above, running the python source code directly.
   - Supports general python imports in the control module.
   - If the scipy package is available, this has additional features omitted from the executable due to file size.
 * "source\Make_Documentation.py"
   - Generates updated documentation for this project, as markdown formatted files README.md and Documentation.md.
 * "source\Make_Executable.py"
   - Generates a standalone executable and support files, placed in the bin folder. Requires the PyInstaller package be available.
 * "source\Make_Patches.py"
   - Generates patch files for this project from some select modified game scripts. Requires the modified scripts be present in the patches folder; these scripts are not included in the repository.
 * "source\Make_Release.py"
   - Generates a zip file with all necessary binaries and source files for general release.

Setup and behavior:

  * Transforms will operate on source files (eg. tships.txt) which are either provided as loose files, or extracted automatically from the game's cat/dat files.

  * Source files are searched for in this priority order, where .pck versions of files take precedence:
    - From an optional user specified source folder, with a folder structure matching the X3 directory structure (without 'addon' path). Eg. [source_folder]/types/TShips.txt
    - From the normal x3 folders.
    - From the incrementally indexed cat/dat files in the 'addon' folder.
    - From the incrementally indexed cat/dat files in the base x3 folder.
    - Note: any cat/dat files in the 'addon/mods' folder will be ignored, due to ambiguity on which if any might be selected in the game launcher.

  * The user controls the customizer using a command script which will set the path to the X3 installation to customize (using the Set_Path function), and will call the desired transforms with any necessary parameters. This script is written using Python code, which will be executed by the customizer.
  
  * The key command script sections are:
    - "from Transforms import *" to make all transform functions available.
    - Call Set_Path to specify the X3 directory, along with some other path options. See documentation below for parameters.
    - Call a series of transform functions, as desired.
  
  * The quickest way to set up a command script is to copy and edit the input_scripts/Example_Transforms.py file. Included in the repository is Authors_Transforms, the author's personal set of transforms, which can be checked for futher examples of how to use most transforms available.

  * Transformed output files will be generated in an unpacked form in the x3 directories, or to a custom output direction set using Set_Path. Already existing files will be renamed, suffixing with '.x3c.bak', if they do not appear to have been created by the customizer on a prior run. A json log file will be written with information on which files were created or renamed.

  * Warning: this tool will attempt to avoid unsafe behavior, but the user should back up irreplaceable files to be safe against bugs such as accidental overwrites of source files with transformed files.
  

***

Example input file:

    '''
    Example for using the Customizer, setting a path to
    the X3 directory and running some simple transforms.
    '''
    
    # Import all transform functions.
    from X3_Customizer import *
    
    Set_Path(
        # Set the path to the X3 installation folder.
        path_to_x3_folder = r'D:\Steam\SteamApps\common\x3 terran conflict',
    )
    
    # Speed up interceptors by 50%.
    Adjust_Ship_Speed(adjustment_factors_dict = {'SG_SH_M4' : 1.5})
    
    # Increase frigate laser regeneration by 50%.
    Adjust_Ship_Laser_Recharge(adjustment_factors_dict = {'SG_SH_M7': 1.5})
    
    # Reduce Out-of-sector damage by 30%.
    Adjust_Weapon_OOS_Damage(scaling_factor = 0.7)

***

Setup methods:

  * Set_Path

       Sets the pathing to be used for file loading and writing.
   
       * path_to_x3_folder
         - Path to the X3 base folder, where the executable is located.
         - Can be skipped if path_to_addon_folder provided.
   
       * path_to_addon_folder
         - Path to the X3 AP addon folder.
         - Can be skipped if path_to_x3_folder provided.
   
       * path_to_output_folder
         - Optional, path to a folder to place output files in.
         - Defaults to match path_to_x3_folder, so that outputs are directly readable by the game.
   
       * path_to_source_folder
         - Optional, alternate folder which contains source files to be modified.
         - Maybe be given as a relative path to the "addon" directory, or as an absolute path.
         - Files located here should have the same directory structure as standard games files, eg. 'source_folder/types/Jobs.txt'.
   
       * path_to_log_folder
         - Path to the folder to place any output logs in, or to read prior output logs from.
         - Maybe be given as a relative path to the "addon" directory, or as an absolute path.
         - Defaults to 'x3_customizer_logs'.
         - This should not be changed between runs, since recognition of results from a prior customizer run depends on reading the prior run's log file.
   
       * summary_file
         - Name for where a summary file will be written, with any transform results, relative to the log folder.
         - Defaults to 'X3_Customizer_summary.txt'.
   
       * log_file
         - Name for where a json log file will be written, including a summary of files written.
         - This is also the file which will be read for any log from a prior run.
         - Defaults to 'X3_Customizer_log.json'.
       


***

Background Transforms:

 * Adjust_Fade_Start_End_Gap

    Requires: types/TBackgrounds.txt

      Adjust the gap between the start and end fade distance, changing how quickly objects will fade in. This will never affect fade_start, only fade_end.
  
      * fade_gap_min_func, fade_gap_max_func:
        - Functions which take fade_start as the argument, in km, and return the min and max gap allowed.
        - Example: 
          - Set fade gap to be as much as fade start:
            - fade_gap_min_func = lambda start: start*1
          - Require the fade gap be no longer than 20 km:
            - fade_gap_max_func = lambda start: 20
      

 * Adjust_Particle_Count

    Requires: types/TBackgrounds.txt

      Change the number of particles floating in space around the camera. Default game is 100, mods often set to 0, but can keep some small number for a feeling of speed.
  
      * base_count:
        - The base number of particles to use in all sectors. Default is 10, or 10% of the vanilla particle count.
      * fog_factor:
        - The portion of sector fog to add as additional particles. Eg. a fog factor of 0.5 will add 25 more particles in heavy fog.
      

 * Remove_Stars_From_Foggy_Sectors

    Requires: types/TBackgrounds.txt

      Removes star backgrounds from sectors with significant fog and short fade distance. Fogged sectors sharing a background with an unfogged sector will not be modified, as the background needs to be edited for all sectors which use it. Fade is removed from sectors which will not have their stars removed.
      
      * fog_requirement:
        - The fog requirement for star removal; all backgrounds affected need a fog above this much. Default of 12 is set for matching the Maelstrom background.
      * fade_distance_requirement_km:
        - The highest fade distance to allow; all backgrounds affected need a fade_start under this value (to prevent star removal in high visibility sectors). In km.
      

 * Set_Minimum_Fade_Distance

    Requires: types/TBackgrounds.txt

      Sets a floor to fade distance, so that object do not appear too closely. May be useful in some sectors with really short view distances, though may also want to keep those for variety. Note: max fade distance will be set to minimum fade distance if it would otherwise be lower. Recommend following this with a call to Adjust_Fade_Start_End_Gap.
  
      * distance_in_km : 
        - Minimum fade distance, in km.
      


***

Director Transforms:

 * Adjust_Generic_Missions

    Requires: director/3.01 Generic Missions.xml

      Adjust the spawn chance of various generic mission types, relative to each other. Note: decreasing chance on unwanted missions seems to work better than increasing chance on wanted missions.
  
      * adjustment_dict:
        - Dict keyed by mission identifiers or preset categories, holding the chance multiplier.
        - Keys may be cue names, eg. 'L2M104A', or categories, eg. 'Fight'. Specific cue names will override categories.
        - Categories and cue names for the vanilla AP are as follows, where the term after the category is the base mission chance shared by all missions in that category, as used in the game files.
        - Trade (TXXX)
          - L2M104A : Deliver Wares to Station in need
          - L2M104B : Deliver Illegal Wares to Pirate Station
          - L2M104C : Deliver Illegal Wares to Trading Station
          - L2M116  : Transport Cargo
          - L2M130  : Passenger Transport
          - L2M150a : Buy Used Ship
        - Fight (XFXX)
          - L2M101  : Assassination
          - L2M108  : Xenon Invasion
          - L2M119  : Escort Convoy
          - L2M127  : Destroy Convoy
          - L2M134  : Generic Patrol
          - L2M135  : Defend Object
          - L2M183  : Dual Convoy
        - Build (XXBX)
          - L2M122  : Build Station    
        - Think (XXXT)
          - L2M103  : Transport Passenger
          - L2M105  : Return Ship
          - L2M113  : Follow Ship
          - L2M129  : Deliver Matching Ship
          - L2M133  : Freight Scan
          - L2M145  : Scan Asteroids
          - L2M180  : Repair Station
          - L2M181  : Multiple Transport
          - L2M182  : Tour Of A Lifetime
          - L2M136  : Notoriety Hack
          - L2M144  : Buy Asteroid Survey
          - L2M147  : Buy Sector Data
          - L2M161  : Buy Blueprints
          - DPL2M186: Sell Blueprints
      * cap_at_100:
        - Bool, if True then mission chance adjustment will cap at 100, the typical highest in vanilla AP. Default False.
      

 * Convoys_made_of_race_ships

    Requires: director/2.119 Trade Convoy.xml

      If convoy defense missions should use the convoy's race to select their ship type. The vanilla script uses randomized ship types (eg. a terran convoy flying teladi ships).
      

 * Disable_Generic_Missions

    Requires: director/3.01 Generic Missions.xml

      Disable generic missions from spawning. Existing generic missions will be left untouched.
      

 * Standardize_Start_Plot_Overtunings (incompatible with: LU)

    Requires: director/3.05 Gamestart Missions.xml

      Set the starting plots with overtuned ships to have their tunings standardized instead of being random.
  
      * fraction_of_max:
        - Float, typically between 0 and 1, the fraction of the max overtuning to use. A value of 0 will remove overtunings, and 1 will give max overtuning that is available in vanilla. Default of 0.7 is set to mimic moderate game reloading results.
      

 * Standardize_Tunings (incompatible with: LU)

    Requires: director/3.08 Sector Management.xml

      Set the number of randomized tuning creates at gamestart to be de-randomized into a standard number of tunings. Note: vanilla has 2-5 average tunings per crate, 8 crates total. Default args here reach this average, biasing toward engine tunings.
  
      * enging_tuning_crates:
        - Int, the number of engine tuning crates to spawn. Default 4.
      * rudder_tuning_crates:
        - Int, the number of rudder tuning crates to spawn. Default 4.
      * engine_tunings_per_crate:
        - Int, the number of tunings in each engine crate. Default 4.
      * rudder_tunings_per_crate:
        - Int, the number of tunings in each rudder crate. Default 3.
  
      


***

Factory Transforms:

 * Add_More_Factory_Sizes

    Requires: types/TFactories.txt, maps/WareTemplate.xml

      Adds factories of alternate sizes, from basic to XL. Price and volume of new sizes is based on the scaling common to existing factories. Factories will be added to existing shipyards the first time a game is loaded after running this transform; this may take several seconds to complete, during which time the game will be unresponsive. Warning: it is unsafe to remove factories once they have been added to an existing save.
  
      * factory_types:
        - List of factory type names to add new sizes for. Defaults are ['SG_FAC_BIO','SG_FAC_FOOD','SG_FAC_POWER','SG_FAC_TECH']. The other potentially useful type is 'SG_FAC_MINE'.
      * sizes:
        - List of sizes to add, if not already present, given as strings. Defaults are ['s','m','l','xl'].
      * race_types:
        - List of race names whose factories will have sizes added. By default, the following are included: [Argon, Boron, Split, Paranid, Teladi, Pirates, Terran, Yaki].
      * cue_index:
        - Int, index for the director cue which will update shipyards with added variants. Increment this when changing the variants in an existing save, as the update script will otherwise not fire again for an already used cue_index. Default is 0.
      * linear_cost_scaling:
        - Bool, if True then scaling of factory cost will be linear with production rate, otherwise it will scale in the same manner as argon solar power plants. Default False. Note: volume always scales like solar power plants, to avoid excessively large volumes.
      * print_count:
        - If True, the number of new factories is printed to the summary file.
      * warn_on_waretemplate_bugs:
        - If True, potential bugs in WareTemplate for nonexistent factories are printed to the summary file. This will not affect this transform, and is only intended to indicate potential problems in source files.
      


***

Gate Transforms:

 * Adjust_Gate_Rings

    Requires: types/TGates.txt, types/TSpecial.txt

      Various options to modify gate rings, with the aim of reducing capital ship suicides when colliding with the pylons shortly after the player enters a sector. Includes ring removal, rotation, reversal, and model swaps. Inactive versions of gates will also be updated for consistency. When applied to an existing save, gate changes will appear on a sector change.
  
      * standard_ring_option:
        - String, one of the following options to be applied to the standard gates.
          - 'use_plain_ring': Replaces the gate ring with a plain version lacking projecting pylons on either side. Default.
          - 'use_reversed_hub': Replaces the gate ring with the Hub ring reversed 180 degrees, resulting in pylons only being on the back side.
          - 'rotate_45': Rotates the gate 45 degrees, offsetting the pylons to be in corners.
          - 'rotate_90': Rotates the gate 90 degrees, offsetting the pylons to be at the top and bottom.
          - 'remove': Removes the gate ring entirely, leaving only a portal. This will not affect disabled gates.
          - 'use_terran': Replaces the gate ring with the Terran gate from the Aldrin expansion plot.
          - None: no change.
      * hub_ring_option:
        - String, one of the options for standard_ring_option, defaulting to 'use_reversed_hub', along with a new option:
          - 'use_standard_ring_option': The Hub ring will match the option used for the standard ring.
      


***

Global Transforms:

 * Adjust_Global

    Requires: types/Globals.txt

      Adjust a global flag by the given multiplier. Generic transform works on any named global field.
  
      * field_name:
        - String, name of the field in Globals.txt
      * scaling_factor:
        - Multiplier to apply to the existing value.
      

 * Adjust_Strafe

    Requires: types/Globals.txt

      Strafe adjustment factor.  Experimental. Note: this does not appear to have any effect during brief testing.
      
      * small_ship_factor:
        - Multiplier on small ship strafe.
      * big_ship_factor:
        - Multiplier on big ship strafe.
      

 * Set_Communication_Distance

    Requires: types/Globals.txt

      Set max distance for opening communications with factories and ships.
  
      * distance_in_km
        - Int, max communication distance.
      

 * Set_Complex_Connection_Distance

    Requires: types/Globals.txt

      Set max range between factories in a complex. With complex cleaner and tubeless complexes, this can practically be anything, particularly useful when connecting up distant asteroids.
  
      * distance_in_km
        - Int, max connection distance.
      

 * Set_Dock_Storage_Capacity

    Requires: types/Globals.txt

      Change the capacity of storage docks: equipment docks, trading posts, etc.
  
      * player_factor:
        - Int, multiplier for player docks. Vanilla default is 3.
      * npc_factor:
        - Int, multiplier for npc docks. Vanilla default is 1.
      * hub_factor:
        - Int, multiplier for the Hub. Vanilla default is 6.
      

 * Set_Global

    Requires: types/Globals.txt

      Set a global flag to the given value. Generic transform works on any named global field.
  
      * field_name:
        - String, name of the field in Globals.txt
      * value:
        - Int, the value to set.
      


***

Job Transforms:

 * Add_Job_Ship_Variants

    Requires: types/Jobs.txt

      Allows jobs to spawn with a larger selection of variant ships. This does not affect jobs with a preselected ship to spawn, only those with random selection. Variants are added when the basic version of the ship is allowed, to preserve cases where a variant has been preselected.
      
      * jobs_types:
        - List of keys for the jobs to modify.
        - Key will try to match a boolean field in the jobs file, (eg. 'owner_argon' or 'classification_trader', see File_Fields for field names), or failing that will try to do a job name match (partial match supported) based on the name in the jobs file.
        - '*' will match all jobs not otherwise matched.
      * ship_types:
        - List of ship types to allow variants for, eg. 'SG_SH_M1'. Note that M0 and TM are not allowed since they do not have flags in the job entries.  Default includes all ship types possible.
      * variant_types:
        - List of variant types to allow. Variant names are given as strings. The default list is: ['vanguard', 'sentinel', 'raider', 'hauler', 'super freighter', 'tanker', 'tanker xl', 'super freighter xl']. The 'miner' variant is supported but omitted from the defaults.
      

 * Adjust_Job_Count

    Requires: types/Jobs.txt

      Adjusts job ship counts using a multiplier. These will always have a minimum of 1. Jobs are matched by name or an attribute flag, eg. 'owner_pirate'. This will also increase the max number of jobs per sector accordingly.
  
      * job_count_factors:
        - List of tuples pairing an identifier key with the adjustment value to apply. The first match will be used.
        - Key will try to match a boolean field in the jobs file (see File_Fields for field names), or failing that will try to do a job name match (partial match supported) based on the name in the jobs file.
        - '*' will match all jobs not otherwise matched.
      

 * Adjust_Job_Respawn_Time

    Requires: types/Jobs.txt

      Adjusts job respawn times, using an adder and multiplier on the existing respawn time.
  
      * time_adder_list, time_multiplier_list:
        - Lists of tuples pairing an identifier key with the adjustment value to apply. The first match will be used.
        - Key will try to match a boolean field in the jobs file, (eg. 'owner_argon' or 'classification_trader', see File_Fields for field names), or failing that will try to do a job name match (partial match supported) based on the name in the jobs file.
        - '*' will match all jobs not otherwise matched.
      

 * Set_Job_Spawn_Locations

    Requires: types/Jobs.txt

      Sets the spawn location of ships created for jobs, eg. at a shipyard, at a gate, docked at a station, etc.
      
      * jobs_types:
        - List of keys for the jobs to modify.
        - Key will try to match a boolean field in the jobs file, (eg. 'owner_argon' or 'classification_trader', see File_Fields for field names), or failing that will try to do a job name match (partial match supported) based on the name in the jobs file.
        - '*' will match all jobs not otherwise matched.
      * sector_flags_to_set:
        - List of sector selection flag names to be set. Unselected flags will be cleared. Supported names are:
          - 'select_owners_sector'
          - 'select_not_enemy_sector'
          - 'select_core_sector'
          - 'select_border_sector'
          - 'select_shipyard_sector'
          - 'select_owner_station_sector'
      * creation_flags_to_set:
        - List of creation flag names to be set. Unselected flags will be cleared. Supported names are:
          - 'create_in_shipyard'
          - 'create_in_gate'
          - 'create_inside_sector'
          - 'create_outside_sector'
      * docked_chance:
        - Int, 0 to 100, the percentage chance the ship is docked when spawned.
      


***

Missile Transforms:

 * Add_Ship_Boarding_Pod_Support

    Requires: types/TShips.txt

      Adds boarding pod launch capability to selected classes of ships, eg. destroyers. Ships should support marines, so limit to M1, M2, M7, M6, TL, TM, TP.
      
      * ship_types:
        - List of ship names or types to add equipment to, eg. ['SS_SH_OTAS_M2', 'SG_SH_M1']. Default includes M6,M7,M2,M1.
      * required_missiles:
        - List of missile types, a ship must support one of these missiles before it will be given boarding pod support. Default is ['SG_MISSILE_HEAVY','SG_MISSILE_TR_HEAVY'], requiring ships to already support heavy missiles.
      

 * Add_Ship_Cross_Faction_Missiles

    Requires: types/TShips.txt

      Adds terran missile compatibility to commonwealth ships, and vice versa. Missiles are added based on category matching, eg. a terran ship that can fire light terran missiles will gain light commonwealth missiles. Note that AI ship loadouts may include any missile they can fire.
      
      * race_types:
        - List of race names whose ships will have missiles added. By default, the following are included: [Argon, Boron, Split, Paranid, Teladi, Xenon, Pirates, Goner, ATF, Terran, Yaki].
      

 * Adjust_Missile_Damage

    Requires: types/Globals.txt, types/TMissiles.txt

      Adjust missile damage values, by a flat scaler or configured scaling formula. 
      
      * scaling_factor:
        - The base multiplier to apply to missile damage.
      * use_scaling_equation:
        - If True, a scaling formula will be applied, such that missiles near target_damage_to_adjust see the full scaling_factor, and missiles near damage_to_keep_static remain largely unchanged. Otherwise, scaling_factor is applied to all missiles.
      * target_damage_to_adjust, damage_to_keep_static:
        - Equation tuning values.
      * adjust_volume:
        - If True, cargo volume is adjusted corresponding to damage. Defaults False.
      * adjust_price:
        - If True, price is adjusted corresponding to damage. Defaults False.
      * mosquito_safety_cap
        - If True, mosquito missiles will be capped at 350 damage, below the cutoff point (400) for usage in OOS combat. Defaults True.
      * print_changes:
        - If True, speed adjustments are printed to the summary file.
      

 * Adjust_Missile_Hulls

    Requires: types/Globals.txt

      Adjust the hull value for all missiles by the scaling factor. Does not affect boarding pod hulls.
  
      * scaling_factor:
        - Multiplier on missile hull values.
      

 * Adjust_Missile_Range

    Requires: types/TMissiles.txt

      Adjust missile range by changing lifetime, by a flat scaler or configured scaling formula. This is particularly effective for the re-lock missiles like flail, to reduce their ability to keep retargetting across a system, instead running out of fuel from the zigzagging.
       
      * scaling_factor:
        - The base multiplier to apply to missile range.
      * use_scaling_equation:
        - If True, a scaling formula will be applied, such that missiles near target_range_to_adjust_km see the full scaling_factor, and missiles near range_to_keep_static_km remain largely unchanged. Otherwise, scaling_factor is applied to all missiles.
      * target_range_to_adjust_km, range_to_keep_static_km:
        - Equation tuning values, in kilometers.
      * print_changes:
        - If True, speed adjustments are printed to the summary file.
      

 * Adjust_Missile_Speed

    Requires: types/TMissiles.txt

      Adjust missile speeds, by a flat scaler or configured scaling formula.
      
      * scaling_factor:
        - The base multiplier to apply to missile speeds.
      * use_scaling_equation:
        - If True, a scaling formula will be applied, such that missiles near target_speed_to_adjust see the full scaling_factor, and missiles near speed_to_keep_static remain largely unchanged. Otherwise, scaling_factor is applied to all missiles.
      * target_speed_to_adjust, speed_to_keep_static:
        - Equation tuning values, in m/s.
      * print_changes:
        - If True, speed adjustments are printed to the summary file.
      

 * Enhance_Mosquito_Missiles

    Requires: types/TMissiles.txt

      Makes mosquito missiles more maneuverable, generally by increasing the turn rate or adding blast radius, to make anti-missile abilities more reliable.
  
      * acceleration_factor:
        - Multiplier to the mosquito's acceleration.
      * turn_rate_factor:
        - Multiplier to the mosquito's turn rate.
      * proximity_meters:
        - If not 0, adds a proximity fuse with the given distance. For comparison, vanilla Silkworm missiles have a 200 meter radius.
      

 * Expand_Bomber_Missiles

    Requires: types/TShips.txt

      Allows bombers and missile frigates to use a wider variety of missiles. Bombers will gain fighter tier missiles, while frigates will gain corvette tier missiles. Terran ships will gain Terran missiles. Note that AI ship loadouts may include any missile they can fire, such that bombers will have fewer heavy missiles and more standard missiles.
      
      * include_bombers:
        - Bool, if True ships supporting bomber type missiles are modified. Default True.
      * include_frigates:
        - Bool, if True ships supporting missile frigate missiles are modified. Default True.
      * add_bomber_missiles_to_frigates:
        - Bool, if True frigates will also gain bomber type missiles. Default False. Low cargo volume of bomber missiles may be unbalanced on frigates.
      

 * Set_Missile_Swarm_Count

    Requires: types/TMissiles.txt, types/Globals.txt

      Set the number of submissiles fired by swarm missiles. Submissile damage is adjusted accordingly to maintain overall damage.
  
      * swarm_count:
        - Int, the number of missiles per swarm.
      


***

Obj_Code Transforms:

 * Adjust_Max_Seta

    Requires: L/x3story.obj

      Changes the maximum SETA speed multiplier. Higher multipliers than the game default of 10 may cause oddities.
      
      * speed_factor
        - Int, the multiplier to use. At least 2. X3 debug mode allows up to 50. This transform will soft cap at 127, the max positive single byte value.
      

 * Adjust_Max_Speedup_Rate

    Requires: L/x3story.obj

      Changes the rate at which SETA turns on. By default, it will accelerate by (selected SETA -1)/10 every 250 milliseconds. This transform will reduce the delay between speedup ticks.
      
      * scaling_factor
        - Float, the amount to boost the speedup rate by. Eg. 2 will reduce the delay between ticks to 125 ms. Practical limit may be set by game frame rate, eg. approximately 15x at 60 fps.
      

 * Allow_Valhalla_To_Jump_To_Gates (incompatible with: LU)

    Requires: L/x3story.obj

      Removes a restriction on the Valhalla, or whichever ship is at offset 211 in tships, from jumping to gates. This should only be applied alongside another mod that either reduces the valhalla size, increases gate size, removes gate rings, or moves/removes the forward pylons, to avoid collision problems.
      

 * Disable_Asteroid_Respawn (incompatible with: LU)

    Requires: L/x3story.obj

      Stops any newly destroyed asteroids from being set to respawn. This can be set temporarily when wishing to clear out some unwanted asteroids. It is not recommended to leave this transform applied long term, without some other method of replacing asteroids.
      

 * Disable_Combat_Music (incompatible with: LU)

    Requires: L/x3story.obj

      Turns off combat music, keeping the normal environment musc playing when nearing hostile objects. If applied to a saved game already in combat mode, combat music may continue to play for a moment. The beep on nearing an enemy will still be played.
      

 * Keep_TLs_Hired_When_Empty

    Requires: L/x3story.obj

      When a hired TL places its last station, it will remain hired until the player explicitly releases it instead of being automatically dehired.
      

 * Kill_Spaceflies (incompatible with: LU)

    Requires: L/x3story.obj

      Kills active spaceflies by changing their "is disabled" script command to make them self destruct. Intended for use with games that have accumulated many stale spacefly swarms generated by Improved Races 2.0 or Salvage Command Software or other mods which accidentally add excess spaceflies through the "create ship" command, causing accumulating slowdown (eg. 85% SETA slowdown after 10 game days). Use Prevent_Accidental_Spacefly_Swarms to stop future spacefly accumulation, and this transform to clean out existing spaceflies.
  
      Deaths are delayed by 10 seconds so that mods generating and killing the spaceflies have time to record their information. It may take a minute for accumulated spaceflies to die. Progress can be checked in the script editor by watching the active spacefly script counts.
      

 * Prevent_Accidental_Spacefly_Swarms

    Requires: L/x3story.obj

      Prevents spaceflies from spawning swarms when created by a script using the 'create ship' command. Aimed at mods such as Improved Races 2.0 and SCS, which create and destroy a spacefly but accidentally leave behind a swarm with active scripts, causing spacefly accumulation and game slowdown.
      

 * Remove_Factory_Build_Cutscene (incompatible with: LU)

    Requires: L/x3story.obj

      Removes the cutscene that plays when placing factories by shortening the duration to 0.  Also prevents the player ship from being stopped. May still have some visible camera shifts for an instant.
      

 * Set_Max_Marines (incompatible with: LU)

    Requires: L/x3story.obj

      Sets the maximum number of marines that each ship type can carry. These are byte values, signed, so max is 127.
      
      * tm_count
        - Int, marines carried by TMs.
      * tp_count
        - Int, marines carried by TPs.
      * m6_count
        - Int, marines carried by M6s.
      * capital_count
        - Int, marines carried by capital ships: M1, M2, M7, TL.
      * sirokos_count
        - Int, marines carried by the Sirokos, or whichever ship is located at entry 263 in Tships (when starting count at 1). Note: XRM does not use this slot in Tships.
      

 * Stop_Events_From_Disabling_Seta (incompatible with: LU)

    Requires: L/x3story.obj

      Stop SETA from being turned off automatically upon certain events, such as missile attacks.
      
      * on_missile_launch
        - If True, Seta will not turn off when a missile is fired at the player ship.
      * on_receiving_priority_message
        - If True, Seta will not turn off when a priority message is received, such as a police notice of being scanned.
      * on_collision_warning
        - If True, Seta will not turn off when a near collision occurs.
      * on_frame_input
        - If True, the PerFrameInput function will not turn off seta, allowing menus to be opened.
      

 * Stop_GoD_From_Removing_Stations

    Requires: L/x3story.obj

      Stops the GoD engine from removing stations which are nearly full on products or nearly starved of resources for extended periods of time.  This will not affect stations already removed or in the process of being removed.
      


***

Script Transforms:

 * Add_CLS_Software_To_More_Docks

    Requires: None

      Adds Commodity Logistics Software, internal and external, to all equipment docks which stock Trade Command Software Mk2. This is implemented as a setup script which runs on the game loading. Once applied, this transform may be disabled to remove the script run time. This change is not reversable.
      

 * Allow_CAG_Apprentices_To_Sell (incompatible with: LU)

    Requires: scripts/plugin.com.agent.main.xml

      Allows Commercial Agents to sell factory products at pilot rank 0. May require CAG restart to take effect.
      

 * Complex_Cleaner_Bug_Fix (incompatible with: LU)

    Requires: scripts/plugin.gz.CmpClean.Main.xml

      Apply bug fixes to the Complex Cleaner mod. Designed for version 4.09 of that mod. Includes a fix for mistargetted a wrong hub in systems with multiple hubs, and a fix for some factories getting ignored when crunching. Patches plugin.gz.CmpClean.Main.xml.
      

 * Complex_Cleaner_Use_Small_Cube (incompatible with: LU)

    Requires: scripts/plugin.gz.CmpClean.crunch.xml

      Forces the Complex Cleaner to use the smaller cube model always when combining factories. Patches plugin.gz.CmpClean.crunch.xml.
      

 * Convert_Attack_To_Attack_Nearest

    Requires: None

      Modifies the Attack command when used on an owned asset to instead enact Attack Nearest. In vanilla AP, such attack commands are quietly ignored. Intended for use when commanding groups, where Attack is available but Attack Nearest is not. This replaces '!ship.cmd.attack.std'.
      

 * Disable_OOS_War_Sector_Spawns (incompatible with: LU)

    Requires: scripts/!fight.war.protectsector.xml

      Disables spawning of dedicated ships in the AP war sectors which attack player assets when the player is out-of-sector. By default, these ships scale up with player assets, and immediately respawn upon being killed. This patches '!fight.war.protectsector'.
      

 * Fix_OOS_Laser_Missile_Conflict (incompatible with: LU)

    Requires: scripts/!plugin.acp.fight.attack.object.xml

      Allows OOS combat to include both missile and laser fire in the same attack round. In vanilla AP, a ship firing a missile will not fire its lasers for a full round, generally causing a large drop in damage output. With the change, adding missiles to OOS ships will not hurt their performance.
      

 * Fleet_Interceptor_Bug_Fix (incompatible with: LU)

    Requires: scripts/!lib.fleet.shipsfortarget.xml

      Apply bug fixes to the Fleet logic for selecting ships to launch at enemies. A mispelling of 'interecept' causes M6 ships to be launched against enemy M8s instead of interceptors. Patches !lib.fleet.shipsfortarget.xml.
      

 * Increase_Escort_Engagement_Range (incompatible with: LU)

    Requires: scripts/!move.follow.template.xml

      Increases the distance at which escort ships will break and attack a target. In vanilla AP an enemy must be within 3km of the escort ship. This transform will give custom values based on the size of the escorted ship, small, medium (m6), or large (m7+).
      
      * small_range:
        - Int, distance in meters when the escorted ship is not classified as a Big Ship or Huge Ship. Default 3000.
      * medium_range:
        - Int, distance in meters when the escorted ship is classified as a Big Ship but not a Huge Ship, eg. m6. Default 4000.
      * long_range:
        - Int, distance in meters when the escorted ship is classified as a Huge Ship, eg. m7 and larger. Default 7000.
      


***

Shield Transforms:

 * Adjust_Shield_Regen

    Requires: types/TShields.txt

      Adjust shield regeneration rate by changing efficiency values.
      
      * scaling_factor:
        - Multiplier to apply to all shield types.
      


***

Ship Transforms:

 * Add_Ship_Equipment

    Requires: types/TShips.txt, types/WareLists.txt

      Adds equipment as built-in wares for select ship classes.
  
      * ship_types:
        - List of ship names or types to add equipment to, eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].        
      * equipment_list:
        - List of equipment names from the ware files, eg. ['SS_WARE_LIFESUPPORT'].
      

 * Add_Ship_Life_Support

    Requires: types/TShips.txt, types/WareLists.txt

      Adds life support as a built-in ware for select ship classes. This is a convenience transform which calls Add_Ship_Equipment. Warning: mission director scripts do not seem to have a way to check for built in wares, and typically use a special TP check to get around this. Other ship types with built-in life support will not be able to pick up passengers in some cases.
  
      * ship_types:
        - List of ship types to add life support to, eg. ['SG_SH_M2']. By default, this includes M6, M7, M2, M1, TL, TM.
      

 * Adjust_Ship_Hull

    Requires: types/TShips.txt

      Adjust ship hull values. When applied to a existing save, ship hulls will not be updated automatically if hulls are increased.  Run the temp.srm.hull.reload.xml script from the XRM hull packs to refill all ships to 100% hull. Alternatively, ship hulls will be updated as ships die and respawn.
  
      * scaling_factor:
        - Multiplier to apply to any ship type not found in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a scaling factor to be applied.
      * adjust_repair_lasers:
        - Bool, if True (default) repair lasers will be scaled by the M6 hull scaling (if given), to avoid large changes in repair times.
      

 * Adjust_Ship_Laser_Recharge

    Requires: types/TShips.txt

      Adjust ship laser regeneration rate, either globally or per ship class.
      
      * scaling_factor:
        - Multiplier to apply to any ship type not found in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a scaling factor to be applied.
      * adjust_energy_cap:
        - Bool, if True the ship maximum energy is also adjusted. This may cause oddities if applied to an existing save. Defaults False.
      

 * Adjust_Ship_Pricing

    Requires: types/TShips.txt

      Adjust ship pricing, either globally or per ship class.
  
      * scaling_factor:
        - Multiplier for any ship not matched in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a scaling factor to be applied.
      

 * Adjust_Ship_Shield_Regen

    Requires: types/TShips.txt

      Adjust ship shield regeneration rate, either globally or per ship class. This may have no effect beyond where all ship shields are powered at their individual max rates.
      
      * scaling_factor:
        - Multiplier to apply to all ship types on top of those present in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a tuple of (targeted_recharge_rate, reduction_factor, max_rate) where any recharges above targeted_recharge_rate will have the reduction_factor applied to the difference in original and target rates. Recharge rates will be capped at max_rate.
      

 * Adjust_Ship_Shield_Slots

    Requires: types/TShips.txt

      Adjust ship shielding by changing shield slot counts. Shield types will remain unchanged, and at least 1 shield slot will be left in place. When applied to an existing save, ship shields will not be updated automatically, as some ships may continue to have excess shields equipped, or ships may lack enough shield inventory to fill up added slots.
      
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a tuple of (targeted_total_shielding, reduction_factor), where any ships with shields above targeted_total_shielding will have reduction_factor applied to their shield amount above the target.
      

 * Adjust_Ship_Speed

    Requires: types/TShips.txt

      Adjust ship speed and acceleration, globally or per ship class.
      
      * scaling_factor:
        - Multiplier to apply to any ship type not found in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type or name, holding a scaling factor to be applied.
      

 * Boost_Truelight_Seeker_Shield_Reactor (incompatible with: XRM, LU)

    Requires: types/TShips.txt

      Enhances the Truelight Seeker's shield reactor. In vanilla AP the TLS has a shield reactor only around 1/10 of what is normal for similar ships. This transform sets the TLS shield reactor to be the same as the Centaur. If the TLS is already at least 1/5 of Centaur shielding, this transform is not applied.
      

 * Fix_Pericles_Pricing (incompatible with: XRM, LU)

    Requires: types/TShips.txt

      Applies a bug fix to the enhanced pericles in vanilla AP, which has its npc value set to 1/10 of player value, causing it price to be 1/10 what it should be. Does nothing if the existing npc and player prices are matched.
      

 * Patch_Ship_Variant_Inconsistencies

    Requires: types/TShips.txt

      Applies some patches to some select inconsistencies in ship variants. Modified ships include the Baldric Miner and XRM Medusa Vanguard, both manually named instead of using the variant system. This is meant to be run prior to Add_Ship_Variants, to avoid the non-standard ships creating their own sub-variants. There may be side effects if the variant inconsistencies were intentional.
  
      * include_xrm_fixes
        - Bool, if True then the Medusa Vanguard is patched if found and in the form set by XRM. Default True.
      

 * Remove_Khaak_Corvette_Spin

    Requires: None

      Remove the spin on the secondary hull of the Khaak corvette. The replacement file used is expected to work for vanilla, xrm, and other mods that don't change the model scene file.
      

 * Simplify_Engine_Trails

    Requires: types/TShips.txt

      Change engine trail particle effects to basic or none. This will switch to effect 1 for medium and light ships and 0 for heavy ships, as in vanilla AP.
  
      * remove_trails:
        - If True, this will remove trails from all ships.
      

 * Standardize_Ship_Tunings

    Requires: types/TShips.txt

      Standardize max engine or rudder tuning amounts across all ships. Eg. instead of scouts having 25 and carriers having 5 engine runings, both will have some fixed number. Maximum ship speed and turn rate is kept constant, but minimum will change. If applied to an existing save, existing ships may end up overtuned; this is recommended primarily for new games, pending inclusion of a modification script which can recap ships to max tunings. Ships with 0 tunings will remain unedited.
  
      * engine_tunings:
        - Int, the max engine tunings to set.
      * rudder_tunings:
        - Int, the max rudder tunings to set.
      * ship_types:
        - List of ship names or types to adjust tunings for. If empty (default), all ships are adjusted.
      


***

Ships_Variant Transforms:

 * Add_Ship_Combat_Variants

    Requires: types/TShips.txt, types/WareLists.txt, types/TWareT.txt

      Adds combat variants for combat ships. This is a convenience function which calls Add_Ship_Variants with variants [vanguard, sentinel, raider, hauler], for ship types [M0-M8]. See Add_Ship_Variants documentation for other parameters.
      

 * Add_Ship_Trade_Variants

    Requires: types/TShips.txt, types/WareLists.txt, types/TWareT.txt

      Adds trade variants for trade ships. This is a convenience function which calls Add_Ship_Variants with variants [hauler, miner, tanker (xl), super freighter (xl)], for ship types [TS,TP,TM,TL]. See Add_Ship_Variants documentation for other parameters.    
      

 * Add_Ship_Variants

    Requires: types/TShips.txt, types/WareLists.txt, types/TWareT.txt

      Adds variants for various ships. Variant attribute modifiers are based on the average differences between existing variants and their basic ship, where only M3,M4,M5 are analyzed for combat variants, and only TS,TP are analyzed for trade variants, with Hauler being considered both a combat variant. Variants will be added to existing shipyards the first time a game is loaded after running this transform; this may take several seconds to complete, during which time the game will be unresponsive. Warning: it is unsafe to remove variants once they have been added to an existing save.
  
      Special attributes, such as turret count and weapon compatibitities, are not considered. Variants are added base on ship name and race; pirate variants are handled separately from standard variants. Ships without extensions or cargo are ignored (eg. drones, weapon platforms).
      
      * ship_types:
        - List of ship names or types to add variants for, eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].
      * variant_types:
        - List of variant types to add. Variant names are given as strings or as integers (1-19). The default list, with supported names and corresponding integers in parentheses, is: ['vanguard' (1), 'sentinel' (2), 'raider' (3), 'hauler' (4), 'miner' (5), 'super freighter' (6), 'tanker' (7) , 'tanker xl' (14), 'super freighter xl' (15) ]
      * price_multiplier:
        - Float, extra scaling to apply to pricing for the new variants, on top of standard variant modifiers.
      * blacklist:
        - List of names of ships not to generate variants for.
      * race_types:
        - List of race names whose ships will have variants added. By default, the following are included: [Argon, Boron, Split, Paranid, Teladi, Xenon, Khaak, Pirates, Goner, ATF, Terran, Yaki].
      * include_advanced_ships:
        - Bool, if True then existing heavy ships (variation 20) and other non-basic ships will have variants added. This may result in some redundancies, eg. variants of Mercury and Advanced Mercury. In some cases, the existing ship will be reclassified as a basic version; see variant_indices_to_reset_on_base_ships.
      * variant_indices_to_ignore:
        - List of integers, any existing variants to be ignored for analysis and variant generation. Default list includes 8, XRM Mk.1 ships.
      * variant_indices_to_reset_on_base_ships:
        - List of integers, any variant types which will be set to 0 when that variant is used as a base ship. Eg. a Hyperion Vanguard (variation 16) may be switched to a base Hyperion, from which vanguard and other variants are made. Default list includes 16 (redundant vanguard) and 19 (redundant hauler).
      * shield_conversion_ratios:
        - Dict of floats, keyed by ship attribute strings. When shielding cannot be adjusted accurately due to the X3 shielding system, this gives the rate at which shield adjustment error is converted to other ship attributes. Eg. if a ship is supposed to receive a 5% shield boost that cannot be given, and this dict has en entry with {'shield_power':1}, then an extra 5% boost will be given to the shield power generator instead. By default, shield error will convert using {'shield_power': 1, 'weapon_energy': 1, 'weapon_recharge_factor': 1}. Possible entries include: ['yaw','pitch','roll','speed','acceleration', 'shield_power','weapon_energy','weapon_recharge_factor','cargo', 'hull_strength','angular_acceleration','price']. Price should generally have a negative multiplier.
      * add_mining_equipment:
        - Bool, if True mining equipment will be added to Miner variants. Default True.
      * prepatch_ship_variant_inconsistencies:
        - Bool, if True then Patch_Ship_Variant_Inconsistencies will be run prior to this transform, to avoid some spurious variant generation. Default True with XRM fixes enabled; this should be safe to apply to vanilla AP.
      * print_variant_count:
        - If True, the number of new variants is printed to the summary file.
      * print_variant_modifiers:
        - If True  the calculated attributes used for variants will be printed to the summary file, given as multipliers on base attributes.
      * cue_index:
        - Int, index for the director cue which will update shipyards with added variants. Increment this when changing the variants in an existing save, as the update script will otherwise not fire again for an already used cue_index. Default is 0.
      

 * Remove_Ship_Variants

    Requires: types/TShips.txt

      Removes variants for selected ships. May be used after Add_Ship_Variants has already been applied to an existing save, to safely remove variants while leaving their tships entries intact. In this case, leave the Add_Ship_Variants call as it was previously with undesired variants, and use this tranform to prune the variants. Existing ships will remain in game, categorized as unknown race, though new ships will not spawn automatically. Variants will be removed from existing shipyards the first time a game is loaded after running this transform.
      
      * ship_types:
        - List of ship names or types to remove variants for, eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].
      * variant_types:
        - List of variant types to remove. See Add_Ship_Variants for details.
      * blacklist:
        - List of names of ships not to remove variants for.
      * race_types:
        - List of race names whose ships will have variants removed. By default, the following are included: [Argon, Boron, Split, Paranid, Teladi, Xenon, Khaak, Pirates, Goner, ATF, Terran, Yaki].
      * cue_index:
        - Int, index for the director cue which will update shipyards with added variants. Increment this when changing the variants in an existing save, as the update script will otherwise not fire again for an already used cue_index. Default is 0.
      * print_variant_count:
        - If True, the number of removed variants is printed to the summary file.
      


***

Sound Transforms:

 * Remove_Combat_Beep

    Requires: None

      Removes the beep that plays when entering combat.
      

 * Remove_Sound

    Requires: None

      Removes a sound by writing an empty file in its place, based on the sound's id.
  
      * sound_id
       - Int, the id of the sound file to be overwritten.
      


***

Universe Transforms:

 * Change_Sector_Music

    Requires: None

      Generic transform to change the music for a given sector. Currently, this only operates as a director script, and does not alter the universe file. To reverse the change, a new call must be made with a new cue name and the prior music_id.
      
      * sector_x, sector_y:
        - Integer values for the location of the sector to edit.
      * music_id:
        - Integer, 5 digit value of the music to use, matching an mp3 file in the soundtrack folder.
      * cue_name:
        - String, name to use for the director cue and the generated file. This should be different than any used earlier in a given saved game.
      

 * Color_Sector_Names (incompatible with: LU)

    Requires: maps/x3_universe.xml, t/0001-L044.xml, t/7027-L044.xml, t/7360-L044.xml

      Colors sector names in the map based on race owners declared in the x3_universe file. Some sectors may remain uncolored if their name is not set in the standard way through text files. Only works on the English files, L044, for now. Note: searching sectors by typing a name will no longer work except on uncolored sectors, eg. unknown sectors.
  
      * race_color_letters:
        - Dict matching race id string to the color code string to be used. Default is filled out similar to the standalone colored sectors mod.
      

 * Restore_Aldrin_rock (incompatible with: Vanilla, LU)

    Requires: maps/x3_universe.xml

      Restors the big rock in Aldrin for XRM, reverting to the vanilla sector layout. Note: only works on a new game.
      

 * Restore_Hub_Music (incompatible with: Vanilla, LU)

    Requires: maps/x3_universe.xml

      If Hub sector (13,8) music should be restored to that in AP. (XRM sets the track to 0.) Applies to new games, and optionally to an existing save.
  
      * apply_to_existing_save:
        - If True, makes a drop-in director script that will fire once and change the music for an existing save game. This is not reversable at this time.
      

 * Restore_M148_Music (incompatible with: Vanilla, LU)

    Requires: maps/x3_universe.xml

      If Argon Sector M148 (14,8) music should be restored to that in AP. (XRM changes this to the argon prime music.) Applies to new games, and optionally to an existing save.
      
      * apply_to_existing_save:
        - If True, makes a drop-in director script that will fire once and change the music for an existing save game. This is not reversable at this time.
      


***

Ware Transforms:

 * Change_Ware_Size

    Requires: None

      Change the cargo size of a given ware.
  
      * ware_name:
        - String, the name of the ware, eg. 'SS_WARE_WARPING' for jumpdrive. This may include lasers, factories, etc.
      * new_size:
        - Integer for the ware size. Exact meaning of the integers depends on any mods in use. In vanilla AP, 1-5 are small through ST. In XRM, 0-5 are small through ST, where 4 is XXL.
      * ware_file:
        - Optional string to help identify the ware file to look in, eg. 'TWareT' or 'TLaser'. If not given, ware files will be searched in order, skipping those not found in the source folder.
      

 * Restore_Vanilla_Tuning_Pricing (incompatible with: Vanilla, LU)

    Requires: types/TWareT.txt

      Sets the price for ship tunings (engine, rudder, cargo) to those used in vanilla AP.  Meant for use with XRM.
      

 * Set_Ware_Pricing

    Requires: types/TWareT.txt

      Sets ware pricing for the given ware list. Prices are the basic values in the T file, and have some adjustment before reaching the game pricing. Currently only works on tech wares in TWareT.txt.
  
      * name_price_dict:
        - Dict keyed by ware name (eg. 'SS_WARE_TECH213'), holding the flat value to apply for its T file price.
      * name_price_factor_dict:
        - As above, except holding a multiplier to apply to the existing price for the ware. Applies after name_price_dict if an item is in both dicts.
      


***

Weapons Transforms:

 * Adjust_Beam_Weapon_Duration

    Requires: types/TBullets.txt

      Adjusts the duration of beam weapons. Shot damage will be applied over the duration of the beam, such that shorter beams will apply their damage more quickly. Longer duration beams are weaker against small targets which move out of the beam before its damage is fully applied. Beam range will remain unchanged. Note: this does not affect fire rate, so multiple beams may become active at the same time.
  
      * bullet_name_adjustment_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to apply, as a tuple of (min, factor, max), where min and max are given in seconds.
        - None may be entered for min or max to disable those limits.
        - '*' entry will match all beam weapons not otherwise named.
      * ignore_repair_lasers:
        - Bool, if True (default) then repair lasers will be ignored.
      

 * Adjust_Beam_Weapon_Width

    Requires: types/TBullets.txt

      Adjusts the width of beam weapons. Narrower beams will have more trouble hitting small targets at a distance. In vanilla AP beam widths are generally set to 1, though in XRM the widths have much wider variety. This can be used to nerf anti-fighter defense of capital ships with beam mounts.
  
      * bullet_name_adjustment_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to apply, as a tuple of (min, factor, max), applied to height and width.
        - None may be entered for min or max to disable those limits.
        - '*' entry will match all beam weapons not otherwise named.
      

 * Adjust_Weapon_DPS

    Requires: types/TBullets.txt, types/TLaser.txt

      Adjust weapon damage/second by changing bullet damage. If a bullet is used by multiple lasers, the first laser will be used for DPS calculation. Energy efficiency will remain constant, changing energy/second.
  
      * scaling_factor:
        - The base multiplier to apply to shot speeds.
      * adjust_hull_damage_only:
        - Bool, if True only hull damage is modified. Default False.
      * adjust_shield_damage_only:
        - Bool, if True only shield damage is modified. Default False.
      * use_scaling_equation:
        - If True, a scaling formula will be applied, such that shots near damage_to_adjust_kdps see the full scaling_factor, and shots near damage_to_keep_static_kdps remain largely unchanged.
      * damage_to_adjust_kdps, damage_to_keep_static_kdps:
        - Equation tuning values, in units of kdps, eg. 1 for 1000 damage/second. Scaling values are for shield DPS; hull DPS will be scaled at a rate of 1/6 of shield DPS.
      * bullet_name_adjustment_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with the multiplier to apply. This also supports matching to bullet flags using a 'flag_' prefix, eg. 'flag_beam' will match to beam weapons. Flag matches are lower priority than name matches.
        - If multiple flag matches are found, the first flag will be used if the input is an OrderedDict, otherwise any Python default is used (likely equivelent to ordereddict in Python 3.6).
        - '*' entry will match all weapons not otherwise matched, equivelent to setting scaling_factor and not using the scaling equation.
      * maintain_energy_efficiency:
        - Bool, if True (default) then weapon energy usage will be scaled to keep the same damage/energy ratio, otherwise damage is adjusted but energy is unchanged.
      * ignore_repair_lasers:
        - Bool, if True (default) then repair lasers will be ignored.
      * print_changes:
        - If True, speed adjustments are printed to the summary file.  
      

 * Adjust_Weapon_Energy_Usage

    Requires: types/TBullets.txt

      Adjusts weapon energy usage by the given multiplier, globally or for selected bullets.
  
      * scaling_factor:
        - Multiplier to apply to all weapons without specific settings.
      * bullet_name_energy_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the multiplier to apply. This will override scaling_factor for this weapon.
      * ignore_repair_lasers:
        - Bool, if True (default) then repair lasers will be ignored.
      

 * Adjust_Weapon_Fire_Rate

    Requires: types/TBullets.txt, types/TLaser.txt

      Adjust weapon fire rates. DPS and energy efficiency will remain constant. This may be used to reduce fire rates for performance improvements. Secondary weapon effects are not modified. If a bullet is used by multiple lasers, the first laser will be used for fire rate damage and energy adjustment.
  
      * scaling_factor:
        - The base multiplier to apply to fire rate.
      * laser_name_adjustment_dict:
        - Dict, keyed by laser name (eg. 'SS_LASER_HEPT'), with the multiplier to apply instead of using the scaling_factor.     
      * fire_rate_floor:
        - Int, the floor below which fire rate will not be reduced, in shots per minute. Eg. 60 for 1/second.
      * skip_ammo_weapons:
        - If True, the fire rate change will ignore ammo weapons, since there is no good way to adjust ammo consumption.
      

 * Adjust_Weapon_OOS_Damage

    Requires: types/TBullets.txt, types/TLaser.txt

      Scale OOS damage. Damage may be scaled down to improve accuracy in combat evaluation, at the potential drawback of stalemates when shield regeneration outperforms damage.
  
      * scaling_factor:
        - The base multiplier to apply to OOS damage.
      

 * Adjust_Weapon_Range

    Requires: types/TBullets.txt

      Adjusts weapon range by adjusting lifetime or speed. To modify range, consider that range = speed * lifetime. Eg. 1.2 * 1.2 = 44% range increase.
  
      * lifetime_scaling_factor:
        - Multiplier to apply to all bullet lifetimes.
      * speed_scaling_factor:
        - Multiplier to apply to all bullet speeds.
      

 * Adjust_Weapon_Shot_Speed

    Requires: types/TBullets.txt

      Adjust weapon shot speeds. Range will remain constant. Beam weapons will not be affected.
  
      * scaling_factor:
        - The base multiplier to apply to shot speeds.
      * use_scaling_equation:
        - If True, a scaling formula will be applied, such that shots near target_speed_to_adjust see the full scaling_factor, and shots near speed_to_keep_static remain largely unchanged.
      * target_speed_to_adjust, speed_to_keep_static:
        - Equation tuning values, in meters/second.
      * bullet_name_adjustment_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with the multiplier to apply.
        - '*' entry will match all weapons not otherwise named, equivelent to setting scaling_factor and not using the scaling equation.
      * skip_areal:
        - If True, areal weapons (eg. PD and PSG) are skipped, since their damage delivery may be partially dependent on shot speed.
      * skip_flak: 
        - If True, flak weapons are skipped.
      * print_changes:
        - If True, speed adjustments are printed to the summary file.
      

 * Clear_Weapon_Flag

    Requires: types/TBullets.txt

      Clears a specified flag from all weapons.
  
      * flag_name:
        - Bullet property flag name, as found in Flags.py. Eg. 'charged'.
      

 * Convert_Beams_To_Bullets

    Requires: types/TBullets.txt

      Converts beam weapons to bullet weapons, to help with game slowdown when beams are fired at large ships and stations. Bullet speed will be set based on sampling other bullets of similar damage.
  
      * beams_not_converted:
        - List of bullet names for weapons not to be converted. Repair and tug lasers are added to this list by default.
      * speed_samples:
        - Int, the number of similar DPS weapons to sample when setting the bullet speed. Default 4.
      * sample_type:
        - String, one of ['min','avg'], if the minimum or average of speed ratio of sampled similar DPS weapons should be used. Default 'min'.
      

 * Convert_Weapon_To_Ammo

    Requires: types/TBullets.txt

      Converts the given weapons, determined by bullet type, to use ammunition instead of energy.
  
      * bullet_name_energy_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the ammo type to use in the replacement. Ammo type is given by a ware id value, or by a preconfigured string name. Currently supported ammo names: ['Mass Driver Ammunition']
      * energy_reduction_factor:
        - Multiplier on existing weapon energy, such that after ammo conversion the weapon will still use a small energy amount. Default will cut energy use by 90%, which is roughly the Vanilla difference between MD and PAC energy.
      

 * Convert_Weapon_To_Energy

    Requires: types/TBullets.txt

      Converts the given weapons, determined by bullet type, to use energy instead of ammunition. Ammo type may support general wares, and will reduce a ware by 1 per 200 shots.
  
      * bullet_name_energy_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the energy value to use in the replacement.
      

 * Remove_Weapon_Charge_Up

    Requires: types/TBullets.txt

      Remove charge up from all weapons, to make PPCs and similar easier to use in a manner consistent with the npcs (eg. hold trigger to just keep firing), as charging is a player-only option.
      

 * Remove_Weapon_Drain_Flag

    Requires: types/TBullets.txt

      Removes the weapon drain flag from any weapons. May also stop equipment damage being applied through shielding for these weapons.
      

 * Remove_Weapon_Shot_Sound

    Requires: types/TBullets.txt

      Removes impact sound from bullets. Little performance benefit expected, though untested.
      

 * Replace_Weapon_Shot_Effects

    Requires: types/TBullets.txt

      Replaces shot effects to possibly reduce lag. This appears to have little to no benefit in brief testing.
  
      * impact_replacement:
        - Int, the effect to use for impacts. Eg. 19 for mass driver effect. Avoid using 0, else sticky white lights have been observed.
      * launch_replacement:
        - Int, the effect to use for weapon launch.
      

 * Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio

    Requires: types/TBullets.txt

      Increases hull damage on weapons to achieve a specified hull:shield damage ratio requirement. Typical weapons are around a 1/6 ratio, though some weapons can be 1/100 or lower, such as ion weaponry. This transform can be used to give such weapons a viable hull damage amount.
  
      * minimum_ratio:
        - Float, the required ratio. Recommend something below 1/6 to avoid significant changes to most weapons. Default 1/20.
      


***

Change Log:
 * 1.x
   - Original project development for private use.
 * 2.0
   - Restructuring of project for general use, isolating individual transforms, separating out transform calls, adding robustness. Filling out documentation generation.
 * 2.1
   - Added Convert_Beams_To_Bullets.
 * 2.2
   - Added Adjust_Generic_Missions.
   - Added new arguments to Enhance_Mosquito_Missiles.
   - Adjusted default ignored weapons for Convert_Beams_To_Bullets.
 * 2.3
   - Added Add_Ship_Life_Support.
   - Added Adjust_Shield_Regen.
   - Added Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio.
   - Added Standardize_Ship_Tunings.
   - New options added for Adjust_Weapon_DPS.
   - New option for Adjust_Ship_Hull to scale repair lasers as well.
   - Several weapon transforms now ignore repair lasers by default.
   - Command line call defaults to User_Transforms.py if a file not given.
 * 2.4
   - Added Add_Ship_Equipment.
   - Added XRM_Standardize_Medusa_Vanguard.
   - Added Add_Ship_Variants, Add_Ship_Combat_Variants, Add_Ship_Trade_Variants.
 * 2.5
   - Updates to Add_Ship_Variants to refine is behavior and options.
   - Added in-game script for adding generated variants to shipyards.
   - XRM_Standardize_Medusa_Vanguard replaced with Patch_Ship_Variant_Inconsistencies.
 * 2.6
   - Updated scaling equation fitter to be more robust; functionality unchanged.
   - Update to Adjust_Missile_Damage to standardize the scaling function to support typical tuning paramaters.
   - Added Expand_Bomber_Missiles.
   - Added Add_Ship_Cross_Faction_Missiles.
   - Add_Ship_Boarding_Pod_Support.
   - Changed documentation generator to include more text in the readme file, and to categorize transforms.
 * 2.7
   - Minor tweak to Add_Ship_Variants, allowing selection of which variant will be set to 0 when an existing variant is used as a base ship.
   - Adjust_Missile_Damage has new parameters to scale missile ware volume and price in line with the damage adjustment.
 * 2.8
   - Added Adjust_Gate_Rings.
   - Removed Swap_Standard_Gates_To_Terran_Gates, which is replaced by an option in the new transform.
 * 2.9
   - Added Add_Job_Ship_Variants.
   - Added Change_Ware_Size.
   - Tweaked Add_Ship_Variants to specify shield_conversion_ratios in args.
   - Unedited source files will now be copied to the main directory, in case a prior run did edit them and needs overwriting.
 * 2.10
   - New option added to Adjust_Gate_Rings, supporting a protrusionless ring.
   - Added Add_Script, generic transform to add pregenerated scripts.
   - Added Disable_OOS_War_Sector_Spawns.
   - Added Convert_Attack_To_Attack_Nearest.
   - Bugfix for when the first transform called does not have file dependencies.
   - Renames the script 'a.x3customizer.add.variants.to.shipyards.xml' to remove the 'a.' prefix.
 * 2.11
   - Minor fix to rename .pck files in the addon/types folder that interfere with customized files.
 * 2.12
   - Added Add_CLS_Software_To_More_Docks.
   - Added Remove_Khaak_Corvette_Spin.
   - Added option to Adjust_Ship_Laser_Recharge to adjust ship maximum laser energy as well.
   - Added cap on mosquito missile damage when adjusting damages, to avoid possible OOS combat usage.
   - Bugfix for transforms which adjust laser energy usage, to ensure the laser can store enough charge for at least one shot.
   - Bugfix for adjusting missile hulls, to add entries to globals when missing.
   - Bugfix for file reading which broke in recent python update.
   - Added patch support for editing files without doing full original source uploads. Disable_OOS_War_Sector_Spawns now uses a patch.
   - Added support for automatically filling in the source folder with any necessary scripts.
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
   - Bug fixes for the director scripts, to ensure they work on new games and on terran/atf shipyards with cross-faction wares.
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
   - Added support for loading source files from cat/dat pairs, when the file is not found in the specified source folder.
   - Message log, as well as a log of files written, will now be written to a log folder customized by Set_Path.
 * 3.0
   - Major rewrite of the file handling system.
   - Can now load original data from loose files in the game directories as well as the user source folder and cat/dat pairs.
   - Normalized file creation in all transforms.
   - Added hashes to log of files written, to recognize when they change externally.
   - Added executable generation using pyinstaller.
   - Added alternative scaling functions to bypass scipy requirement, which otherwise bloats the exe.
 * 3.1
   - Bugfix for gate edits, adding an end-of-file newline that x3 requires and was lost in the file system conversion.
   - Added Allow_Valhalla_To_Jump_To_Gates.
 * 3.2
   - Added support for generating a zip file for release, containing necessary binaries and related files.
   - Converted patch creation from an input command script to a standalone make script.
 * 3.3
   - Bug fix in Adjust_Weapon_Fire_Rate.
   - More graceful handling of failed transforms.
   - Added flags on some transforms that are incompatible with LU.
   - Added Disable_Generic_Missions, a wrapper over Adjust_Generic_Missions.
 * 3.4
   - Changes Obj patches to search for code patterns instead of using hard offsets, to better adapt to different obj files.
   - Enabled support for LU for Adjust_Max_Seta, Adjust_Max_Speedup_Rate, and tentatively Stop_GoD_From_Removing_Stations.
   - Added on_frame_input option to Stop_Events_From_Disabling_Seta, allowing opening of menus while in seta.
 * 3.4.1
   - Minor tweak to catch gzip errors nicely, pending support for differently compressed files (eg. TWareT generated by x3 plugin manager).
 * 3.4.2
   - Added support for x2 style pck files in loose folders (eg. should now work better with x3 plugin manager).
 * 3.4.3
   - Raises exception if the x3/addon path appears incorrect instead of still attempting to run, unless -allow_path_error is enabled.
   - Some other minor cleanup of exception handling on path problems.
 * 3.5
   - Added Remove_Factory_Build_Cutscene.
   - Added Keep_TLs_Hired_When_Empty.
   - Added Kill_Spaceflies.
   - Added Prevent_Accidental_Spacefly_Swarms.
   - Restructured as a full Python package to support external imports and internal relative imports.
   - Control scripts need to be swapped from importing Transforms to importing X3_Customizer.
 * 3.5.1
   - Documentation refinement.
   - Added a helpful message when finding input scripts from pre-3.5.
 * 3.5.2
   - Added documentation support for forum BB code.
   - Added _Benchmark_Gate_Traversal_Time for private use.