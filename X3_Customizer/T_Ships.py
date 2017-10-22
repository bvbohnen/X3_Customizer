'''
Similar to X3_Weapons, this will open the Tships file and perform systematic edits.
'''
from File_Manager import *
import Flags
import math


#TODO:
#Reduce speed of the special aldrin ships, which are both around twice
# as fast as others in their tier.
#Could cut in half and still have them be competetive in vanilla.
#XRM still has aldrin ships fast, but brings other similar ships up to a closer
# speed, and all ships in those classes get a speed nerf further below, so nerfing
# aldrin ships specifically isn't as important.
    
#TODO:
#Consider if corvette turn rates should be reduced, and perhaps those of
# capital ships in general as well.
#Greatly reducing cap turning could be part of a mod for dogfighting around
# caps, also nerfing their anti-fighter weapons.

#TODO: maybe add cargo life support to the wares of capital ships by default.
#It looks like xrm does this anyway.
#It seems like it would be changed elsewhere, in some wares file maybe, since
# ships just have an index for the built in wares to a list somewhere.


@Check_Dependencies('TShips.txt')
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
    for this_dict in Load_File('TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict or scaling_factor != 1:
            value = int(this_dict['hull_strength'])
            
            #Pick the table scaling factor, or the default.
            if this_dict['subtype'] in adjustment_factors_dict:
                new_value = value * adjustment_factors_dict[this_dict['subtype']]
            else:
                new_value = value * scaling_factor

            #Most hulls appear to be in the thousands, so round to nearest thousand.
            #Skip this for ships with very small hulls, eg. fighter drones (10) and
            # similar, using a smaller rounding.
            if new_value > 10000:
                new_value = math.ceil(new_value/1000)*1000
            elif new_value > 1000:
                new_value = math.ceil(new_value/100)*100
            else:
                new_value = math.ceil(new_value/10)*10
            #Error check on hull getting 0'd out on a ship that didn't already
            # have 0 hull (as in some dummy entries)
            assert new_value != 0 or value == 0
            this_dict['hull_strength'] = str(new_value)


    #Upscale repair lasers if M3 scaling given.
    #This could work on m3 or m6 hull scaling, though needs to pick one
    # or the other to be safe against multiple transform calls.
    #Eg. if averaging m3 and m6 by x2 and x4, then the average is x3
    # if this is done in one call. But over two calls, the averages
    # will be 3/2 and 5/2, for 15/4 or 3.75, which is not the same.
    #The latter case would work okay if bonuses were tracked and added
    # from multiple calls, then applied during cleanup, but that is
    # probably more effort than wanted right now.
    #Go with M6 to be more player friendly, since repairs are most likely
    # to be attempted but get frustrating on an M6.
    if adjust_repair_lasers and 'SG_SH_M6' in adjustment_factors_dict:
        laser_scaling = adjustment_factors_dict['SG_SH_M6']
        #Call the dps adjustment transform to handle this.
        import T_Weapons
        T_Weapons.Adjust_Weapon_DPS(
            bullet_name_adjustment_dict = {'flag_repair': laser_scaling},
            maintain_energy_efficiency = False
        )


            
@Check_Dependencies('TShips.txt')
def Adjust_Ship_Speed(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship speeds. Does not affect acceleration.
    
    * scaling_factor:
      - Multiplier to apply to any ship type not found in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type or name, holding a scaling factor to be applied.
    '''
    #Approach could be to set a target average speed for each tier of ship, calculate the
    # existing average of that tier, and use the ratio as a multiplier to bring the average
    # in line. Target averages can be set by analyzing the vanilla game speeds using the
    # same code on an earlier pass.
    #Here, ratios will be hard set based on feel or other analysis.
    #Note: while acceleration could also be changed, since it was buffed to a lesser extent
    # as well, it should be safe to leave it alone for now.
    for this_dict in Load_File('TShips.txt'):

        #Determine the scaling factor.
        this_scaling_factor = scaling_factor
        #Check for specific ship name.
        if this_dict['name'] in adjustment_factors_dict:
            this_scaling_factor = adjustment_factors_dict[this_dict['name']]
        #Check for ship type.
        elif this_dict['subtype'] in adjustment_factors_dict:
            this_scaling_factor = adjustment_factors_dict[this_dict['subtype']]

        #Adjust speed.
        if this_scaling_factor != 1:
            #Only really need to adjust base speed itself, not tuning count.
            value = int(this_dict['speed'])
            new_value = value * this_scaling_factor
            #Round it off.
            new_value = round(new_value)
            #Put it back.
            this_dict['speed'] = str(new_value)

            
@Check_Dependencies('TShips.txt')
def Adjust_Ship_Laser_Recharge(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship laser regeneration rate.
    
    * scaling_factor:
      - Multiplier to apply to any ship type not found in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type, holding a scaling factor to be applied.
    '''
    for this_dict in Load_File('TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict or scaling_factor != 1:
            #Note that weapon recharge is a float, so do no rounding.
            value = float(this_dict['weapon_recharge_factor'])

            #Pick the table scaling factor, or the default.
            if this_dict['subtype'] in adjustment_factors_dict:
                new_value = value * adjustment_factors_dict[this_dict['subtype']]
            else:
                new_value = value * scaling_factor

            this_dict['weapon_recharge_factor'] = str(new_value)

            
            
@Check_Dependencies('TShips.txt')
def Adjust_Ship_Pricing(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship pricing.

    * scaling_factor:
      - Multiplier for any ship not matched in adjustment_factors_dict.
    * adjustment_factors_dict:
      - Dict keyed by ship type, holding a scaling factor to be applied.
    '''
    for this_dict in Load_File('TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict or scaling_factor != 1:
            #Apply change to both npc and player costs.
            for field in ['production_value_npc', 'production_value_player']:
                value = int(this_dict[field])

                #Pick the table scaling factor, or the default.
                if this_dict['subtype'] in adjustment_factors_dict:
                    new_value = value * adjustment_factors_dict[this_dict['subtype']]
                else:
                    new_value = value * scaling_factor

                #Round it off.
                new_value = round(new_value)
                #Put it back.
                this_dict[field] = str(new_value)


                
@Check_Dependencies('TShips.txt')
def Adjust_Ship_Shield_Regen(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship shield regeneration rate.
    
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
    for this_dict in Load_File('TShips.txt'):
        if this_dict['subtype'] in adjustment_factors_dict:
            #Get the subfields from the dict.
            target, factor, max_val = adjustment_factors_dict[this_dict['subtype']]

            #Get the original shield power.
            value = int(this_dict['shield_power'])

            #Only apply factor if it was over the target.
            if value > target:
                new_value = target + (value - target) * factor
                #Apply max if given.
                if max_val != None:
                     new_value = min(new_value, max_val)
                #Round to the nearest 50, since shield regen is normally scaled to
                # 100 or occasionally 50. Sometimes it goes lower for light ships,
                # so update this to round to 10.
                new_value = round(new_value/10)*10
                this_dict['shield_power'] = str(int(new_value))
                
        #Do a global adjustment separate from the category adjustments.
        if scaling_factor != 1:
            value = int(this_dict['shield_power'])
            new_value = value * scaling_factor
            #Scale to nearest 10, as above.
            new_value = round(new_value/10)*10
            this_dict['shield_power'] = str(int(new_value))
                

            
@Check_Dependencies('TShips.txt')
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
    #TODO: maybe support increasing shielding.
    for this_dict in Load_File('TShips.txt'):
        #Check if this ship is being adjusted.
        if this_dict['subtype'] in adjustment_factors_dict:

            #Get the subfields from the dict.
            target = adjustment_factors_dict[this_dict['subtype']][0]
            factor = adjustment_factors_dict[this_dict['subtype']][1]

            #Get the original shield slots and the size of each shield.
            shield_slots = int(this_dict['max_shields'])
            shield_size  = Flags.Shield_type_size_dict[int(this_dict['shield_type'])]

            #Calculate total shielding.
            total_shields = shield_size * shield_slots

            #Only adjust if it was over the target.
            if total_shields > target:
                #Find the new total shields to aim for.
                new_shield_target = target + (total_shields - target) * factor
                #Round this to the closest integer for the shield size.
                new_shield_target = round(new_shield_target / shield_size) * shield_size
                #Now figure out how many slots are needed to meet or exceed this value.
                while 1:
                    #Test remove a shield.
                    this_shield_slots = shield_slots - 1
                    this_total_shields = shield_size * this_shield_slots
                    #If this went past the overall target, stop searching.
                    if this_total_shields < target:
                        break
                    #If went past the new target, stop searching; the previous
                    # iteration likely hit the target directly if things rounded properly.
                    if this_total_shields < new_shield_target:
                        break
                    #Complete the slots reduction.
                    shield_slots = this_shield_slots
                    #Error check.
                    assert shield_slots >= 1

                #Verification things worked; the new target should have been met exactly.
                assert shield_size * shield_slots == new_shield_target
                #Apply the new shield slot count.
                this_dict['max_shields'] = str(shield_slots)
                
            
                
@Check_Dependencies('TShips.txt')
def Fix_Pericles_Pricing():
    '''
    Applies a bug fix to the enhanced pericles, which has its
     npc value set to 1/10 of player value, causing it price to be 1/10
     what it should be.
    Does nothing if the existing npc and player prices are matched.
    '''
    for this_dict in Load_File('TShips.txt'):
        if this_dict['name'] == 'SS_SH_P_M4_ENH':
            #Verify the bug is in place, with mismatched pricing.
            #If this was already fixed in the source file, skip this step.
            npc_price    = int(this_dict['production_value_npc'])
            player_price = int(this_dict['production_value_player'])
            if npc_price < player_price:
                this_dict['production_value_npc'] = this_dict['production_value_player']
            break

                
@Check_Dependencies('TShips.txt')
def Boost_Truelight_Seeker_Shield_Reactor():
    '''
    Enhances the Truelight Seeker's shield reactor.
    In AP the TLS has a shield reactor only around 1/10 what is normal 
     for similar ships; this applies a 10x increase.
    If the TLS is already at least 1/5 of Centaur shielding, this
     transform is not applied.
    '''
    #Look for the centaur.
    for this_dict in Load_File('TShips.txt'):
        if this_dict['name'] == 'SS_SH_A_M6_P':
            #Note its shield reactor.
            centaur_shield_power = int(this_dict['shield_power'])
            break
    #Look for the TLS.
    for this_dict in Load_File('TShips.txt'):
        if this_dict['name'] == 'SS_SH_TLS':
            shield_power = int(this_dict['shield_power'])
            #Apply change if not within 1/5 of the centaur shielding.
            if shield_power < centaur_shield_power / 5:
                this_dict['shield_power'] = str(shield_power * 10)
            break

        
@Check_Dependencies('TShips.txt')
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
    #Classify the light ships to get a basic trail.
    light_ships = [
            'SG_SH_M5',
            'SG_SH_M4',
            'SG_SH_M3',
            'SG_SH_M8',
            'SG_SH_M6',
            #'SG_SH_M7',
            #'SG_SH_M2',
            #'SG_SH_M1',
            #'SG_SH_M0',
            'SG_SH_TS',
            'SG_SH_TM',
            'SG_SH_TP',
            #'SG_SH_TL',
            'SG_SH_GO',
            ]
    for this_dict in Load_File('TShips.txt'):
        #Light ships get a 1 if not removing trails entirely.
        if this_dict['subtype'] in light_ships and not remove_trails:
            this_dict['particle_effect'] = '1'
        else:
            this_dict['particle_effect'] = '0'
                


@Check_Dependencies('TShips.txt')
def Standardize_Ship_Tunings(
        engine_tunings = None,
        rudder_tunings = None,
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

    * engine_tunings:
      - Int, the max engine tunings to set.
    * rudder_tunings:
      - Int, the max rudder tunings to set.
    '''
    #TODO: maybe provide a script to run which resets ships to their
    # max tunings if they went over (though would mess with overtuned
    # ships that may exist).
    for this_dict in Load_File('TShips.txt'):

        #Loop over the engine and rudder tunings, to share code.
        for tuning_amount, tuning_field, scaled_field_list in zip(
                [engine_tunings, rudder_tunings],
                ['speed_tunings', 'rudder_tunings'],
                #TODO: should angular acceleration be modified as well?
                [['speed','acceleration'],
                 ['yaw','pitch','roll']]
            ):
            #Skip if unspecified.
            if tuning_amount == None:
                continue

            #Get the base max tunings.
            max_tunings = int(this_dict[tuning_field])
            #Get the scaling factor to apply to the scaled fields.
            #Tunings provide 10% each, so the old max was
            # (1 + max_tunings / 10), and the new max will be
            # (1 + new_tunings / 10), so the scaling
            # will be the ratio of these.
            #Put new tunings on bottom; if tuning count is being reduced,
            # then the bottom term will be smaller, leading to a >1 scaling
            # to make up for the smaller tuning amount.
            # Eg. if max_tunings were 10, the tuning_amount is 0, then the
            # scaling will be x2 to make up for the loss of tunings.
            scaling = (1 + max_tunings / 10) / (1 + tuning_amount / 10)

            #Loop over the scaled fields.
            for scaled_field in scaled_field_list:
                #Unfortunately, the speed terms are int while rudder terms
                # are float, so need to parse based on type.
                if tuning_field == 'speed_tunings':
                    value = int(this_dict[scaled_field])
                    new_value = value * scaling
                    #Round it off.
                    new_value = round(new_value)
                    #Put it back.
                    this_dict[scaled_field] = str(new_value)
                else:
                    value = float(this_dict[scaled_field])
                    new_value = value * scaling
                    #Put it back, with 6 decimal places. Some existing
                    # terms had up to ~7 or so (suggests single precision float),
                    # and some terms can get down to the 4th decimal place for
                    # slow turning ships.
                    this_dict[scaled_field] = str('{0:.6f}'.format(new_value))

            #Update the tuning amount.
            this_dict[tuning_field] = str(tuning_amount)

            
@Check_Dependencies('TShips.txt', 'WareLists.txt')
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
    Note: switches ships to a matching ware list with life support included
    when possible, else adds life support to the existing ware list. Some
    non-capital ships may be affected if they share an edited list.

    * ship_types:
      - List of ship types to add life support to, eg. ['SG_SH_M2'].
        By default, this includes M6, M7, M2, M1, TL, TM.
    '''
    #Ship built-in wares are specified in a two step process:
    # 1) The ship gives an index of a ware list.
    # 2) The warelist file at that index has a list of wares to include.
    #The approach here will be to determine all ware list ids used by
    # capital ships, then either find a replacement list which has the
    # same wares but including life support (to be swapped to), or to
    # edit the ware lists to include life support.
    #Life support is assumed to always be 'SS_WARE_LIFESUPPORT', not changed
    # by mods. If this is ever a problem, it could potentially be deduced from
    # TP ware lists.

    #Get a set of ware list ids for capital ships being modified.
    cap_ware_list_ids = set()
    #Loop over all ships.
    for this_dict in Load_File('TShips.txt'):

        #Skip if this is not a ship to add life support to.
        if this_dict['subtype'] not in ship_types:
            continue

        #Record the list.
        this_ware_list_id = int(this_dict['ware_list'])
        cap_ware_list_ids.add(this_ware_list_id)


    #Go through all ware lists and parse their actual wares.
    ware_list_list = []
    for index, this_dict in enumerate(Load_File('WareLists.txt')):

        #Note: an oddity with the warelist is that the data lines and the
        # header line can be the same size (2), so that header line will
        # need to be pruned here manually.
        #Can identify the header as having 2 entries, the second being just
        # a newline.
        if len(this_dict) == 2 and this_dict['slash_index_comment'] == '\n':
            #This should be the first item.
            assert index == 0
            continue

        #Get the wares, as a list of strings.
        #Skip the first entry (count) and last entry (slash_index+newline).
        this_ware_list = list(this_dict.values())[1:-1]

        #Verify the right count.
        assert len(this_ware_list) == int(this_dict['ware_count'])

        #Record the ware list.
        ware_list_list.append(this_ware_list)


    #Prune out the cap ship wares that already have life support.
    for id in list(cap_ware_list_ids):
        if 'SS_WARE_LIFESUPPORT' in ware_list_list[id]:
            cap_ware_list_ids.remove(id)

    #Try to match the remaining lists to an existing list with the same
    # contents but including life support.
    #This occurs in XRM for TLs, which have the TS ware list, but there
    # is a cruiseliner list that has life support and the TS trade ware
    # which can be swapped to without adding life support to all traders.
    #When replacements found, the original id will be removed from
    # the cap_ware_list_ids set.
    #Any valid replacements go in this dict.
    ware_list_id_replacement_dict = {}
    for id in list(cap_ware_list_ids):

        #Grab the original wares as a set, for easy superset checks.
        original_list = set(ware_list_list[id])
        #Calculate the expected size of a replacement list; should only
        # be +1 for life support.
        replacement_list_size = len(original_list) +1

        #Loop over all ware lists.
        for other_list_id, other_ware_list in enumerate(ware_list_list):
            #Probably safe to check against self, so don't bother skipping
            # that case.
            #No match if the other list is not the original list +1 in size.
            if len(other_ware_list) != replacement_list_size:
                continue

            #Not a match if the other list doesn't have life support.
            if 'SS_WARE_LIFESUPPORT' not in other_ware_list:
                continue

            #Not a match if the other list is not a superset.
            if not original_list <= set(other_ware_list):
                continue

            #When here, this is a match.
            ware_list_id_replacement_dict[id] = other_list_id
            cap_ware_list_ids.remove(id)
            break


    #If replacements were found, go back through tships and change the
    # ware list ids as needed.
    if ware_list_id_replacement_dict:    
        for this_dict in Load_File('TShips.txt'):    
            #Skip if this is not a ship to add life support to.
            if this_dict['subtype'] not in ship_types:
                continue

            #Skip if the ship's ware list doesn't need replacement.
            this_ware_list_id = int(this_dict['ware_list'])
            if this_ware_list_id not in ware_list_id_replacement_dict:
                continue

            #Apply the replacement.
            this_dict['ware_list'] = str(ware_list_id_replacement_dict[this_ware_list_id])


    #If ware list ids are left that couldn't be replaced, edit in
    # list support for them.
    if cap_ware_list_ids:
        #Note that since the header line gets returned, the actual ware
        # list index is 1 less than the enumerated value.
        for index_p1, this_dict in enumerate(Load_File('WareLists.txt')):
            
            #Note: an oddity with the warelist is that the data lines and the
            # header line can be the same size (2), so that header line will
            # need to be pruned here manually.
            #Can identify the header as having 2 entries, the second being just
            # a newline.
            if len(this_dict) == 2 and this_dict['slash_index_comment'] == '\n':
                #This should be the first item.
                assert index_p1 == 0
                continue
            #Adjust to get the proper index.
            index = index_p1 -1

            #Skip if this is not a list to add life support to.
            if index not in cap_ware_list_ids:
                continue

            #Grab the original ware list, parsed above.
            #this_ware_list = ware_list_list[index]

            #Put life support in it, at the front for now since that is where
            # it shows up in some sampled lines.
            #this_ware_list.insert(0, 'SS_WARE_LIFESUPPORT')

            #The entire dict will need its indices adjusted to make
            # room for the new ware.
            #It should be safe to just pop off the last item, put in life
            # support, and put the last item back (the slash_index_comment).
            slash_index_comment = this_dict['slash_index_comment']
            del(this_dict['slash_index_comment'])
            this_dict[len(this_dict)] = 'SS_WARE_LIFESUPPORT'
            this_dict['slash_index_comment'] = slash_index_comment

            #Adjust the ware count.
            this_dict['ware_count'] = str(int(this_dict['ware_count']) +1)

    return

