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
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship hull values. When applied to a existing save, ship hulls will
    not be updated automatically if hulls are increased.  Run the 
    temp.srm.hull.reload.xml script from the XRM hull packs to refill all 
    ships to 100% hull. Alternatively, ship hulls will be updated as 
    ships die and respawn.

    scaling_factor:
        Multiplier to apply to any ship type not found in adjustment_factors_dict.
    adjustment_factors_dict:
        Dict keyed by ship type, holding a scaling factor to be applied.
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


            
@Check_Dependencies('TShips.txt')
def Adjust_Ship_Speed(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship speeds. Does not affect acceleration.
    
    scaling_factor:
        Multiplier to apply to any ship type not found in adjustment_factors_dict.
    adjustment_factors_dict:
        Dict keyed by ship type, holding a scaling factor to be applied.
    '''
    #Approach could be to set a target average speed for each tier of ship, calculate the
    # existing average of that tier, and use the ratio as a multiplier to bring the average
    # in line. Target averages can be set by analyzing the vanilla game speeds using the
    # same code on an earlier pass.
    #Here, ratios will be hard set based on feel or other analysis.
    #Note: while acceleration could also be changed, since it was buffed to a lesser extent
    # as well, it should be safe to leave it alone for now.
    for this_dict in Load_File('TShips.txt'):
        #Adjust speed.
        if this_dict['subtype'] in adjustment_factors_dict or scaling_factor != 1:
            #Only really need to adjust base speed itself, not tuning count.
            value = int(this_dict['speed'])

            #Pick the table scaling factor, or the default.
            if this_dict['subtype'] in adjustment_factors_dict:
                new_value = value * adjustment_factors_dict[this_dict['subtype']]
            else:
                new_value = value * scaling_factor

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
    
    scaling_factor:
        Multiplier to apply to any ship type not found in adjustment_factors_dict.
    adjustment_factors_dict:
        Dict keyed by ship type, holding a scaling factor to be applied.
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

            new_value = value * adjustment_factors_dict[this_dict['subtype']]
            this_dict['weapon_recharge_factor'] = str(new_value)

            
            
@Check_Dependencies('TShips.txt')
def Adjust_Ship_Pricing(
    scaling_factor = 1,
    adjustment_factors_dict = {}
    ):
    '''
    Adjust ship pricing.

    The adjustment_factors_dict is a dict keyed by ship type, holding a scaling
     factor to be applied.
    The flat scaling_factor will be applied to any ship type not found in
     adjustment_factors_dict.
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
    
    scaling_factor:
        Multiplier to apply to all ship types on top of those present
        in adjustment_factors_dict.
    adjustment_factors_dict:
        Dict keyed by ship type, holding a  tuple of 
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
    
    The adjustment_factors_dict is a dict keyed by ship type, holding a
     tuple of (targeted_total_shielding, reduction_factor), where any ships 
     with shield above targeted_total_shielding will have reduction_factor
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

    remove_trails:
        If True, this will remove trails from all ships.
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
                

