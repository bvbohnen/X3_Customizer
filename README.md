X3 Customizer 3.16
-----------------

This tool will read in source files from X3, modify on them based on user selected transforms, and write the results back to the game directory. Transforms will often perform complex or repetitive tasks succinctly, avoiding the need for hand editing of source files. Many transforms will also do analysis of game files, to intelligently select appropriate edits to perform.  Some transforms carry out binary code edits, allowing for options not found elsewhere.

Source files will generally support any prior modding. Most transforms support input arguments to set parameters and adjust behavior, according to user preferences. Most transforms will work on an existing save.

This tool is written in Python, and tested on version 3.7. As of customizer version 3, an executable will be generated for users who do not wish to run the Python source code directly, and is available on the github Releases page.  These will be provided as convenient, generally for 64-bit Windows.  For Linux or 32-bit Windows users, the source code can be run directly using an appopriate version of Python.

This tool is designed primarily for Albion Prelude v3.3. Most transforms will support prior or later versions of AP. TC 3.4 is tentatively supported for many transforms, though has not been thoroughly tested. Farnham's Legacy support has been added as well.

When used alongside the X3 Plugin Manager: if the customizer outputs to a catalog (the default), these tools can run in either order; if the customizer outputs to loose files (a command line option), the customizer should be run second, after the plugin manager is closed, since the plugin manager generates a TWareT.pck file when closed that doesn't capture changes in TWareT.txt made by this tool.

Usage for Releases:

 * "Launch_X3_Customizer.bat [path to user_transform_module.py]"
   - Call from the command line for full options, or run directly for default options.
   - Runs the customizer, using the provided python user_transform_module which will specify the path to the X3 directory and the transforms to be run.
   - By default, attempts to run User_Transforms.py in the input_scripts folder.
   - Call with '-h' to see any additional arguments.
 * "Clean_X3_Customizer.bat [path to user_transform_module.py]"
   - Similar to Launch_X3_Customizer, except appends the "-clean" flag, which will undo any transforms from a prior run.

Usage for the Python source code:

 * "X3_Customizer\Main.py [path to user_transform_module.py]"
   - This is the primary entry function for the python source code.
   - Does not fill in a default transform file unless the -default_script option is used.
   - Supports general python imports in the user_transform_module.
   - If the scipy package is available, this supports smoother curve fits for some transforms, which were omitted from the Release due to file size.
 * "X3_Customizer\Make_Documentation.py"
   - Generates updated documentation for this project, as markdown formatted files README.md and Documentation.md.
 * "X3_Customizer\Make_Executable.py"
   - Generates a standalone executable and support files, placed in the bin folder. Requires the PyInstaller package be available. The executable will be created for the system it was generated on.
 * "X3_Customizer\Make_Patches.py"
   - Generates patch files for this project from some select modified game scripts. Requires the modified scripts be present in the patches folder; these scripts are not included in the repository.
 * "X3_Customizer\Make_Release.py"
   - Generates a zip file with all necessary binaries and source files for general release.

Setup and behavior:

  * Transforms will operate on source files (eg. tships.txt) which are either provided as loose files, or extracted automatically from the game's cat/dat files.

  * Source files are searched for in this priority order, where packed versions (pck, pbb, pbd) of files take precedence:
    - From an optional user specified source folder, with a folder structure matching the X3 directory structure (without 'addon' path). Eg. [source_folder]/types/TShips.txt
    - From the normal x3 folders.
    - From the incrementally indexed cat/dat files in the 'addon' or 'addon2' folder.
    - From the incrementally indexed cat/dat files in the base x3 folder.
    - Note: any cat/dat files in the 'addon/mods' folder will be ignored, due to ambiguity on which if any might be selected in the game launcher.

  * The user controls the customizer using a command script which will set the path to the X3 installation to customize (using the Set_Path function), and will call the desired transforms with any necessary parameters. This script is written using Python code, which will be executed by the customizer.
  
  * The key command script sections are:
    - "from X3_Customizer import *" to make all transform functions available.
    - Call Set_Path to specify the X3 directory, along with some other path options. See documentation for parameters.
    - Call a series of transform functions, as desired.
  
  * The quickest way to set up the command script is to copy and edit the "input_scripts/User_Transforms_template.py" file, renaming it to "User_Transforms.py" for recognition by Launch_X3_Customizer.bat. Included in the repository is Authors_Transforms, the author's personal set of transforms, which can be checked for futher examples.

  * Transformed output files will be generated to a catalog file in the addon folder by default, or as loose files in the x3 directories if requested. Scripts are always placed in the scripts folder. Already existing loose files will be renamed, suffixing with '.x3c.bak', if they do not appear to have been created by the customizer on a prior run. A json log file will be written with information on which files were created or renamed.

  * Warning: this tool will attempt to avoid unsafe behavior, but the user should back up irreplaceable files to be safe against bugs such as accidental overwrites of source files with transformed files.
  

Other contributors: RoverTX

Full documentation found in Documentation.md.

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

Background Transforms:

 * Adjust_Fade_Start_End_Gap

      Adjust the gap between the start and end fade distance, changing how quickly objects will fade in. This will never affect fade_start, only fade_end.

 * Adjust_Particle_Count

      Change the number of particles floating in space around the camera. Default game is 100, mods often set to 0, but can keep some small number for a feeling of speed.

 * Remove_Stars_From_Foggy_Sectors

      Removes star backgrounds from sectors with significant fog and short fade distance. Fogged sectors sharing a background with an unfogged sector will not be modified, as the background needs to be edited for all sectors which use it. Fade is removed from sectors which will not have their stars removed.

 * Set_Minimum_Fade_Distance

      Sets a floor to fade distance, so that object do not appear too closely. May be useful in some sectors with really short view distances, though may also want to keep those for variety. Note: max fade distance will be set to minimum fade distance if it would otherwise be lower. Recommend following this with a call to Adjust_Fade_Start_End_Gap.


***

Director Transforms:

 * Adjust_Generic_Missions (incompatible with: FL)

      Adjust the spawn chance of various generic mission types, relative to each other. Note: decreasing chance on unwanted missions seems to work better than increasing chance on wanted missions.

 * Convoys_made_of_race_ships (incompatible with: FL)

      If convoy defense missions should use the convoy's race to select their ship type. The vanilla script uses randomized ship types (eg. a terran convoy flying teladi ships).

 * Disable_Generic_Missions (incompatible with: FL)

      Disable generic missions from spawning. Existing generic missions will be left untouched.

 * Fix_Corporation_Troubles_Balance_Rollover (incompatible with: FL)

      In the Corporation Troubles plot, prevents the bank balance from reaching >2 billion and rolling over due to the 32-bit signed integer limit.

 * Fix_Dual_Convoy_Invincible_Stations (incompatible with: FL)

      Fixes Dual Convoy generic missions to no longer leave stations permenently invincible, and to no longer risk clearing invincibility from plot stations, as well as fixes a minor bug in the parameter list.

 * Fix_Reset_Invincible_Stations (incompatible with: FL)

      Resets the invinciblity flag on stations in an existing save. Works by re-triggering the matching script contained in an AP patch, which will preserve invincibilty for AP plot related stations. Warnings: invincibility flags from other sources (eg. TC plots for AP) may be lost. Pending test and verification.

 * Fix_Terran_Plot_Aimless_TPs (incompatible with: FL)

      In the Terran Conflict plot when allied TPs move to capture an Elephant, fix replacement TPs to move toward the Elephant instead of wandering aimlessly.

 * Standardize_Start_Plot_Overtunings (incompatible with: LU, FL)

      Set the starting plots with overtuned ships to have their tunings standardized instead of being random.

 * Standardize_Tunings (incompatible with: LU, TC, FL)

      Set the number of randomized tuning creates at gamestart to be de-randomized into a standard number of tunings. Note: vanilla has 2-5 average tunings per crate, 8 crates total. Default args here reach this average, biasing toward engine tunings.


***

Factory Transforms:

 * Add_More_Factory_Sizes

      Adds factories of alternate sizes, from basic to XL. Price and volume of new sizes is based on the scaling common to existing factories. Factories will be added to existing shipyards the first time a game is loaded after running this transform; this may take several seconds to complete, during which time the game will be unresponsive. Warning: it is unsafe to remove factories once they have been added to an existing save.


***

Gate Transforms:

 * Adjust_Gate_Rings

      Various options to modify gate rings, with the aim of reducing capital ship suicides when colliding with the pylons shortly after the player enters a sector. Includes ring removal, rotation, reversal, and model swaps. Inactive versions of gates will also be updated for consistency. When applied to an existing save, gate changes will appear on a sector change.


***

Global Transforms:

 * Adjust_Global

      Adjust a global flag by the given scaling_factor. Generic transform works on any named global field.

 * Adjust_Strafe

      Strafe adjustment factor.  Experimental. Note: this does not appear to have any effect during brief testing.

 * Set_Communication_Distance

      Set max distance for opening communications with factories and ships.

 * Set_Complex_Connection_Distance

      Set max range between factories in a complex. With complex cleaner and tubeless complexes, this can practically be anything, particularly useful when connecting up distant asteroids.

 * Set_Dock_Storage_Capacity

      Change the capacity of storage docks: equipment docks, trading posts, etc.

 * Set_Global

      Set a global flag to the given value. Generic transform works on any named global field.


***

Job Transforms:

 * Add_Job_Ship_Variants

      Allows jobs to spawn with a larger selection of variant ships. This does not affect jobs with a preselected ship to spawn, only those with random selection. Variants are added when the basic version of the ship is allowed, to preserve cases where a variant has been preselected.

 * Adjust_Job_Count

      Adjusts job ship counts using a multiplier. These will always have a minimum of 1. Jobs are matched by name or an attribute flag, eg. 'owner_pirate'. This will also increase the max number of jobs per sector accordingly.

 * Adjust_Job_Respawn_Time

      Adjusts job respawn times, using an adder and multiplier on the existing respawn time.

 * Set_Job_Spawn_Locations

      Sets the spawn location of ships created for jobs, eg. at a shipyard, at a gate, docked at a station, etc.


***

Missile Transforms:

 * Add_Ship_Boarding_Pod_Support

      Adds boarding pod launch capability to selected classes of ships, eg. destroyers. Ships should support marines, so limit to M1, M2, M7, M6, TL, TM, TP.

 * Add_Ship_Cross_Faction_Missiles

      Adds terran missile compatibility to commonwealth ships, and vice versa. Missiles are added based on category matching, eg. a terran ship that can fire light terran missiles will gain light commonwealth missiles. Note that AI ship loadouts may include any missile they can fire.

 * Adjust_Missile_Damage

      Adjust missile damage values, by a flat scaler or configured scaling formula. 

 * Adjust_Missile_Hulls

      Adjust the hull value for all missiles by the scaling factor. Does not affect boarding pod hulls.

 * Adjust_Missile_Range

      Adjust missile range by changing lifetime, by a flat scaler or configured scaling formula. This is particularly effective for the re-lock missiles like flail, to reduce their ability to keep retargetting across a system, instead running out of fuel from the zigzagging.

 * Adjust_Missile_Speed

      Adjust missile speeds, by a flat scaler or configured scaling formula.

 * Enhance_Mosquito_Missiles

      Makes mosquito missiles more maneuverable, generally by increasing the turn rate or adding blast radius, to make anti-missile abilities more reliable.

 * Expand_Bomber_Missiles

      Allows bombers and missile frigates to use a wider variety of missiles. Bombers will gain fighter tier missiles, while frigates will gain corvette tier missiles. Terran ships will gain Terran missiles. Note that AI ship loadouts may include any missile they can fire, such that bombers will have fewer heavy missiles and more standard missiles.

 * Set_Missile_Swarm_Count

      Set the number of submissiles fired by swarm missiles. Submissile damage is adjusted accordingly to maintain overall damage.


***

Obj_Code Transforms:

 * Adjust_Max_Seta (incompatible with: TC)

      Changes the maximum SETA speed multiplier. Higher multipliers than the game default of 10 may cause oddities.

 * Adjust_Max_Speedup_Rate

      Changes the rate at which SETA turns on. By default, it will accelerate by (selected SETA -1)/10 every 250 milliseconds. This transform will reduce the delay between speedup ticks.

 * Allow_Valhalla_To_Jump_To_Gates (incompatible with: LU, TC, FL)

      Removes a restriction on the Valhalla, or whichever ship is at offset 211 in tships, from jumping to gates. This should only be applied alongside another mod that either reduces the valhalla size, increases gate size, removes gate rings, or moves/removes the forward pylons, to avoid collision problems.

 * Disable_Asteroid_Respawn (incompatible with: LU)

      Stops any newly destroyed asteroids from being set to respawn. This can be set temporarily when wishing to clear out some unwanted asteroids. It is not recommended to leave this transform applied long term, without some other method of replacing asteroids.

 * Disable_Combat_Music

      Turns off combat music, keeping the normal environment music playing when nearing hostile objects. If applied to a saved game already in combat mode, combat music may continue to play for a moment. The beep on nearing an enemy will still be played.

 * Disable_Docking_Music

      Prevents docking music from playing when the player manually requests docking.

 * Force_Infinite_Loop_Detection

      Use with caution. Turns on infinite loop detection in the script engine for all scripts. Once turned on, loop detection will stay on for running scripts even if this transform is removed. This is intended for limited debug usage, and should preferably not be applied to a main save file to avoid bugs when scripts are ended due to false positives.

 * Hide_Lasertowers_Outside_Radar

      Prevents lasertowers and mines from showing up on sector maps when outside the radar ranges of player ships.

 * Keep_TLs_Hired_When_Empty

      When a hired TL places its last station, it will remain hired until the player explicitly releases it instead of being automatically dehired.

 * Kill_Spaceflies (incompatible with: LU, FL)

      Kills active spaceflies by changing their "is disabled" script command to make them self destruct. Intended for use with games that have accumulated many stale spacefly swarms generated by Improved Races 2.0 or Salvage Command Software or other mods which accidentally add excess spaceflies through the "create ship" command, causing accumulating slowdown (eg. 85% SETA slowdown after 10 game days). Use Prevent_Accidental_Spacefly_Swarms to stop future spacefly accumulation, and this transform to clean out existing spaceflies.

 * Make_Terran_Stations_Make_Terran_Marines (incompatible with: LU, TC)

      Allow Terran stations (eg. orbital patrol bases) to generate Terran marines instead of random commonwealth marines. Additional modding may be needed to add marines as products of some Terran stations (not included here) before an effect is seen.

 * Max_Marines_Video_Id_Overwrite (incompatible with: LU, TC)

      Remove the sirokos overwrite and put in its place a check for ships video ID Which if larger than the default value will overwrite

 * Preserve_Captured_Ship_Equipment (incompatible with: FL)

      Preserves equipment of captured ships.  This is expected to affect bailed ships, marine captured ships, the "pilot eject from ship" script command, and the "force pilot to leave ship" director command.

 * Prevent_Accidental_Spacefly_Swarms

      Prevents spaceflies from spawning swarms when created by a script using the 'create ship' command. Aimed at mods such as Improved Races 2.0 and SCS, which create and destroy a spacefly but accidentally leave behind a swarm with active scripts, causing spacefly accumulation and game slowdown.

 * Prevent_Ship_Equipment_Damage (incompatible with: LU)

      Damage to a ship's hull will no longer randomly destroy equipment.

 * Remove_Complex_Related_Sector_Switch_Delay (incompatible with: LU, TC, FL)

      Disables calls to the SA_CleanUpObjects function when changing sectors. This function introduces a potentially very long delay in games that have built large complexes, for unknown reasons. Exact purpose of the function is not known, but unwanted side effects have not been observed or reported by users.

 * Remove_Factory_Build_Cutscene (incompatible with: LU)

      Removes the cutscene that plays when placing factories by shortening the duration to 0.  Also prevents the player ship from being stopped. May still have some visible camera shifts for an instant.

 * Remove_Modified_Check

      Partially removes the modified flag check for achievements. This will allow achievements to display and increment, but is not sufficient on its own for unlocks.  (May need to be paired with a modified executable.)

 * Set_LaserTower_Equipment (incompatible with: LU, TC)

      Sets laser and shield type and count that are auto equipped for lasertowers and Terran orbital lasers. May need corresponding changes in Tships to enable equipment compatibility (not included here).

 * Set_Max_Marines (incompatible with: LU, TC, FL)

      Sets the maximum number of marines that each ship type can carry. These are byte values, signed, so max is 127. Note: in some cases, a larger ship type may use the marine count of a smaller ship if it is greater. Note: FL sets per-ship limits through tboarding.txt instead.

 * Stop_Events_From_Disabling_Seta (incompatible with: LU)

      Stop SETA from being turned off automatically upon certain events, such as missile attacks.

 * Stop_GoD_From_Removing_Stations

      Stops the GoD engine from removing stations which are nearly full on products or nearly starved of resources for extended periods of time.  This will not affect stations already removed or in the process of being removed.


***

Script Transforms:

 * Add_CLS_Software_To_More_Docks (incompatible with: FL)

      Adds Commodity Logistics Software, internal and external, to all equipment docks which stock Trade Command Software Mk2. This is implemented as a setup script which runs on the game loading. Once applied, this transform may be disabled to remove the script run time. This change is not easily reversable.

 * Allow_CAG_Apprentices_To_Sell (incompatible with: LU, TC, FL)

      Allows Commercial Agents to sell factory products at pilot rank 0. May require CAG restart to take effect.

 * Complex_Cleaner_Bug_Fix (incompatible with: LU, FL)

      Apply bug fixes to the Complex Cleaner mod. Designed for version 4.09 of that mod. Includes a fix for mistargetted a wrong hub in systems with multiple hubs, and a fix for some factories getting ignored when crunching. Patches plugin.gz.CmpClean.Main.xml.

 * Complex_Cleaner_Use_Small_Cube (incompatible with: LU, FL)

      Forces the Complex Cleaner to use the smaller cube model always when combining factories. Patches plugin.gz.CmpClean.crunch.xml.

 * Convert_Attack_To_Attack_Nearest

      Modifies the Attack command when used on an owned asset to instead enact Attack Nearest. In vanilla AP, such attack commands are quietly ignored. Intended for use when commanding groups, where Attack is available but Attack Nearest is not. This replaces '!ship.cmd.attack.std'.

 * Disable_OOS_War_Sector_Spawns (incompatible with: LU, TC, FL)

      Disables spawning of dedicated ships in the AP war sectors which attack player assets when the player is out-of-sector. By default, these ships scale up with player assets, and immediately respawn upon being killed. This patches '!fight.war.protectsector'.

 * Fix_OOS_Laser_Missile_Conflict (incompatible with: LU, TC, FL)

      Allows OOS combat to include both missile and laser fire in the same attack round. In vanilla AP, a ship firing a missile will not fire its lasers for a full round, generally causing a large drop in damage output. With the change, adding missiles to OOS ships should not hurt their performance.

 * Fleet_Interceptor_Bug_Fix (incompatible with: LU, TC, FL)

      Apply bug fixes to the Fleet logic for selecting ships to launch at enemies. A mispelling of 'interecept' causes M6 ships to be launched against enemy M8s instead of interceptors. Patches !lib.fleet.shipsfortarget.xml.

 * Increase_Escort_Engagement_Range (incompatible with: LU, TC, FL)

      Increases the distance at which escort ships will break and attack a target. In vanilla AP an enemy must be within 3km of the escort ship. This transform will give custom values based on the size of the escorted ship, small, medium (m6), or large (m7+).


***

Shield Transforms:

 * Adjust_Shield_Regen

      Adjust shield regeneration rate by changing efficiency values.


***

Ship Transforms:

 * Add_Ship_Equipment

      Adds equipment as built-in wares for select ship classes.

 * Add_Ship_Life_Support

      Adds life support as a built-in ware for select ship classes. Various mission director scripts with special TP checks will be extended to check for these modified ships, since the mission director does not support built-in wares and requires special code in these cases.

 * Adjust_Ship_Hull

      Adjust ship hull values. When applied to a existing save, ship hulls will not be updated automatically if hulls are increased.  Run the temp.srm.hull.reload.xml script from the XRM hull packs to refill all ships to 100% hull. Alternatively, ship hulls will be updated as ships die and respawn.

 * Adjust_Ship_Laser_Recharge

      Adjust ship laser regeneration rate, either globally or per ship class.

 * Adjust_Ship_Pricing

      Adjust ship pricing, either globally or per ship class.

 * Adjust_Ship_Shield_Regen

      Adjust ship shield regeneration rate, either globally or per ship class. This may have no effect beyond where all ship shields are powered at their individual max rates.

 * Adjust_Ship_Shield_Slots

      Adjust ship shielding by changing shield slot counts. Shield types will remain unchanged, and at least 1 shield slot will be left in place. When applied to an existing save, ship shields will not be updated automatically, as some ships may continue to have excess shields equipped, or ships may lack enough shield inventory to fill up added slots.

 * Adjust_Ship_Speed

      Adjust ship speed and acceleration, globally or per ship class.

 * Boost_Truelight_Seeker_Shield_Reactor (incompatible with: XRM, LU)

      Enhances the Truelight Seeker's shield reactor. In vanilla AP the TLS has a shield reactor only around 1/10 of what is normal for similar ships. This transform sets the TLS shield reactor to be the same as the Centaur. If the TLS is already at least 1/5 of Centaur shielding, this transform is not applied.

 * Fix_Pericles_Pricing (incompatible with: XRM, LU)

      Applies a bug fix to the enhanced pericles in vanilla AP, which has its npc value set to 1/10 of player value, causing its price to be 1/10 what it should be. Does nothing if the existing npc and player prices are matched.

 * Patch_Ship_Variant_Inconsistencies

      Applies some patches to some select inconsistencies in ship variants. Modified ships include the Baldric Miner and XRM Medusa Vanguard, both manually named instead of using the variant system. This is meant to be run prior to Add_Ship_Variants, to avoid the non-standard ships creating their own sub-variants. There may be side effects if the variant inconsistencies were intentional.

 * Remove_Engine_Trails

      Remove engine trail particle effects.

 * Remove_Khaak_Corvette_Spin

      Remove the spin on the secondary hull of the Khaak corvette. The replacement file used is expected to work for vanilla, xrm, and other mods that don't change the model scene file.

 * Simplify_Engine_Trails

      Change engine trail particle effects to basic or none. This will switch to effect 1 for medium and light ships and 0 for heavy ships, as in vanilla AP.  Intended for use primarily with XRM.

 * Standardize_Ship_Tunings

      Standardize max engine or rudder tuning amounts across all ships. Eg. instead of scouts having 25 and carriers having 5 engine runings, both will have some fixed number. Maximum ship speed and turn rate is kept constant, but minimum will change. If applied to an existing save, existing ships may end up overtuned; this is recommended primarily for new games, pending inclusion of a modification script which can recap ships to max tunings. Ships with 0 tunings will remain unedited.


***

Ships_Variant Transforms:

 * Add_Ship_Combat_Variants

      Adds combat variants for combat ships. This is a convenience function which calls Add_Ship_Variants with variants [vanguard, sentinel, raider, hauler], for ship types [M0-M8]. See Add_Ship_Variants documentation for other parameters.

 * Add_Ship_Trade_Variants

      Adds trade variants for trade ships. This is a convenience function which calls Add_Ship_Variants with variants [hauler, miner, tanker (xl), super freighter (xl)], for ship types [TS,TP,TM,TL]. See Add_Ship_Variants documentation for other parameters.    

 * Add_Ship_Variants

      Adds variants for various ships. Variant attribute modifiers are based on the average differences between existing variants and their basic ship, where only M3,M4,M5 are analyzed for combat variants, and only TS,TP are analyzed for trade variants, with Hauler being considered both a combat variant. Variants will be added to existing shipyards the first time a game is loaded after running this transform; this may take several seconds to complete, during which time the game will be unresponsive. Warning: it is unsafe to remove variants once they have been added to an existing save.

 * Remove_Ship_Variants

      Removes variants for selected ships. May be used after Add_Ship_Variants has already been applied to an existing save, to safely remove variants while leaving their tships entries intact. In this case, leave the Add_Ship_Variants call as it was previously with undesired variants, and use this tranform to prune the variants. Existing ships will remain in game, categorized as unknown race, though new ships will not spawn automatically. Variants will be removed from existing shipyards the first time a game is loaded after running this transform. Note: this transform is only lightly tested.


***

Sound Transforms:

 * Remove_Combat_Beep

      Removes the beep that plays when entering combat.

 * Remove_Sound

      Removes a sound by writing an empty file in its place, based on the sound's id.


***

Universe Transforms:

 * Change_Sector_Music

      Generic transform to change the music for a given sector. Currently, this only operates as a director script, and does not alter the universe file. To reverse the change, a new call must be made with a new cue name and the prior music_id.

 * Color_Sector_Names (incompatible with: LU, FL)

      Colors sector names in the map based on race owners declared in the x3_universe file. Some sectors may remain uncolored if their name is not set in the standard way through text files. Only works on the English files, L044, for now. Note: searching sectors by typing a name will no longer work except on uncolored sectors, eg. unknown sectors.

 * Restore_Aldrin_rock (incompatible with: AP, LU, FL)

      Restors the big rock in Aldrin for XRM, reverting to the vanilla sector layout. Note: only works on a new game.

 * Restore_Hub_Music (incompatible with: AP, LU, FL)

      If Hub sector (13,8) music should be restored to that in AP. (XRM sets the track to 0.) Applies to new games, and optionally to an existing save.

 * Restore_M148_Music (incompatible with: AP, LU, FL)

      If Argon Sector M148 (14,8) music should be restored to that in AP. (XRM changes this to the argon prime music.) Applies to new games, and optionally to an existing save.


***

Ware Transforms:

 * Change_Ware_Size

      Change the cargo size of a given ware.

 * Restore_Vanilla_Tuning_Pricing (incompatible with: AP, LU, FL)

      Sets the price for ship tunings (engine, rudder, cargo) to those used in vanilla AP.  Meant for use with XRM.

 * Set_Ware_Pricing

      Sets ware pricing for the given ware list. Prices are the basic values in the T file, and have some adjustment before reaching the game pricing. Currently only works on tech wares in TWareT.txt.


***

Weapons Transforms:

 * Adjust_Beam_Weapon_Duration

      Adjusts the duration of beam weapons. Shot damage will be applied over the duration of the beam, such that shorter beams will apply their damage more quickly. Longer duration beams are weaker against small targets which move out of the beam before its damage is fully applied. Beam range will remain unchanged. Note: this does not affect fire rate, so multiple beams may become active at the same time.

 * Adjust_Beam_Weapon_Width

      Adjusts the width of beam weapons. Narrower beams will have more trouble hitting small targets at a distance. In vanilla AP beam widths are generally set to 1, though in XRM the widths have much wider variety. This can be used to nerf anti-fighter defense of capital ships with beam mounts.

 * Adjust_Weapon_DPS

      Adjust weapon damage/second by changing bullet damage. If a bullet is used by multiple lasers, the first laser will be used for DPS calculation. Energy efficiency will remain constant, changing energy/second.

 * Adjust_Weapon_Energy_Usage

      Adjusts weapon energy usage by the given multiplier, globally or for selected bullets.

 * Adjust_Weapon_Fire_Rate

      Adjust weapon fire rates. DPS and energy efficiency will remain constant. This may be used to reduce fire rates for performance improvements. Secondary weapon effects are not modified. If a bullet is used by multiple lasers, the first adjusted laser (by TLaser order) will be used to set the bullet's damage and energy adjustment.

 * Adjust_Weapon_OOS_Damage

      Scale OOS damage. Damage may be scaled down to improve accuracy in combat evaluation, at the potential drawback of stalemates when shield regeneration outperforms damage.

 * Adjust_Weapon_Range

      Adjusts weapon range by adjusting lifetime or speed. To modify range, consider that range = speed * lifetime. Eg. 1.2 * 1.2 = 44% range increase.

 * Adjust_Weapon_Shot_Speed

      Adjust weapon shot speeds. Range will remain constant. Beam weapons will not be affected.

 * Clear_Weapon_Flag

      Clears a specified flag from all weapons.

 * Convert_Beams_To_Bullets

      Converts beam weapons to bullet weapons, to help with game slowdown when beams are fired at large ships and stations. Bullet speed will be set based on sampling other bullets of similar damage.

 * Convert_Weapon_To_Ammo

      Converts the given weapons, determined by bullet type, to use ammunition instead of energy.

 * Convert_Weapon_To_Energy

      Converts the given weapons, determined by bullet type, to use energy instead of ammunition. Ammo type may support general wares, and will reduce a ware by 1 per 200 shots.

 * Remove_Weapon_Charge_Up

      Remove charge up from all weapons, to make PPCs and similar easier to use in a manner consistent with the npcs (eg. hold trigger to just keep firing), as charging is a player-only option.

 * Remove_Weapon_Drain_Flag

      Removes the weapon drain flag from any weapons. May also stop equipment damage being applied through shielding for these weapons.

 * Remove_Weapon_Shot_Sound

      Removes impact sound from bullets. Little performance benefit expected, though untested.

 * Replace_Weapon_Shot_Effects

      Replaces shot effects to possibly reduce lag. This appears to have little to no benefit in brief testing.

 * Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio

      Increases hull damage on weapons to achieve a specified hull:shield damage ratio requirement. Typical weapons are around a 1/6 ratio, though some weapons can be 1/100 or lower, such as ion weaponry. This transform can be used to give such weapons a viable hull damage amount.


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
 * 3.6
   - Added initial support for Terran Conflict without AP installed.
   - Refined handling obj patches failures, so that all patches for a given transform are skipped if any patch has an error.
   - Increased robustness when Globals.txt does not have an expected field.
 * 3.7
   - Added LU support for Disable_Combat_Music.
   - Swapped _Benchmark_Gate_Traversal_Time to Remove_Complex_Related_Sector_Switch_Delay to make it available for general use, though it is still experimental.
 * 3.8
   - Added support for generating a catalog file collecting all non-script changes.
   - Add_Life_Support now edits various scripts that use special checks for ships with built-in life support (normally TPs only), to support the modified ship classes.
   - Add_Ship_Variants now edits the Bounce mod's wall file, if found, to include entries for the new ships which share a model with an existing ship present in the bounce file.
 * 3.9
   - Added Disable_Docking_Music.
 * 3.10
   - Added Preserve_Captured_Ship_Equipment.
 * 3.11
   - Added Hide_Lasertowers_Outside_Radar.
   - Changed default args for Adjust_Gate_Rings to plain ring for normal gates, reversed hub ring for hub gates.
 * 3.12
   - Added Force_Infinite_Loop_Detection.
 * 3.12.1
   - Added operation_limit argument to Force_Infinite_Loop_Detection and defaulting to 1 million (up from 32k) to reduce false positives.
   - Obj patches now support balanced insertions and deletions.
 * 3.12.2
   - Added better support for launching by double clicking the bat file, along with a little more guidance for new users.
   - Added convenience transform Remove_Engine_Trails.
 * 3.12.3
   - Bug fixes in Adjust_Weapon_Fire_Rate: the fire_rate_floor will no longer be mistakenly applied when increasing fire rate, and setting skip_ammo_weapons to False will now be recognized.
 * 3.12.4
   - Bug fix in Adjust_Weapon_Fire_Rate: fire_rate_floor will no longer speed up named lasers that started below the floor while attempting to reduce their fire rate.
 * 3.13
   - Added Max_Marines_Video_Id_Overwrite.
   - Tentatively added Set_LaserTower_Equipment and Make_Terran_Stations_Make_Terran_Marines.
 * 3.14
   - Added Fix_Corporation_Troubles_Balance_Rollover.
   - Added Fix_Terran_Plot_Aimless_TPs.
   - Added Fix_Dual_Convoy_Invincible_Stations; pending testing.
   - Added Fix_Reset_Invincible_Stations.
 * 3.14.1
   - Fix to Force_Infinite_Loop_Detection to prevent a false positive case.
 * 3.14.2
   - Fix to handle negative numbers for missile flag masks in tships.
 * 3.15
   - Added Prevent_Ship_Equipment_Damage.
 * 3.16
   - Added support for Farnham's Legacy.