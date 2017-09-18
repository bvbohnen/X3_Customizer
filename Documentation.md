
X3 Customizer v2.0
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

***

Setup methods:

  * Set_Path
   
       Sets the pathing to be used for file loading and writing.
   
       path_to_addon_folder:
           Path to the X3 AP addon folder, containing the source_folder.
           Output files will be written relative to here.
           If this is not the addon folder, a warning will be printed but
           operation will continue, writing files to this folder, though
           files will need to be moved to the proper addon folder to be
           applied to the game. Some generated files may be placed in
           the directory above this folder, eg. the expected TC directory.
   
       source_folder:
           Subfolder in the addon directory containing unmodified files, 
           internally having the same folder structure as addon to be
           used when writing out transform results.
           (eg. output to addon	ypes will source from input in
            addon\source_folder	ypes).
       


***

Transform List:

 * Adjust_Beam_Weapon_Duration
  
    Requires: TBullets.txt
  
      Adjusts the duration of beam weapons.
      Shot damage will be applied over the duration of the beam, such that
       shorter beams will apply their damage more quickly. 
      Longer duration beams are weaker against small targets which move out 
       of the beam before its damage is fully applied.
      Beam range will remain unchanged.
      Note: this does not affect fire rate, so multiple beams may become
       active at the same time.
  
      bullet_name_adjustment_dict:
          Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to
          apply, as a tuple of (min, factor, max), where min and max are
          given in seconds.
          None may be entered for min or max to disable those limits.
          '*' entry will match all beam weapons not otherwise named.
      

 * Adjust_Beam_Weapon_Width
  
    Requires: TBullets.txt
  
      Adjusts the width of beam weapons. Narrower beams will have more 
      trouble hitting small targets at a distance.
      In vanilla AP beam widths are generally set to 1, though in XRM the
      widths have much wider variety. This can be used to nerf anti-fighter
      defense of capital ships with beam mounts.
  
      bullet_name_adjustment_dict:
          Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to
          apply, as a tuple of (min, factor, max), applied to height and width.
          None may be entered for min or max to disable those limits.
          '*' entry will match all beam weapons not otherwise named.
      

 * Adjust_Fade_Start_End_Gap
  
    Requires: TBackgrounds.txt
  
      Adjust the gap between the start and end fade distance, changing how
      quickly objects will fade in.
      This will never affect fade_start, only fade_end.
  
      fade_gap_min_func, fade_gap_max_func:
          Functions which take fade_start as the argument, in km, and return
          the min and max gap allowed.
          Example: 
              Set fade gap to be as much as fade start:
                  fade_gap_min_func = lambda start: start*1
              Require the fade gap be no longer than 20 km:
                  fade_gap_max_func = lambda start: 20
      

 * Adjust_Global
  
    Requires: Globals.txt
  
      Adjust a global flag by the given multiplier.
      Generic transform works on any named global field.
      

 * Adjust_Job_Count
  
    Requires: Jobs.txt
  
      Adjusts job counts using a multiplier.
      These will always have a minimum of 1.
       new_count = max(1, old_counter * factor)
  
      job_count_factors:
          List of tuples pairing an identifier key with the adjustment value to apply.
          The first match will be used.
          Key will try to match an boolean field in the jobs file (see File_Fields
          for field names), or failing that will try to do a job name match (partial
          match supported) based on the name in the jobs file.
          '*' will match all jobs not otherwise matched.
      

 * Adjust_Job_Respawn_Time
  
    Requires: Jobs.txt
  
      Adjusts job respawn times, using an adder and multiplier on
       the existing respawn time.
          new_time = old_time * multiplier + adder
  
      time_adder_list, time_multiplier_list:
          Lists of tuples pairing an identifier key with the adjustment value to apply.
          The first match will be used.
          Key will try to match an boolean field in the jobs file (see File_Fields
          for field names), or failing that will try to do a job name match (partial
          match supported) based on the name in the jobs file.
          '*' will match all jobs not otherwise matched.
      

 * Adjust_Missile_Damage
  
    Requires: Globals.txt, TMissiles.txt
  
      Adjust missile damage values.
      The scaling_factor is applied prior to the diminishing returns
       formula.
  
      use_diminishing_returns:
          If True, a hardcoded diminishing returns formula is applied 
          which reduces heavy missile damage by up to ~80%,
          while keeping small missiles unchanged.
      print_changes:
          If True, speed adjustments are printed to the summary file.
      

 * Adjust_Missile_Hulls
  
    Requires: Globals.txt
  
      Adjust the hull value for all missiles by the scaling factor.
      Does not affect boarding pod hulls.
      

 * Adjust_Missile_Range
  
    Requires: TMissiles.txt
  
      Adjust missile range/lifetime.
      This is particularly effective for the re-lock missiles like flail,
       to reduce their ability to just keep retargetting across a system,
       instead running out of fuel from the zigzagging.
  
      If use_diminishing_returns == True, this will attempt to adjust
       missiles with a range near target_range_to_adjust_km by the scaling_factor,
       while missiles with a range near range_to_keep_static_km will be
       kept largely unchanged.
       Otherwise, scaling_factor is applied to all missiles.
      target_range_to_adjust_km, range_to_keep_static_km:
          Equation tuning values, in kilometers.
      print_changes:
          If True, speed adjustments are printed to the summary file.
      

 * Adjust_Missile_Speed
  
    Requires: TMissiles.txt
  
      Adjust missile speeds.
  
      If use_diminishing_returns == True, this will attempt to adjust
       missiles with a speed near target_speed_to_adjust by the scaling_factor,
       while missiles with a speed near speed_to_keep_static will be
       kept largely unchanged.
       Otherwise, scaling_factor is applied to all missiles.
      target_speed_to_adjust, speed_to_keep_static:
          Equation tuning values, in m/s.
      print_changes:
          If True, speed adjustments are printed to the summary file.
      

 * Adjust_Particle_Count
  
    Requires: TBackgrounds.txt
  
      Change the number of particles floating in space around the camera.
      Default game is 100, mods often set to 0, but can keep some small number
       for a feeling of speed.
  
      base_count:
          The base number of particles to use in all sectors.
          Default is 10, or 10% of the vanilla particle count.
      fog_factor:
          The portion of sector fog to add as additional particles.
          Eg. a fog factor of 0.5 will add 25 more particles in heavy fog.
      

 * Adjust_Ship_Hull
  
    Requires: TShips.txt
  
      Adjust ship hull values. When applied to a existing save, ship hulls will
      not be updated automatically if hulls are increased.  Run the 
      temp.srm.hull.reload.xml script from the XRM hull packs to refill all 
      ships to 100% hull. Alternatively, ship hulls will be updated as 
      ships die and respawn.
  
      scaling_factor:
          Multiplier to apply to any ship type not found in adjustment_factors_dict.
      adjustment_factors_dict:
          Dict keyed by ship type, holding a scaling factor to be applied.
      

 * Adjust_Ship_Laser_Recharge
  
    Requires: TShips.txt
  
      Adjust ship laser regeneration rate.
      
      scaling_factor:
          Multiplier to apply to any ship type not found in adjustment_factors_dict.
      adjustment_factors_dict:
          Dict keyed by ship type, holding a scaling factor to be applied.
      

 * Adjust_Ship_Pricing
  
    Requires: TShips.txt
  
      Adjust ship pricing.
  
      The adjustment_factors_dict is a dict keyed by ship type, holding a scaling
       factor to be applied.
      The flat scaling_factor will be applied to any ship type not found in
       adjustment_factors_dict.
      

 * Adjust_Ship_Shield_Regen
  
    Requires: TShips.txt
  
      Adjust ship shield regeneration rate.
      
      scaling_factor:
          Multiplier to apply to all ship types on top of those present
          in adjustment_factors_dict.
      adjustment_factors_dict:
          Dict keyed by ship type, holding a  tuple of 
          (targeted_recharge_rate, reduction_factor, max_rate)
          where any recharges above targeted_recharge_rate will have the 
          reduction_factor applied to the difference in original and target 
          rates. Recharge rates will be capped at max_rate.
      

 * Adjust_Ship_Shield_Slots
  
    Requires: TShips.txt
  
      Adjust ship shielding by changing shield slot counts.
      Shield types will remain unchanged, and at least 1 shield slot will
       be left in place.
      When applied to an existing save, ship shields will not be updated
       automatically, as some ships may continue to have excess shields
       equipped, or ships may lack enough shield inventory to fill
       up added slots.
      
      The adjustment_factors_dict is a dict keyed by ship type, holding a
       tuple of (targeted_total_shielding, reduction_factor), where any ships 
       with shield above targeted_total_shielding will have reduction_factor
       applied to their shield amount above the target.
      

 * Adjust_Ship_Speed
  
    Requires: TShips.txt
  
      Adjust ship speeds. Does not affect acceleration.
      
      scaling_factor:
          Multiplier to apply to any ship type not found in adjustment_factors_dict.
      adjustment_factors_dict:
          Dict keyed by ship type, holding a scaling factor to be applied.
      

 * Adjust_Strafe
  
    Requires: Globals.txt
  
      Strafe adjustment factor.
      Note: this does not appear to have any effect.
      
      small_ship_factor:
          Multiplier on small ship strafe.
      big_ship_factor:
          Multiplier on big ship strafe.
      

 * Adjust_Weapon_DPS
  
    Requires: TBullets.txt, TLaser.txt
  
      Adjust weapon damage/second by changing bullet damage.
      If a bullet is used by multiple lasers, the first laser will
      be used for DPS calculation.
      Energy efficiency will remain constant, changing energy/second.
  
      scaling_factor:
          The base multiplier to apply to shot speeds.
      use_scaling_equation:
          If True, a scaling formula will be applied, such
          that shots near damage_to_adjust_kdps see the full scaling_factor,
          and shots near damage_to_keep_static_kdps remain largely unchanged.
      damage_to_adjust_kdps, damage_to_keep_static_kdps:
          Equation tuning values, in units of kdps, eg. 1 for 1000 damage/second.
          Scaling values are for shield DPS; hull DPS will be scaled at a
          rate of 1/6 of shield DPS.
      bullet_name_adjustment_dict:
          Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with the
          multiplier to apply. This also supports matching to bullet
          flags using a 'flag_' prefix, eg. 'flag_beam' will match
          to beam weapons. Flag matches are lower priority than
          name matches.
          If multiple flag matches are found, the first flag will
          be used if the input is an OrderedDict, otherwise any
          Python default is used (likely equivelent to ordereddict
          in Python 3.6).
          '*' entry will match all weapons not otherwise matched,
          equivelent to setting scaling_factor and not using the
          scaling equation.
      print_changes:
          If True, speed adjustments are printed to the summary file.  
      

 * Adjust_Weapon_Energy_Usage
  
    Requires: TBullets.txt
  
      Adjusts weapon energy usage by the given multiplier.
  
      scaling_factor:
          Multiplier to apply to all weapons without specific settings.
      bullet_name_energy_dict:
          Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the
          multiplier to apply. This will override scaling_factor for
          this weapon.
      

 * Adjust_Weapon_Fire_Rate
  
    Requires: TBullets.txt, TLaser.txt
  
      Adjust weapon fire rates. DPS and energy efficiency will remain constant.
      This may be used to reduce fire rates for performance improvements.
      Fire rate changes will apply to IS damage only; OOS does not use fire rate.
      Secondary weapon effects are not modified.
      If a bullet is used by multiple lasers, the first laser will
       be used for fire rate damage and energy adjustment.
  
      scaling_factor:
          The base multiplier to apply to fire rate.
      laser_name_adjustment_dict:
          Dict, keyed by laser name (eg. 'SS_LASER_HEPT'), with the
          multiplier to apply instead of using the scaling_factor.     
      fire_rate_floor:
          Int, the floor below which fire rate will not be reduced, 
          in shots per minute. Eg. 60 for 1/second.
      skip_ammo_weapons:
          If True, the fire rate change will ignore ammo weapons, since there is 
          no good way to adjust ammo consumption.
      

 * Adjust_Weapon_OOS_Damage
  
    Requires: TBullets.txt, TLaser.txt
  
      Scale OOS damage. Damage may be scaled down to improve accuracy in
       combat evaluation, at the potential drawback of stalemates when shield
       regeneration outperforms damage.
  
      scaling_factor:
          The base multiplier to apply to OOS damage.
      

 * Adjust_Weapon_Range
  
    Requires: TBullets.txt
  
      Adjusts weapon range by adjusting lifetime or speed.
      To modify range, consider that range = speed * lifetime.
       Eg. 1.2 * 1.2 = 44% range increase.
  
      lifetime_scaling_factor:
          Multiplier to apply to all bullet lifetimes.
      speed_scaling_factor:
          Multiplier to apply to all bullet speeds.
      

 * Adjust_Weapon_Shot_Speed
  
    Requires: TBullets.txt
  
      Adjust weapon shot speeds. Range will remain constant.
      Beam weapons will not be affected.
  
      scaling_factor:
          The base multiplier to apply to shot speeds.
      use_scaling_equation:
          If True, a scaling formula will be applied, such
          that shots near target_speed_to_adjust see the full scaling_factor,
          and shots near speed_to_keep_static remain largely unchanged.
      target_speed_to_adjust, speed_to_keep_static:
          Equation tuning values, in meters/second.
      bullet_name_adjustment_dict:
          Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with the
          multiplier to apply.
          '*' entry will match all weapons not otherwise named,
          equivelent to setting scaling_factor and not using the
          scaling equation.
      skip_areal:
          If True, areal weapons (eg. PD and PSG) are skipped, since their
          damage delivery may be partially dependent on shot speed.
      skip_flak: 
          If True, flak weapons are skipped.
      print_changes:
          If True, speed adjustments are printed to the summary file.
      

 * Boost_Truelight_Seeker_Shield_Reactor
  
    Requires: TShips.txt
  
      Enhances the Truelight Seeker's shield reactor.
      In AP the TLS has a shield reactor only around 1/10 what is normal 
       for similar ships; this applies a 10x increase.
      If the TLS is already at least 1/5 of Centaur shielding, this
       transform is not applied.
      

 * Clear_Weapon_Flag
  
    Requires: TBullets.txt
  
      Clears the specified flag from all weapons.
      

 * Color_Sector_Names
  
    Requires: x3_universe.xml, 0001-L044.xml, 7027-L044.xml, 7360-L044.xml
  
      Colors sector names in the map based on race owners declared
      in the x3_universe file. Some sectors may remain uncolored if
      their name is not set in the standard way through text files.
      Only works on the English files, L044, for now.
      Note: searching sectors by typing a name will no longer work
       except on uncolored sectors, eg. unknown sectors.
  
      race_color_letters:
          Dict matching race id to the color code to be used.
          Default is filled out similar to the standalone colored sectors mod.
      

 * Convert_Weapon_To_Ammo
  
    Requires: TBullets.txt
  
      Converts the given weapons, determined by bullet type, to use ammo
      instead of ammunition.
  
      bullet_name_energy_dict:
          Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the ammo
          type to use in the replacement.
          Ammo type is given by a ware id value, or by a preconfigured string
          name.
          Currently supported ammo names:
              'Mass Driver Ammunition'
      energy_reduction_factor:
          Multiplier on existing weapon energy, such that after ammo conversion
          the weapon will still use a small energy amount.
          Default will cut energy use by 90%, which is roughly the Vanilla 
          difference between MD and PAC energy.
      

 * Convert_Weapon_To_Energy
  
    Requires: TBullets.txt
  
      Converts the given weapons, determined by bullet type, to use energy
      instead of ammunition. Ammo type may support general wares, and
      will reduce a ware by 1 per 200 shots.
  
      bullet_name_energy_dict:
          Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the energy
          value to use in the replacement.
      

 * Convoys_made_of_race_ships
  
    Requires: 2.119 Trade Convoy.xml
  
      If convoy defense missions should use the convoy's race to select their ship type.
      The vanilla script uses randomized ship types (eg. a terran convoy flying teladi ships).
      

 * Enhance_Mosquito_Missiles
  
    Requires: TMissiles.txt
  
      Makes mosquito missiles more maneuverable, generally by doubling
      the turn rate, to make anti-missile abilities more reliable.
      

 * Fix_Pericles_Pricing
  
    Requires: TShips.txt
  
      Applies a bug fix to the enhanced pericles, which has its
       npc value set to 1/10 of player value, causing it price to be 1/10
       what it should be.
      Does nothing if the existing npc and player prices are matched.
      

 * Remove_Stars_From_Foggy_Sectors
  
    Requires: TBackgrounds.txt
  
      Removes star backgrounds from sectors with significant fog and short fade
      distance. Fogged sectors sharing a background with an unfogged sector will
      not be modified, as the background needs to be edited for all sectors
      which use it. Fade is removed from sectors which will not have their
      stars removed.
      
      fog_requirement:
          The fog requirement for star removal; all backgrounds affected need a
           fog above this much.
          This is not as important as fade distance in general, it seems.
           Set to 12, which is used by a background that shares images with the
            background used by Maelstrom, which should be faded.
      fade_distance_requirement_km:
          The highest fade distance to allow; all backgrounds affected need a
           fade_start under this value (to prevent star removal in high visibility
           sectors). In km.
      

 * Remove_Weapon_Charge_Up
  
    Requires: TBullets.txt
  
      Remove charge up from all weapons, to make PPCs and similar easier to use in
       a manner consistent with the npcs (eg. hold trigger to just keep firing), as
       charging is a player-only option.
      

 * Remove_Weapon_Drain_Flag
  
    Requires: TBullets.txt
  
      Removes the weapon drain flag from any weapons.
      May also stop equipment damage being applied through shielding
      for these weapons. Note: not yet verified.
      

 * Remove_Weapon_Shot_Sound
  
    Requires: TBullets.txt
  
      Removes impact sound from bullets.
      Little performance benefit expected, though untested.
      

 * Replace_Weapon_Shot_Effects
  
    Requires: TBullets.txt
  
      Replaces shot effects to possibly reduce lag.
      This appears to have little to no benefit in brief testing.
  
      impact_replacement:
          Int, the effect to use for impacts. Eg. 19 for mass driver effect.
          Avoid using 0, else sticky white lights have been observed.
      launch_replacement:
          Int, the effect to use for weapon launch.
      

 * Restore_Aldrin_rock
  
    Requires: x3_universe.xml
  
      Restors the big rock in Aldrin for XRM, reverting to the vanilla
      sector layout.
      Note: only works on a new game.
      

 * Restore_Hub_Music
  
    Requires: x3_universe.xml
  
      If Hub music should be restored (XRM breaks it by setting the track to 0).
      Note: editing x3_universe only works on a new game.
  
      apply_to_existing_save:
       If True, makes a drop-in director script that will fire once
       and change the music for an existing save game.
      

 * Restore_M148_Music
  
    Requires: x3_universe.xml
  
      If Argon Sector M148 music should be restored to that in AP.
       (XRM changes this to the argon prime music.)
      Note: editing x3_universe only works on a new game.
  
      apply_to_existing_save:
       If True, makes a drop-in director script that will fire once
       and change the music for an existing save game.
      

 * Restore_Vanilla_Tuning_Pricing
  
    Requires: TWareT.txt
  
      Sets the price for ship tunings (engine, rudder, cargo) to those
      used in vanilla AP.
      

 * Restore_heavy_missile_trail
  
    Requires: TMissiles.txt
  
      Minor transform to set heavy missile trails to those in vanilla AP.
      

 * Set_Communication_Distance
  
    Requires: Globals.txt
  
      Set max distance for opening communications with factories and ships.
      

 * Set_Complex_Connection_Distance
  
    Requires: Globals.txt
  
      Set max range between factories in a complex.
      With complex cleaner and tubeless complexes, this can practically be anything, 
       particularly useful when connecting up distant asteroids.
      

 * Set_Dock_Storage_Capacity
  
    Requires: Globals.txt
  
      Change the capacity of storage docks: equipment docks, trading posts, etc.
  
      player_factor:
          Multiplier for player docks. Vanilla default is 3.
      npc_factor:
          Multiplier for npc docks. Vanilla default is 1.
      hub_factor:
          Multiplier for the Hub. Vanilla default is 6.
      

 * Set_Global
  
    Requires: Globals.txt
  
      Set a global flag to the given value.
      Generic transform works on any named global field.
      

 * Set_Minimum_Fade_Distance
  
    Requires: TBackgrounds.txt
  
      Sets a floor to fade distance, so that object do not appear
       too closely. May be useful in some sectors with really short view
       distances, though may also want to keep those for variety.
      Note: max fade distance will be set to minimum fade distance if
       it would otherwise be lower. Recommend following this with a
       call to Adjust_Fade_Start_End_Gap.
  
      distance_in_km : 
          Minimum fade distance, in km.
      

 * Set_Missile_Swarm_Count
  
    Requires: Globals.txt, TMissiles.txt
  
      Set the number of submissiles fired by swarm missiles.
      Submissile damage is adjusted accordingly to maintain overall damage.
      

 * Set_Ware_Pricing
  
    Requires: TWareT.txt
  
      Sets ware pricing for the given ware list. Prices are the basic
      values in the T file, and have some adjustment before reaching
      the game pricing.
      Currently only works on tech wares in TWareT.txt.
  
      name_price_dict:
          Dict keyed by ware name (eg. SS_WARE_TECH213), holding the
          flat value to apply for its T file price.
      name_price_factor_dict:
          As above, except holding a multiplier to apply to the existing
          price for the ware.
          Applies after name_price_dict if an item is in both dicts.
      

 * Simplify_Engine_Trails
  
    Requires: TShips.txt
  
      Change engine trail particle effects to basic or none.
      This will switch to effect 1 for medium and light ships 
       and 0 for heavy ships, as in vanilla AP.
  
      remove_trails:
          If True, this will remove trails from all ships.
      

 * Standardize_Start_Plot_Overtunings
  
    Requires: 3.05 Gamestart Missions.xml
  
      Set the starting plots with overtuned ships to have their tunings
       standardized instead of being random.
  
      fraction_of_max:
          Float, typically between 0 and 1, the fraction of the max overtuning
          to use. A value of 0 will remove overtunings, and 1 will give max 
          overtuning that is available in vanilla.
          Default of 0.7 is set to mimic moderate game reloading results.
      

 * Standardize_Tunings
  
    Requires: 3.08 Sector Management.xml
  
      If the number of randomized tuning creates at gamestart should be
       de-randomized into a standard number of tunings.
      Note: vanilla has 3.5 average tunings per crate, 8 crates total.
      Default args here reach this average, biasing slightly toward engine tunings.
  
      enging_tuning_crates:
          Int, the number of engine tuning crates to spawn.
      rudder_tuning_crates:
          Int, the number of rudder tuning crates to spawn.
      engine_tunings_per_crate:
          Int, the number of tunings in each engine crate.
      rudder_tunings_per_crate:
          Int, the number of tunings in each rudder crate.
  
      

 * Swap_Standard_Gates_To_Terran_Gates
  
    Requires: TGates.txt
  
      Changes standard gates into Terran gates, possibly helping reduce
      large ship suicides when entering a system.
      


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

Copyright (c) 2016,2017 Brent Vince Bohnenstiehl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.