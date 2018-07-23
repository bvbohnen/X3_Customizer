
from ... import File_Manager
from ...Common import Flags
from .Shared import *

@File_Manager.Transform_Wrapper('types/TBullets.txt')
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
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):        
        # Pull the hull/shield damage.
        hull_damage       = int(this_dict['hull_damage'])
        hull_damage_oos   = int(this_dict['hull_damage_oos'])
        shield_damage     = int(this_dict['shield_damage'])

        # Set an adjustment ratio if the hull damage is too low.
        if hull_damage < minimum_ratio * shield_damage:
            ratio = minimum_ratio * shield_damage / hull_damage

            # Apply the ratio to IS and OOS damage.            
            # Modify and round, minimum of 1.
            hull_damage     = round(hull_damage     * ratio)
            hull_damage_oos = round(hull_damage_oos * ratio)
            # Put back.
            this_dict['hull_damage']       = str(int( hull_damage ))
            this_dict['hull_damage_oos']   = str(int( hull_damage_oos ))


@File_Manager.Transform_Wrapper('types/TBullets.txt')
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
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        if impact_replacement != None:
            this_dict['impact_effect'] = str(impact_replacement)
        if launch_replacement != None:
            this_dict['launch_effect'] = str(launch_replacement)

            
@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Remove_Weapon_Shot_Sound():
    '''
    Removes impact sound from bullets.
    Little performance benefit expected, though untested.
    '''
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        # Simply set to 0 appears as if it will quiet the bullet.
        # Note: untested.
        this_dict['impact_sound'] = '0'

            
@File_Manager.Transform_Wrapper('types/TBullets.txt')
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
    # TODO: maybe add per-bullet support.
    # Stop early if factors are at defaults.
    if lifetime_scaling_factor == 1 and speed_scaling_factor == 1:
        return
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        # Read the original values.
        lifetime = int(this_dict['lifetime'])
        speed    = int(this_dict['speed'])
        # Apply scaling.
        lifetime *= lifetime_scaling_factor
        speed    *= speed_scaling_factor
        # Put the updated values back as ints.
        this_dict['lifetime'] = str(int(lifetime))
        this_dict['speed']    = str(int(speed))

            
        
@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Adjust_Weapon_Energy_Usage(
    scaling_factor = 1,
    bullet_name_multiplier_dict = {},
    # Don't modify repair lasers, mainly to avoid having to put this
    #  in every transform call individually, since normally these don't
    #  need modification.
    ignore_repair_lasers = True,
    
    ):
    '''
    Adjusts weapon energy usage by the given multiplier, globally or
    for selected bullets.

    * scaling_factor:
      - Multiplier to apply to all weapons without specific settings.
    * bullet_name_energy_dict:
      - Dict, keyed by bullet name (eg. 'SS_BULLET_MASS'), with the
        multiplier to apply. This will override scaling_factor for
        this weapon.
    * ignore_repair_lasers:
      - Bool, if True (default) then repair lasers will be ignored.
    '''
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        
        if this_dict['name'] in bullet_name_multiplier_dict or scaling_factor != 1:

            # If ignoring repair lasers, and this is a repair weapon, skip.
            flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)
            if flags_dict['repair'] and ignore_repair_lasers:
                continue

            energy = int(this_dict['energy_used'])

            # Pick the table or default multiplier.
            if this_dict['name'] in bullet_name_multiplier_dict:
                multiplier = bullet_name_multiplier_dict[this_dict['name']]
            else:
                multiplier = scaling_factor

            new_energy = energy * multiplier
            this_dict['energy_used'] = str(int(new_energy))

    #  Since bullet energies were changed, update the max laser energies.
    Floor_Laser_Energy_To_Bullet_Energy()
    

# Id integers for various named ammos.
# TODO: maybe set up a generalized table of item names to id codes, perhaps
#  autogenerating it from game files to be used as documentation.
# It looks like perhaps anything can be used as ammo, perhaps with the game just 
#  checking for this item in inventory and decrementing by 1 for every 200 shots.
# There may be interesting opportunities to make stuff like energy cells into ammo.
Ammo_name_id_dict = {
    'Mass Driver Ammunition': 42,
    }

@File_Manager.Transform_Wrapper('types/TBullets.txt')
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
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        if this_dict['name'] in bullet_name_ammo_dict:
            flags_dict = Flags.Unpack_Tbullets_Flags(bullet_dict)

            # Clear the ammo flag.
            flags_dict['use_ammo'] = False
            # Copy over the energy value to use. 
            # TODO: maybe do some sanity check on this.
            new_energy = bullet_name_ammo_dict[this_dict['name']]

            # Put new values back.
            Flags.Pack_Tbullets_Flags(this_dict, flags_dict)
            this_dict['energy_used'] = str(int(new_energy))

    #  Since bullet energies were changed, update the max laser energies.
    Floor_Laser_Energy_To_Bullet_Energy()

            
@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Convert_Weapon_To_Ammo(
    bullet_name_ammo_dict = {},
    energy_reduction_factor = 0.1
    ):
    '''
    Converts the given weapons, determined by bullet type, to use ammunition
    instead of energy.

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
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):

        if this_dict['name'] in bullet_name_ammo_dict:
            flags_dict = Flags.Unpack_Tbullets_Flags(bullet_dict)
            
            # Set the ammo flag.
            flags_dict['use_ammo'] = True

            # Cut the energy.
            energy = int(this_dict['energy_used'])
            new_energy = energy * energy_reduction_factor

            # Look up an ammo type code if an item name given.
            ammo_type = bullet_name_ammo_dict[this_dict['name']]
            if isinstance(ammo_type, str):
                ammo_type = Ammo_name_id_dict[ammo_type]

            # Set the ammo type.
            this_dict['ammo_type'] = str(ammo_type)

            # Put new values back.
            Flags.Pack_Tbullets_Flags(this_dict, flags_dict)
            this_dict['energy_used'] = str(int(new_energy))
            
    #  Since bullet energies were changed, update the max laser energies.
    Floor_Laser_Energy_To_Bullet_Energy()

            
@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Clear_Weapon_Flag(flag_name):
    '''
    Clears a specified flag from all weapons.

    * flag_name:
      - Bullet property flag name, as found in Flags.py. Eg. 'charged'.
    '''
    for this_dict in File_Manager.Load_File('types/TBullets.txt'):
        # Look up the flag, and set to False.
        flags_dict = Flags.Unpack_Tbullets_Flags(this_dict)
        assert flag_name in flags_dict
        flags_dict[flag_name] = False
        Flags.Pack_Tbullets_Flags(this_dict, flags_dict)
        
        
@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Remove_Weapon_Charge_Up():
    '''
    Remove charge up from all weapons, to make PPCs and similar easier to use
    in a manner consistent with the npcs (eg. hold trigger to just keep
    firing), as charging is a player-only option.
    '''
    Clear_Weapon_Flag('charged')


# Disable weapon drain effects.
# Weapon drain may cause equipment damage before shields go down.
# In XRM, Xenon beams do this equipment damage and are only notable for having
#  this flag set. Try clearing it to see if this helps (as part of the
#  general beam nerf).
@File_Manager.Transform_Wrapper('types/TBullets.txt')
def Remove_Weapon_Drain_Flag():
    '''
    Removes the weapon drain flag from any weapons.
    May also stop equipment damage being applied through shielding
    for these weapons.
    '''
    # TODO: doubly verify this works. Gameplay since making this
    #  change has not seen equipment destroyed by Xenon cap ship
    #  weapons in XRM, which were the motivation for this change.
    Clear_Weapon_Flag('weapon_drain')

