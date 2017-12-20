X3 Customizer v2.12
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


Full documentation found in Documentation.md.


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

 * Adjust_Generic_Missions

      Adjust the spawn chance of various generic mission types, relative to each other. Note: decreasing chance on unwanted missions seems to work better than increasing chance on wanted missions.

 * Convoys_made_of_race_ships

      If convoy defense missions should use the convoy's race to select their ship type. The vanilla script uses randomized ship types (eg. a terran convoy flying teladi ships).

 * Standardize_Start_Plot_Overtunings

      Set the starting plots with overtuned ships to have their tunings standardized instead of being random.

 * Standardize_Tunings

      Set the number of randomized tuning creates at gamestart to be de-randomized into a standard number of tunings. Note: vanilla has 2-5 average tunings per crate, 8 crates total. Default args here reach this average, biasing toward engine tunings.


***

Gate Transforms:

 * Adjust_Gate_Rings

      Various options to modify gate rings, with the aim of reducing capital ship suicides when colliding with the pylons shortly after the player enters a sector. Includes ring removal, rotation, reversal, and model swaps. Inactive versions of gates will also be updated for consistency. When applied to an existing save, gate changes will appear on a sector change.


***

Global Transforms:

 * Adjust_Global

      Adjust a global flag by the given multiplier. Generic transform works on any named global field.

 * Adjust_Strafe

      Strafe adjustment factor. Note: this does not appear to have any effect during brief testing.

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

Script Transforms:

 * Add_CLS_Software_To_More_Docks

      Adds Commodity Logistics Software, internal and external, to all equipment docks which stock Trade Command Software Mk2. This is implemented as a setup script which runs on the game loading. Once applied, this transform may be disabled to remove the script run time. This change is not reversable.

 * Add_Script

      Add a script to the addon/scripts folder. If an existing xml version of the script already exists, it is overwritten. If an existing pck version of the script already exists, it is renamed with suffix '.x3c.bak'. Note: this is only for use with full scripts, not those defined by diffs from existing scripts.

 * Convert_Attack_To_Attack_Nearest

      Modifies the Attack command when used on an owned asset to instead enact Attack Nearest. In vanilla AP, such attack commands are quietly ignored. Intended for use when commanding groups, where Attack is available but Attack Nearest is not. This replaces '!ship.cmd.attack.std'.

 * Disable_OOS_War_Sector_Spawns

      Disables spawning of dedicated ships in the AP war sectors which attack player assets when the player is out-of-sector. By default, these ships scale up with player assets, and immediately respawn upon being killed. This patches '!fight.war.protectsector'.


***

Shield Transforms:

 * Adjust_Shield_Regen

      Adjust shield regeneration rate by changing efficiency values.


***

Ship Transforms:

 * Add_Ship_Combat_Variants

      Adds combat variants for combat ships. This is a convenience function which calls Add_Ship_Variants with variants [vanguard, sentinel, raider, hauler], for ship types [M0-M8]. See Add_Ship_Variants documentation for other parameters.

 * Add_Ship_Equipment

      Adds equipment as built-in wares for select ship classes.

 * Add_Ship_Life_Support

      Adds life support as a built-in ware for select ship classes. This is a convenience transform which calls Add_Ship_Equipment. Warning: mission director scripts do not seem to have a way to check for built in wares, and typically use a special TP check to get around this. Other ship types with built-in life support will not be able to pick up passengers in some cases.

 * Add_Ship_Trade_Variants

      Adds trade variants for trade ships. This is a convenience function which calls Add_Ship_Variants with variants [hauler, miner, tanker (xl), super freighter (xl)], for ship types [TS,TP,TM,TL]. See Add_Ship_Variants documentation for other parameters.    

 * Add_Ship_Variants

      Adds variants for various ships. Variant attribute modifiers are based on the average differences between existing variants and their basic ship, where only M3,M4,M5 are analyzed for combat variants, and only TS,TP are analyzed for trade variants, with Hauler being considered both a combat variant. After variants are created, a script may be manually run in game from the script editor which will add variants to all shipyards that sell the base ship. Run 'x3customizer.add.variants.to.shipyards.xml', no input args. Note: this will add all stock variants as well, as it currently has no way to distinguish the new ships from existing ones. Warning: it is unsafe to remove variants once they have been added to an existing save.

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

 * Boost_Truelight_Seeker_Shield_Reactor

      Enhances the Truelight Seeker's shield reactor. In AP the TLS has a shield reactor only around 1/10 what is normal for similar ships; this applies a 10x increase. If the TLS is already at least 1/5 of Centaur shielding, this transform is not applied.

 * Fix_Pericles_Pricing

      Applies a bug fix to the enhanced pericles, which has its npc value set to 1/10 of player value, causing it price to be 1/10 what it should be. Does nothing if the existing npc and player prices are matched.

 * Patch_Ship_Variant_Inconsistencies

      Applies some patches to some select inconsistencies in ship variants. Modified ships include the Baldric Miner and XRM Medusa Vanguard, both manually named instead of using the variant system. This is meant to be run prior to Add_Ship_Variants, to avoid the non-standard ships creating their own sub-variants. There may be side effects if the variant inconsistencies were intentional.

 * Remove_Khaak_Corvette_Spin

      Remove the spin on the secondary hull of the Khaak corvette. The replacement file used is expected to work for vanilla, xrm, and other mods that don't change the model scene file.

 * Simplify_Engine_Trails

      Change engine trail particle effects to basic or none. This will switch to effect 1 for medium and light ships and 0 for heavy ships, as in vanilla AP.

 * Standardize_Ship_Tunings

      Standardize max engine or rudder tuning amounts across all ships. Eg. instead of scouts having 25 and carriers having 5 engine runings, both will have some fixed number. Maximum ship speed and turn rate is kept constant, but minimum will change. If applied to an existing save, existing ships may end up overtuned; this is recommended primarily for new games, pending inclusion of a modification script which can recap ships to max tunings. Ships with 0 tunings will remain unedited.


***

Universe Transforms:

 * Color_Sector_Names

      Colors sector names in the map based on race owners declared in the x3_universe file. Some sectors may remain uncolored if their name is not set in the standard way through text files. Only works on the English files, L044, for now. Note: searching sectors by typing a name will no longer work except on uncolored sectors, eg. unknown sectors.

 * Restore_Aldrin_rock

      Restors the big rock in Aldrin for XRM, reverting to the vanilla sector layout. Note: only works on a new game.

 * Restore_Hub_Music

      If Hub sector (13,8) music should be restored to that in AP. (XRM sets the track to 0.) Applies to new games, and optionally to an existing save.

 * Restore_M148_Music

      If Argon Sector M148 (14,8) music should be restored to that in AP. (XRM changes this to the argon prime music.) Applies to new games, and optionally to an existing save.


***

Ware Transforms:

 * Change_Ware_Size

      Change the cargo size of a given ware.

 * Restore_Vanilla_Tuning_Pricing

      Sets the price for ship tunings (engine, rudder, cargo) to those used in vanilla AP.

 * Set_Ware_Pricing

      Sets ware pricing for the given ware list. Prices are the basic values in the T file, and have some adjustment before reaching the game pricing. Currently only works on tech wares in TWareT.txt.


***

Weapon Transforms:

 * Adjust_Beam_Weapon_Duration

      Adjusts the duration of beam weapons. Shot damage will be applied over the duration of the beam, such that shorter beams will apply their damage more quickly. Longer duration beams are weaker against small targets which move out of the beam before its damage is fully applied. Beam range will remain unchanged. Note: this does not affect fire rate, so multiple beams may become active at the same time.

 * Adjust_Beam_Weapon_Width

      Adjusts the width of beam weapons. Narrower beams will have more trouble hitting small targets at a distance. In vanilla AP beam widths are generally set to 1, though in XRM the widths have much wider variety. This can be used to nerf anti-fighter defense of capital ships with beam mounts.

 * Adjust_Weapon_DPS

      Adjust weapon damage/second by changing bullet damage. If a bullet is used by multiple lasers, the first laser will be used for DPS calculation. Energy efficiency will remain constant, changing energy/second.

 * Adjust_Weapon_Energy_Usage

      Adjusts weapon energy usage by the given multiplier, globally or for selected bullets.

 * Adjust_Weapon_Fire_Rate

      Adjust weapon fire rates. DPS and energy efficiency will remain constant. This may be used to reduce fire rates for performance improvements. Secondary weapon effects are not modified. If a bullet is used by multiple lasers, the first laser will be used for fire rate damage and energy adjustment.

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
 * 2.07:
   - Minor tweak to Add_Ship_Variants, allowing selection of which variant will be set to 0 when an existing variant is used as a base ship.
   - Adjust_Missile_Damage has new parameters to scale missile ware volume and price in line with the damage adjustment.
 * 2.08:
   - Added Adjust_Gate_Rings.
   - Removed Swap_Standard_Gates_To_Terran_Gates, which is replaced by an option in the new transform.
 * 2.09:
   - Added Add_Job_Ship_Variants.
   - Added Change_Ware_Size.
   - Tweaked Add_Ship_Variants to specify shield_conversion_ratios in args.
   - Unedited source files will now be copied to the main directory, in case a prior run did edit them and needs overwriting.
 * 2.10:
   - New option added to Adjust_Gate_Rings, supporting a protrusionless ring.
   - Added Add_Script, generic transform to add pregenerated scripts.
   - Added Disable_OOS_War_Sector_Spawns.
   - Added Convert_Attack_To_Attack_Nearest.
   - Bugfix for when the first transform called does not have file dependencies.
   - Renames the script 'a.x3customizer.add.variants.to.shipyards.xml' to remove the 'a.' prefix.
 * 2.11:
   - Minor fix to rename .pck files in the addon/types folder that interfere with customized files.
 * 2.12:
   - Added Add_CLS_Software_To_More_Docks.
   - Added Remove_Khaak_Corvette_Spin.
   - Added option to Adjust_Ship_Laser_Recharge to adjust ship maximum laser energy as well.
   - Added cap on mosquito missile damage when adjusting damages, to avoid possible OOS combat usage.
   - Bugfix for transforms which adjust laser energy usage, to ensure the laser can store enough charge for at least one shot.
   - Bugfix for adjusting missile hulls, to add entries to globals when missing.
   - Bugfix for file reading which broke in recent python update.
   - Added patch support for editing files without doing full original source uploads. Disable_OOS_War_Sector_Spawns now uses a patch.
   - Added support for automatically filling in the source folder with any necessary scripts.