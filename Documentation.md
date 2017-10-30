X3 Customizer v2.06
------------------

This tool will read in source files from X3, perform transforms on them, and write the results back out. Transforms will often perform complex or repetitive tasks succinctly, avoiding the need for hand editing of source files. Many transforms will also do analysis of game files, to intelligently select appropriate edits to perform. Source files will generally support any prior modding. Nearly all transforms support input arguments to set parameters and adjust behavior, according to user preferences. Most transforms will work on an existing save.

This tool is written in Python, and tested on version 3.6. To run this script, the user will need to install Python.

Usage:
 * "X3_Customizer <user_transform_module.py>"
   - Runs the customizer, using the provided control module which will specify the path to the AP directory, the folder containing the source files to be modified, and the transforms to be run. See User_Transforms_Example.py for an example. Defaults to running 'User_Transforms.py' if an argument is not provided.
 * "Make_Documentation.py"
   - Generates documentation for this project, as markdown supporting files README.md and Documentation.md.

Setup:
  * Transforms will operate on source files (eg. tships.txt) which need to be set up prior to running this tool. Source files can be extracted using X3 Editor 2 if needed. Source files may be provided after any other mods have been applied.

  * Source files need to be located in a folder underneath the specified AP addon directory, and will have an internal folder structure matching that of the files in the normal addon directory.

  * The user must write a Python script which will specify paths and control the customizer by calling transforms.

  * Output files will be generated in the addon directory matching the folder structure in the source folder. Non-transformed files will generate output files. Files which do not have a name matching the requirement of any transform will be ignored and not copied. In some cases, files may be generated one directory up, in the presumed Terran Conflict folder.

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

   This will write to the following files, overwriting any existing ones:   

    <path to X3 installation>
        addon
            maps
                x3_universe.xml
            types
                TBullets.txt
                TLaser.txt
                TShips.txt


***

Setup methods:

  * Set_Path

       Sets the pathing to be used for file loading and writing.
   
       * path_to_addon_folder:
         - Path to the X3 AP addon folder, containing the source_folder. Output files will be written relative to here.
         - If this is not the addon folder, a warning will be printed but operation will continue, writing files to this folder, though files will need to be moved to the proper addon folder to be applied to the game. Some generated files may be placed in the directory above this folder, eg. the expected TC directory.
   
       * source_folder:
         - Subfolder in the addon directory containing unmodified files, internally having the same folder structure as addon to be used when writing out transform results.
         - (eg. output to addon	ypes will source from input in addon\source_folder	ypes).
   
       * summary_file:
         - Path and name for where a summary file will be written, with any transform results. Defaults to 'X3_Customizer_summary.txt' in the addon directory.
       


***

Background Transforms:

 * Adjust_Fade_Start_End_Gap

    Requires: TBackgrounds.txt

      Adjust the gap between the start and end fade distance, changing how quickly objects will fade in. This will never affect fade_start, only fade_end.
  
      * fade_gap_min_func, fade_gap_max_func:
        - Functions which take fade_start as the argument, in km, and return the min and max gap allowed.
        - Example: 
          - Set fade gap to be as much as fade start:
            - fade_gap_min_func = lambda start: start*1
          - Require the fade gap be no longer than 20 km:
            - fade_gap_max_func = lambda start: 20
      

 * Adjust_Particle_Count

    Requires: TBackgrounds.txt

      Change the number of particles floating in space around the camera. Default game is 100, mods often set to 0, but can keep some small number for a feeling of speed.
  
      * base_count:
        - The base number of particles to use in all sectors. Default is 10, or 10% of the vanilla particle count.
      * fog_factor:
        - The portion of sector fog to add as additional particles. Eg. a fog factor of 0.5 will add 25 more particles in heavy fog.
      

 * Remove_Stars_From_Foggy_Sectors

    Requires: TBackgrounds.txt

      Removes star backgrounds from sectors with significant fog and short fade distance. Fogged sectors sharing a background with an unfogged sector will not be modified, as the background needs to be edited for all sectors which use it. Fade is removed from sectors which will not have their stars removed.
      
      * fog_requirement:
        - The fog requirement for star removal; all backgrounds affected need a fog above this much. Default of 12 is set for matching the Maelstrom background.
      * fade_distance_requirement_km:
        - The highest fade distance to allow; all backgrounds affected need a fade_start under this value (to prevent star removal in high visibility sectors). In km.
      

 * Set_Minimum_Fade_Distance

    Requires: TBackgrounds.txt

      Sets a floor to fade distance, so that object do not appear too closely. May be useful in some sectors with really short view distances, though may also want to keep those for variety. Note: max fade distance will be set to minimum fade distance if it would otherwise be lower. Recommend following this with a call to Adjust_Fade_Start_End_Gap.
  
      * distance_in_km : 
        - Minimum fade distance, in km.
      


***

Director Transforms:

 * Adjust_Generic_Missions

    Requires: 3.01 Generic Missions.xml

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

    Requires: 2.119 Trade Convoy.xml

      If convoy defense missions should use the convoy's race to select their ship type. The vanilla script uses randomized ship types (eg. a terran convoy flying teladi ships).
      

 * Standardize_Start_Plot_Overtunings

    Requires: 3.05 Gamestart Missions.xml

      Set the starting plots with overtuned ships to have their tunings standardized instead of being random.
  
      * fraction_of_max:
        - Float, typically between 0 and 1, the fraction of the max overtuning to use. A value of 0 will remove overtunings, and 1 will give max overtuning that is available in vanilla. Default of 0.7 is set to mimic moderate game reloading results.
      

 * Standardize_Tunings

    Requires: 3.08 Sector Management.xml

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

Gate Transforms:

 * Swap_Standard_Gates_To_Terran_Gates

    Requires: TGates.txt

      Changes standard gates into Terran gates, possibly helping reduce large ship suicides when entering a system.
      


***

Global Transforms:

 * Adjust_Global

    Requires: Globals.txt

      Adjust a global flag by the given multiplier. Generic transform works on any named global field.
  
      * field_name:
        - String, name of the field in Globals.txt
      * scaling_factor:
        - Multiplier to apply to the existing value.
      

 * Adjust_Strafe

    Requires: Globals.txt

      Strafe adjustment factor. Note: this does not appear to have any effect during brief testing.
      
      * small_ship_factor:
        - Multiplier on small ship strafe.
      * big_ship_factor:
        - Multiplier on big ship strafe.
      

 * Set_Communication_Distance

    Requires: Globals.txt

      Set max distance for opening communications with factories and ships.
  
      * distance_in_km
        - Int, max communication distance.
      

 * Set_Complex_Connection_Distance

    Requires: Globals.txt

      Set max range between factories in a complex. With complex cleaner and tubeless complexes, this can practically be anything, particularly useful when connecting up distant asteroids.
  
      * distance_in_km
        - Int, max connection distance.
      

 * Set_Dock_Storage_Capacity

    Requires: Globals.txt

      Change the capacity of storage docks: equipment docks, trading posts, etc.
  
      * player_factor:
        - Int, multiplier for player docks. Vanilla default is 3.
      * npc_factor:
        - Int, multiplier for npc docks. Vanilla default is 1.
      * hub_factor:
        - Int, multiplier for the Hub. Vanilla default is 6.
      

 * Set_Global

    Requires: Globals.txt

      Set a global flag to the given value. Generic transform works on any named global field.
  
      * field_name:
        - String, name of the field in Globals.txt
      * value:
        - Int, the value to set.
      


***

Job Transforms:

 * Adjust_Job_Count

    Requires: Jobs.txt

      Adjusts job counts using a multiplier. These will always have a minimum of 1.
  
      * job_count_factors:
        - List of tuples pairing an identifier key with the adjustment value to apply. The first match will be used.
        - Key will try to match a boolean field in the jobs file (see File_Fields for field names), or failing that will try to do a job name match (partial match supported) based on the name in the jobs file.
        - '*' will match all jobs not otherwise matched.
      

 * Adjust_Job_Respawn_Time

    Requires: Jobs.txt

      Adjusts job respawn times, using an adder and multiplier on the existing respawn time.
  
      * time_adder_list, time_multiplier_list:
        - Lists of tuples pairing an identifier key with the adjustment value to apply. The first match will be used.
        - Key will try to match a boolean field in the jobs file, (eg. 'owner_argon' or 'classification_trader', see File_Fields for field names), or failing that will try to do a job name match (partial match supported) based on the name in the jobs file.
        - '*' will match all jobs not otherwise matched.
      

 * Set_Job_Spawn_Locations

    Requires: Jobs.txt

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

    Requires: TShips.txt

      Adds boarding pod launch capability to selected classes of ships, eg. destroyers. Ships should support marines, so limit to M1, M2, M7, M6, TL, TM, TP.
      
      * ship_types:
        - List of ship names or types to add equipment to, eg. ['SS_SH_OTAS_M2', 'SG_SH_M1']. Default includes M6,M7,M2,M1.
      * required_missiles:
        - List of missile types, a ship must support one of these missiles before it will be given boarding pod support. Default is ['SG_MISSILE_HEAVY','SG_MISSILE_TR_HEAVY'], requiring ships to already support heavy missiles.
      

 * Add_Ship_Cross_Faction_Missiles

    Requires: TShips.txt

      Adds terran missile compatibility to commonwealth ships, and vice versa. Missiles are added based on category matching, eg. a terran ship that can fire light terran missiles will gain light commonwealth missiles. Note that AI ship loadouts may include any missile they can fire.
      
      * race_types:
        - List of race names whose ships will have missiles added. By default, the following are included: [Argon, Boron, Split, Paranid, Teladi, Xenon, Pirates, Goner, ATF, Terran, Yaki].
      

 * Adjust_Missile_Damage

    Requires: Globals.txt, TMissiles.txt

      Adjust missile damage values, by a flat scaler or configured scaling formula.
      
      * scaling_factor:
        - The base multiplier to apply to missile damage.
      * use_scaling_equation:
        - If True, a scaling formula will be applied, such that missiles near target_damage_to_adjust see the full scaling_factor, and missiles near damage_to_keep_static remain largely unchanged. Otherwise, scaling_factor is applied to all missiles.
      * target_damage_to_adjust, damage_to_keep_static:
        - Equation tuning values.
      * print_changes:
        - If True, speed adjustments are printed to the summary file.
      

 * Adjust_Missile_Hulls

    Requires: Globals.txt

      Adjust the hull value for all missiles by the scaling factor. Does not affect boarding pod hulls.
  
      * scaling_factor:
        - Multiplier on missile hull values.
      

 * Adjust_Missile_Range

    Requires: TMissiles.txt

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

    Requires: TMissiles.txt

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

    Requires: TMissiles.txt

      Makes mosquito missiles more maneuverable, generally by increasing the turn rate or adding blast radius, to make anti-missile abilities more reliable.
  
      * acceleration_factor:
        - Multiplier to the mosquito's acceleration.
      * turn_rate_factor:
        - Multiplier to the mosquito's turn rate.
      * proximity_meters:
        - If not 0, adds a proximity fuse with the given distance. For comparison, vanilla Silkworm missiles have a 200 meter radius.
      

 * Expand_Bomber_Missiles

    Requires: TShips.txt

      Allows bombers and missile frigates to use a wider variety of missiles. Bombers will gain fighter tier missiles, while frigates will gain corvette tier missiles. Terran ships will gain Terran missiles. Note that AI ship loadouts may include any missile they can fire, such that bombers will have fewer heavy missiles and more standard missiles.
      
      * include_bombers:
        - Bool, if True ships supporting bomber type missiles are modified. Default True.
      * include_frigates:
        - Bool, if True ships supporting missile frigate missiles are modified. Default True.
      * add_bomber_missiles_to_frigates:
        - Bool, if True frigates will also gain bomber type missiles. Default False. Low cargo volume of bomber missiles may be unbalanced on frigates.
      

 * Set_Missile_Swarm_Count

    Requires: TMissiles.txt, Globals.txt

      Set the number of submissiles fired by swarm missiles. Submissile damage is adjusted accordingly to maintain overall damage.
  
      * swarm_count:
        - Int, the number of missiles per swarm.
      


***

Shield Transforms:

 * Adjust_Shield_Regen

    Requires: TShields.txt

      Adjust shield regeneration rate by changing efficiency values.
      
      * scaling_factor:
        - Multiplier to apply to all shield types.
      


***

Ship Transforms:

 * Add_Ship_Combat_Variants

    Requires: TShips.txt, WareLists.txt, TWareT.txt

      Adds combat variants for combat ships. This is a convenience function which calls Add_Ship_Variants with variants [vanguard, sentinel, raider, hauler], for ship types [M0-M8]. See Add_Ship_Variants documentation for other parameters.
      

 * Add_Ship_Equipment

    Requires: TShips.txt, WareLists.txt

      Adds equipment as built-in wares for select ship classes.
  
      * ship_types:
        - List of ship names or types to add equipment to, eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].        
      * equipment_list:
        - List of equipment names from the ware files, eg. ['SS_WARE_LIFESUPPORT'].
      

 * Add_Ship_Life_Support

    Requires: TShips.txt, WareLists.txt

      Adds life support as a built-in ware for select ship classes. This is a convenience transform which calls Add_Ship_Equipment.
  
      * ship_types:
        - List of ship types to add life support to, eg. ['SG_SH_M2']. By default, this includes M6, M7, M2, M1, TL, TM.
      

 * Add_Ship_Trade_Variants

    Requires: TShips.txt, WareLists.txt, TWareT.txt

      Adds trade variants for trade ships. This is a convenience function which calls Add_Ship_Variants with variants [hauler, miner, tanker (xl), super freighter (xl)], for ship types [TS,TP,TM,TL]. See Add_Ship_Variants documentation for other parameters.    
      

 * Add_Ship_Variants

    Requires: TShips.txt, WareLists.txt, TWareT.txt

      Adds variants for various ships. Variant attribute modifiers are based on the average differences between existing variants and their basic ship, where only M3,M4,M5 are analyzed for combat variants, and only TS,TP are analyzed for trade variants, with Hauler being considered both a combat variant. After variants are created, a script may be manually run in game from the script editor which will add variants to all shipyards that sell the base ship. Run 'a.x3customizer.add.variants.to.shipyards.xml', no input args. Note: this will add all stock variants as well, as it currently has no way to distinguish the new ships from existing ones. Warning: it is unsafe to remove variants once they have been added to an existing save.
  
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
        - Bool, if True then existing heavy ships (variation 20) and other non-basic ships will have variants added. This may result in some redundancies, eg. variants of Mercury and Advanced Mercury. In some cases, the existing ship will be reclassified as a basic version to remove their suffix, eg. Hyperion Vanguard will become a base Hyperion from which a vanguard and other variants are generated. Default True.
      * variant_indices_to_ignore:
        - List of integers, any existing variants to be ignored for analysis and variant generation. Default list includes 8, XRM Mk.1 ships.
      * add_mining_equipment:
        - Bool, if True mining equipment will be added to Miner variants. Default True.
      * prepatch_ship_variant_inconsistencies:
        - Bool, if True then Patch_Ship_Variant_Inconsistencies will be run prior to this transform, to avoid some spurious variant generation. Default True with XRM fixes enabled; this should be safe to apply to vanilla AP.
      * print_variant_count:
        - If True, the number of new variants is printed to the summary file.
      * print_variant_modifiers:
        - If True  the calculated attributes used for variants will be printed to the summary file, given as multipliers on base attributes.
      

 * Adjust_Ship_Hull

    Requires: TShips.txt

      Adjust ship hull values. When applied to a existing save, ship hulls will not be updated automatically if hulls are increased.  Run the temp.srm.hull.reload.xml script from the XRM hull packs to refill all ships to 100% hull. Alternatively, ship hulls will be updated as ships die and respawn.
  
      * scaling_factor:
        - Multiplier to apply to any ship type not found in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a scaling factor to be applied.
      * adjust_repair_lasers:
        - Bool, if True (default) repair lasers will be scaled by the M6 hull scaling (if given), to avoid large changes in repair times.
      

 * Adjust_Ship_Laser_Recharge

    Requires: TShips.txt

      Adjust ship laser regeneration rate, either globally or per ship class.
      
      * scaling_factor:
        - Multiplier to apply to any ship type not found in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a scaling factor to be applied.
      

 * Adjust_Ship_Pricing

    Requires: TShips.txt

      Adjust ship pricing, either globally or per ship class.
  
      * scaling_factor:
        - Multiplier for any ship not matched in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a scaling factor to be applied.
      

 * Adjust_Ship_Shield_Regen

    Requires: TShips.txt

      Adjust ship shield regeneration rate, either globally or per ship class. This may have no effect beyond where all ship shields are powered at their individual max rates.
      
      * scaling_factor:
        - Multiplier to apply to all ship types on top of those present in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a tuple of (targeted_recharge_rate, reduction_factor, max_rate) where any recharges above targeted_recharge_rate will have the reduction_factor applied to the difference in original and target rates. Recharge rates will be capped at max_rate.
      

 * Adjust_Ship_Shield_Slots

    Requires: TShips.txt

      Adjust ship shielding by changing shield slot counts. Shield types will remain unchanged, and at least 1 shield slot will be left in place. When applied to an existing save, ship shields will not be updated automatically, as some ships may continue to have excess shields equipped, or ships may lack enough shield inventory to fill up added slots.
      
      * adjustment_factors_dict:
        - Dict keyed by ship type, holding a tuple of (targeted_total_shielding, reduction_factor), where any ships with shields above targeted_total_shielding will have reduction_factor applied to their shield amount above the target.
      

 * Adjust_Ship_Speed

    Requires: TShips.txt

      Adjust ship speed and acceleration, globally or per ship class.
      
      * scaling_factor:
        - Multiplier to apply to any ship type not found in adjustment_factors_dict.
      * adjustment_factors_dict:
        - Dict keyed by ship type or name, holding a scaling factor to be applied.
      

 * Boost_Truelight_Seeker_Shield_Reactor

    Requires: TShips.txt

      Enhances the Truelight Seeker's shield reactor. In AP the TLS has a shield reactor only around 1/10 what is normal for similar ships; this applies a 10x increase. If the TLS is already at least 1/5 of Centaur shielding, this transform is not applied.
      

 * Fix_Pericles_Pricing

    Requires: TShips.txt

      Applies a bug fix to the enhanced pericles, which has its npc value set to 1/10 of player value, causing it price to be 1/10 what it should be. Does nothing if the existing npc and player prices are matched.
      

 * Patch_Ship_Variant_Inconsistencies

    Requires: TShips.txt

      Applies some patches to some select inconsistencies in ship variants. Modified ships include the Baldric Miner and XRM Medusa Vanguard, both manually named instead of using the variant system. This is meant to be run prior to Add_Ship_Variants, to avoid the non-standard ships creating their own sub-variants. There may be side effects if the variant inconsistencies were intentional.
  
      * include_xrm_fixes
        - Bool, if True then the Medusa Vanguard is patched if found and in the form set by XRM. Default True.
      

 * Simplify_Engine_Trails

    Requires: TShips.txt

      Change engine trail particle effects to basic or none. This will switch to effect 1 for medium and light ships and 0 for heavy ships, as in vanilla AP.
  
      * remove_trails:
        - If True, this will remove trails from all ships.
      

 * Standardize_Ship_Tunings

    Requires: TShips.txt

      Standardize max engine or rudder tuning amounts across all ships. Eg. instead of scouts having 25 and carriers having 5 engine runings, both will have some fixed number. Maximum ship speed and turn rate is kept constant, but minimum will change. If applied to an existing save, existing ships may end up overtuned; this is recommended primarily for new games, pending inclusion of a modification script which can recap ships to max tunings. Ships with 0 tunings will remain unedited.
  
      * engine_tunings:
        - Int, the max engine tunings to set.
      * rudder_tunings:
        - Int, the max rudder tunings to set.
      * ship_types:
        - List of ship names or types to adjust tunings for. If empty (default), all ships are adjusted.
      


***

Universe Transforms:

 * Color_Sector_Names

    Requires: x3_universe.xml, 0001-L044.xml, 7027-L044.xml, 7360-L044.xml

      Colors sector names in the map based on race owners declared in the x3_universe file. Some sectors may remain uncolored if their name is not set in the standard way through text files. Only works on the English files, L044, for now. Note: searching sectors by typing a name will no longer work except on uncolored sectors, eg. unknown sectors.
  
      * race_color_letters:
        - Dict matching race id string to the color code string to be used. Default is filled out similar to the standalone colored sectors mod.
      

 * Restore_Aldrin_rock

    Requires: x3_universe.xml

      Restors the big rock in Aldrin for XRM, reverting to the vanilla sector layout. Note: only works on a new game.
      

 * Restore_Hub_Music

    Requires: x3_universe.xml

      If Hub sector (13,8) music should be restored to that in AP. (XRM sets the track to 0.) Applies to new games, and optionally to an existing save.
  
      * apply_to_existing_save:
        - If True, makes a drop-in director script that will fire once and change the music for an existing save game. This is not reversable at this time.
      

 * Restore_M148_Music

    Requires: x3_universe.xml

      If Argon Sector M148 (14,8) music should be restored to that in AP. (XRM changes this to the argon prime music.) Applies to new games, and optionally to an existing save.
      
      * apply_to_existing_save:
        - If True, makes a drop-in director script that will fire once and change the music for an existing save game. This is not reversable at this time.
      


***

Ware Transforms:

 * Restore_Vanilla_Tuning_Pricing

    Requires: TWareT.txt

      Sets the price for ship tunings (engine, rudder, cargo) to those used in vanilla AP.
      

 * Set_Ware_Pricing

    Requires: TWareT.txt

      Sets ware pricing for the given ware list. Prices are the basic values in the T file, and have some adjustment before reaching the game pricing. Currently only works on tech wares in TWareT.txt.
  
      * name_price_dict:
        - Dict keyed by ware name (eg. 'SS_WARE_TECH213'), holding the flat value to apply for its T file price.
      * name_price_factor_dict:
        - As above, except holding a multiplier to apply to the existing price for the ware. Applies after name_price_dict if an item is in both dicts.
      


***

Weapon Transforms:

 * Adjust_Beam_Weapon_Duration

    Requires: TBullets.txt

      Adjusts the duration of beam weapons. Shot damage will be applied over the duration of the beam, such that shorter beams will apply their damage more quickly. Longer duration beams are weaker against small targets which move out of the beam before its damage is fully applied. Beam range will remain unchanged. Note: this does not affect fire rate, so multiple beams may become active at the same time.
  
      * bullet_name_adjustment_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to apply, as a tuple of (min, factor, max), where min and max are given in seconds.
        - None may be entered for min or max to disable those limits.
        - '*' entry will match all beam weapons not otherwise named.
      * ignore_repair_lasers:
        - Bool, if True (default) then repair lasers will be ignored.
      

 * Adjust_Beam_Weapon_Width

    Requires: TBullets.txt

      Adjusts the width of beam weapons. Narrower beams will have more trouble hitting small targets at a distance. In vanilla AP beam widths are generally set to 1, though in XRM the widths have much wider variety. This can be used to nerf anti-fighter defense of capital ships with beam mounts.
  
      * bullet_name_adjustment_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to apply, as a tuple of (min, factor, max), applied to height and width.
        - None may be entered for min or max to disable those limits.
        - '*' entry will match all beam weapons not otherwise named.
      

 * Adjust_Weapon_DPS

    Requires: TBullets.txt, TLaser.txt

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

    Requires: TBullets.txt

      Adjusts weapon energy usage by the given multiplier, globally or for selected bullets.
  
      * scaling_factor:
        - Multiplier to apply to all weapons without specific settings.
      * bullet_name_energy_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the multiplier to apply. This will override scaling_factor for this weapon.
      * ignore_repair_lasers:
        - Bool, if True (default) then repair lasers will be ignored.
      

 * Adjust_Weapon_Fire_Rate

    Requires: TBullets.txt, TLaser.txt

      Adjust weapon fire rates. DPS and energy efficiency will remain constant. This may be used to reduce fire rates for performance improvements. Fire rate changes will apply to IS damage only; OOS does not use fire rate. Secondary weapon effects are not modified. If a bullet is used by multiple lasers, the first laser will be used for fire rate damage and energy adjustment.
  
      * scaling_factor:
        - The base multiplier to apply to fire rate.
      * laser_name_adjustment_dict:
        - Dict, keyed by laser name (eg. 'SS_LASER_HEPT'), with the multiplier to apply instead of using the scaling_factor.     
      * fire_rate_floor:
        - Int, the floor below which fire rate will not be reduced, in shots per minute. Eg. 60 for 1/second.
      * skip_ammo_weapons:
        - If True, the fire rate change will ignore ammo weapons, since there is no good way to adjust ammo consumption.
      

 * Adjust_Weapon_OOS_Damage

    Requires: TBullets.txt, TLaser.txt

      Scale OOS damage. Damage may be scaled down to improve accuracy in combat evaluation, at the potential drawback of stalemates when shield regeneration outperforms damage.
  
      * scaling_factor:
        - The base multiplier to apply to OOS damage.
      

 * Adjust_Weapon_Range

    Requires: TBullets.txt

      Adjusts weapon range by adjusting lifetime or speed. To modify range, consider that range = speed * lifetime. Eg. 1.2 * 1.2 = 44% range increase.
  
      * lifetime_scaling_factor:
        - Multiplier to apply to all bullet lifetimes.
      * speed_scaling_factor:
        - Multiplier to apply to all bullet speeds.
      

 * Adjust_Weapon_Shot_Speed

    Requires: TBullets.txt

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

    Requires: TBullets.txt

      Clears a specified flag from all weapons.
  
      * flag_name:
        - Bullet property flag name, as found in Flags.py. Eg. 'charged'.
      

 * Convert_Beams_To_Bullets

    Requires: TBullets.txt

      Converts beam weapons to bullet weapons, to help with game slowdown when beams are fired at large ships and stations. Bullet speed will be set based on sampling other bullets of similar damage.
  
      * beams_not_converted:
        - List of bullet names for weapons not to be converted. Repair and tug lasers are added to this list by default.
      * speed_samples:
        - Int, the number of similar DPS weapons to sample when setting the bullet speed. Default 4.
      * sample_type:
        - String, one of ['min','avg'], if the minimum or average of speed ratio of sampled similar DPS weapons should be used. Default 'min'.
      

 * Convert_Weapon_To_Ammo

    Requires: TBullets.txt

      Converts the given weapons, determined by bullet type, to use ammunition instead of energy.
  
      * bullet_name_energy_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the ammo type to use in the replacement. Ammo type is given by a ware id value, or by a preconfigured string name. Currently supported ammo names: ['Mass Driver Ammunition']
      * energy_reduction_factor:
        - Multiplier on existing weapon energy, such that after ammo conversion the weapon will still use a small energy amount. Default will cut energy use by 90%, which is roughly the Vanilla difference between MD and PAC energy.
      

 * Convert_Weapon_To_Energy

    Requires: TBullets.txt

      Converts the given weapons, determined by bullet type, to use energy instead of ammunition. Ammo type may support general wares, and will reduce a ware by 1 per 200 shots.
  
      * bullet_name_energy_dict:
        - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the energy value to use in the replacement.
      

 * Remove_Weapon_Charge_Up

    Requires: TBullets.txt

      Remove charge up from all weapons, to make PPCs and similar easier to use in a manner consistent with the npcs (eg. hold trigger to just keep firing), as charging is a player-only option.
      

 * Remove_Weapon_Drain_Flag

    Requires: TBullets.txt

      Removes the weapon drain flag from any weapons. May also stop equipment damage being applied through shielding for these weapons.
      

 * Remove_Weapon_Shot_Sound

    Requires: TBullets.txt

      Removes impact sound from bullets. Little performance benefit expected, though untested.
      

 * Replace_Weapon_Shot_Effects

    Requires: TBullets.txt

      Replaces shot effects to possibly reduce lag. This appears to have little to no benefit in brief testing.
  
      * impact_replacement:
        - Int, the effect to use for impacts. Eg. 19 for mass driver effect. Avoid using 0, else sticky white lights have been observed.
      * launch_replacement:
        - Int, the effect to use for weapon launch.
      

 * Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio

    Requires: TBullets.txt

      Increases hull damage on weapons to achieve a specified hull:shield damage ratio requirement. Typical weapons are around a 1/6 ratio, though some weapons can be 1/100 or lower, such as ion weaponry. This transform can be used to give such weapons a viable hull damage amount.
  
      * minimum_ratio:
        - Float, the required ratio. Recommend something below 1/6 to avoid significant changes to most weapons. Default 1/20.
      


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

***

Change Log:
 * 1.x :
   - Original project development for private use.
 * 2.0 :
   - Restructuring of project for general use, isolating individual transforms, separating out transform calls, adding robustness. Filling out documentation generation.
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
 * 2.05:
   - Updates to Add_Ship_Variants to refine is behavior and options.
   - Added in-game script for adding generated variants to shipyards.
   - XRM_Standardize_Medusa_Vanguard replaced with Patch_Ship_Variant_Inconsistencies.
 * 2.06:
   - Updated scaling equation fitter to be more robust; functionality unchanged.
   - Update to Adjust_Missile_Damage to standardize the scaling function to support typical tuning paramaters.
   - Added Expand_Bomber_Missiles.
   - Added Add_Ship_Cross_Faction_Missiles.
   - Add_Ship_Boarding_Pod_Support.
   - Changed documentation generator to include more text in the readme file, and to categorize transforms.