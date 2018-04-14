'''
Transforms to missiles.
'''
'''
Similar to X3_Weapons, this will open the Tmissiles file and perform systematic edits.
Initial functions:
-Reduce damage of all missiles following a diminishing returns formula.
-Selectively edit mosquito missiles to make them better at interception.


Damage reduction was done using a global formula, to reduce bias against
particular missiles.
Different formulas were tried out with spreadsheet help.
The basic formula type was:
 dam_new = ((dam_old / pow) * ref) / ((dam_old / pow) + ref) * pow
 where pow = 10, ref = 25
The idea was to apply a general damage scaler, use a D*X/D+X formula,
 and scale it back. This may not be the best scaling equation, but seems
 to work out.
The old damage used a couple adjustments:
 -Translated into e3 scale before formula, eg 1k damage = 1.
 -If multi-warhead, multiply by 8 before the formula.
 -Undo adjustments at the end, and round to nearest 100 or 1000 (hand selected).
 -Optionally ignore missiles under 10k damage.
These changes will be recalculated and applied here.

TODO: consider moving to a simpler formula: x*w*(y/(x+y))^z, which can be optimized
 for a few select desired scaling points (3 points should be fine, 
 coving high/low/med).
 See X3_test module for some code to optimize this quickly.


'''
from File_Manager import *
from . import Scaling_Equations
from Common import Flags

# TODO: add cargo volume adjustment, so that ships with
#  heavily weakened missiles get more of them to fire before running
#  out.
@Check_Dependencies('types/Globals.txt', 'types/TMissiles.txt')
def Adjust_Missile_Damage(
    scaling_factor = 1,
    # If diminishing returns should be used, so that low damage
    #  missiles are less affected.
    use_scaling_equation = False,
    # Set the tuning points.
    # The target damage to adjust. About 1000000 for super heavy missiles.
    target_damage_to_adjust = 1000000,
    # The damage to pin in place on the low end, about 10000.
    damage_to_keep_static = 10000,
    adjust_volume = False,
    adjust_price = False,
    mosquito_safety_cap = True,
    print_changes = False
    ):
    '''
    Adjust missile damage values, by a flat scaler or configured
    scaling formula. 
    
    * scaling_factor:
      - The base multiplier to apply to missile damage.
    * use_scaling_equation:
      - If True, a scaling formula will be applied, such that missiles
        near target_damage_to_adjust see the full scaling_factor,
        and missiles near damage_to_keep_static remain largely unchanged.
        Otherwise, scaling_factor is applied to all missiles.
    * target_damage_to_adjust, damage_to_keep_static:
      - Equation tuning values.
    * adjust_volume:
      - If True, cargo volume is adjusted corresponding to damage.
        Defaults False.
    * adjust_price:
      - If True, price is adjusted corresponding to damage.
        Defaults False.
    * mosquito_safety_cap
      - If True, mosquito missiles will be capped at 350
        damage, below the cutoff point (400) for usage in OOS combat.
        Defaults True.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.
    '''
    
    if print_changes:
        Write_Summary_Line('\nMissile damage adjustments:')
        
    if use_scaling_equation:
        # Create a set of points to be tuned against.
        # The primary adjustment point.
        x_main = target_damage_to_adjust
        y_main = x_main * scaling_factor
        # The secondary, static point, where x=y.
        x_static = damage_to_keep_static
        y_static = damage_to_keep_static
            
        # To encourage fitting the lower end more than the higher end, can represent
        #  low end values multiple times.
        # Give two low points for now, the one provided and another nearby, to help
        #  stabalize the equation coefs.
        x_vec   = [x_main, x_static, x_static * .8]
        y_vec   = [y_main, y_static, y_static * .8]
            
        # Get the function.
        scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec)

    # Grab the number of missiles in each swarm volley, read from Globals.
    for this_dict in Load_File('types/Globals.txt'):
        if this_dict['name'] == 'SG_MISSILE_SWARM_COUNT':
            num_multishot_missiles = int(this_dict['value'])
            break

    # Step through each missile.
    for this_dict in Load_File('types/TMissiles.txt'):

        damage = int(this_dict['damage'])

        # Determine if this is a multishot missile.
        flags_dict = Flags.Unpack_Tmissiles_Flags(this_dict)
        multishot = flags_dict['fragmentation']
        
        # If damage is low, do not do adjustment.
        # Eg. boarding pod is 5 damage, and dont want it getting rounded away.
        if damage < 1000:
            new_damage_round = damage

        else:
            # -Removed; use a proper scaling eq, and don't do the /1000 scaling
            #  since it shouldn't be needed. This also didn't handle the flat
            #  scaling factor well.
            # if 0:
            #     #Rescale to the 1e3
            #     damage_e3 = damage / 1000
            # 
            #     #Apply the scaling factor.
            #     damage_e3 *= scaling_factor
            # 
            #     #Apply the diminishing returns formula as requested.
            #     if use_scaling_equation:
            #         #Prebuff damage for multishot missiles.
            #         if multishot:
            #             damage_e3 *= num_multishot_missiles
            # 
            #         #Run the formula.
            #         pow = 10
            #         ref = 25
            #         damage_e3 = (damage_e3 / pow * ref) / ((damage_e3 / pow) + ref) * pow
            # 
            #     #Remove the e3 scaling.
            #     new_damage_old_style = damage_e3 * 1000

                
            # Adjust the damage, using equation or flat factor.
            if use_scaling_equation:
                # Prebuff damage for multishot missiles.
                multishot_damage = damage
                if multishot:
                    multishot_damage *= num_multishot_missiles
                # Run the scaling func.
                new_damage = scaling_func(multishot_damage)
                # Remove the multishot scaling.
                if multishot:
                    new_damage /= num_multishot_missiles
            else:
                new_damage = damage * scaling_factor


            # Round to the nearest 1k if the missile is >=10k , else to nearest 100.
            if new_damage > 10000:
                # Clumsy way to do this, but should work to just divide down, round off
                #  the decimal, and multiply back up.
                new_damage_round = round(new_damage / 1000)*1000
            else:
                new_damage_round = round(new_damage / 100)*100

            # Cap mosquitos.
            if mosquito_safety_cap and this_dict['subtype'] == 'SG_MISSILE_COUNTER':
                #  In the lib.get.best.missile.for.target script, any missiles
                #  below 400 damage are ignored for OOS selection.
                # If a missile is picked for OOS combat, the ship will not
                #  fire its lasers that turn, which makes it rather harmful
                #  for mosquitos to get picked.
                # Capping mosquito damage should avoid this problem.
                # Can go up to 399, but use 350 for a nicer looking number.
                new_damage_round = min(350, new_damage_round)

            # Put the value back.
            this_dict['damage'] = str(int(new_damage_round))

            # Based on the new/old damage ratio, maybe adjust volumne and
            #  price if requested.
            if adjust_volume:
                volume = int(this_dict['volume'])
                # Ensure volume stays at least 1.
                new_volume = max(1, volume * new_damage_round / damage)
                this_dict['volume'] = str(int(new_volume))
                
            if adjust_price:
                for field in ['relative_value_npc', 'relative_value_player']:
                    value = int(this_dict[field])
                    new_value = max(1, value * new_damage_round / damage)
                    this_dict[field] = str(int(new_value))


        # Debug printout.
        # Give missile name, old and new damage,
        #  and the scaling factor.
        if print_changes:
            Write_Summary_Line('{:<30} : {:>10} -> {:>10}, x{}'.format(
                this_dict['name'],
                damage,
                new_damage_round,
                # Give only two sig digits for the scaling factor.
                round(new_damage_round / damage, 2)
                ))

    return
            
            
@Check_Dependencies('types/TMissiles.txt')
def Enhance_Mosquito_Missiles(
    acceleration_factor = 5,
    turn_rate_factor = 10,
    proximity_meters = 30
    ):
    '''
    Makes mosquito missiles more maneuverable, generally by increasing
    the turn rate or adding blast radius, to make anti-missile 
    abilities more reliable.

    * acceleration_factor:
      - Multiplier to the mosquito's acceleration.
    * turn_rate_factor:
      - Multiplier to the mosquito's turn rate.
    * proximity_meters:
      - If not 0, adds a proximity fuse with the given distance.
        For comparison, vanilla Silkworm missiles have a 200 meter radius.
    '''
    # TODO: maybe also add a damage boost option, so they can kill
    #  fighter drones properly in XRM, where for some reason it takes
    #  multiple mosquitos. The base game files don't make the problem
    #  obvious since drones have 10 health, mosquitos have 200 damage.
    #  This cannot go >= 400 without OOS problems, though.

    # Step through each missile.
    for this_dict in Load_File('types/TMissiles.txt'):
        # Determine if this is a mosquito missile.
        if this_dict['model_scene'] == 'weapons\missiles\Mosquito_IR':
            # The general problem is when a mosq orbits another missile that it is
            #  trying to hit, never quite landing.
            # Can either aim to improve turning, or try to add a proximity fuse
            #  with a blast radius.
            # Acceleration may also help depending on how the game handles max
            #  speed turning. Update: acceleration probably does nothing.
            acceleration = int(this_dict['acceleration']) * acceleration_factor
            this_dict['acceleration'] = str(int(acceleration))
            for field in ['rotation_x','rotation_x']:
                value = float(this_dict[field]) * turn_rate_factor
                this_dict[field]   = str(value)

            if proximity_meters != 0:
                # Get the flags.
                flags_dict = Flags.Unpack_Tmissiles_Flags(this_dict)
                # Turn on proximity detonation.
                flags_dict['proximity'] = True
                Flags.Pack_Tmissiles_Flags(this_dict, flags_dict)
                # Set the proximity distance.
                # This is in 500 units per meter.
                this_dict['blast_radius'] = str(int(proximity_meters * 500))

            break
    return


 
# -Removed for now; mostly just adds clutter, and didn't work well for
#  xrm, probably since trails were edited such that the original ap
#  trail isn't present at the original index.
# @Check_Dependencies('types/TMissiles.txt')
# def Restore_Heavy_Missile_Trail():
#     '''
#     Minor transform to set heavy missile trails to those in vanilla AP.
#     '''
#     #Step through each missile.
#     for this_dict in Load_File('types/TMissiles.txt'):
#         #Check if this is a missile to restore.
#         if this_dict['name'] in ['SS_MISSILE_TORP_CAPITAL']:
#             #The vanilla game gives a trail effect of 167.
#             #TODO: verify this works.
#             this_dict['trail_effect'] = str(167)
#             break
            


# XRM increases speeds, eg wasp being 834 instead of 560, which could
#  afford to be reduced back down (since wasp appears to have better
#  rpm for landing hits anyway).
@Check_Dependencies('types/TMissiles.txt')
def Adjust_Missile_Speed(
    # The adjustment factor. -25% felt like too little, so try -50%.
    scaling_factor = 0.5,
    # If diminishing returns should be used, so that short range
    #  missiles are less affected.
    use_scaling_equation = False,
    # Set the tuning points.
    # The target speed to adjust, in dps. About 700+ on fast missiles.
    target_speed_to_adjust = 700,
    # The speed to pin in place on the low end.
    speed_to_keep_static = 150,
    print_changes = False
    ):
    '''
    Adjust missile speeds, by a flat scaler or configured
    scaling formula.
    
    * scaling_factor:
      - The base multiplier to apply to missile speeds.
    * use_scaling_equation:
      - If True, a scaling formula will be applied, such that missiles
        near target_speed_to_adjust see the full scaling_factor,
        and missiles near speed_to_keep_static remain largely unchanged.
        Otherwise, scaling_factor is applied to all missiles.
    * target_speed_to_adjust, speed_to_keep_static:
      - Equation tuning values, in m/s.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.
    '''
    if print_changes:
        Write_Summary_Line('\nMissile speed adjustments:')

    if use_scaling_equation:
        # Create a set of points to be tuned against.
        # The primary adjustment point.
        x_main = target_speed_to_adjust
        y_main = x_main * scaling_factor
        # The secondary, static point, where x=y.
        x_static = speed_to_keep_static
        y_static = speed_to_keep_static
            
        # To encourage fitting the lower end more than the higher end, can represent
        #  low end values multiple times.
        # Give two low points for now, the one provided and another nearby, to help
        #  stabalize the equation coefs.
        x_vec   = [x_main, x_static, x_static * .8]
        y_vec   = [y_main, y_static, y_static * .8]
            
        # Get the function.
        scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec)
        
    # Step through each missile.
    for this_dict in Load_File('types/TMissiles.txt'):

        # Get speed in m/s, using /500 factor.
        speed = int(this_dict['speed']) / 500
        
        # Adjust the range, using equation or flat factor.
        if use_scaling_equation:
            new_speed = scaling_func(speed)
        else:
            new_speed = speed * scaling_factor

        # To keep range unchanged, boost lifetime by a corresponding amount.
        lifetime = int(this_dict['lifetime'])
        new_lifetime = lifetime * speed / new_speed

        # Adjust acceleration proportional with speed.
        acceleration = int(this_dict['acceleration'])
        new_acceleration = acceleration * new_speed / speed

        # Put speed back with *500 factor.
        this_dict['speed']    = str(int(new_speed * 500))
        this_dict['acceleration'] = str(int(new_acceleration))
        this_dict['lifetime'] = str(int(new_lifetime))
        
        # Debug printout.
        # Give missile name, old and new value,
        #  and the scaling factor.
        if print_changes:
            Write_Summary_Line('{:<30} : {:>10.2f} -> {:>10.2f}, x{}'.format(
                this_dict['name'],
                speed,
                new_speed,
                # Give only two sig digits for the scaling factor.
                round(new_speed / speed, 2)
                ))
            
    return
            
            
@Check_Dependencies('types/TMissiles.txt')
def Adjust_Missile_Range(
    # The adjustment factor. Cut in half for now.
    # -Half feels about right in game.
    scaling_factor = 0.5,
    # If diminishing returns should be used, so that short range
    #  missiles are less affected.
    use_scaling_equation = False,
    # Set the tuning points.
    # The target range to adjust, in km. About 50km+ and longer missiles.
    target_range_to_adjust_km = 50,
    # The range to pin in place on the low end, about 10km.
    range_to_keep_static_km = 10,
    print_changes = False
    ):
    '''
    Adjust missile range by changing lifetime, by a flat scaler or
    configured scaling formula.
    This is particularly effective for the re-lock missiles like flail,
    to reduce their ability to keep retargetting across a system,
    instead running out of fuel from the zigzagging.
     
    * scaling_factor:
      - The base multiplier to apply to missile range.
    * use_scaling_equation:
      - If True, a scaling formula will be applied, such that missiles
        near target_range_to_adjust_km see the full scaling_factor,
        and missiles near range_to_keep_static_km remain largely unchanged.
        Otherwise, scaling_factor is applied to all missiles.
    * target_range_to_adjust_km, range_to_keep_static_km:
      - Equation tuning values, in kilometers.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.
    '''
    if print_changes:
        Write_Summary_Line('\nMissile range adjustments:')
        
    if use_scaling_equation:
        # Create a set of points to be tuned against.
        # The primary adjustment point.
        x_main = target_range_to_adjust_km
        y_main = x_main * scaling_factor
        # The secondary, static point, where x=y.
        x_static = range_to_keep_static_km
        y_static = range_to_keep_static_km
            
        # To encourage fitting the lower end more than the higher end, can represent
        #  low end values multiple times.
        # Give two low points for now, the one provided and another nearby, to help
        #  stabalize the equation coefs.
        x_vec   = [x_main, x_static, x_static * .8]
        y_vec   = [y_main, y_static, y_static * .8]
            
        # Get the function.
        scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec)
        
    # Step through each missile.
    for this_dict in Load_File('types/TMissiles.txt'):

        # Calculate original range from speed and lifetime.
        speed = int(this_dict['speed'])
        lifetime = int(this_dict['lifetime'])

        # Translate to km, where speed was meters per 500 s and
        #  lifetime was in ms.
        range_km = speed * lifetime / 500 / 1000 / 1000

        # Adjust the range, using equation or flat factor.
        if use_scaling_equation:
            new_range_km = scaling_func(range_km)
        else:
            new_range_km = range_km * scaling_factor

        # Apply new range by adjusting lifetime.
        new_lifetime = lifetime * new_range_km / range_km
        this_dict['lifetime'] = str(int(new_lifetime))
        
        # Debug printout.
        # Give missile name, old and new range,
        #  and the scaling factor.
        if print_changes:
            Write_Summary_Line('{:<30} : {:>10.2f} -> {:>10.2f}, x{}'.format(
                this_dict['name'],
                range_km,
                new_range_km,
                # Give only two sig digits for the scaling factor.
                round(new_range_km / range_km, 2)
                ))

    return