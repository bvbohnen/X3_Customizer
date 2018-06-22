'''
Shared functions for weapon editing.
'''
import math
from ... import File_Manager
from ...Common import Flags
from .Shared import *

# The hull to shield dps equivelence factor. Many weapons have this
#  around 5-6. This is used to set the scaling equation for hull dps,
#  where the above metrics were aimed at shield dps.
# May also be used in other transforms, so set it here for all.
Hull_to_shield_factor = 6

# Names of lasers/bullets to ignore in some cases.
# This will hold the mining and tractor beam, since there is not
#  much point to changing them in general, and the mining laser can
#  be sensetive since some ships only barely have enough energy
#  to fire it.
Ignored_lasers_and_bullets = [
    'SS_LASER_MINING',
    'SS_BULLET_MINING',
    'SS_LASER_TUG',
    'SS_BULLET_TUG',
    ]

##########################################################################################


# Record which bullets spawn which child bullets, to help with figuring out
#  all bullets spawned by a laser indirectly.
# This is keyed by parent bullet index, value is fragment index.
_Bullet_parent_to_child_dict = {}
def _Initialize_Bullet_parent_to_child_dict():
    # Loop over all bullets.
    for index, this_dict in enumerate(File_Manager.Load_File('types/TBullets.txt')):
        flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)
        # Check if this bullet fragments.
        if flags_dict['fragmentation']:
            # Record the pairing.
            _Bullet_parent_to_child_dict[index] = int(this_dict['fragment_bullet'])
            
def Get_Laser_Bullets(laser_dict):
    '''
    Determine the bullets created by this laser, directly or indirectly.
    Eg. a fragmentation chain may result in multiple bullets (eg. cluster flak).
    Returns a list of integers, the bullet indices in tbullets.
    '''
    # On first call, initialize the bullet parent/child dict.
    if not _Bullet_parent_to_child_dict:
        _Initialize_Bullet_parent_to_child_dict()

    # Get the index of the bullet this laser creates.
    this_bullet_index = int(laser_dict['bullet'])
    bullet_list = []
    # Start at the laser's initial bullet.
    current_bullet = this_bullet_index
    # Loop until no more fragments.
    while 1:
        # Record this bullet (captures the start bullet).
        bullet_list.append(current_bullet)
        # Stop if this bullet does not fragment.
        if current_bullet not in _Bullet_parent_to_child_dict:
            break
        # Proceed to the fragment bullet.
        current_bullet = _Bullet_parent_to_child_dict[current_bullet]
    return bullet_list


# Record which lasers spawn which bullets.
# If multiple lasers spawn a bullet, the first laser will be returned.
# This is keyed by parent bullet name, value is a laser dict.
Bullet_to_laser_dict = {}
def Initialize_Bullet_to_laser_dict():

    # Set up a dict which tracks seen bullets, to prevent a bullet
    #  being recorded more than once by different lasers.
    bullet_indices_seen_list = []
    tbullets_dict_list = File_Manager.Load_File('types/TBullets.txt')

    # Loop over all lasers.
    for laser_dict in File_Manager.Load_File('types/TLaser.txt'):
        # Loop over the bullets created by this laser.
        for bullet_index in Get_Laser_Bullets(laser_dict):
            # Look up the bullet.
            bullet_dict = tbullets_dict_list[bullet_index]
                
            # Skip if this bullet was already seen.
            if bullet_index in bullet_indices_seen_list:
                continue
            # Add this bullet to the seen list.
            bullet_indices_seen_list.append(bullet_index)
            # Record the laser.
            Bullet_to_laser_dict[bullet_dict['name']] = laser_dict
    return



def Floor_Laser_Energy_To_Bullet_Energy():
    '''
    Support transform which will ensure the amount of energy stored
    by a laser is enough to fire at least one bullet.
    For use when bullet energy is modified, possibly beyond the laser
    energy cap.
    '''
    tbullets_dict_list = File_Manager.Load_File('types/TBullets.txt')
    #  Step through each laser.
    for laser_dict in File_Manager.Load_File('types/TLaser.txt'):

        #  Grab the max laser energy storage.
        laser_energy = int(laser_dict['max_energy'])
        
        #  Look up the primary bullet to be fired.
        #  Extra child bullets shouldn't matter here.
        this_bullet_index = int(laser_dict['bullet'])
        bullet_dict = tbullets_dict_list[this_bullet_index]

        #  Get the bullet required energy.
        bullet_energy = int(bullet_dict['energy_used'])

        #  If needed, upscale the laser storage.
        if laser_energy < bullet_energy:
            laser_dict['max_energy'] = str(bullet_energy)

    return


def Update_Bullet_Speed(bullet_dict, new_speed):
    '''
    Support function to modify a bullet to have a new speed, while
    keeping range constant through a lifetime adjustment.
    '''
    # Look up the original lifetime and speed.
    speed    = int(bullet_dict['speed'])
    lifetime = int(bullet_dict['lifetime'])

    # Round speed to nearest 10 for nicer looking number in game.
    # Round up in case a bullet is really slow.
    # Bullet speeds are in units of 500 ticks per meter, so
    #  would need to round to nearest 5000 to get this to-10 effect.
    new_speed = math.ceil(new_speed/5000)*5000         

    # Calculate a new lifetime so that range remains unchanged.
    # Ranges in game are not generally rounded, so don't bother with
    #  making that look nice here.
    new_lifetime = lifetime * speed / new_speed

    # Put them back, rounded.
    bullet_dict['speed'] = str(int(new_speed))
    bullet_dict['lifetime'] = str(int(new_lifetime))
