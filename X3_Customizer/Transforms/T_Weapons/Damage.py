
from collections import OrderedDict
from ... import File_Manager
from ...Common import Flags
from ...Common import Scaling_Equations
from .Shared import *

# Note: this function has been overhauled to remove IS DPS calculation;
#  the original idea that ROF wasn't accounted for OOS was mistaken.
@File_Manager.Transform_Wrapper('types/TBullets.txt', 'types/TLaser.txt')
def Adjust_Weapon_OOS_Damage(
    scaling_factor = 1,

    # -Removed.
    # Multiplier to use to recreate (approximately) vanilla OOS bullet damage with
    #  ROF factored in; calibrated for HEPT (see comments at start of file).
    #  9.4k shield dps, 795 OOS shield damage value.
    # This will be used for XRM as well, since it is a general calibration to put
    #  damages where the underlying OOS combat code was built around.
    # vanilla_calibration_factor = 795 / 9400,
    
    # -Removed.
    # Set a default for all areal weapons, in case a mod mixes them up.
    # The numbers calculated below can be roughly approximated here.
    # areal_weapon_multiplier = 12,

    bullet_name_multiplier_dict = {
        # Plasma burst generator (PD).
        # Vanilla sets OOS PD shield damage = 5x HEPT, which is probably way too high.
        # In sector dps: 
        #  PD_dps_shield = 1/22 HEPT_dps_shield * number_of_hits_per_shot.
        #  PD_dps_hull   = 1/13.7  HEPT_dps_hull   * number_of_hits_per_shot.
        # If the two are assumed to be balanced on average (not just when a player is
        #  in the sweet spot), then can mult PD by 18.
        # 'SS_BULLET_PD' : 18,

        # Phased shockwave generator (PSG).
        # Compare this against Flak (same tier and anti-fighter role).
        # PSG_dps = x Flak_dps * number_of_hits_per_shot.
        #  PSG_dps_shield = 1/5.1   Flak_dps_shield * number_of_hits_per_shot.
        #  PSG_dps_hull   = 1/14.1  Flak_dps_hull   * number_of_hits_per_shot.
        # PSG does far less hull damage, so direct comparison is imperfect, but go with it.
        # 'SS_BULLET_PSG' : 9,
        
        # TODO: how to dynamically determine this:
        # PD  has areal flag set, speed 375, lifetime 2.1
        # PSG has areal flag set, speed 254, lifetime 5.7
        # It is unclear on how long the bullet might be (which is needed to know how long
        #  it will overlap a target point), what the hit rate is (time between collision 
        #  checks), and what effect the size of the target might have.
        # There may be more complicated effects as well, like having a thinner coverage on
        #  the outside of the attack cone.
        },
    ):
    '''
    Scale OOS damage. Damage may be scaled down to improve accuracy in
     combat evaluation, at the potential drawback of stalemates when shield
     regeneration outperforms damage.

    * scaling_factor:
      - The base multiplier to apply to OOS damage.
    '''
    # Step through the bullets and scale their OOS numbers.
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        if scaling_factor != 1:
            for field in ['hull_damage_oos', 'shield_damage_oos']:
                value = int(this_dict[field])
                this_dict[field] = str(round(value * scaling_factor))

    # -Removed; older code from when it was thought ROF was ignored OOS.
    # vanilla_calibration_factor:
    #     Multiplier to use to recreate (approximately) vanilla OOS bullet damage with
    #     ROF factored in; calibrated for HEPT by default.
    #     This is applied in addition to other multipliers, and can generally be
    #     left at default.
    # areal_weapon_multiplier:
    #     Weapons with areal effects (eg. plasma burst generator (PD) or phased
    #     shockwave cannon) will have an additional factor applied, 
    #     representing multiple hits per shot.
    #     Default is 12x, approximately calibrated based on vanilla areal
    #     values compared to their contemporary weapons (eg. PD vs HEPT).
    # bullet_name_hits_per_shot_dict:
    #     Dict, keyed by bullet name (eg. 'SS_BULLET_PD'), with the
    #     multiplier to apply to represent a shot hitting multiple times.
    #     This is applied in addition to scaling_factor, and will
    #     override the multiplier from areal_weapon_multiplier, to be
    #     used in customizing the number of hits per areal weapons.
    # 
    ##TODO: maybe give a selective buff to beam weapons, since they seem oddly
    ## weak in OOS combat (maybe; it is hard to say for sure without tests).
    # tbullets_dict_list = File_Manager.Load_File('types/TBullets.txt')
    # 
    #     
    ##Set up a dict which tracks modified bullets, to prevent a bullet
    ## being modded more than once by different lasers (though it might
    ## not matter if they are set instead of multiply the value).
    # bullet_indices_seen_list = []
    # 
    ##Step through each laser.
    # for laser_dict in File_Manager.Load_File('types/TLaser.txt'):
    # 
    #     #Grab the fire delay, in milliseconds.
    #     this_fire_delay = int(laser_dict['fire_delay'])
    # 
    #     #Determine fire rate, per second.
    #     fire_rate = Flags.Game_Ticks_Per_Minute / this_fire_delay / 60
    #         
    #     #Loop over the bullets created by this laser.
    #     for bullet_index in Get_Laser_Bullets(laser_dict):
    #         #Look up the bullet.
    #         bullet_dict = tbullets_dict_list[bullet_index]
    # 
    #         #Unpack the flags.
    #         flags_dict = Flags.Unpack_Tbullets_Flags(bullet_dict)
    #             
    #         #Skip if this bullet was already seen.
    #         if bullet_index in bullet_indices_seen_list:
    #             continue
    #         #Add this bullet to the seen list.
    #         bullet_indices_seen_list.append(bullet_index)
    # 
    #         #Note: if multiple lasers use the same bullet, the latest laser will
    #         # be the one whose fire_rate is used here.
    #         #Assume lasers using the same bullet are very similar to each other,
    #         # eg. the experimental aldrin weapons and terran counterparts.
    # 
    #         #Loop over the hull and shield fields, IS and OOS.
    #         for is_field, oos_field in zip(
    #             ['hull_damage', 'shield_damage'],
    #             ['hull_damage_oos', 'shield_damage_oos']):
    #                                         
    #             #Pull the IS hull/shield damage.
    #             damage_is = int(bullet_dict[is_field])
    # 
    #             #Calculate hull and shield dps for this weapon.
    #             dps_is = damage_is * fire_rate
    # 
    #             #Convert dps to OOS damage units, applying the calibrated vanilla factor
    #             # along with the extra derating factor.
    #             damage_oos = dps_is * vanilla_calibration_factor * scaling_factor
    # 
    #             #If this bullet has a special bonus multiplier, apply it,
    #             # to represent areal weapon multihit.
    #             if bullet_dict['name'] in bullet_name_multiplier_dict:
    #                 damage_oos   *= bullet_name_multiplier_dict[bullet_dict['name']]
    #             #Otherwise, if this is an areal weapon, apply its multiplier.
    #             elif flags_dict['areal']:
    #                 damage_oos *= areal_weapon_multiplier
    # 
    #             #-Removed; old version modified existing entries, but those were found to be
    #             # rotten since they had stuff like PSP doing 10x the damage of PPC.
    #             #hull_damage_oos   = int(this_list[tbullets_field_index_dict['hull_damage_oos']])
    #             #shield_damage_oos = int(this_list[tbullets_field_index_dict['shield_damage_oos']])
    #             #hull_damage_oos   = max(1, round(hull_damage_oos   * damage_factor_oos))
    #             #shield_damage_oos = max(1, round(shield_damage_oos * damage_factor_oos))
    # 
    #             #Floor at 1, and round off fraction.
    #             damage_oos   = max(1, round(damage_oos))
    # 
    #             #Put the updated value back.
    #             bullet_dict[oos_field] = str(int(damage_oos  ))



@File_Manager.Transform_Wrapper('types/TBullets.txt', 'types/TLaser.txt')
def Adjust_Weapon_DPS(
    # A flat factor to use for damage adjustment.
    # This is applied after the scaling equation below, so that that
    #  equation can be configured to the base xrm numbers.
    # Go with 2.5 to be conservative, or even 2 since some ships have more
    #  turret gun mounts than in vanilla.
    # This helps bring up energy drain as well.
    scaling_factor = 1,

    bullet_name_adjustment_dict = {},

    # If a scaling equation should be used for the damage adjustment.
    use_scaling_equation = False,
    # Set the tuning points.
    # Note: these numbers will have an implicit 10^3 factor, to avoid the
    #  scaling equation overflowing.
    damage_to_adjust_kdps = 9,
    # The damage to pin in place on the low end.
    damage_to_keep_static_kdps = 3,

    # If laser energy efficiency should be modified or not.
    maintain_energy_efficiency = True,

    # Options to change only hull or shield dps.
    adjust_hull_damage_only     = False,
    adjust_shield_damage_only   = False,

    # Don't modify repair lasers, mainly to avoid having to put this
    #  in every transform call individually, since normally these don't
    #  need modification.
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
    # Add the ignored entries if not present.
    for name in Ignored_lasers_and_bullets:
        if name not in bullet_name_adjustment_dict:
            bullet_name_adjustment_dict[name] = 1

    tbullets_dict_list = File_Manager.Load_File('types/TBullets.txt')
    
    if print_changes:
        File_Manager.Write_Summary_Line('\nDamage adjustments:')
        
    if use_scaling_equation:
        # Get formula and its coefficients here.
                    
        # Create a set of points to be tuned against.
        # The primary adjustment point.
        x_main = damage_to_adjust_kdps
        y_main = x_main * scaling_factor
        # The secondary, static point, where x=y.
        x_static = damage_to_keep_static_kdps
        y_static = damage_to_keep_static_kdps
            
        # To encourage fitting the lower end more than the higher end, can represent
        #  low end values multiple times.
        # Give two low points for now, the one provided and another nearby, to help
        #  stabalize the equation coefs.
        x_vec   = [x_main, x_static, x_static * .8]
        y_vec   = [y_main, y_static, y_static * .8]
            
        # Get the function and its coefs to use.
        shield_scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec, reversed = False)
        # Also get one for hull damage, which has lower damage values.
        x_vec = [x / Hull_to_shield_factor for x in x_vec]
        y_vec = [y / Hull_to_shield_factor for y in y_vec]
        hull_scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec, reversed = False)
    else:
        shield_scaling_func = None
        hull_scaling_func = None
        
    # Parse out the flag matches from the input dict.
    # This will pull off the 'flag_' prefix.
    # Flag ordering will be kept intact, if an ordered dict was provided.
    flag_match_dict = OrderedDict((key.replace('flag_',''), value)
                       for key,value in bullet_name_adjustment_dict.items() 
                       if key.startswith('flag_'))

    # Set up a dict which tracks modified bullets, to prevent a bullet
    #  being modded more than once by different lasers (which would cause
    #  accumulated damage buffing).
    bullet_indices_seen_list = []

    # Similar to above, need to pair lasers with bullets to get all of the necessary
    #  metrics for this calculation.
    # Step through each laser.
    for laser_dict in File_Manager.Load_File('types/TLaser.txt'):

        # Grab the fire delay, in milliseconds.
        this_fire_delay = int(laser_dict['fire_delay'])

        # Determine fire rate, per second.
        fire_rate = Flags.Game_Ticks_Per_Minute / this_fire_delay / 60            

        # Loop over the bullets created by this laser.
        for bullet_index in Get_Laser_Bullets(laser_dict):

            # Skip if this bullet was already seen.
            if bullet_index in bullet_indices_seen_list:
                continue
            # Add this bullet to the seen list.
            bullet_indices_seen_list.append(bullet_index)

            # Look up the bullet.
            bullet_dict = tbullets_dict_list[bullet_index]

            # Unpack the flags.
            flags_dict = Flags.Unpack_Tbullets_Flags(bullet_dict)

            # If ignoring repair lasers, and this is a repair weapon, skip.
            if flags_dict['repair'] and ignore_repair_lasers:
                continue
                
            # There are two options here:
            #  1) Handle shield and hull damage together, combining them into a
            #     single metric.
            #     -Drawback: a weapon like the ion cannon may be treated as a
            #     lower tier weapon due to its average shield/hull damage being
            #     much lower than its specialized shield damage.
            #  2) Handle shield and hull separately.
            #     -Drawback: it is harder to determine the energy usage adjustment
            #     if the shield/hull factors differ by much.
            #  Go with option (2), but keep some commented code left over from
            #  option (1).
                
            # -Removed; from option (1) above.
            # hull_damage       = int(bullet_dict['hull_damage'])
            # shield_damage     = int(bullet_dict['shield_damage'])                
            ##Calculate hull and shield dps for this weapon.
            # hull_dps   = hull_damage   * fire_rate
            # shield_dps = shield_damage * fire_rate
            ##Calculate overall dps, applying scaling on hull.
            ##The hull scaling
            # overall_dps = (shield_dps + hull_dps * Hull_to_shield_factor)/2

            # Keep a dict to temporarily store scaling factors.
            scaling_factor_dict = {}
            # Loop over the field types; catch the OOS field name as well for
            #  writing back the new damages later, and select the matching
            #  scaling equation.
            for field, oos_field, scaling_func in [
                        ('hull_damage'  , 'hull_damage_oos'  , hull_scaling_func),
                        ('shield_damage', 'shield_damage_oos', shield_scaling_func)]:

                # Skip hull or shield changes as requested.
                if adjust_hull_damage_only and field == 'shield_damage':
                    continue
                elif adjust_shield_damage_only and field == 'hull_damage':
                    continue

                # Look up the IS damage, and calculate dps.
                damage = int(bullet_dict[field])
                overall_dps = damage   * fire_rate

                # Skip ahead if dps is 0, eg. shield dps for mass drivers.
                if overall_dps == 0:
                    continue

                # Determine the scaling factor to apply.
                # Look up this bullet in the override dict first.
                if bullet_dict['name'] in bullet_name_adjustment_dict:
                    this_scaling_factor = bullet_name_adjustment_dict[bullet_dict['name']]

                # Look for any flag match.
                elif any(flags_dict[flag] for flag in flag_match_dict):
                    # Grab the first flag match.
                    for flag, value in flag_match_dict.items():
                        if flags_dict[flag]:
                            this_scaling_factor = value
                            break

                # If there is a wildcard use that.
                elif '*' in bullet_name_adjustment_dict:
                    this_scaling_factor = bullet_name_adjustment_dict['*']

                elif use_scaling_equation:
                    this_scaling_factor = 1
                    # Run the scaling formula.
                    # This takes in a weighted average of original shield/hull dps,
                    #  and returns the replacement dps, from which the scaling
                    #  can be calculated.
                    # This takes dps in kdps, eg. with a 10^3 implicit factor,
                    #  to avoid overflow.
                    new_overall_dps = 1e3* scaling_func(overall_dps/1e3)
                    this_scaling_factor *= new_overall_dps / overall_dps
                    
                elif scaling_factor != 1:
                    this_scaling_factor = scaling_factor
                else:
                    continue

                # Store the factor in the temp dict.
                scaling_factor_dict[field] = this_scaling_factor

                # Debug printout.
                if print_changes:
                    # Give bullet name, old and new dps,
                    #  and the scaling factor.
                    File_Manager.Write_Summary_Line(
                        '{:<30} {:<15}:  {:>10} -> {:>10}, x{}'.format(
                            bullet_dict['name'],
                            field,
                            round(overall_dps),
                            round(overall_dps * this_scaling_factor),
                            # Give only two sig digits for the scaling factor.
                            round(this_scaling_factor, 2)
                        ))

                # Apply the scaling factors to their IS and OOS fields.
                for writeback_field in [field, oos_field]:
                    value = int(bullet_dict[writeback_field])
                    bullet_dict[writeback_field] = str(int(value * this_scaling_factor))

            # If no adjustments were made to the bullet, skip ahead.
            if not scaling_factor_dict:
                continue

            # Adjust energy usage.
            # This can be done with the average of the factors or the max
            #  of the factors.
            # For specialized weapons like ion cannons, which likely had a much
            #  bigger factor on shield damage than hull damage on the expectation
            #  they will only be used against shields, it makes the most sense
            #  to adjust energy based on the biggest factor (the main use case
            #  for the weapon).
            if maintain_energy_efficiency:
                max_factor = max(scaling_factor_dict.values())
                value = int(bullet_dict['energy_used'])
                bullet_dict['energy_used'] = str(int(value * max_factor))
                
    #  Since bullet energies may have been changed, update the max laser energies.
    Floor_Laser_Energy_To_Bullet_Energy()


