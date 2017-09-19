'''
Edits to the ware lists.
'''
from File_Manager import *

#In XRM, ship tuning pricing starts at a high value on the first tuning, then counts down.
#This leads to capped ships selling for a bit much (their small number of tunings
# being highly valued), and odd decision making on tunings (ignore or go all-in).
#Some notes on how tuning pricing works are given further below.
#This transform will restore the vanilla tuning prices.

#-Removed, not very effective.
'''
#Bump up the cost of engine and rudder tunings, to make their purchase more
# meaningful, and help with immersion when most ships in the universe do not
# have full tunings.
Increase_Tuning_Prices = True
#The game appears to fix the price scaling to end at 3000 credits for the last engine
# upgrade (a 25 tuning scout and 15 tuning interceptor both experienced this).
#Similarly, rudder fixes the last upgrade at 2000.
#As such, adjusting the price here might just affect the first tuning price, and the
# resulting price trend (eg. if it starts at 3000, then engine tunings should have
# flat pricing).
#(In xrm, the starting high price goes down to 3000 on the last upgrade, suggesting
# that is the cause if the count down problem.)
#If avoiding count-down issues, then the most tuning cost could be increase by
# is ~2x (the 0 to 3k case averages 1.5k, and the new average would be 3k).
#If keeping this transform, rethink how the base price is set, since a multiplier
# is insufficient as the original base price is extremely low and swamped out
# by the hardcoded price scaling (eg. base price of 20 has jumps in the hundreds).
Tuning_cost_multiplier = 5
'''

@Check_Dependencies('TWareT.txt')
def Restore_Vanilla_Tuning_Pricing():
    '''
    Sets the price for ship tunings (engine, rudder, cargo) to those
    used in vanilla AP.
    '''
    #Dict of ware names and their relative values to use,
    # taken from the vanilla file in 02.cat.
    tuning_relative_value_dict = {
        #Cargo
        'SS_WARE_TECH251': 2,
        #Engine
        'SS_WARE_TECH213': 5,
        #Rudder
        'SS_WARE_TECH246': 3,
        }
    Set_Ware_Pricing(name_price_dict = tuning_relative_value_dict)


#TODO: dynamic ware file check based on the item being modified.
@Check_Dependencies('TWareT.txt')
def Set_Ware_Pricing(
    #Dict of ware names and their relative values to use.
    name_price_dict = {},
    name_price_factor_dict = {}
    ):
    '''
    Sets ware pricing for the given ware list. Prices are the basic
    values in the T file, and have some adjustment before reaching
    the game pricing.
    Currently only works on tech wares in TWareT.txt.

    * name_price_dict:
      - Dict keyed by ware name (eg. 'SS_WARE_TECH213'), holding the
        flat value to apply for its T file price.
    * name_price_factor_dict:
      - As above, except holding a multiplier to apply to the existing
        price for the ware.
        Applies after name_price_dict if an item is in both dicts.
    '''    
    #Loop over the tech wares.
    for this_dict in Load_File('TWareT.txt'):

        #Check if this ware is one of the ones affected.
        if this_dict['name'] in name_price_dict:
            value = name_price_dict[this_dict['name']]
            #Loop over the fields being edited, for npc and player pricing.
            for field in ['relative_value_npc','relative_value_player']:
                this_dict[field] = str(int(value))

        #Do multiplier second.        
        if this_dict['name'] in name_price_factor_dict:
            #Loop over the fields being edited, for npc and player pricing.
            for field in ['relative_value_npc','relative_value_player']:
                #Get the value, multiply, and put back.
                value = int(this_dict[field])
                value *= name_price_factor_dict[this_dict['name']]
                this_dict[field] = str(int(value))

