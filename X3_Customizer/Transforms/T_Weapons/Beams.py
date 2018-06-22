
from ... import File_Manager
from ...Common import Flags
from .Shared import *

@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Adjust_Beam_Weapon_Duration(
    bullet_name_adjustment_dict = {},
    # Don't modify repair lasers, mainly to avoid having to put this
    #  in every transform call individually, since normally these don't
    #  need modification.
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
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)
         
        # Skip if this isn't a beam.
        if not flags_dict['beam']:
            continue
        
        # If ignoring repair lasers, and this is a repair weapon, skip.
        if flags_dict['repair'] and ignore_repair_lasers:
            continue

        # This will need to adjust the lifetime and speed again, to keep
        #  the range constant.
        # Damage does not need modification, since it is already treated
        #  as damage per shot, regardless of a beam's duration, just spread
        #  out over the duration.

        # Determine the scaling and min/max.
        if this_dict['name'] in bullet_name_adjustment_dict:
            min_seconds, factor, max_seconds = bullet_name_adjustment_dict[this_dict['name']]
        elif 'default' in bullet_name_adjustment_dict:
            min_seconds, factor, max_seconds = bullet_name_adjustment_dict['default']
        else:
            continue

        # Read the original values.
        lifetime = int(this_dict['lifetime'])
        speed    = int(this_dict['speed'])

        # Apply scaling.
        new_lifetime = lifetime * factor
        # Apply the max (in milliseconds).
        if max_seconds != None:
            new_lifetime = min(new_lifetime, max_seconds*1000)
        # Apply the min.
        if min_seconds != None:
            new_lifetime = max(new_lifetime, min_seconds*1000)

        # Speed needs the reversed scaling, since speed*lifetime = range, and
        #  want a constant range.
        #  Eg. if lifetime goes up 2x, then speed drops by 1/2.
        speed *= (lifetime / new_lifetime)
        # Put the updated values back as ints.
        this_dict['lifetime'] = str(int(new_lifetime))
        this_dict['speed']    = str(int(speed))

              
# -Removed, had no performance benefit.
# TODO: consider a general transform to change bullet length, since it
#  might be neat visually. Could limit bullet length based on fire
#  rate and speed to ensure bullets aren't longer than their spacing.
# @File_Manager.Transform_Wrapper('types/TBullets.txt')
# def Adjust_Beam_Weapon_Bullet_Length(
#     scaling_factor = 10,
#     beams_not_converted = [
#         #Don't adjust repair lasers or tractor laser.
#         'SS_BULLET_TUG',
#         'SS_BULLET_REPAIR',
#         'SS_BULLET_REPAIR2',
#         ]
#     ):
#     '''
#     Adjusts the length of beam weapon bullets. Goal is to improve
#     performance by forming beams from fewer bullet objects, on
#     the theory that few bullets do fewer collision checks.
# 
#     scaling_factor:
#         Multiplier on existing bullet length.
#     beams_not_converted:
#         List of bullet names for weapons not to be modified.
#     '''
#     #TODO: make into a generic transform with a bullet dict, and key
#     # off of a flag match.
#     for this_dict in File_Manager.Load_File('types/TBullets.txt'):
#         flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)
# 
#         #Skip non-beams.
#         if not flags_dict['beam']:
#             continue
#         
#         #Skip skipped bullets.
#         if this_dict['name'] in beams_not_converted:
#             continue
# 
#         value = float(this_dict['box_length'])
#         #Typical values are around 4 or so.
#         #Try out a super long length.
#         value *= scaling_factor
#         #Floor at 0.1 to be safe.
#         value = max(0.1, value)
#         #Put it back, with 1 decimal place.
#         this_dict['box_length'] = '{0:.1f}'.format(value)


                
@File_Manager.Transform_Wrapper('types/TBullets.txt')
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
    # TODO: consider length increases, which may have performance benefit at the
    #  drawback of beams maybe visually going through small targets slightly.
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)

        # Skip if this isn't a beam.
        if not flags_dict['beam']:
            continue

        # Determine the scaling, or skip if a scaling not found.
        if this_dict['name'] in bullet_name_adjustment_dict:
            min_val, factor, max_val = bullet_name_adjustment_dict[this_dict['name']]
        elif '*' in bullet_name_adjustment_dict:
            min_val, factor, max_val = bullet_name_adjustment_dict['*']
        else:
            continue

        # Apply to width and height.
        for field in ['box_width', 'box_height']:
            # Look up the value, apply scalings.
            value = float(this_dict[field])
            value *= factor
            if min_val != None:
                value = max(value, min_val)
            if max_val != None:
                value = min(value, max_val)
            # Put it back, with 1 decimal place.
            this_dict[field] = '{0:.1f}'.format(value)
            

# Replace beams with normal shots.
# Beam weapons in general, while cool looking, can be bad for the gameplay,
#  both due to performance issues/slowdown and due to balance issues with them
#  being too accurate, plus a general problem with player controlled beams
#  being able to be always-on, increasing dps potentially drastically.
# This will need some thought for shot speed, as well as picking the bullet
#  effect to use (the laser bullet may not be well suited to standalone
#  bullets).
@File_Manager.Transform_Wrapper('types/TBullets.txt')
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
    # Add tractor beam and repair lasers to ignored list.
    # Put there here instead of at input arg, so the user doesn't have to
    #  add them if they just want to skip some other weapon.
    # TODO: special way to identify tug lasers, if there is one, to be
    #  adaptable to mods.  Repair lasers can check their flag dict.
    beams_not_converted += ['SS_BULLET_TUG']

    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)

        # Skip non-beams.
        if not flags_dict['beam']:
            continue

        # Skip skipped bullets.
        if this_dict['name'] in beams_not_converted:
            continue
        
        # If this is a repair weapon, skip.
        if flags_dict['repair']:
            continue
        
        # -Removed; bullet length doesn't actually affect the visual
        #  at all.
        ##For visual similarity, try lengthening the shots a bunch.
        ##This would be more like star wars lasers.
        # value = float(this_dict['box_length'])
        ##Typical values are around 4 or so.
        ##Try out a super long length.
        # value *= 10
        ##Put it back, with 1 decimal place.
        # this_dict['box_length'] = '{0:.1f}'.format(value)

        # How much should shot speed be adjusted?
        # Originally, speed was only used for determining range
        #  based on lifetime.
        # Often, lifetime is much shorter on beams than it is on
        #  comperable weapons, eg. ppc lifetime is around 10x that
        #  of capital beams. This trend may not hold with weaker
        #  beams, though.
        # Just fit to similar bullets based on damage for now.
        new_speed = _Get_Bullet_Speed_By_Damage(this_dict,
                                                speed_samples,
                                                sample_type)

        # Apply the speed update, keeping range constant.
        Update_Bullet_Speed(this_dict, new_speed)
        
        # Clear the beam flag.
        # Do this after the above, so a beam isn't included in the
        #  bullet to speed analysis.
        flags_dict['beam'] = False
        Flags.Pack_Tbullets_Flags(this_dict, flags_dict)


def _Get_Average_Damage(bullet_dict):
    '''
    Support funcion to return average of hull and shield damage 
    for a bullet, scaling hull damage by Hull_to_shield_factor.
    '''
    return (int(bullet_dict['hull_damage']) * Hull_to_shield_factor 
            + int(bullet_dict['shield_damage'])) /2


# Cached sorted list for the function below.
_Bullet_damage_range_tuples = []
def _Get_Bullet_Speed_By_Damage(bullet_dict, speed_samples, sample_type):
    '''
    Support function to estimate the speed of a bullet based on its
    damage value and other similar bullets.
    '''
    # Goal is to match eg. capital ship tier bullets to other cap
    #  ship bullets.
    # This can be awkward in some cases, such as with flak, which
    #  may be outliers for damage and speed.
    # Instead of doing a match-to-nearest-damage, aim to smooth out the
    #  estimation a bit to balance outliers better.
    # Also want something simple for now, so that it is easy to set up.
    # A full linear fit across all bullets may fail to capture any
    #  nonlinearities, eg. if bullets slow by half going from small
    #  to medium, then slow by another quarter going medium to large.
    # Best approach may be to do a local fit, where the nearest
    #  X bullets are found, and a linear fit or maybe a simple averaging
    #  is done.
    # Want to avoid numpy/similar and stick to standard packages, so
    #  go with the local average idea.
    
    # Init the bullet to laser dict if needed.
    if not Bullet_to_laser_dict:
        Initialize_Bullet_to_laser_dict()

    # Select the scaling metric to use.
    def Get_Scaling_Metric(bullet_dict):

        # Start with bullet damage.
        damage = _Get_Average_Damage(bullet_dict)

        # This should be based on DPS and not bullet damage.
        # Look up the laser's fire delay.
        laser_dict = Bullet_to_laser_dict[bullet_dict['name']]

        # Grab the fire delay, in milliseconds.
        this_fire_delay = int(laser_dict['fire_delay'])
        # Scaling will be damage/delay.
        return damage / this_fire_delay

    # On first call, fill out a sorted list of bullet tuples of
    #  (scaling_metric, speed*scaling_metric, speed).
    # The multiplier simply makes range calculation later easier, since it
    #  will be focused on how speed scales with damage rather than raw speed
    #  (to be more robust), and a multiplier gives a steadier returned value
    #  since speed goes down as damage goes up.
    # The extra speed argument is simply for debug checking that results
    #  make sense.

    # Check if the dict is initialized yet.
    if not _Bullet_damage_range_tuples:
        for this_dict in File_Manager.Load_File('types/TBullets.txt'):

            # Skip beams.
            flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)
            if flags_dict['beam']:
                continue

            # Skip bullets that don't have associated lasers.
            if this_dict['name'] not in Bullet_to_laser_dict:
                continue

            # Skip some special stuff like mining lasers.
            if this_dict['name'] in ['SS_BULLET_MINING']:
                continue

            # Get the scaling meetric.
            metric = Get_Scaling_Metric(this_dict)

            # Add the tuple.
            _Bullet_damage_range_tuples.append((
                metric,
                int(this_dict['speed']) * metric,
                int(this_dict['speed'])
                ))
        
    # Skip bullets that don't have associated lasers.
    # This showed up on a Dummy beam laser in xrm.
    if bullet_dict['name'] not in Bullet_to_laser_dict:
        # Return speed unmodified.
        return int(bullet_dict['speed'])

    # There are different ways to find the nearest elements.
    # The simplest appears to be resorting the list based on how far
    #  away each tuple is from the input metric, then just take the
    #  nearst some number of elements.
    new_metric = Get_Scaling_Metric(bullet_dict)
    resorted_list = sorted(_Bullet_damage_range_tuples, 
                           key = lambda x: abs(x[0] - new_metric))

    # Average the nearest some number of items.
    # This will get the speed*metric values averaged, so is somewhat robust
    #  if the new bullet it outside the normal range of the list.
    if sample_type == 'avg':
        speed_x_metric = sum(x[1] for x in resorted_list[:speed_samples]) / speed_samples
    # The above wasn't working very well because of flak and similar.
    # Instead, take the minimum from the nearest elements, filtering
    #  out flak, and also somewhat offsetting a beam weapon's damage
    #  becoming concentrated in one ball by making it harder to hit.
    elif sample_type == 'min':
        speed_x_metric = min(x[1] for x in resorted_list[:speed_samples])
    else:
        raise Exception('Speed sample type {} not understood'.format(sample_type))

    # Can now calculate and return a speed.
    new_speed = speed_x_metric / new_metric
    return new_speed



