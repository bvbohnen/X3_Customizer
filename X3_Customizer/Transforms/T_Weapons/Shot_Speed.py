
from ... import File_Manager
from ...Common import Flags
from ...Common import Scaling_Equations
from .Shared import *

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

@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Adjust_Weapon_Shot_Speed(
    scaling_factor = 1,
    # Special dict entries will override the above formula.
    bullet_name_adjustment_dict = {},

    # Use the formula for adjustments.
    use_scaling_equation = False,
    # Set the tuning points:
    # The target speed to adjust, in m/s.
    target_speed_to_adjust = 1400,
    # The speed to pin in place.
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
    # Add the ignored entries if not present.
    for name in Ignored_lasers_and_bullets:
        if name not in bullet_name_adjustment_dict:
            bullet_name_adjustment_dict[name] = 1

    if print_changes:
        File_Manager.Write_Summary_Line('\nShot speed adjustments:')

    # If using a formula, get it and its coefficients here.
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
            
        # Note: since speeds are kept in 500 meters/s format, need to either
        #  adjust the configuration points here, or the speeds fed to the
        #  equation further down.  Do it here to keep it simpler.
        # Give the m/s speed, scale to 500 m/s units with *500.
        x_vec   = [500*i for i in x_vec]
        y_vec   = [500*i for i in y_vec]

        # Get the function.
        scaling_func = Scaling_Equations.Get_Scaling_Fit(x_vec, y_vec)

    # Loop over the bullets.
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):

        # Unpack the flags.
        flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)

        # Always skip beam weapons, including zigzag.
        if flags_dict['beam'] or flags_dict['zigzag']:
            continue

        # If this is an areal skip it.
        if skip_areal and flags_dict['areal']:
            continue
        # Skip flak as well (maybe condition this on a setting later)
        if skip_flak and flags_dict['flak']:
            continue
                
        # Get original speed.
        speed    = int(this_dict['speed'])
                
        # Skip if bullet has no speed (eg. frag children bullets).
        if speed == 0:
            continue

        # If this bullet has a speed factor override, use it.
        if this_dict['name'] in bullet_name_adjustment_dict:
            new_speed = speed * bullet_name_adjustment_dict[this_dict['name']]
        # If there is a wildcard use that.
        elif '*' in bullet_name_adjustment_dict:
            new_speed = speed * bullet_name_adjustment_dict['*']             
        # Otherwise, if using the speed formula, calculate a new speed.
        elif use_scaling_equation:                    
            new_speed = scaling_func(speed)
        # Otherwise, apply the scaling factor if not 1.
        elif scaling_factor != 1:
            new_speed = speed * scaling_factor
        else:
            # Skip this bullet.
            continue

        # Use a shared function to apply the speed change, keeping
        #  range constant.
        Update_Bullet_Speed(this_dict, new_speed)
                
        # Debug printout.
        if print_changes:        
            # Give bullet name, old and new speed,
            #  and the scaling factor.
            File_Manager.Write_Summary_Line(
                '{:<30} : {:>10.1f} -> {:>10.1f}, x{:.2f}'.format(
                    this_dict['name'],
                    # Convert back to m/s
                    speed / 500,
                    new_speed / 500,
                    # Give only two sig digits for the scaling factor.
                    round(new_speed / speed, 2)
                ))


