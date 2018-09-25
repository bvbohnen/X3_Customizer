'''
Notes:
-Vanilla game OOS damage values appear to assume fire rate applies OOS.
-In game testing makes it seem like fire rate does not apply OOS.
 Simple test:
    Setup: 1 PPC vs. 1 PSP attacking a factory (Xenon Station in this case).
    Reasoning: PSP OOS damage is ~5x that of PPC, and IS fire rate is ~1/7,
     so if fire rate is used OOS, the damage rate should be about equal, otherwise
     very unequal.
    Measurement: Pull up info on the factory, watch shield percentage across
     30 second OOS damage ticks.
    Result: PSP does ~10% shield damage per 30s, PPC does ~2% shield damage.
    Conclusion: Fire rate is ignored OOS, even though damage values depend on
     it being used for weapons to be balanced.
Update:
-Testing more directly, by changing fire rate on lasers by an 10-50x, shows that
 fire rate is accounted for, with the higher rate doing more damage.
-Above observations are not explained, though may be due to variance if the game
 considered the PPC test to have missed much more often than the PSP test.


-IS, lag appears to be related to collision detection between many bullets and
 ships with large amounts of geometry.
 Example: fighters attacking a capital ship causes a slide show.
-Simplest way to partially help with this is to reduce weapon fire rates, which
 decreases the number of bullets that need to be collision checked.
 Weapon damage, energy usage, and energy drain are increased accordingly.

-OOS combat has poor resolution (eg. the 30 second rounds) by default, causing poor
 modeling where often the first ship to attack will win a fight, and groups of ships
 are not able to react together as the first ship engaged is often destroyed before
 its supporters are allowed a turn.
--The only fix for this is to (greatly) reduce OOS damage values, such that more turns
 are needed to complete a combat. Even a few turns will give much better results than
 the common 1-turn combat in vanilla. Note this may cause some oddities with shield regen
 being proportionally stronger.

-Added option to disable fire rate changes on ammo based weapons, since there is no good way to
adjust ammo consumption.
-Added option to adjust bullet lifetime and speed. Speed*lifetime = range.

TODO: maybe add options to change sound on the EMPC and PSG, which have the bothersome delayed
 hull thunk sound. Can also change this in the source tbullets file.


Notes on XRM:
Some weapons appear heavily nerfed (eg. hept doing 1/3 damage), causing 
 combat to sometimes feel too slow to break shields and hull.
Many weapon shots were sped up, eg. 2x speed for PAC, which has some negative
 effects with fighters being too easy to shoot down (scouts especially get hit hard).
These together can lead to gameplay that is much less 'dodging big dangerous hits' 
 and more 'ships plinking at each other until one dies'.

To return the excitement of AP, weapons will need to have their damage returned,
 and their speed reduced.
Unfortunately, the XRM changes cannot be directly rolled back, since it also flattens
 a lot of weapons to the same general performance as a byproduct of shoehorning ships
 into a narrow selection of race affiliated lasers (which then need to be balanced
 across races, and hence against each other).
Undoing weapon flattening is likely too much effort for now, since it would require opening
 back up ship laser options (and in their turrets, found in tcockpits), though that
 may be doable with some effort if enabling weapons based on a mix of ship class
 and race.
Since XRM also sped up fighters (though not nearly as much as shot speed), shot speed
 shouldn't be dialed back too much without also slowing fighters, since there is
 a danger of fighters being harder to hit than vanilla.
Take this into consideration dps changes if modifying ship hulls as well; without
 increasing dps, hulls shouldn't be upped too much.

For XRM OOS combat, the heavily nerfed values exist for various weapons. Eg:
    Vanilla pac does 460 OOS shield damage, XRM pac does 106, a 4.3x difference.
    Vanilla ppc does 13698 OOS shield damage, XRM ppc does 3048, a 4.4x difference.
This problem is made worse by many ships having increased shield regeneration, such as
 small transports with 10x the shield regen, destroyers with 3x shield regen, or
 orbital weapons platforms with 10x shield regen.
The effect is that OOS combat often stalemates with ships unable to kill each other,
 such as pirates being stuck attacking a transport (which circles in place since
 under attack), or a xenon capital ship stuck attacking a OWP.
Fixing this requires bringing up OOS damage values in general (contrary to the
 general reduction used in the vanilla game), and also preferably reducing ship
 shield regen values.
At this time, it doesn't look like factories need any adjustment.

'''
from ... import File_Manager
from ...Common import Flags
from .Shared import *

@File_Manager.Transform_Wrapper('types/TBullets.txt', 'types/TLaser.txt')
def Adjust_Weapon_Fire_Rate(
    scaling_factor = 1,
    laser_name_adjustment_dict = {},
    fire_rate_floor = 40,
    # If the fire rate change should ignore ammo weapons, since there is no good way
    #  to adjust ammo consumption, leaving them buffed as a result of changes.
    skip_ammo_weapons = True,
    ):
    '''
    Adjust weapon fire rates. DPS and energy efficiency will remain constant.
    This may be used to reduce fire rates for performance improvements.
    Secondary weapon effects are not modified.
    If a bullet is used by multiple lasers, the first adjusted laser
    (by TLaser order) will be used to set the bullet's damage and energy
    adjustment.

    * scaling_factor:
      - The base multiplier to apply to fire rate.
    * laser_name_adjustment_dict:
      - Dict, keyed by laser name (eg. 'SS_LASER_HEPT'), with the
        multiplier to apply instead of using the scaling_factor.     
    * fire_rate_floor:
      - Int, the floor below which fire rate will not be reduced, 
        in shots per minute. Eg. 60 for 1/second.
    * skip_ammo_weapons:
      - If True, the fire rate change will ignore ammo weapons, since there is 
        no good way to adjust ammo consumption.
    '''
    # Add the ignored entries if not present.
    for name in Ignored_lasers_and_bullets:
        if name not in laser_name_adjustment_dict:
            laser_name_adjustment_dict[name] = 1

    # TODO: adjust secondary effects: energy drain, etc.
    # -Would need to know what 'damage over time - energy' does, since in testing it does
    #  not affect target laser energy at all.
    tbullets_dict_list = File_Manager.Load_File('types/TBullets.txt')
        
    # Start by building a list of bullets that use ammo, by index.
    # Used mainly to speed up checking for lasers than use ammo bullets.
    ammo_based_bullet_list = []
    # Loop over all bullets.
    for index, this_dict in enumerate(tbullets_dict_list):
        # Unpack the flags.
        flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)
        # If an ammo user, record its name.
        if flags_dict['use_ammo']:
            ammo_based_bullet_list.append(index)
        
    # Set up a dict which tracks modified bullets, to prevent a bullet
    #  being modded more than once by different lasers.
    bullet_indices_seen_list = []
    # TODO: update this code to make use of Bullet_to_laser_dict, since
    #  there is some redundancy now.

    # Step through each laser.
    for this_dict in File_Manager.Load_File('types/TLaser.txt'):

        # Grab the fire delay, in milliseconds.
        this_fire_delay = int(this_dict['fire_delay'])

        # Determine fire rate, per min.
        this_fire_rate = Flags.Game_Ticks_Per_Minute / this_fire_delay

        # Skip lasers that use ammo.
        if skip_ammo_weapons and int(this_dict['bullet']) in ammo_based_bullet_list:
            continue

        # Determine the fire rate adjustment, from dict or generic scaling.
        if this_dict['name'] in laser_name_adjustment_dict:
            this_scaling_factor = laser_name_adjustment_dict[this_dict['name']]
        else:
            this_scaling_factor = scaling_factor

        # If the scaling is just 1x, don't need to continue.
        if scaling_factor == 1:
            continue
        
        # No changes if fire rate already below the floor, when scaling
        #  is <1.  Do not do this check when speeding up weapons, eg.
        #  for LU where nearly all weapons are already slower than the
        #  default floor of 60.
        if this_scaling_factor <= 1 and this_fire_rate < fire_rate_floor:
            continue

        # Apply change factor.  TODO: maybe support diminishing returns.
        this_fire_rate *= this_scaling_factor

        # Apply the floor. Eg. if the fire rate fell below 60 and the floor
        #  is 60, use the floor.
        # Only apply this when reducing fire rates, as above.
        # Cases where the weapon was originally above the floor were
        #  already skipped (to avoid already slow weapons from getting
        #  sped up accidentally).
        if this_scaling_factor <= 1:
            this_fire_rate = max(this_fire_rate, fire_rate_floor)

        # Get the new delay, and round it.
        new_fire_delay = round(Flags.Game_Ticks_Per_Minute / this_fire_rate)

        # Store the updated value.
        # TODO: add another adjustment to this if the related bullets were
        #  already modified by another laser, in which case the laser fire
        #  rate can be recalculated based on the new bullet damage to keep
        #  dps constant (when considering the fire rate floor).
        this_dict['fire_delay'] = str(new_fire_delay)

        # Calculate the fire rate change factor, using the rounded delay.
        new_fire_rate_factor = this_fire_delay / new_fire_delay
        
        # Loop over the bullets created by this laser.
        for bullet_index in Get_Laser_Bullets(this_dict):
            # Look up the bullet.
            bullet_dict = tbullets_dict_list[bullet_index]
                
            # Skip if this bullet was already seen.
            if bullet_index in bullet_indices_seen_list:
                continue
            # Add this bullet to the seen list.
            bullet_indices_seen_list.append(bullet_index)

            # Pull the fire rate, IS hull/shield damage, and energy use.
            # TODO: modify special fields like energy drain.
            hull_damage       = int(bullet_dict['hull_damage'])
            shield_damage     = int(bullet_dict['shield_damage'])
            energy_used       = int(bullet_dict['energy_used'])
                        
            # Scale energy use by inverse of the fire rate factor (half rate = double energy).
            energy_factor = 1 / new_fire_rate_factor
            # Scale damage by the inverse as well (half rate = double damage).
            damage_factor_is  = 1 / new_fire_rate_factor
            
            # Modify and round, minimum of 1.
            # These will also update the values for use in the OOS code below, so that
            #  the damage values match the new fire rate.
            hull_damage   = max(1, round(hull_damage    * damage_factor_is))
            shield_damage = max(1, round(shield_damage  * damage_factor_is))
            energy_used   = round(energy_used           * energy_factor)

            # Put back.
            bullet_dict['hull_damage']       = str(int(hull_damage  ))
            bullet_dict['shield_damage']     = str(int(shield_damage))
            bullet_dict['energy_used']       = str(int(energy_used  ))

    #  Since bullet energies were changed, update the max laser energies.
    Floor_Laser_Energy_To_Bullet_Energy()
                
    