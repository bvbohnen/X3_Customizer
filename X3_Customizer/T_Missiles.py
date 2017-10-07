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
import Scaling_Equations
import Flags


@Check_Dependencies('Globals.txt', 'TMissiles.txt')
def Adjust_Missile_Damage(
    scaling_factor = 1,
    #If diminishing returns should be used, so that short range
    # missiles are less affected.
    use_diminishing_returns = False,
    print_changes = False
    ):
    '''
    Adjust missile damage values.
    The scaling_factor is applied prior to the diminishing returns
     formula.

    * use_diminishing_returns:
      - If True, a hardcoded diminishing returns formula is applied 
        which reduces heavy missile damage by up to ~80%,
        while keeping small missiles unchanged.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.
    '''
    #TODO: support setting the scaling equation tuning factors.
    
    if print_changes:
        Write_Summary_Line('\nMissile damage adjustments:')

    #Grab the number of missiles in each swarm volley, read from Globals.
    for this_dict in Load_File('Globals.txt'):
        if this_dict['name'] == 'SG_MISSILE_SWARM_COUNT':
            num_multishot_missiles = int(this_dict['value'])
            break

    #Step through each missile.
    for this_dict in Load_File('TMissiles.txt'):

        damage = int(this_dict['damage'])

        #Determine if this is a multishot missile.
        flags_dict = Flags.Unpack_Tmissiles_flags(this_dict['flags'])
        multishot = flags_dict['fragmentation']
        
        #If damage is low, do not do adjustment.
        #Eg. boarding pod is 5 damage, and dont want it getting rounded away.
        if damage < 1000:
            new_damage_round = damage

        else:
            #Rescale to the 1e3
            damage_e3 = damage / 1000

            #Apply the scaling factor.
            damage_e3 *= scaling_factor

            #Apply the diminishing returns formula as requested.
            if use_diminishing_returns:
                #Prebuff damage for multishot missiles.
                if multishot:
                    damage_e3 *= num_multishot_missiles

                #Run the formula.
                pow = 10
                ref = 25
                damage_e3 = (damage_e3 / pow * ref) / ((damage_e3 / pow) + ref) * pow

            #Remove the e3 and multishot scalings.
            new_damage = damage_e3 * 1000
            if multishot:
                new_damage /= num_multishot_missiles

            #Round to the nearest 1k if the missile is >=10k , else to nearest 100.
            if new_damage > 10000:
                #Clumsy way to do this, but should work to just divide down, round off
                # the decimal, and multiply back up.
                new_damage_round = round(new_damage / 1000)*1000
            else:
                new_damage_round = round(new_damage / 100)*100

            #Put the value back.
            this_dict['damage'] = str(int(new_damage_round))

        #Debug printout.
        #Give missile name, old and new damage,
        # and the scaling factor.
        if print_changes:
            Write_Summary_Line('{:<30} : {:>10} -> {:>10}, x{}'.format(
                this_dict['name'],
                damage,
                new_damage_round,
                #Give only two sig digits for the scaling factor.
                round(new_damage_round / damage, 2)
                ))

            
            
@Check_Dependencies('TMissiles.txt')
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
    #TODO: maybe also add a damage boost option, so they can kill
    # fighter drones properly in XRM, where for some reason it takes
    # multiple mosquitos. The base game files don't make the problem
    # obvious since drones have 10 health, mosquitos have 200 damage.

    #Step through each missile.
    for this_dict in Load_File('TMissiles.txt'):
        #Determine if this is a mosquito missile.
        if this_dict['model_scene'] == 'weapons\missiles\Mosquito_IR':
            #The general problem is when a mosq orbits another missile that it is
            # trying to hit, never quite landing.
            #Can either aim to improve turning, or try to add a proximity fuse
            # with a blast radius.
            #Acceleration may also help depending on how the game handles max
            # speed turning. Update: acceleration probably does nothing.
            acceleration = int(this_dict['acceleration']) * acceleration_factor
            this_dict['acceleration'] = str(int(acceleration))
            for field in ['rotation_x','rotation_x']:
                value = float(this_dict[field]) * turn_rate_factor
                this_dict[field]   = str(value)

            if proximity_meters != 0:
                #Get the flags.
                flags_dict = Flags.Unpack_Tmissiles_flags(this_dict['flags'])
                #Turn on proximity detonation.
                flags_dict['proximity'] = True
                this_dict['flags'] = Flags.Pack_Flags(flags_dict)
                #Set the proximity distance.
                #This is in 500 units per meter.
                this_dict['blast_radius'] = str(int(proximity_meters * 500))

            return


        
@Check_Dependencies('TMissiles.txt')
def Restore_Heavy_Missile_Trail():
    '''
    Minor transform to set heavy missile trails to those in vanilla AP.
    '''
    #Step through each missile.
    for this_dict in Load_File('TMissiles.txt'):
        #Check if this is a missile to restore.
        if this_dict['name'] in ['SS_MISSILE_TORP_CAPITAL']:
            #The vanilla game gives a trail effect of 167.
            #TODO: verify this works.
            this_dict['trail_effect'] = str(167)
            break
            


#XRM increases speeds, eg wasp being 834 instead of 560, which could
# afford to be reduced back down (since wasp appears to have better
# rpm for landing hits anyway).
@Check_Dependencies('TMissiles.txt')
def Adjust_Missile_Speed(
    #The adjustment factor. -25% felt like too little, so try -50%.
    scaling_factor = 0.5,
    #If diminishing returns should be used, so that short range
    # missiles are less affected.
    use_diminishing_returns = False,
    #Set the tuning points.
    #The target speed to adjust, in dps. About 700+ on fast missiles.
    target_speed_to_adjust = 700,
    #The speed to pin in place on the low end.
    speed_to_keep_static = 150,
    print_changes = False
    ):
    '''
    Adjust missile speeds.

    * use_diminishing_returns:
      - If True, this will attempt to adjust missiles with a speed near 
      target_speed_to_adjust by the scaling_factor, while missiles with a 
      speed near speed_to_keep_static will be kept largely unchanged.
      Otherwise, scaling_factor is applied to all missiles.
    * target_speed_to_adjust, speed_to_keep_static:
      - Equation tuning values, in m/s.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.
    '''
    if print_changes:
        Write_Summary_Line('\nMissile speed adjustments:')

    if use_diminishing_returns:
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
            
        #Get the function.
        scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec)
        
    #Step through each missile.
    for this_dict in Load_File('TMissiles.txt'):

        #Get speed in m/s, using /500 factor.
        speed = int(this_dict['speed']) / 500
        
        #Adjust the range, using equation or flat factor.
        if use_diminishing_returns:
            new_speed = scaling_func(speed)
        else:
            new_speed = speed * scaling_factor

        #To keep range unchanged, boost lifetime by a corresponding amount.
        lifetime = int(this_dict['lifetime'])
        new_lifetime = lifetime * speed / new_speed

        #Put speed back with *500 factor.
        this_dict['speed']    = str(int(new_speed * 500))
        this_dict['lifetime'] = str(int(new_lifetime))
        
        #Debug printout.
        #Give missile name, old and new value,
        # and the scaling factor.
        if print_changes:
            Write_Summary_Line('{:<30} : {:>10.2f} -> {:>10.2f}, x{}'.format(
                this_dict['name'],
                speed,
                new_speed,
                #Give only two sig digits for the scaling factor.
                round(new_speed / speed, 2)
                ))
            
            
@Check_Dependencies('TMissiles.txt')
def Adjust_Missile_Range(
    #The adjustment factor. Cut in half for now.
    #-Half feels about right in game.
    scaling_factor = 0.5,
    #If diminishing returns should be used, so that short range
    # missiles are less affected.
    use_diminishing_returns = False,
    #Set the tuning points.
    #The target range to adjust, in km. About 50km+ and longer missiles.
    target_range_to_adjust_km = 50,
    #The range to pin in place on the low end, about 10km.
    range_to_keep_static_km = 10,
    print_changes = False
    ):
    '''
    Adjust missile range/lifetime.
    This is particularly effective for the re-lock missiles like flail,
     to reduce their ability to just keep retargetting across a system,
     instead running out of fuel from the zigzagging.
     
    * use_diminishing_returns:
      - If True, this will attempt to adjust missiles with a range near 
      target_range_to_adjust_km by the scaling_factor, while missiles with a 
      range near range_to_keep_static_km will be kept largely unchanged.
      Otherwise, scaling_factor is applied to all missiles.
    * target_range_to_adjust_km, range_to_keep_static_km:
      - Equation tuning values, in kilometers.
    * print_changes:
      - If True, speed adjustments are printed to the summary file.
    '''
    if print_changes:
        Write_Summary_Line('\nMissile range adjustments:')
        
    if use_diminishing_returns:
        #Create a set of points to be tuned against.
        #The primary adjustment point.
        x_main = target_range_to_adjust_km
        y_main = x_main * scaling_factor
        #The secondary, static point, where x=y.
        x_static = range_to_keep_static_km
        y_static = range_to_keep_static_km
            
        #To encourage fitting the lower end more than the higher end, can represent
        # low end values multiple times.
        #Give two low points for now, the one provided and another nearby, to help
        # stabalize the equation coefs.
        x_vec   = [x_main, x_static, x_static * .8]
        y_vec   = [y_main, y_static, y_static * .8]
            
        #Get the function.
        scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec)
        
    #Step through each missile.
    for this_dict in Load_File('TMissiles.txt'):

        #Calculate original range from speed and lifetime.
        speed = int(this_dict['speed'])
        lifetime = int(this_dict['lifetime'])

        #Translate to km, where speed was meters per 500 s and
        # lifetime was in ms.
        range_km = speed * lifetime / 500 / 1000 / 1000

        #Adjust the range, using equation or flat factor.
        if use_diminishing_returns:
            new_range_km = scaling_func(range_km)
        else:
            new_range_km = range_km * scaling_factor

        #Apply new range by adjusting lifetime.
        new_lifetime = lifetime * new_range_km / range_km
        this_dict['lifetime'] = str(int(new_lifetime))
        
        #Debug printout.
        #Give missile name, old and new range,
        # and the scaling factor.
        if print_changes:
            Write_Summary_Line('{:<30} : {:>10.2f} -> {:>10.2f}, x{}'.format(
                this_dict['name'],
                range_km,
                new_range_km,
                #Give only two sig digits for the scaling factor.
                round(new_range_km / range_km, 2)
                ))

