#Rescale weapons and bullets for X3:AP.
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
from File_Manager import *
import Flags
import Scaling_Equations
from collections import OrderedDict
import math

#The hull to shield dps equivelence factor. Many weapons have this
# around 5-6. This is used to set the scaling equation for hull dps,
# where the above metrics were aimed at shield dps.
#May also be used in other transforms, so set it here for all.
Hull_to_shield_factor = 6

##########################################################################################


#Record which bullets spawn which child bullets, to help with figuring out
# all bullets spawned by a laser indirectly.
#This is keyed by parent bullet index, value is fragment index.
Bullet_parent_to_child_dict = {}
def _Initialize_Bullet_parent_to_child_dict():
    #Loop over all bullets.
    for index, this_dict in enumerate(Load_File('TBullets.txt')):
        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])
        #Check if this bullet fragments.
        if flags_dict['fragmentation']:
            #Record the pairing.
            Bullet_parent_to_child_dict[index] = int(this_dict['fragment_bullet'])
            
def Get_Laser_Bullets(laser_dict):
    '''
    Determine the bullets created by this laser, directly or indirectly.
    Eg. a fragmentation chain may result in multiple bullets (eg. cluster flak).
    Returns a list of integers, the bullet indices in tbullets.
    '''
    #On first call, initialize the bullet parent/child dict.
    if not Bullet_parent_to_child_dict:
        _Initialize_Bullet_parent_to_child_dict()

    #Get the index of the bullet this laser creates.
    this_bullet_index = int(laser_dict['bullet'])
    bullet_list = []
    #Start at the laser's initial bullet.
    current_bullet = this_bullet_index
    #Loop until no more fragments.
    while 1:
        #Record this bullet (captures the start bullet).
        bullet_list.append(current_bullet)
        #Stop if this bullet does not fragment.
        if current_bullet not in Bullet_parent_to_child_dict:
            break
        #Proceed to the fragment bullet.
        current_bullet = Bullet_parent_to_child_dict[current_bullet]
    return bullet_list


#Record which lasers spawn which bullets.
#If multiple lasers spawn a bullet, the first laser will be returned.
#This is keyed by parent bullet name, value is a laser dict.
Bullet_to_laser_dict = {}
def _Initialize_Bullet_to_laser_dict():

    #Set up a dict which tracks seen bullets, to prevent a bullet
    # being recorded more than once by different lasers.
    bullet_indices_seen_list = []
    tbullets_dict_list = Load_File('TBullets.txt')

    #Loop over all lasers.
    for laser_dict in Load_File('TLaser.txt'):
        #Loop over the bullets created by this laser.
        for bullet_index in Get_Laser_Bullets(laser_dict):
            #Look up the bullet.
            bullet_dict = tbullets_dict_list[bullet_index]
                
            #Skip if this bullet was already seen.
            if bullet_index in bullet_indices_seen_list:
                continue
            #Add this bullet to the seen list.
            bullet_indices_seen_list.append(bullet_index)
            #Record the laser.
            Bullet_to_laser_dict[bullet_dict['name']] = laser_dict
    return



@Check_Dependencies('TBullets.txt', 'TLaser.txt')
def Adjust_Weapon_Fire_Rate(
    scaling_factor = 1,
    laser_name_adjustment_dict = {},
    fire_rate_floor = 40,
    #If the fire rate change should ignore ammo weapons, since there is no good way
    # to adjust ammo consumption, leaving them buffed as a result of changes.
    skip_ammo_weapons = True,

    ):
    '''
    Adjust weapon fire rates. DPS and energy efficiency will remain constant.
    This may be used to reduce fire rates for performance improvements.
    Fire rate changes will apply to IS damage only; OOS does not use fire rate.
    Secondary weapon effects are not modified.
    If a bullet is used by multiple lasers, the first laser will
     be used for fire rate damage and energy adjustment.

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
    #TODO: adjust secondary effects: energy drain, etc.
    #-Would need to know what 'damage over time - energy' does, since in testing it does
    # not affect target laser energy at all.
    tbullets_dict_list = Load_File('TBullets.txt')
        
    #Start by building a list of bullets that use ammo, by index.
    #Used mainly to speed up checking for lasers than use ammo bullets.
    ammo_based_bullet_list = []
    #Loop over all bullets.
    for this_dict, index in enumerate(tbullets_dict_list):
        #Unpack the flags.
        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])
        #If an ammo user, record its name.
        if flags_dict['use_ammo']:
            ammo_based_bullet_list.append(index)
        
    #Set up a dict which tracks modified bullets, to prevent a bullet
    # being modded more than once by different lasers.
    bullet_indices_seen_list = []
    #TODO: update this code to make use of Bullet_to_laser_dict, since
    # there is some redundancy now.

    #Step through each laser.
    for this_dict in Load_File('TLaser.txt'):            

        #Grab the fire delay, in milliseconds.
        this_fire_delay = int(this_dict['fire_delay'])

        #Determine fire rate, per min.
        this_fire_rate = Flags.Game_Ticks_Per_Minute / this_fire_delay

        #Skip lasers that use ammo.
        if int(this_dict['bullet']) in ammo_based_bullet_list:
            continue

        #Determine the fire rate adjustment.        
        if this_dict['name'] in laser_name_adjustment_dict:
            this_scaling_factor = laser_name_adjustment_dict[this_dict['name']]
        elif scaling_factor != 1:
            #No changes if fire rate already below the floor.
            if this_fire_rate < fire_rate_floor:
                continue
            this_scaling_factor = scaling_factor
        else:
            continue

        #Apply change factor.  TODO: diminishing returns.
        this_fire_rate *= this_scaling_factor

        #Apply the floor, eg. if the fire rate fell below 60 and the floor is 60, 
        # use the floor.
        this_fire_rate = max(this_fire_rate, fire_rate_floor)

        #Get the new delay, and round it.
        new_fire_delay = round(Flags.Game_Ticks_Per_Minute / this_fire_rate)

        #Store the updated value.
        this_dict['fire_delay'] = str(new_fire_delay)

        #Calculate the fire rate change factor, using the rounded delay.
        new_fire_rate_factor = this_fire_delay / new_fire_delay
        
        #Loop over the bullets created by this laser.
        for bullet_index in Get_Laser_Bullets(this_dict):
            #Look up the bullet.
            bullet_dict = tbullets_dict_list[bullet_index]
                
            #Skip if this bullet was already seen.
            if bullet_index in bullet_indices_seen_list:
                continue
            #Add this bullet to the seen list.
            bullet_indices_seen_list.append(bullet_index)

            #Pull the fire rate, IS hull/shield damage, and energy use.
            #TODO: modify special fields like energy drain.
            hull_damage       = int(bullet_dict['hull_damage'])
            shield_damage     = int(bullet_dict['shield_damage'])
            energy_used       = int(bullet_dict['energy_used'])
                        
            #Scale energy use by inverse of the fire rate factor (half rate = double energy).
            energy_factor = 1 / new_fire_rate_factor
            #Scale damage by the inverse as well (half rate = double damage).
            damage_factor_is  = 1 / new_fire_rate_factor
            
            #Modify and round, minimum of 1.
            #These will also update the values for use in the OOS code below, so that
            # the damage values match the new fire rate.
            hull_damage   = max(1, round(hull_damage    * damage_factor_is))
            shield_damage = max(1, round(shield_damage  * damage_factor_is))
            energy_used   = round(energy_used           * energy_factor)

            #Put back.
            bullet_dict['hull_damage']       = str(int(hull_damage  ))
            bullet_dict['shield_damage']     = str(int(shield_damage))
            bullet_dict['energy_used']       = str(int(energy_used  ))

                



#Note: this function has been overhauled to remove IS DPS calculation;
# the original idea that ROF wasn't accounted for OOS was mistaken.
@Check_Dependencies('TBullets.txt', 'TLaser.txt')
def Adjust_Weapon_OOS_Damage(
    scaling_factor = 1,

    #-Removed.
    #Multiplier to use to recreate (approximately) vanilla OOS bullet damage with
    # ROF factored in; calibrated for HEPT (see comments at start of file).
    # 9.4k shield dps, 795 OOS shield damage value.
    #This will be used for XRM as well, since it is a general calibration to put
    # damages where the underlying OOS combat code was built around.
    #vanilla_calibration_factor = 795 / 9400,
    
    #-Removed.
    #Set a default for all areal weapons, in case a mod mixes them up.
    #The numbers calculated below can be roughly approximated here.
    #areal_weapon_multiplier = 12,

    bullet_name_multiplier_dict = {
        #Plasma burst generator (PD).
        #Vanilla sets OOS PD shield damage = 5x HEPT, which is probably way too high.
        #In sector dps: 
        # PD_dps_shield = 1/22 HEPT_dps_shield * number_of_hits_per_shot.
        # PD_dps_hull   = 1/13.7  HEPT_dps_hull   * number_of_hits_per_shot.
        #If the two are assumed to be balanced on average (not just when a player is
        # in the sweet spot), then can mult PD by 18.
        #'SS_BULLET_PD' : 18,

        #Phased shockwave generator (PSG).
        #Compare this against Flak (same tier and anti-fighter role).
        #PSG_dps = x Flak_dps * number_of_hits_per_shot.
        # PSG_dps_shield = 1/5.1   Flak_dps_shield * number_of_hits_per_shot.
        # PSG_dps_hull   = 1/14.1  Flak_dps_hull   * number_of_hits_per_shot.
        #PSG does far less hull damage, so direct comparison is imperfect, but go with it.
        #'SS_BULLET_PSG' : 9,
        
        #TODO: how to dynamically determine this:
        #PD  has areal flag set, speed 375, lifetime 2.1
        #PSG has areal flag set, speed 254, lifetime 5.7
        #It is unclear on how long the bullet might be (which is needed to know how long
        # it will overlap a target point), what the hit rate is (time between collision 
        # checks), and what effect the size of the target might have.
        #There may be more complicated effects as well, like having a thinner coverage on
        # the outside of the attack cone.
        },
    ):
    '''
    Scale OOS damage. Damage may be scaled down to improve accuracy in
     combat evaluation, at the potential drawback of stalemates when shield
     regeneration outperforms damage.

    * scaling_factor:
      - The base multiplier to apply to OOS damage.
    '''
    #Step through the bullets and scale their OOS numbers.
    for this_dict in Load_File('TBullets.txt'):
        if scaling_factor != 1:
            for field in ['hull_damage_oos', 'shield_damage_oos']:
                value = int(this_dict[field])
                this_dict[field] = str(round(value * scaling_factor))

    #-Removed; older code from when it was thought ROF was ignored OOS.
    #vanilla_calibration_factor:
    #    Multiplier to use to recreate (approximately) vanilla OOS bullet damage with
    #    ROF factored in; calibrated for HEPT by default.
    #    This is applied in addition to other multipliers, and can generally be
    #    left at default.
    #areal_weapon_multiplier:
    #    Weapons with areal effects (eg. plasma burst generator (PD) or phased
    #    shockwave cannon) will have an additional factor applied, 
    #    representing multiple hits per shot.
    #    Default is 12x, approximately calibrated based on vanilla areal
    #    values compared to their contemporary weapons (eg. PD vs HEPT).
    #bullet_name_hits_per_shot_dict:
    #    Dict, keyed by bullet name (eg. 'SS_BULLET_PD'), with the
    #    multiplier to apply to represent a shot hitting multiple times.
    #    This is applied in addition to scaling_factor, and will
    #    override the multiplier from areal_weapon_multiplier, to be
    #    used in customizing the number of hits per areal weapons.
    #
    ##TODO: maybe give a selective buff to beam weapons, since they seem oddly
    ## weak in OOS combat (maybe; it is hard to say for sure without tests).
    #tbullets_dict_list = Load_File('TBullets.txt')
    #
    #    
    ##Set up a dict which tracks modified bullets, to prevent a bullet
    ## being modded more than once by different lasers (though it might
    ## not matter if they are set instead of multiply the value).
    #bullet_indices_seen_list = []
    #
    ##Step through each laser.
    #for laser_dict in Load_File('TLaser.txt'):
    #
    #    #Grab the fire delay, in milliseconds.
    #    this_fire_delay = int(laser_dict['fire_delay'])
    #
    #    #Determine fire rate, per second.
    #    fire_rate = Flags.Game_Ticks_Per_Minute / this_fire_delay / 60
    #        
    #    #Loop over the bullets created by this laser.
    #    for bullet_index in Get_Laser_Bullets(laser_dict):
    #        #Look up the bullet.
    #        bullet_dict = tbullets_dict_list[bullet_index]
    #
    #        #Unpack the flags.
    #        flags_dict = Flags.Unpack_Tbullets_flags(bullet_dict['flags'])
    #            
    #        #Skip if this bullet was already seen.
    #        if bullet_index in bullet_indices_seen_list:
    #            continue
    #        #Add this bullet to the seen list.
    #        bullet_indices_seen_list.append(bullet_index)
    #
    #        #Note: if multiple lasers use the same bullet, the latest laser will
    #        # be the one whose fire_rate is used here.
    #        #Assume lasers using the same bullet are very similar to each other,
    #        # eg. the experimental aldrin weapons and terran counterparts.
    #
    #        #Loop over the hull and shield fields, IS and OOS.
    #        for is_field, oos_field in zip(
    #            ['hull_damage', 'shield_damage'],
    #            ['hull_damage_oos', 'shield_damage_oos']):
    #                                        
    #            #Pull the IS hull/shield damage.
    #            damage_is = int(bullet_dict[is_field])
    #
    #            #Calculate hull and shield dps for this weapon.
    #            dps_is = damage_is * fire_rate
    #
    #            #Convert dps to OOS damage units, applying the calibrated vanilla factor
    #            # along with the extra derating factor.
    #            damage_oos = dps_is * vanilla_calibration_factor * scaling_factor
    #
    #            #If this bullet has a special bonus multiplier, apply it,
    #            # to represent areal weapon multihit.
    #            if bullet_dict['name'] in bullet_name_multiplier_dict:
    #                damage_oos   *= bullet_name_multiplier_dict[bullet_dict['name']]
    #            #Otherwise, if this is an areal weapon, apply its multiplier.
    #            elif flags_dict['areal']:
    #                damage_oos *= areal_weapon_multiplier
    #
    #            #-Removed; old version modified existing entries, but those were found to be
    #            # rotten since they had stuff like PSP doing 10x the damage of PPC.
    #            #hull_damage_oos   = int(this_list[tbullets_field_index_dict['hull_damage_oos']])
    #            #shield_damage_oos = int(this_list[tbullets_field_index_dict['shield_damage_oos']])
    #            #hull_damage_oos   = max(1, round(hull_damage_oos   * damage_factor_oos))
    #            #shield_damage_oos = max(1, round(shield_damage_oos * damage_factor_oos))
    #
    #            #Floor at 1, and round off fraction.
    #            damage_oos   = max(1, round(damage_oos))
    #
    #            #Put the updated value back.
    #            bullet_dict[oos_field] = str(int(damage_oos  ))


            



'''
Bullet speed adjustment notes for XRM:

It is unclear on the best way to handle this without having to specify each weapon
individually.
Perhaps a scaling formula can be developed, using a curve fit to vanilla weapons which
looks at shield/hull dps, lifetime, shot speed, power draw, ammo usage, area effects,
multi-hit, pricetag, and maybe special effects or other aspects (eg. volume, ship
tier, etc.).

Attempts to find an equation by hand in excel generally failed, with large errors.
Attempts to find it using scipy.optimize did better, but the best result at the
time of this comment still had up to 40% error on shot speed estimates, when
the aim is closer to 10-15% to be comfortable.


An alternative approach is to use a scaling formula similar to X3_Missiles, which
slows down fast shots heavily, but barely adjusts slow shots.
Such a formula would need careful tuning, since the spread between fast (2000 m/s)
and slow (400 m/s, 5x spread) is much smaller than it was with missiles (100x spread).

The formula was set up in Scaling_Equations; see that module for details.
Coefficients for the formula are generated dynamically based on 
 Top_speed_adjustment_factor set below.

'''

@Check_Dependencies('TBullets.txt')
def Adjust_Weapon_Shot_Speed(
    scaling_factor = 1,
    #Special dict entries will override the above formula.
    bullet_name_adjustment_dict = {},

    #Use the formula for adjustments.
    use_scaling_equation = False,
    #Set the tuning points:
    #The target speed to adjust, in m/s.
    target_speed_to_adjust = 1400,
    #The speed to pin in place.
    speed_to_keep_static = 500,

    skip_areal = True,
    skip_flak = True,           
    print_changes = False
    ):
    '''
    Adjust weapon shot speeds. Range will remain constant.
    Beam weapons will not be affected.

    * scaling_factor:
      - The base multiplier to apply to shot speeds.
    * use_scaling_equation:
      - If True, a scaling formula will be applied, such
        that shots near target_speed_to_adjust see the full scaling_factor,
        and shots near speed_to_keep_static remain largely unchanged.
    * target_speed_to_adjust, speed_to_keep_static:
      - Equation tuning values, in meters/second.
    * bullet_name_adjustment_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with the
        multiplier to apply.
      - '*' entry will match all weapons not otherwise named,
        equivelent to setting scaling_factor and not using the
        scaling equation.
    * skip_areal:
      - If True, areal weapons (eg. PD and PSG) are skipped, since their
        damage delivery may be partially dependent on shot speed.
    * skip_flak: 
      - If True, flak weapons are skipped.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.
    '''

    if print_changes:
        Write_Summary_Line('\nShot speed adjustments:')

    #If using a formula, get it and its coefficients here.
    if use_scaling_equation:
            
        #Create a set of points to be tuned against.
        #The primary adjustment point.
        x_main = target_speed_to_adjust
        y_main = x_main * scaling_factor
        #The secondary, static point, where x=y.
        x_static = speed_to_keep_static
        y_static = speed_to_keep_static
            
        #To encourage fitting the lower end more than the higher end, can represent
        # low end values multiple times.
        #Give two low points for now, the one provided and another nearby, to help
        # stabalize the equation coefs.
        x_vec   = [x_main, x_static, x_static * .8]
        y_vec   = [y_main, y_static, y_static * .8]
            
        #Note: since speeds are kept in 500 meters/s format, need to either
        # adjust the configuration points here, or the speeds fed to the
        # equation further down.  Do it here to keep it simpler.
        #Give the m/s speed, scale to 500 m/s units with *500.
        x_vec   = [500*i for i in x_vec]
        y_vec   = [500*i for i in y_vec]

        #Get the function.
        scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec)

    #Loop over the bullets.
    for this_dict in Load_File('TBullets.txt'):

        #Unpack the flags.
        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])

        #Always skip beam weapons, including zigzag.
        if flags_dict['beam'] or flags_dict['zigzag']:
            continue

        #If this is an areal skip it.
        if skip_areal and flags_dict['areal']:
            continue
        #Skip flak as well (maybe condition this on a setting later)
        if skip_flak and flags_dict['flak']:
            continue
                
        #Get original speed.
        speed    = int(this_dict['speed'])
                
        #Skip if bullet has no speed (eg. frag children bullets).
        if speed == 0:
            continue

        #If this bullet has a speed factor override, use it.
        if this_dict['name'] in bullet_name_adjustment_dict:
            new_speed = speed * bullet_name_adjustment_dict[this_dict['name']]
        #If there is a wildcard use that.
        elif '*' in bullet_name_adjustment_dict:
            new_speed = speed * bullet_name_adjustment_dict['*']             
        #Otherwise, if using the speed formula, calculate a new speed.
        elif use_scaling_equation:                    
            new_speed = scaling_func(speed)
        #Otherwise, apply the scaling factor if not 1.
        elif scaling_factor != 1:
            new_speed = speed * scaling_factor
        else:
            #Skip this bullet.
            continue

        #Use a shared function to apply the speed change, keeping
        # range constant.
        _Update_Bullet_Speed(this_dict, new_speed)
                
        #Debug printout.
        if print_changes:        
            #Give bullet name, old and new speed,
            # and the scaling factor.
            Write_Summary_Line('{:<30} : {:>10} -> {:>10}, x{}'.format(
                this_dict['name'],
                #Convert back to m/s
                speed / 500,
                new_speed / 500,
                #Give only two sig digits for the scaling factor.
                round(new_speed / speed, 2)
                ))


def _Update_Bullet_Speed(bullet_dict, new_speed):
    '''
    Support function to modify a bullet to have a new speed, while
    keeping range constant through a lifetime adjustment.
    '''
    #Look up the original lifetime and speed.
    speed    = int(bullet_dict['speed'])
    lifetime = int(bullet_dict['lifetime'])

    #Round speed to nearest 10 for nicer looking number in game.
    #Round up in case a bullet is really slow.
    #Bullet speeds are in units of 500 ticks per meter, so
    # would need to round to nearest 5000 to get this to-10 effect.
    new_speed = math.ceil(new_speed/5000)*5000         

    #Calculate a new lifetime so that range remains unchanged.
    #Ranges in game are not generally rounded, so don't bother with
    # making that look nice here.
    new_lifetime = lifetime * speed / new_speed

    #Put them back, rounded.
    bullet_dict['speed'] = str(int(new_speed))
    bullet_dict['lifetime'] = str(int(new_lifetime))

            
@Check_Dependencies('TBullets.txt', 'TLaser.txt')
def Adjust_Weapon_DPS(
    #A flat factor to use for damage adjustment.
    #This is applied after the scaling equation below, so that that
    # equation can be configured to the base xrm numbers.
    #Go with 2.5 to be conservative, or even 2 since some ships have more
    # turret gun mounts than in vanilla.
    #This helps bring up energy drain as well.
    scaling_factor = 1,

    bullet_name_adjustment_dict = {},

    #If a scaling equation should be used for the damage adjustment.
    use_scaling_equation = False,
    #Set the tuning points.
    #Note: these numbers will have an implicit 10^3 factor, to avoid the
    # scaling equation overflowing.
    damage_to_adjust_kdps = 9,
    #The damage to pin in place on the low end.
    damage_to_keep_static_kdps = 3,

    #If laser energy efficiency should be modified or not.
    maintain_energy_efficiency = True,

    #Options to change only hull or shield dps.
    adjust_hull_damage_only     = False,
    adjust_shield_damage_only   = False,

    #Don't modify repair lasers, mainly to avoid having to put this
    # in every transform call individually, since normally these don't
    # need modification.
    ignore_repair_lasers = True,
    
    print_changes = False
    ):
    '''
    Adjust weapon damage/second by changing bullet damage.
    If a bullet is used by multiple lasers, the first laser will
    be used for DPS calculation.
    Energy efficiency will remain constant, changing energy/second.

    * scaling_factor:
      - The base multiplier to apply to shot speeds.
    * adjust_hull_damage_only:
      - Bool, if True only hull damage is modified. Default False.
    * adjust_shield_damage_only:
      - Bool, if True only shield damage is modified. Default False.
    * use_scaling_equation:
      - If True, a scaling formula will be applied, such
        that shots near damage_to_adjust_kdps see the full scaling_factor,
        and shots near damage_to_keep_static_kdps remain largely unchanged.
    * damage_to_adjust_kdps, damage_to_keep_static_kdps:
      - Equation tuning values, in units of kdps, eg. 1 for 1000 damage/second.
        Scaling values are for shield DPS; hull DPS will be scaled at a
        rate of 1/6 of shield DPS.
    * bullet_name_adjustment_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with the
        multiplier to apply. This also supports matching to bullet
        flags using a 'flag_' prefix, eg. 'flag_beam' will match
        to beam weapons. Flag matches are lower priority than
        name matches.
      - If multiple flag matches are found, the first flag will
        be used if the input is an OrderedDict, otherwise any
        Python default is used (likely equivelent to ordereddict
        in Python 3.6).
      - '*' entry will match all weapons not otherwise matched,
        equivelent to setting scaling_factor and not using the
        scaling equation.
    * maintain_energy_efficiency:
      - Bool, if True (default) then weapon energy usage will be scaled to
        keep the same damage/energy ratio, otherwise damage is adjusted but
        energy is unchanged.
    * ignore_repair_lasers:
      - Bool, if True (default) then repair lasers will be ignored.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.  
    '''
    tbullets_dict_list = Load_File('TBullets.txt')
    
    if print_changes:
        Write_Summary_Line('\nDamage adjustments:')
        
    if use_scaling_equation:
        #Get formula and its coefficients here.
                    
        #Create a set of points to be tuned against.
        #The primary adjustment point.
        x_main = damage_to_adjust_kdps
        y_main = x_main * scaling_factor
        #The secondary, static point, where x=y.
        x_static = damage_to_keep_static_kdps
        y_static = damage_to_keep_static_kdps
            
        #To encourage fitting the lower end more than the higher end, can represent
        # low end values multiple times.
        #Give two low points for now, the one provided and another nearby, to help
        # stabalize the equation coefs.
        x_vec   = [x_main, x_static, x_static * .8]
        y_vec   = [y_main, y_static, y_static * .8]
            
        #Get the function and its coefs to use.
        shield_scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec, reversed = False)
        #Also get one for hull damage, which has lower damage values.
        x_vec = [x / Hull_to_shield_factor for x in x_vec]
        y_vec = [y / Hull_to_shield_factor for y in y_vec]
        hull_scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec, reversed = False)
    else:
        shield_scaling_func = None
        hull_scaling_func = None
        
    #Parse out the flag matches from the input dict.
    #This will pull off the 'flag_' prefix.
    #Flag ordering will be kept intact, if an ordered dict was provided.
    flag_match_dict = OrderedDict((key.replace('flag_',''), value)
                       for key,value in bullet_name_adjustment_dict.items() 
                       if key.startswith('flag_'))

    #Set up a dict which tracks modified bullets, to prevent a bullet
    # being modded more than once by different lasers (which would cause
    # accumulated damage buffing).
    bullet_indices_seen_list = []

    #Similar to above, need to pair lasers with bullets to get all of the necessary
    # metrics for this calculation.
    #Step through each laser.
    for laser_dict in Load_File('TLaser.txt'):

        #Grab the fire delay, in milliseconds.
        this_fire_delay = int(laser_dict['fire_delay'])

        #Determine fire rate, per second.
        fire_rate = Flags.Game_Ticks_Per_Minute / this_fire_delay / 60            

        #Loop over the bullets created by this laser.
        for bullet_index in Get_Laser_Bullets(laser_dict):

            #Skip if this bullet was already seen.
            if bullet_index in bullet_indices_seen_list:
                continue
            #Add this bullet to the seen list.
            bullet_indices_seen_list.append(bullet_index)

            #Look up the bullet.
            bullet_dict = tbullets_dict_list[bullet_index]

            #Unpack the flags.
            flags_dict = Flags.Unpack_Tbullets_flags(bullet_dict['flags'])

            #If ignoring repair lasers, and this is a repair weapon, skip.
            if flags_dict['repair'] and ignore_repair_lasers:
                continue
                
            #There are two options here:
            # 1) Handle shield and hull damage together, combining them into a
            #    single metric.
            #    -Drawback: a weapon like the ion cannon may be treated as a
            #    lower tier weapon due to its average shield/hull damage being
            #    much lower than its specialized shield damage.
            # 2) Handle shield and hull separately.
            #    -Drawback: it is harder to determine the energy usage adjustment
            #    if the shield/hull factors differ by much.
            # Go with option (2), but keep some commented code left over from
            # option (1).
                
            #-Removed; from option (1) above.
            #hull_damage       = int(bullet_dict['hull_damage'])
            #shield_damage     = int(bullet_dict['shield_damage'])                
            ##Calculate hull and shield dps for this weapon.
            #hull_dps   = hull_damage   * fire_rate
            #shield_dps = shield_damage * fire_rate
            ##Calculate overall dps, applying scaling on hull.
            ##The hull scaling
            #overall_dps = (shield_dps + hull_dps * Hull_to_shield_factor)/2

            #Keep a dict to temporarily store scaling factors.
            scaling_factor_dict = {}
            #Loop over the field types; catch the OOS field name as well for
            # writing back the new damages later, and select the matching
            # scaling equation.
            for field, oos_field, scaling_func in [
                        ('hull_damage'  , 'hull_damage_oos'  , hull_scaling_func),
                        ('shield_damage', 'shield_damage_oos', shield_scaling_func)]:

                #Skip hull or shield changes as requested.
                if adjust_hull_damage_only and field == 'shield_damage':
                    continue
                elif adjust_shield_damage_only and field == 'hull_damage':
                    continue

                #Look up the IS damage, and calculate dps.
                damage = int(bullet_dict[field])
                overall_dps = damage   * fire_rate

                #Skip ahead if dps is 0, eg. shield dps for mass drivers.
                if overall_dps == 0:
                    continue

                #Determine the scaling factor to apply.
                #Look up this bullet in the override dict first.
                if bullet_dict['name'] in bullet_name_adjustment_dict:
                    this_scaling_factor = bullet_name_adjustment_dict[bullet_dict['name']]

                #Look for any flag match.
                elif any(flags_dict[flag] for flag in flag_match_dict):
                    #Grab the first flag match.
                    for flag, value in flag_match_dict.items():
                        if flags_dict[flag]:
                            this_scaling_factor = value
                            break

                #If there is a wildcard use that.
                elif '*' in bullet_name_adjustment_dict:
                    this_scaling_factor = bullet_name_adjustment_dict['*']

                elif use_scaling_equation:
                    this_scaling_factor = 1
                    #Run the scaling formula.
                    #This takes in a weighted average of original shield/hull dps,
                    # and returns the replacement dps, from which the scaling
                    # can be calculated.
                    #This takes dps in kdps, eg. with a 10^3 implicit factor,
                    # to avoid overflow.
                    new_overall_dps = 1e3* scaling_func(overall_dps/1e3)
                    this_scaling_factor *= new_overall_dps / overall_dps
                    
                elif scaling_factor != 1:
                    this_scaling_factor = scaling_factor
                else:
                    continue

                #Store the factor in the temp dict.
                scaling_factor_dict[field] = this_scaling_factor

                #Debug printout.
                if print_changes:
                    #Give bullet name, old and new dps,
                    # and the scaling factor.
                    Write_Summary_Line('{:<30} {:<15}:  {:>10} -> {:>10}, x{}'.format(
                        bullet_dict['name'],
                        field,
                        round(overall_dps),
                        round(overall_dps * this_scaling_factor),
                        #Give only two sig digits for the scaling factor.
                        round(this_scaling_factor, 2)
                        ))

                #Apply the scaling factors to their IS and OOS fields.
                for writeback_field in [field, oos_field]:
                    value = int(bullet_dict[writeback_field])
                    bullet_dict[writeback_field] = str(int(value * this_scaling_factor))

            #If no adjustments were made to the bullet, skip ahead.
            if not scaling_factor_dict:
                continue

            #Adjust energy usage.
            #This can be done with the average of the factors or the max
            # of the factors.
            #For specialized weapons like ion cannons, which likely had a much
            # bigger factor on shield damage than hull damage on the expectation
            # they will only be used against shields, it makes the most sense
            # to adjust energy based on the biggest factor (the main use case
            # for the weapon).
            if maintain_energy_efficiency:
                max_factor = max(scaling_factor_dict.values())
                value = int(bullet_dict['energy_used'])
                bullet_dict['energy_used'] = str(int(value * max_factor))


@Check_Dependencies('TBullets.txt')
def Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio(
    minimum_ratio = 1/20,
    ):
    '''
    Increases hull damage on weapons to achieve a specified hull:shield
    damage ratio requirement. Typical weapons are around a 1/6 ratio, 
    though some weapons can be 1/100 or lower, such as ion weaponry.
    This transform can be used to give such weapons a viable hull damage amount.

    * minimum_ratio:
      - Float, the required ratio. Recommend something below 1/6 to avoid
        significant changes to most weapons. Default 1/20.
    '''
    for this_dict in Load_File('TBullets.txt'):        
        #Pull the hull/shield damage.
        hull_damage       = int(this_dict['hull_damage'])
        hull_damage_oos   = int(this_dict['hull_damage_oos'])
        shield_damage     = int(this_dict['shield_damage'])

        #Set an adjustment ratio if the hull damage is too low.
        if hull_damage < minimum_ratio * shield_damage:
            ratio = minimum_ratio * shield_damage / hull_damage

            #Apply the ratio to IS and OOS damage.            
            #Modify and round, minimum of 1.
            hull_damage     = round(hull_damage     * ratio)
            hull_damage_oos = round(hull_damage_oos * ratio)
            #Put back.
            this_dict['hull_damage']       = str(int( hull_damage ))
            this_dict['hull_damage_oos']   = str(int( hull_damage_oos ))

           

@Check_Dependencies('TBullets.txt')
def Adjust_Beam_Weapon_Duration(
    bullet_name_adjustment_dict = {},
    #Don't modify repair lasers, mainly to avoid having to put this
    # in every transform call individually, since normally these don't
    # need modification.
    ignore_repair_lasers = True,
    ):
    '''
    Adjusts the duration of beam weapons.
    Shot damage will be applied over the duration of the beam, such that
     shorter beams will apply their damage more quickly. 
    Longer duration beams are weaker against small targets which move out 
     of the beam before its damage is fully applied.
    Beam range will remain unchanged.
    Note: this does not affect fire rate, so multiple beams may become
     active at the same time.

    * bullet_name_adjustment_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to
        apply, as a tuple of (min, factor, max), where min and max are
        given in seconds.
      - None may be entered for min or max to disable those limits.
      - '*' entry will match all beam weapons not otherwise named.
    * ignore_repair_lasers:
      - Bool, if True (default) then repair lasers will be ignored.
    '''
    for this_dict in Load_File('TBullets.txt'):
        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])
         
        #Skip if this isn't a beam.
        if not flags_dict['beam']:
            continue
        
        #If ignoring repair lasers, and this is a repair weapon, skip.
        if flags_dict['repair'] and ignore_repair_lasers:
            continue

        #This will need to adjust the lifetime and speed again, to keep
        # the range constant.
        #Damage does not need modification, since it is already treated
        # as damage per shot, regardless of a beam's duration, just spread
        # out over the duration.

        #Determine the scaling and min/max.
        if this_dict['name'] in bullet_name_adjustment_dict:
            min_seconds, factor, max_seconds = bullet_name_adjustment_dict[this_dict['name']]
        elif 'default' in bullet_name_adjustment_dict:
            min_seconds, factor, max_seconds = bullet_name_adjustment_dict['default']
        else:
            continue

        #Read the original values.
        lifetime = int(this_dict['lifetime'])
        speed    = int(this_dict['speed'])

        #Apply scaling.
        new_lifetime = lifetime * factor
        #Apply the max (in milliseconds).
        if max_seconds != None:
            new_lifetime = min(new_lifetime, max_seconds*1000)
        #Apply the min.
        if min_seconds != None:
            new_lifetime = max(new_lifetime, min_seconds*1000)

        #Speed needs the reversed scaling, since speed*lifetime = range, and
        # want a constant range.
        # Eg. if lifetime goes up 2x, then speed drops by 1/2.
        speed *= (lifetime / new_lifetime)
        #Put the updated values back as ints.
        this_dict['lifetime'] = str(int(new_lifetime))
        this_dict['speed']    = str(int(speed))

              
#-Removed, had no performance benefit.
#TODO: consider a general transform to change bullet length, since it
# might be neat visually. Could limit bullet length based on fire
# rate and speed to ensure bullets aren't longer than their spacing.
#@Check_Dependencies('TBullets.txt')
#def Adjust_Beam_Weapon_Bullet_Length(
#    scaling_factor = 10,
#    beams_not_converted = [
#        #Don't adjust repair lasers or tractor laser.
#        'SS_BULLET_TUG',
#        'SS_BULLET_REPAIR',
#        'SS_BULLET_REPAIR2',
#        ]
#    ):
#    '''
#    Adjusts the length of beam weapon bullets. Goal is to improve
#    performance by forming beams from fewer bullet objects, on
#    the theory that few bullets do fewer collision checks.
#
#    scaling_factor:
#        Multiplier on existing bullet length.
#    beams_not_converted:
#        List of bullet names for weapons not to be modified.
#    '''
#    #TODO: make into a generic transform with a bullet dict, and key
#    # off of a flag match.
#    for this_dict in Load_File('TBullets.txt'):
#        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])
#
#        #Skip non-beams.
#        if not flags_dict['beam']:
#            continue
#        
#        #Skip skipped bullets.
#        if this_dict['name'] in beams_not_converted:
#            continue
#
#        value = float(this_dict['box_length'])
#        #Typical values are around 4 or so.
#        #Try out a super long length.
#        value *= scaling_factor
#        #Floor at 0.1 to be safe.
#        value = max(0.1, value)
#        #Put it back, with 1 decimal place.
#        this_dict['box_length'] = '{0:.1f}'.format(value)


                
@Check_Dependencies('TBullets.txt')
def Adjust_Beam_Weapon_Width(
    bullet_name_adjustment_dict = {}
    ):
    '''
    Adjusts the width of beam weapons. Narrower beams will have more 
    trouble hitting small targets at a distance.
    In vanilla AP beam widths are generally set to 1, though in XRM the
    widths have much wider variety. This can be used to nerf anti-fighter
    defense of capital ships with beam mounts.

    * bullet_name_adjustment_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_PBC'), with options to
        apply, as a tuple of (min, factor, max), applied to height and width.
      - None may be entered for min or max to disable those limits.
      - '*' entry will match all beam weapons not otherwise named.
    '''
    #TODO: consider length increases, which may have performance benefit at the
    # drawback of beams maybe visually going through small targets slightly.
    for this_dict in Load_File('TBullets.txt'):
        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])

        #Skip if this isn't a beam.
        if not flags_dict['beam']:
            continue

        #Determine the scaling, or skip if a scaling not found.
        if this_dict['name'] in bullet_name_adjustment_dict:
            min_val, factor, max_val = bullet_name_adjustment_dict[this_dict['name']]
        elif '*' in bullet_name_adjustment_dict:
            min_val, factor, max_val = bullet_name_adjustment_dict['*']
        else:
            continue

        #Apply to width and height.
        for field in ['box_width', 'box_height']:
            #Look up the value, apply scalings.
            value = float(this_dict[field])
            value *= factor
            if min_val != None:
                value = max(value, min_val)
            if max_val != None:
                value = min(value, max_val)
            #Put it back, with 1 decimal place.
            this_dict[field] = '{0:.1f}'.format(value)
            

#Replace beams with normal shots.
#Beam weapons in general, while cool looking, can be bad for the gameplay,
# both due to performance issues/slowdown and due to balance issues with them
# being too accurate, plus a general problem with player controlled beams
# being able to be always-on, increasing dps potentially drastically.
#This will need some thought for shot speed, as well as picking the bullet
# effect to use (the laser bullet may not be well suited to standalone
# bullets).
@Check_Dependencies('TBullets.txt')
def Convert_Beams_To_Bullets(
    beams_not_converted = None,
    speed_samples = 4,
    sample_type = 'min'
    ):
    '''
    Converts beam weapons to bullet weapons, to help with game slowdown
    when beams are fired at large ships and stations. Bullet speed will 
    be set based on sampling other bullets of similar damage.

    * beams_not_converted:
      - List of bullet names for weapons not to be converted.
        Repair and tug lasers are added to this list by default.
    * speed_samples:
      - Int, the number of similar DPS weapons to sample when setting the
        bullet speed. Default 4.
    * sample_type:
      - String, one of ['min','avg'], if the minimum or average of speed
        ratio of sampled similar DPS weapons should be used. Default 'min'.
    '''
    if beams_not_converted == None:
        beams_not_converted = []
    #Add tractor beam and repair lasers to ignored list.
    #Put there here instead of at input arg, so the user doesn't have to
    # add them if they just want to skip some other weapon.
    #TODO: special way to identify tug lasers, if there is one, to be
    # adaptable to mods.  Repair lasers can check their flag dict.
    beams_not_converted += ['SS_BULLET_TUG']

    for this_dict in Load_File('TBullets.txt'):
        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])

        #Skip non-beams.
        if not flags_dict['beam']:
            continue

        #Skip skipped bullets.
        if this_dict['name'] in beams_not_converted:
            continue
        
        #If this is a repair weapon, skip.
        if flags_dict['repair']:
            continue
        
        #-Removed; bullet length doesn't actually affect the visual
        # at all.
        ##For visual similarity, try lengthening the shots a bunch.
        ##This would be more like star wars lasers.
        #value = float(this_dict['box_length'])
        ##Typical values are around 4 or so.
        ##Try out a super long length.
        #value *= 10
        ##Put it back, with 1 decimal place.
        #this_dict['box_length'] = '{0:.1f}'.format(value)

        #How much should shot speed be adjusted?
        #Originally, speed was only used for determining range
        # based on lifetime.
        #Often, lifetime is much shorter on beams than it is on
        # comperable weapons, eg. ppc lifetime is around 10x that
        # of capital beams. This trend may not hold with weaker
        # beams, though.
        #Just fit to similar bullets based on damage for now.
        new_speed = _Get_Bullet_Speed_By_Damage(this_dict,
                                                speed_samples,
                                                sample_type)

        #Apply the speed update, keeping range constant.
        _Update_Bullet_Speed(this_dict, new_speed)
        
        #Clear the beam flag.
        #Do this after the above, so a beam isn't included in the
        # bullet to speed analysis.
        flags_dict['beam'] = False
        this_dict['flags'] = Flags.Pack_Flags(flags_dict)


def _Get_Average_Damage(bullet_dict):
    '''
    Support funcion to return average of hull and shield damage 
    for a bullet, scaling hull damage by Hull_to_shield_factor.
    '''
    return (int(bullet_dict['hull_damage']) * Hull_to_shield_factor 
            + int(bullet_dict['shield_damage'])) /2


#Cached sorted list for the function below.
_Bullet_damage_range_tuples = []
def _Get_Bullet_Speed_By_Damage(bullet_dict, speed_samples, sample_type):
    '''
    Support function to estimate the speed of a bullet based on its
    damage value and other similar bullets.
    '''
    #Goal is to match eg. capital ship tier bullets to other cap
    # ship bullets.
    #This can be awkward in some cases, such as with flak, which
    # may be outliers for damage and speed.
    #Instead of doing a match-to-nearest-damage, aim to smooth out the
    # estimation a bit to balance outliers better.
    #Also want something simple for now, so that it is easy to set up.
    #A full linear fit across all bullets may fail to capture any
    # nonlinearities, eg. if bullets slow by half going from small
    # to medium, then slow by another quarter going medium to large.
    #Best approach may be to do a local fit, where the nearest
    # X bullets are found, and a linear fit or maybe a simple averaging
    # is done.
    #Want to avoid numpy/similar and stick to standard packages, so
    # go with the local average idea.
    
    #Init the bullet to laser dict if needed.
    if not Bullet_to_laser_dict:
        _Initialize_Bullet_to_laser_dict()

    #Select the scaling metric to use.
    def Get_Scaling_Metric(bullet_dict):

        #Start with bullet damage.
        damage = _Get_Average_Damage(bullet_dict)

        #This should be based on DPS and not bullet damage.
        #Look up the laser's fire delay.
        laser_dict = Bullet_to_laser_dict[bullet_dict['name']]

        #Grab the fire delay, in milliseconds.
        this_fire_delay = int(laser_dict['fire_delay'])
        #Scaling will be damage/delay.
        return damage / this_fire_delay

    #On first call, fill out a sorted list of bullet tuples of
    # (scaling_metric, speed*scaling_metric, speed).
    #The multiplier simply makes range calculation later easier, since it
    # will be focused on how speed scales with damage rather than raw speed
    # (to be more robust), and a multiplier gives a steadier returned value
    # since speed goes down as damage goes up.
    #The extra speed argument is simply for debug checking that results
    # make sense.

    #Check if the dict is initialized yet.
    if not _Bullet_damage_range_tuples:
        for this_dict in Load_File('TBullets.txt'):

            #Skip beams.
            flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])
            if flags_dict['beam']:
                continue

            #Skip bullets that don't have associated lasers.
            if this_dict['name'] not in Bullet_to_laser_dict:
                continue

            #Skip some special stuff like mining lasers.
            if this_dict['name'] in ['SS_BULLET_MINING']:
                continue

            #Get the scaling meetric.
            metric = Get_Scaling_Metric(this_dict)

            #Add the tuple.
            _Bullet_damage_range_tuples.append((
                metric,
                int(this_dict['speed']) * metric,
                int(this_dict['speed'])
                ))
        
    #Skip bullets that don't have associated lasers.
    #This showed up on a Dummy beam laser in xrm.
    if bullet_dict['name'] not in Bullet_to_laser_dict:
        #Return speed unmodified.
        return int(bullet_dict['speed'])

    #There are different ways to find the nearest elements.
    #The simplest appears to be resorting the list based on how far
    # away each tuple is from the input metric, then just take the
    # nearst some number of elements.
    new_metric = Get_Scaling_Metric(bullet_dict)
    resorted_list = sorted(_Bullet_damage_range_tuples, 
                           key = lambda x: abs(x[0] - new_metric))

    #Average the nearest some number of items.
    #This will get the speed*metric values averaged, so is somewhat robust
    # if the new bullet it outside the normal range of the list.
    if sample_type == 'avg':
        speed_x_metric = sum(x[1] for x in resorted_list[:speed_samples]) / speed_samples
    #The above wasn't working very well because of flak and similar.
    #Instead, take the minimum from the nearest elements, filtering
    # out flak, and also somewhat offsetting a beam weapon's damage
    # becoming concentrated in one ball by making it harder to hit.
    elif sample_type == 'min':
        speed_x_metric = min(x[1] for x in resorted_list[:speed_samples])
    else:
        raise Exception('Speed sample type {} not understood'.format(sample_type))

    #Can now calculate and return a speed.
    new_speed = speed_x_metric / new_metric
    return new_speed



        
@Check_Dependencies('TBullets.txt')
def Replace_Weapon_Shot_Effects(
    impact_replacement = None,
    launch_replacement = None
    ):
    '''
    Replaces shot effects to possibly reduce lag.
    This appears to have little to no benefit in brief testing.

    * impact_replacement:
      - Int, the effect to use for impacts. Eg. 19 for mass driver effect.
        Avoid using 0, else sticky white lights have been observed.
    * launch_replacement:
      - Int, the effect to use for weapon launch.
    '''
    for this_dict in Load_File('TBullets.txt'):
        if impact_replacement != None:
            this_dict['impact_effect'] = str(impact_replacement)
        if launch_replacement != None:
            this_dict['launch_effect'] = str(launch_replacement)

            
@Check_Dependencies('TBullets.txt')
def Remove_Weapon_Shot_Sound():
    '''
    Removes impact sound from bullets.
    Little performance benefit expected, though untested.
    '''
    for this_dict in Load_File('TBullets.txt'):
        #Simply set to 0 appears as if it will quiet the bullet.
        #Note: untested.
        this_dict['impact_sound'] = '0'

            
@Check_Dependencies('TBullets.txt')
def Adjust_Weapon_Range(
    lifetime_scaling_factor = 1,
    speed_scaling_factor = 1,
    ):
    '''
    Adjusts weapon range by adjusting lifetime or speed.
    To modify range, consider that range = speed * lifetime.
     Eg. 1.2 * 1.2 = 44% range increase.

    * lifetime_scaling_factor:
      - Multiplier to apply to all bullet lifetimes.
    * speed_scaling_factor:
      - Multiplier to apply to all bullet speeds.
    '''
    #TODO: maybe add per-bullet support.
    #Stop early if factors are at defaults.
    if lifetime_scaling_factor == 1 and speed_scaling_factor == 1:
        return
    for this_dict in Load_File('TBullets.txt'):
        #Read the original values.
        lifetime = int(this_dict['lifetime'])
        speed    = int(this_dict['speed'])
        #Apply scaling.
        lifetime *= lifetime_scaling_factor
        speed    *= speed_scaling_factor
        #Put the updated values back as ints.
        this_dict['lifetime'] = str(int(lifetime))
        this_dict['speed']    = str(int(speed))

            
        
@Check_Dependencies('TBullets.txt')
def Adjust_Weapon_Energy_Usage(
    scaling_factor = 1,
    bullet_name_multiplier_dict = {},
    #Don't modify repair lasers, mainly to avoid having to put this
    # in every transform call individually, since normally these don't
    # need modification.
    ignore_repair_lasers = True,
    
    ):
    '''
    Adjusts weapon energy usage by the given multiplier.

    * scaling_factor:
      - Multiplier to apply to all weapons without specific settings.
    * bullet_name_energy_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the
        multiplier to apply. This will override scaling_factor for
        this weapon.
    * ignore_repair_lasers:
      - Bool, if True (default) then repair lasers will be ignored.
    '''
    for this_dict in Load_File('TBullets.txt'):
        
        if this_dict['name'] in bullet_name_multiplier_dict or scaling_factor != 1:

            #If ignoring repair lasers, and this is a repair weapon, skip.
            flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])
            if flags_dict['repair'] and ignore_repair_lasers:
                continue

            energy = int(this_dict['energy_used'])

            #Pick the table or default multiplier.
            if this_dict['name'] in bullet_name_multiplier_dict:
                multiplier = bullet_name_multiplier_dict[this_dict['name']]
            else:
                multiplier = scaling_factor

            new_energy = energy * multiplier
            this_dict['energy_used'] = str(int(new_energy))
                        
    

#Id integers for various named ammos.
#TODO: maybe set up a generalized table of item names to id codes, perhaps
# autogenerating it from game files to be used as documentation.
#It looks like perhaps anything can be used as ammo, perhaps with the game just 
# checking for this item in inventory and decrementing by 1 for every 200 shots.
#There may be interesting opportunities to make stuff like energy cells into ammo.
Ammo_name_id_dict = {
    'Mass Driver Ammunition': 42,
    }

@Check_Dependencies('TBullets.txt')
def Convert_Weapon_To_Energy(
    bullet_name_energy_dict = {}
    ):
    '''
    Converts the given weapons, determined by bullet type, to use energy
    instead of ammunition. Ammo type may support general wares, and
    will reduce a ware by 1 per 200 shots.

    * bullet_name_energy_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the energy
        value to use in the replacement.
    '''
    for this_dict in Load_File('TBullets.txt'):
        if this_dict['name'] in bullet_name_ammo_dict:
            flags_dict = Flags.Unpack_Tbullets_flags(bullet_dict['flags'])

            #Clear the ammo flag.
            flags_dict['use_ammo'] = False
            #Copy over the energy value to use. 
            #TODO: maybe do some sanity check on this.
            new_energy = bullet_name_ammo_dict[this_dict['name']]

            #Put new values back.
            this_dict['flags'] = Flags.Pack_Flags(flags_dict)
            this_dict['energy_used'] = str(int(new_energy))
    
            
@Check_Dependencies('TBullets.txt')
def Convert_Weapon_To_Ammo(
    bullet_name_ammo_dict = {},
    energy_reduction_factor = 0.1
    ):
    '''
    Converts the given weapons, determined by bullet type, to use ammo
    instead of ammunition.

    * bullet_name_energy_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the ammo
        type to use in the replacement.
        Ammo type is given by a ware id value, or by a preconfigured string
        name.
        Currently supported ammo names:
            ['Mass Driver Ammunition']
    * energy_reduction_factor:
      - Multiplier on existing weapon energy, such that after ammo conversion
        the weapon will still use a small energy amount.
        Default will cut energy use by 90%, which is roughly the Vanilla 
        difference between MD and PAC energy.
    '''
    for this_dict in Load_File('TBullets.txt'):

        if this_dict['name'] in bullet_name_ammo_dict:
            flags_dict = Flags.Unpack_Tbullets_flags(bullet_dict['flags'])
            
            #Set the ammo flag.
            flags_dict['use_ammo'] = True

            #Cut the energy.
            energy = int(this_dict['energy_used'])
            new_energy = energy * energy_reduction_factor

            #Look up an ammo type code if an item name given.
            ammo_type = bullet_name_ammo_dict[this_dict['name']]
            if isinstance(ammo_type, str):
                ammo_type = Ammo_name_id_dict[ammo_type]

            #Set the ammo type.
            this_dict['ammo_type'] = str(ammo_type)

            #Put new values back.
            this_dict['flags'] = Flags.Pack_Flags(flags_dict)
            this_dict['energy_used'] = str(int(new_energy))


            
@Check_Dependencies('TBullets.txt')
def Clear_Weapon_Flag(flag_name):
    '''
    Clears the specified flag from all weapons.

    * flag_name:
      - Bullet property flag name, as found in Flags.py.
    '''
    for this_dict in Load_File('TBullets.txt'):
        #Look up the flag, and set to False.
        flags_dict = Flags.Unpack_Tbullets_flags(this_dict['flags'])
        assert flag_name in flags_dict
        flags_dict[flag_name] = False
        this_dict['flags'] = Flags.Pack_Flags(flags_dict)
        
        
@Check_Dependencies('TBullets.txt')
def Remove_Weapon_Charge_Up():
    '''
    Remove charge up from all weapons, to make PPCs and similar easier to use in
     a manner consistent with the npcs (eg. hold trigger to just keep firing), as
     charging is a player-only option.
    '''
    Clear_Weapon_Flag('charged')


#Disable weapon drain effects.
#Weapon drain may cause equipment damage before shields go down.
#In XRM, Xenon beams do this equipment damage and are only notable for having
# this flag set. Try clearing it to see if this helps (as part of the
# general beam nerf).
@Check_Dependencies('TBullets.txt')
def Remove_Weapon_Drain_Flag():
    '''
    Removes the weapon drain flag from any weapons.
    May also stop equipment damage being applied through shielding
    for these weapons.
    '''
    #TODO: doubly verify this works. Gameplay since making this
    # change has not seen equipment destroyed by Xenon cap ship
    # weapons in XRM, which were the motivation for this change.
    Clear_Weapon_Flag('weapon_drain')


