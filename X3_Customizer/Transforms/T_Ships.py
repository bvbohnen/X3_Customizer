'''
Similar to X3_Weapons, this will open the Tships file and perform systematic edits.

TODO: switch many of the subtype checks to using object type, which will be more
accurate, eg. a fighter drone is subclass M5 but has a unique object type (not M5),
so using object type may be a better filter for actual M5s.
Also, the xrm goner M6 (TLS) is listed as subtype GO, object type M6, so filtering
by object type would capture it better.

Object type is used for marine capacity (according to forum searching); need to know
if it affects anything else if ever editing it to change marine counts.
'''
import math
# from collections import defaultdict
import copy

from .. import File_Manager
from ..Common.Flags import *

# TODO:
# Consider if corvette turn rates should be reduced, and perhaps those of
#  capital ships in general as well.
# Greatly reducing cap turning could be part of a mod for dogfighting around
#  caps, also nerfing their anti-fighter weapons.

# TODO:
# May add SETA as a built-in ware for all ships.

# TODO:
# Cut hull on the 'unknown object' M6 in XRM, which is around 25x higher
#  than what is typical for an M6. Even a 90% reduction would be modest.

@File_Manager.Transform_Wrapper('types/TShips.txt')
def Adjust_Ship_Hull(
    scaling_factor = 1,
    adjustment_factors_dict = {},
    adjust_repair_lasers = True
    ):
    '''
    Adjust ship hull values. When applied to a existing save, ship hulls will
    not be updated automatically if hulls are increased.  Run the 
    temp.srm.hull.reload.xml script from the XRM hull packs to refill all 
    ships to 100% hull. Alternatively, ship hulls will be updated as 
    ships die and respawn.

    * scaling_factor:
      - Multiplier to apply to any ship type not found in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type, holding a scaling factor to be applied.
    * adjust_repair_lasers:
      - Bool, if True (default) repair lasers will be scaled by the M6 
        hull scaling (if given), to avoid large changes in repair times.
    '''
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict or scaling_factor != 1:
            value = int(this_dict['hull_strength'])
            
            # Pick the table scaling factor, or the default.
            if this_dict['subtype'] in adjustment_factors_dict:
                new_value = value * adjustment_factors_dict[this_dict['subtype']]
            else:
                new_value = value * scaling_factor

            # Most hulls appear to be in the thousands, so round to nearest thousand.
            # Skip this for ships with very small hulls, eg. fighter drones (10) and
            #  similar, using a smaller rounding.
            if new_value > 10000:
                new_value = math.ceil(new_value/1000)*1000
            elif new_value > 1000:
                new_value = math.ceil(new_value/100)*100
            else:
                new_value = math.ceil(new_value/10)*10
            # Error check on hull getting 0'd out on a ship that didn't already
            #  have 0 hull (as in some dummy entries)
            assert new_value != 0 or value == 0
            this_dict['hull_strength'] = str(new_value)


    # Upscale repair lasers if M3 scaling given.
    # This could work on m3 or m6 hull scaling, though needs to pick one
    #  or the other to be safe against multiple transform calls.
    # Eg. if averaging m3 and m6 by x2 and x4, then the average is x3
    #  if this is done in one call. But over two calls, the averages
    #  will be 3/2 and 5/2, for 15/4 or 3.75, which is not the same.
    # The latter case would work okay if bonuses were tracked and added
    #  from multiple calls, then applied during cleanup, but that is
    #  probably more effort than wanted right now.
    # Go with M6 to be more player friendly, since repairs are most likely
    #  to be attempted but get frustrating on an M6.
    if adjust_repair_lasers and 'SG_SH_M6' in adjustment_factors_dict:
        laser_scaling = adjustment_factors_dict['SG_SH_M6']
        # Call the dps adjustment transform to handle this.
        from . import T_Weapons
        T_Weapons.Adjust_Weapon_DPS(
            bullet_name_adjustment_dict = {'flag_repair': laser_scaling},
            maintain_energy_efficiency = False
        )


            
@File_Manager.Transform_Wrapper('types/TShips.txt')
def Adjust_Ship_Speed(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship speed and acceleration, globally or per ship class.
    
    * scaling_factor:
      - Multiplier to apply to any ship type not found in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type or name, holding a scaling factor to be applied.
    '''
    # Approach could be to set a target average speed for each tier of ship, calculate the
    #  existing average of that tier, and use the ratio as a multiplier to bring the average
    #  in line. Target averages can be set by analyzing the vanilla game speeds using the
    #  same code on an earlier pass.
    # Here, ratios will be hard set based on feel or other analysis.
    # Note: while acceleration could also be changed, since it was buffed to a lesser extent
    #  as well, it should be safe to leave it alone for now.
    for this_dict in File_Manager.Load_File('types/TShips.txt'):

        # Determine the scaling factor.
        this_scaling_factor = scaling_factor
        # Check for specific ship name.
        if this_dict['name'] in adjustment_factors_dict:
            this_scaling_factor = adjustment_factors_dict[this_dict['name']]
        # Check for ship type.
        elif this_dict['subtype'] in adjustment_factors_dict:
            this_scaling_factor = adjustment_factors_dict[this_dict['subtype']]

        # Adjust speed.
        if this_scaling_factor != 1:
            # Change both speed and acceleration, so that faster ships
            #  are also more maneuverable.
            for field in ['speed','acceleration']:
                # Only really need to adjust base speed itself, not tuning count.
                value = int(this_dict[field])
                new_value = value * this_scaling_factor
                # Round it off.
                new_value = round(new_value)
                # Put it back.
                this_dict[field] = str(new_value)

            
@File_Manager.Transform_Wrapper('types/TShips.txt')
def Adjust_Ship_Laser_Recharge(
    scaling_factor = 1,
    adjustment_factors_dict = {},
    adjust_energy_cap = False
    ):
    '''
    Adjust ship laser regeneration rate, either globally or per ship class.
    
    * scaling_factor:
      - Multiplier to apply to any ship type not found in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type, holding a scaling factor to be applied.
    * adjust_energy_cap:
      - Bool, if True the ship maximum energy is also adjusted.
        This may cause oddities if applied to an existing save.
        Defaults False.
    '''
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict or scaling_factor != 1:
            
            # Pick the table scaling factor, or the default.
            if this_dict['subtype'] in adjustment_factors_dict:
                this_scaling = adjustment_factors_dict[this_dict['subtype']]
            else:
                this_scaling = scaling_factor

            #  The recharge is stored as a multiplier on the ships
            #   maximum stored energy.
            #  When updating the maximum, only it needs to change and the
            #   recharge will scale accordingly.
            #  When not updating maximum, the multiplier needs to be
            #   changed directly.
            if adjust_energy_cap:
                value = int(this_dict['weapon_energy'])
                new_value = value * this_scaling
                this_dict['weapon_energy'] = str(int(new_value))
            else:
                # Note that weapon recharge is a float, so do no rounding.
                value = float(this_dict['weapon_recharge_factor'])
                new_value = value * this_scaling
                # Limit to 6 decimals.
                this_dict['weapon_recharge_factor'] = str('{0:.6f}'.format(new_value))

            
            
@File_Manager.Transform_Wrapper('types/TShips.txt')
def Adjust_Ship_Pricing(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship pricing, either globally or per ship class.

    * scaling_factor:
      - Multiplier for any ship not matched in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type, holding a scaling factor to be applied.
    '''
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict or scaling_factor != 1:
            # Apply change to both npc and player costs.
            for field in ['relative_value_npc', 'relative_value_player']:
                value = int(this_dict[field])

                # Pick the table scaling factor, or the default.
                if this_dict['subtype'] in adjustment_factors_dict:
                    new_value = value * adjustment_factors_dict[this_dict['subtype']]
                else:
                    new_value = value * scaling_factor

                # Round it off.
                new_value = round(new_value)
                # Put it back.
                this_dict[field] = str(new_value)


                
@File_Manager.Transform_Wrapper('types/TShips.txt')
def Adjust_Ship_Shield_Regen(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship shield regeneration rate, either globally or per ship class.
    This may have no effect beyond where all ship shields are powered at their
    individual max rates.
    
    * scaling_factor:
      - Multiplier to apply to all ship types on top of those present
        in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type, holding a tuple of 
        (targeted_recharge_rate, reduction_factor, max_rate)
        where any recharges above targeted_recharge_rate will have the 
        reduction_factor applied to the difference in original and target 
        rates. Recharge rates will be capped at max_rate.
    '''
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict:
            # Get the subfields from the dict.
            target, factor, max_val = adjustment_factors_dict[this_dict['subtype']]

            # Get the original shield power.
            value = int(this_dict['shield_power'])

            # Only apply factor if it was over the target.
            if value > target:
                new_value = target + (value - target) * factor
                # Apply max if given.
                if max_val != None:
                     new_value = min(new_value, max_val)
                # Round to the nearest 50, since shield regen is normally scaled to
                #  100 or occasionally 50. Sometimes it goes lower for light ships,
                #  so update this to round to 10.
                new_value = round(new_value/10)*10
                this_dict['shield_power'] = str(int(new_value))
                
        # Do a global adjustment separate from the category adjustments.
        if scaling_factor != 1:
            value = int(this_dict['shield_power'])
            new_value = value * scaling_factor
            # Scale to nearest 10, as above.
            new_value = round(new_value/10)*10
            this_dict['shield_power'] = str(int(new_value))
                

            
@File_Manager.Transform_Wrapper('types/TShips.txt')
def Adjust_Ship_Shield_Slots(
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship shielding by changing shield slot counts.
    Shield types will remain unchanged, and at least 1 shield slot will
    be left in place.
    When applied to an existing save, ship shields will not be updated
    automatically, as some ships may continue to have excess shields
    equipped, or ships may lack enough shield inventory to fill
    up added slots.
    
    * adjustment_factors_dict:
      - Dict keyed by ship type, holding a tuple of 
        (targeted_total_shielding, reduction_factor), where any ships 
        with shields above targeted_total_shielding will have reduction_factor
        applied to their shield amount above the target.
    '''
    # TODO: maybe support increasing shielding.
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        # Check if this ship is being adjusted.
        if this_dict['subtype'] in adjustment_factors_dict:

            # Get the subfields from the dict.
            target = adjustment_factors_dict[this_dict['subtype']][0]
            factor = adjustment_factors_dict[this_dict['subtype']][1]

            # Get the original shield slots and the size of each shield.
            shield_slots = int(this_dict['max_shields'])
            shield_size  = Shield_type_size_dict[int(this_dict['shield_type'])]

            # Calculate total shielding.
            total_shields = shield_size * shield_slots

            # Only adjust if it was over the target.
            if total_shields > target:
                # Find the new total shields to aim for.
                new_shield_target = target + (total_shields - target) * factor
                # Round this to the closest integer for the shield size.
                new_shield_target = round(new_shield_target / shield_size) * shield_size
                # Now figure out how many slots are needed to meet or exceed this value.
                while 1:
                    # Test remove a shield.
                    this_shield_slots = shield_slots - 1
                    this_total_shields = shield_size * this_shield_slots
                    # If this went past the overall target, stop searching.
                    if this_total_shields < target:
                        break
                    # If went past the new target, stop searching; the previous
                    #  iteration likely hit the target directly if things rounded properly.
                    if this_total_shields < new_shield_target:
                        break
                    # Complete the slots reduction.
                    shield_slots = this_shield_slots
                    # Error check.
                    assert shield_slots >= 1

                # Verification things worked; the new target should have been met exactly.
                assert shield_size * shield_slots == new_shield_target
                # Apply the new shield slot count.
                this_dict['max_shields'] = str(shield_slots)
                
            
# TODO: maybe make this a general fix to ensure player and npc prices are the
#  same, though bugs outside the pericles haven't been noticed.
@File_Manager.Transform_Wrapper('types/TShips.txt', XRM = False, LU = False)
def Fix_Pericles_Pricing():
    '''
    Applies a bug fix to the enhanced pericles in vanilla AP, which has its
    npc value set to 1/10 of player value, causing it price to be 1/10
    what it should be.
    Does nothing if the existing npc and player prices are matched.
    '''
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        if this_dict['name'] == 'SS_SH_P_M4_ENH':
            # Verify the bug is in place, with mismatched pricing.
            # If this was already fixed in the source file, skip this step.
            npc_price    = int(this_dict['relative_value_npc'])
            player_price = int(this_dict['relative_value_player'])
            if npc_price < player_price:
                this_dict['relative_value_npc'] = this_dict['relative_value_player']
            break

       
@File_Manager.Transform_Wrapper('types/TShips.txt')
def Patch_Ship_Variant_Inconsistencies(
        include_xrm_fixes = False
    ):
    '''
    Applies some patches to some select inconsistencies in ship variants.
    Modified ships include the Baldric Miner and XRM Medusa Vanguard,
    both manually named instead of using the variant system.
    This is meant to be run prior to Add_Ship_Variants, to avoid the 
    non-standard ships creating their own sub-variants.
    There may be side effects if the variant inconsistencies were intentional.

    * include_xrm_fixes
      - Bool, if True then the Medusa Vanguard is patched if found and
        in the form set by XRM. Default True.
    '''
    # Make a general patch specification dict.
    # Each ship will specify the base type, the type to patch, and
    #  the variant it is.
    # These will be simple tuples of:
    #  (target ship id, base ship id, variant type)
    ship_patch_tuple_list = [
        ('SS_SH_USC_TS_1', 'SS_SH_USC_TS', 'miner'),
        ]
    if include_xrm_fixes:
        ship_patch_tuple_list += [
            ('SS_SH_P_M3P2', 'SS_SH_P_M3P', 'vanguard'),
            ]
    # Convenience import for variant name to id conversion.
    from .T_Ships_Variants import variant_name_index_dict

    # Loop over the patches to apply.
    for patch_ship_name, base_ship_name, variant in ship_patch_tuple_list:

        # Find the standard name id from the base ship.
        name_id = None
        for this_dict in File_Manager.Load_File('types/TShips.txt'):
            if this_dict['name'] == base_ship_name:
                name_id = this_dict['name_id']
                break

        # If the base name was not found for some reason, skip ahead,
        #  since the target ship may not be from this mod state.
        if name_id == None:
            continue

        # -Removed; this check probably isn't needed, and causes problems
        #  with repeat calls of this transform.
        ##Search to verify no variant exists already, else error.
        ##This may occur if variant addition was already run.
        # error = False
        # for this_dict in File_Manager.Load_File('types/TShips.txt'):
        #     if (this_dict['name_id'] == name_id 
        #     and int(this_dict['variation_index']) == variant_name_index_dict[variant]):
        #         print('Error in Patch_Ship_Variant_Inconsistencies,'
        #              'a standard variant already present.')
        #         error = True
        #         break
        ##On error, skip to the next ship to patch.
        # if error:
        #     continue

        # Find the problem ship.
        # Note: this should be safe across multiple transform calls, just
        #  writing the same fields each time.
        for this_dict in File_Manager.Load_File('types/TShips.txt'):
            if this_dict['name'] == patch_ship_name:
                # Set the name to that of the base ship.
                this_dict['name_id'] = name_id
                # Set the variant using the standard field.
                this_dict['variation_index'] = str(variant_name_index_dict[variant])
                break

                
@File_Manager.Transform_Wrapper('types/TShips.txt', XRM = False, LU = False)
def Boost_Truelight_Seeker_Shield_Reactor():
    '''
    Enhances the Truelight Seeker's shield reactor.
    In vanilla AP the TLS has a shield reactor only around 1/10 of what is 
    normal for similar ships. This transform sets the TLS shield reactor
    to be the same as the Centaur.
    If the TLS is already at least 1/5 of Centaur shielding, this
    transform is not applied.
    '''
    # Look for the centaur.
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        if this_dict['name'] == 'SS_SH_A_M6_P':
            # Note its shield reactor.
            centaur_shield_power = int(this_dict['shield_power'])
            break
    # Look for the TLS.
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        if this_dict['name'] == 'SS_SH_TLS':
            shield_power = int(this_dict['shield_power'])
            # Apply change if not within 1/5 of the centaur shielding.
            if shield_power < centaur_shield_power / 5:
                this_dict['shield_power'] = str(centaur_shield_power)
            break

        
@File_Manager.Transform_Wrapper('types/TShips.txt')
def Simplify_Engine_Trails(
        remove_trails = False
    ):
    '''
    Change engine trail particle effects to basic or none.
    This will switch to effect 1 for medium and light ships 
    and 0 for heavy ships, as in vanilla AP.

    * remove_trails:
      - If True, this will remove trails from all ships.
    '''
    # Classify the light ships to get a basic trail.
    light_ships = [
            'SG_SH_M5',
            'SG_SH_M4',
            'SG_SH_M3',
            'SG_SH_M8',
            'SG_SH_M6',
            # 'SG_SH_M7',
            # 'SG_SH_M2',
            # 'SG_SH_M1',
            # 'SG_SH_M0',
            'SG_SH_TS',
            'SG_SH_TM',
            'SG_SH_TP',
            # 'SG_SH_TL',
            'SG_SH_GO',
            ]
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        # Light ships get a 1 if not removing trails entirely.
        if this_dict['subtype'] in light_ships and not remove_trails:
            this_dict['particle_effect'] = '1'
        else:
            this_dict['particle_effect'] = '0'
                

@File_Manager.Transform_Wrapper('types/TShips.txt')
def Standardize_Ship_Tunings(
        engine_tunings = None,
        rudder_tunings = None,
        ship_types = None,
    ):
    '''
    Standardize max engine or rudder tuning amounts across all ships.
    Eg. instead of scouts having 25 and carriers having 5 engine
    runings, both will have some fixed number.
    Maximum ship speed and turn rate is kept constant, but minimum
    will change.
    If applied to an existing save, existing ships may end up overtuned;
    this is recommended primarily for new games, pending inclusion of
    a modification script which can recap ships to max tunings.
    Ships with 0 tunings will remain unedited.

    * engine_tunings:
      - Int, the max engine tunings to set.
    * rudder_tunings:
      - Int, the max rudder tunings to set.
    * ship_types:
      - List of ship names or types to adjust tunings for.
        If empty (default), all ships are adjusted.
    '''
    # TODO: maybe provide a script to run which resets ships to their
    #  max tunings if they went over (though would mess with overtuned
    #  ships that may exist).
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        
        # Skip if this is not a selected ship.
        if ship_types:
            if (this_dict['subtype'] not in ship_types 
            and this_dict['name'] not in ship_types):
                continue

        # Loop over the engine and rudder tunings, to share code.
        for tuning_amount, tuning_field, scaled_field_list in zip(
                [engine_tunings, rudder_tunings],
                ['speed_tunings', 'rudder_tunings'],
                # TODO: should angular acceleration be modified as well?
                [['speed','acceleration'],
                 ['yaw','pitch','roll']]
            ):
            # Skip if unspecified.
            if tuning_amount == None:
                continue

            # Get the base max tunings.
            max_tunings = int(this_dict[tuning_field])

            # Skip if the ship had 0 tunings; don't add them.
            if max_tunings == 0:
                continue

            # Get the scaling factor to apply to the scaled fields.
            # Tunings provide 10% each, so the old max was
            #  (1 + max_tunings / 10), and the new max will be
            #  (1 + new_tunings / 10), so the scaling
            #  will be the ratio of these.
            # Put new tunings on bottom; if tuning count is being reduced,
            #  then the bottom term will be smaller, leading to a >1 scaling
            #  to make up for the smaller tuning amount.
            #  Eg. if max_tunings were 10, the tuning_amount is 0, then the
            #  scaling will be x2 to make up for the loss of tunings.
            scaling = (1 + max_tunings / 10) / (1 + tuning_amount / 10)

            # Loop over the scaled fields.
            for scaled_field in scaled_field_list:
                # Unfortunately, the speed terms are int while rudder terms
                #  are float, so need to parse based on type.
                if tuning_field == 'speed_tunings':
                    value = int(this_dict[scaled_field])
                    new_value = value * scaling
                    # Round it off.
                    new_value = round(new_value)
                    # Put it back.
                    this_dict[scaled_field] = str(new_value)
                else:
                    value = float(this_dict[scaled_field])
                    new_value = value * scaling
                    # Put it back, with 6 decimal places. Some existing
                    #  terms had up to ~7 or so (suggests single precision float),
                    #  and some terms can get down to the 4th decimal place for
                    #  slow turning ships.
                    this_dict[scaled_field] = str('{0:.6f}'.format(new_value))

            # Update the tuning amount.
            this_dict[tuning_field] = str(tuning_amount)

            

@File_Manager.Transform_Wrapper('types/TShips.txt', 'types/WareLists.txt')
def Add_Ship_Equipment(
        ship_types = [
            ],
        equipment_list = [
            ]
    ):
    '''
    Adds equipment as built-in wares for select ship classes.

    * ship_types:
      - List of ship names or types to add equipment to, 
        eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].        
    * equipment_list:
      - List of equipment names from the ware files, 
        eg. ['SS_WARE_LIFESUPPORT'].
    '''
    # Ship built-in wares are specified in a two step process:
    #  1) The ship gives an index of a ware list.
    #  2) The warelist file at that index has a list of wares to include.
    # The approach here will be to determine all ware list ids used by
    #  capital ships, then either find a replacement list which has the
    #  same wares but including life support (to be swapped to), or to
    #  edit the ware lists to include life support.

    # Get a set of ware list ids for capital ships being modified.
    cap_ware_list_ids = set()
    # Loop over all ships.
    for this_dict in File_Manager.Load_File('types/TShips.txt'):

        # Skip if this is not a ship to add life support to.
        # Check against both name and subtype.
        if (this_dict['subtype'] not in ship_types 
        and this_dict['name'] not in ship_types):
            continue

        # Record the list.
        this_ware_list_id = int(this_dict['ware_list'])
        cap_ware_list_ids.add(this_ware_list_id)


    # Go through all ware lists and parse their actual wares.
    # Also record the line dicts, for copying later if needed.
    ware_list_list = []
    ware_line_dict_list = []
    header_found = False
    for index, this_dict in enumerate(File_Manager.Load_File('types/WareLists.txt')):

        # Note: an oddity with the warelist is that the data lines and the
        #  header line can be the same size (2), so that header line will
        #  need to be pruned here manually.
        # Can identify the header as having 2 entries, the second being just
        #  a newline.
        # Update: and oddity with LU is that the second line is a 0-entry
        #  list, so only skip the first one.
        if len(this_dict) == 2 and not header_found:
            header_found = True
            continue

        # Get the wares, as a list of strings.
        # Skip the first entry (count) and last entry (slash_index+newline).
        this_ware_list = list(this_dict.values())[1:-1]

        # Verify the right count.
        assert len(this_ware_list) == int(this_dict['ware_count'])

        # Record the ware list.
        ware_list_list.append(this_ware_list)
        ware_line_dict_list.append(this_dict)


    # Prune out the ware lists that already have the new equipment.
    for id in list(cap_ware_list_ids):
        if all(x in ware_list_list[id] for x in equipment_list):
            cap_ware_list_ids.remove(id)


    # Try to match the remaining lists to an existing list with the same
    #  contents but including the new equipment.
    # This occurs in XRM for TLs + life support, which have the TS ware list,
    #  but there is a cruiseliner list that has life support and the TS trade
    #  ware which can be swapped to without adding life support to all traders.
    # When replacements found, the original id will be removed from
    #  the cap_ware_list_ids set.
    # Any valid replacements go in this dict.
    ware_list_id_replacement_dict = {}
    for id in list(cap_ware_list_ids):

        # Grab the original wares as a set, for easy superset checks.
        original_list = set(ware_list_list[id])
        # Calculate the expected size of a replacement list; should only
        #  be +1 for life support.
        replacement_list_size = len(original_list) +1

        # Loop over all ware lists.
        for other_list_id, other_ware_list in enumerate(ware_list_list):
            # Probably safe to check against self, so don't bother skipping
            #  that case.
            # No match if the other list is not the original list +1 in size.
            if len(other_ware_list) != replacement_list_size:
                continue

            # Not a match if the other list doesn't have an equipment piece.
            if any(x not in other_ware_list for x in equipment_list):
                continue

            # Not a match if the other list is not a superset.
            if not original_list <= set(other_ware_list):
                continue

            # When here, this is a match.
            ware_list_id_replacement_dict[id] = other_list_id
            cap_ware_list_ids.remove(id)
            break


    # Any ware lists needing updates (not valid for direct replacement)
    #  could either be modified directly (easy), or copied into new lists
    #  that can then be used as replacements (hard, safer).
    # Go with the second option, to make this transform generally robust
    #  against accidentally adding equipment to ships not flagged for
    #  the addition.
    # However, to avoid over-proliferation of new lists across multiple
    #  transform calls, can check if any ware lists being changed are used
    #  purely by the ships having equipment added.
    # Any such lists can be edited directly safely.
    # This will show up if multiple calls are made to add equipment to the
    #  same classes of ships, since the first call will end up doing any
    #  list uniquification.

    # Go through tships again, this time searching for non-selected ships
    #  which use a ware list to be updated.
    # Move any such conflicts to a second list.
    cap_ware_list_ids_to_uniquify = []
    # Loop over all ships.
    for this_dict in File_Manager.Load_File('types/TShips.txt'):

        # Skip the ships being edited; only want to check the others.
        if (this_dict['subtype'] in ship_types 
        or this_dict['name'] in ship_types):
            continue

        # Check if a cap_ware_list_ids item is shared by this ship.
        this_ware_list_id = int(this_dict['ware_list'])
        if this_ware_list_id in cap_ware_list_ids:
            # Move the ware between lists.
            cap_ware_list_ids.remove(this_ware_list_id)
            cap_ware_list_ids_to_uniquify.append(this_ware_list_id)



    # Uniquify the needed ware lists.
    # Keep track of the new ones to stick in the warelist file later.
    new_ware_line_dicts_list = []
    for ware_list_id in cap_ware_list_ids_to_uniquify:

        # Copy the line dict.
        new_ware_line_dict = copy.copy(ware_line_dict_list[ware_list_id])

        # Get the index this will use.
        new_ware_list_id = len(ware_line_dict_list)
        # Add as comment at end of the line.
        new_ware_line_dict['slash_index_comment'] = '/{}\n'.format(new_ware_list_id)

        # Flag the ships using the old index to do a replacement.
        ware_list_id_replacement_dict[ware_list_id] = new_ware_list_id

        # Record the new line dict for use later.
        ware_line_dict_list.append(new_ware_line_dict)
        new_ware_line_dicts_list.append(new_ware_line_dict)

        # Note: this new list will still need the equipment added.
        # Put its index in cap_ware_list_ids so it gets updated below,
        #  after being added back to the warelists file.
        cap_ware_list_ids.add(new_ware_list_id)


    #  Add the entries to the t file.
    File_Manager.Load_File('types/WareLists.txt', return_game_file = True).Add_Entries(
        new_ware_line_dicts_list)
    

    # If ware list ids are still in need of updating with equipment,
    #  handle that now.
    if cap_ware_list_ids:
        # Note that since the header line gets returned, the actual ware
        #  list index is 1 less than the enumerated value.
        header_found = False
        for index_p1, this_dict in enumerate(File_Manager.Load_File('types/WareLists.txt')):
            
            # Skip the header, as above.
            if len(this_dict) == 2 and not header_found:
                header_found = True
                continue

            # Adjust to get the proper index.
            index = index_p1 -1

            # Skip if this is not a list to add life support to.
            if index not in cap_ware_list_ids:
                continue
            
            # The entire dict will need its indices adjusted to make
            #  room for the new ware.
            # It should be safe to just pop off the last item, put in new
            #  equipment, and put the last item back (the slash_index_comment).
            slash_index_comment = this_dict['slash_index_comment']
            del(this_dict['slash_index_comment'])
            for equipment in equipment_list:
                this_dict[len(this_dict)] = equipment
            this_dict['slash_index_comment'] = slash_index_comment

            # Adjust the ware count.
            this_dict['ware_count'] = str(int(this_dict['ware_count']) 
                                          + len(equipment_list))
            

    # If replacements were found, go back through tships and change the
    #  ware list ids as needed.
    if ware_list_id_replacement_dict:    
        for this_dict in File_Manager.Load_File('types/TShips.txt'):
            # Skip if this is not a ship to add equipment to.
            if (this_dict['subtype'] not in ship_types 
            and this_dict['name'] not in ship_types):
                continue

            # Skip if the ship's ware list doesn't need replacement.
            this_ware_list_id = int(this_dict['ware_list'])
            if this_ware_list_id not in ware_list_id_replacement_dict:
                continue

            # Apply the replacement.
            this_dict['ware_list'] = str(ware_list_id_replacement_dict[this_ware_list_id])


    return



@File_Manager.Transform_Wrapper('types/TShips.txt', 'types/WareLists.txt')
def Add_Ship_Life_Support(
        ship_types = [
            'SG_SH_M1',
            'SG_SH_M2',
            'SG_SH_M6',
            'SG_SH_M7',
            'SG_SH_TM',
            'SG_SH_TL',
            ]
    ):
    '''
    Adds life support as a built-in ware for select ship classes.
    This is a convenience transform which calls Add_Ship_Equipment.
    Warning: mission director scripts do not seem to have a way to check
    for built in wares, and typically use a special TP check to get around
    this. Other ship types with built-in life support will not be able
    to pick up passengers in some cases.

    * ship_types:
      - List of ship types to add life support to, eg. ['SG_SH_M2'].
        By default, this includes M6, M7, M2, M1, TL, TM.
    '''
    # Life support is assumed to always be 'SS_WARE_LIFESUPPORT', not changed
    #  by mods. If this is ever a problem, it could potentially be deduced from
    #  TP ware lists.
    Add_Ship_Equipment(
        ship_types = ship_types,
        equipment_list = [
            'SS_WARE_LIFESUPPORT'
            ]
        )
    return



@File_Manager.Transform_Wrapper('types/TShips.txt', category = 'Missile')
def Expand_Bomber_Missiles(
    include_bombers = True,
    include_frigates = True,
    add_bomber_missiles_to_frigates = False
    ):
    '''
    Allows bombers and missile frigates to use a wider variety of missiles.
    Bombers will gain fighter tier missiles, while frigates will gain
    corvette tier missiles. Terran ships will gain Terran missiles.
    Note that AI ship loadouts may include any missile they can fire, such
    that bombers will have fewer heavy missiles and more standard missiles.
    
    * include_bombers:
      - Bool, if True ships supporting bomber type missiles are modified.
        Default True.
    * include_frigates:
      - Bool, if True ships supporting missile frigate missiles are modified.
        Default True.
    * add_bomber_missiles_to_frigates:
      - Bool, if True frigates will also gain bomber type missiles.
        Default False. Low cargo volume of bomber missiles may be unbalanced
        on frigates.
    '''
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        # Unpack the missile flags.
        missile_flags = Unpack_Tships_Missile_Flags(this_dict)
        
        # Check for the different bomber/frigate types based on being
        #  able to fire the corresponding missile type.
        if include_bombers and missile_flags['SG_MISSILE_BOMBER']:
            # Standard bomber.
            # Set appropriate missile flags.
            # Could loop over a list of names, but just expand out for now.
            missile_flags['SG_MISSILE_DMBF'] = 1
            missile_flags['SG_MISSILE_LIGHT'] = 1
            missile_flags['SG_MISSILE_MEDIUM'] = 1
            
        if include_frigates and missile_flags['SG_MISSILE_TORP_CAPITAL']:
            missile_flags['SG_MISSILE_DMBF'] = 1
            missile_flags['SG_MISSILE_LIGHT'] = 1
            missile_flags['SG_MISSILE_MEDIUM'] = 1
            missile_flags['SG_MISSILE_HEAVY'] = 1
            if add_bomber_missiles_to_frigates:
                missile_flags['SG_MISSILE_BOMBER'] = 1

        if include_bombers and missile_flags['SG_MISSILE_TR_BOMBER']:
            missile_flags['SG_MISSILE_TR_LIGHT'] = 1
            missile_flags['SG_MISSILE_TR_MEDIUM'] = 1
            
            
        if include_frigates and missile_flags['SG_MISSILE_TR_TORP_CAPITAL']:
            missile_flags['SG_MISSILE_TR_LIGHT'] = 1
            missile_flags['SG_MISSILE_TR_MEDIUM'] = 1
            missile_flags['SG_MISSILE_TR_HEAVY'] = 1
            if add_bomber_missiles_to_frigates:
                missile_flags['SG_MISSILE_TR_BOMBER'] = 1

        # Repack the modified flags.
        Pack_Tships_Missile_Flags(this_dict, missile_flags)

    return



@File_Manager.Transform_Wrapper('types/TShips.txt', category = 'Missile')
def Add_Ship_Cross_Faction_Missiles(
    race_types = [
        'Argon', 
        'Boron', 
        'Split', 
        'Paranid', 
        'Teladi', 
        'Xenon', 
        'Pirates', 
        'Goner', 
        'ATF', 
        'Terran', 
        'Yaki',
        'Khaak', 
        ]
    ):
    '''
    Adds terran missile compatibility to commonwealth ships, and vice versa.
    Missiles are added based on category matching, eg. a terran ship that can
    fire light terran missiles will gain light commonwealth missiles.
    Note that AI ship loadouts may include any missile they can fire.
    
    * race_types:
      - List of race names whose ships will have missiles added. By default,
        the following are included: [Argon, Boron, Split, Paranid, Teladi, 
        Xenon, Pirates, Goner, ATF, Terran, Yaki].
    '''
    # Missiles needs to be cross-given based on what ships originally 
    #  supported. Eg. if a ship supported commonwealth light missiles,
    #  it will get terran light missiles.
    # Build the pairings here, in both directions.
    # Note: dumbfires need special handling, since they don't have a
    #  direct terran match.
    # These pairings are a little verbose, but do a good job handling
    #  the dumbfire case.
    missile_match_tuples = [
        # Commonwealth to terran.
        ('SG_MISSILE_AF_CAPITAL'   , 'SG_MISSILE_TR_AF_CAPITAL'  ),
        ('SG_MISSILE_BOMBER'       , 'SG_MISSILE_TR_BOMBER'      ),
        ('SG_MISSILE_HEAVY'        , 'SG_MISSILE_TR_HEAVY'       ),
        ('SG_MISSILE_LIGHT'        , 'SG_MISSILE_TR_LIGHT'       ),
        ('SG_MISSILE_MEDIUM'       , 'SG_MISSILE_TR_MEDIUM'      ),
        ('SG_MISSILE_TORP_CAPITAL' , 'SG_MISSILE_TR_TORP_CAPITAL'),
        # Terran to commonwealth.
        ('SG_MISSILE_TR_AF_CAPITAL'   , 'SG_MISSILE_AF_CAPITAL'  ),
        ('SG_MISSILE_TR_BOMBER'       , 'SG_MISSILE_BOMBER'      ),
        ('SG_MISSILE_TR_HEAVY'        , 'SG_MISSILE_HEAVY'       ),
        ('SG_MISSILE_TR_LIGHT'        , 'SG_MISSILE_LIGHT'       ),
        # Also give dumbfire if supporting lights.
        ('SG_MISSILE_TR_LIGHT'        , 'SG_MISSILE_DMBF'        ),
        ('SG_MISSILE_TR_MEDIUM'       , 'SG_MISSILE_MEDIUM'      ),
        ('SG_MISSILE_TR_TORP_CAPITAL' , 'SG_MISSILE_TORP_CAPITAL'),
        ]

    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        
        # Skip races not being modified.
        if Race_code_name_dict[int(this_dict['race'])] not in race_types:
            continue

        # Unpack the missile flags.
        missile_flags = Unpack_Tships_Missile_Flags(this_dict)

        # Loop over the matches.
        missiles_to_add = []
        for existing_missile, new_missile in missile_match_tuples:
            # If this ship has the original missile, queue the
            #  paired missile for addition. Don't add it yet, else
            #  it might be matched later in this loop, which is
            #  probably safe but best avoided.
            if missile_flags[existing_missile]:
                missiles_to_add.append( new_missile )

        # Add the queued missiles.
        for missile in missiles_to_add:
            missile_flags[missile] = 1
                    
        # Repack the modified flags.
        Pack_Tships_Missile_Flags(this_dict, missile_flags)

    return


@File_Manager.Transform_Wrapper('types/TShips.txt', category = 'Missile')
def Add_Ship_Boarding_Pod_Support(
    ship_types = [
        'SG_SH_M1',
        'SG_SH_M2',
        'SG_SH_M6',
        'SG_SH_M7',
        ],
    required_missiles = [        
        'SG_MISSILE_HEAVY',
        'SG_MISSILE_TR_HEAVY',
        ],
    ):
    '''
    Adds boarding pod launch capability to selected classes of
    ships, eg. destroyers. Ships should support marines, so limit
    to M1, M2, M7, M6, TL, TM, TP.
    
    * ship_types:
      - List of ship names or types to add equipment to, 
        eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].
        Default includes M6,M7,M2,M1.
    * required_missiles:
      - List of missile types, a ship must support one of these
        missiles before it will be given boarding pod support.
        Default is ['SG_MISSILE_HEAVY','SG_MISSILE_TR_HEAVY'],
        requiring ships to already support heavy missiles.
    '''
    for this_dict in File_Manager.Load_File('types/TShips.txt'):
        
        # Skip if this is not a ship to add the missile to.
        if (this_dict['subtype'] not in ship_types 
        and this_dict['name'] not in ship_types):
            continue

        # Skip if this is not a marine supporting subtype.
        if this_dict['subtype'] not in [
            'SG_SH_M1',
            'SG_SH_M2',
            'SG_SH_M6',
            'SG_SH_M7',
            'SG_SH_TP',
            'SG_SH_TM',
            'SG_SH_TL',
            ]:
            continue

        # Unpack the missile flags.
        missile_flags = Unpack_Tships_Missile_Flags(this_dict)

        # Skip if a required_missile list given and the ship
        #  does not support the missile.
        if required_missiles:
            if not any(missile_flags[x] for x in required_missiles):
                continue

        # Add boarding pods.
        missile_flags['SG_MISSILE_BOARDINGPOD'] = 1

        # Repack the modified flags.
        Pack_Tships_Missile_Flags(this_dict, missile_flags)

    return

# TODO: patchify this.
@File_Manager.Transform_Wrapper()
def Remove_Khaak_Corvette_Spin():
    '''
    Remove the spin on the secondary hull of the Khaak corvette.
    The replacement file used is expected to work for vanilla, xrm,
    and other mods that don't change the model scene file.
    '''
    #  This will be done with a very simple file replacement, mostly
    #  because it is easy this way.
    #  TODO: maybe switch to a patch style, if ever setting up a way
    #  to pull from the cat/dat files automatically.
    File_Manager.Copy_File('objects/ships/M6/Khaak_m6_scene.bod')
        
    return