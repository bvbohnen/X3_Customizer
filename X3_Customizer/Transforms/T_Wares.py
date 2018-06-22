'''
Edits to the ware lists.
'''
from .. import File_Manager


# In XRM, ship tuning pricing starts at a high value on the first tuning, then 
#  counts down.
# This leads to capped ships selling for a bit much (their small number of tunings
#  being highly valued), and odd decision making on tunings (ignore or go all-in).
# Some notes on how tuning pricing works are given further below.
# This transform will restore the vanilla tuning prices.

# -Removed, not very effective; comments kept for good tuning info.
'''
# Bump up the cost of engine and rudder tunings, to make their purchase more
#  meaningful, and help with immersion when most ships in the universe do not
#  have full tunings.
Increase_Tuning_Prices = True
# The game appears to fix the price scaling to end at 3000 credits for the last engine
#  upgrade (a 25 tuning scout and 15 tuning interceptor both experienced this).
# Similarly, rudder fixes the last upgrade at 2000.
# As such, adjusting the price here might just affect the first tuning price, and the
#  resulting price trend (eg. if it starts at 3000, then engine tunings should have
#  flat pricing).
# (In xrm, the starting high price goes down to 3000 on the last upgrade, suggesting
#  that is the cause if the count down problem.)
# If avoiding count-down issues, then the most tuning cost could be increase by
#  is ~2x (the 0 to 3k case averages 1.5k, and the new average would be 3k).
# If keeping this transform, rethink how the base price is set, since a multiplier
#  is insufficient as the original base price is extremely low and swamped out
#  by the hardcoded price scaling (eg. base price of 20 has jumps in the hundreds).
Tuning_cost_multiplier = 5
'''

@File_Manager.Transform_Wrapper('types/TWareT.txt', Vanilla = False, LU = False)
def Restore_Vanilla_Tuning_Pricing():
    '''
    Sets the price for ship tunings (engine, rudder, cargo) to those
    used in vanilla AP.  Meant for use with XRM.
    '''
    # Dict of ware names and their relative values to use,
    #  taken from the vanilla file in 02.cat.
    tuning_relative_value_dict = {
        # Cargo
        'SS_WARE_TECH251': 2,
        # Engine
        'SS_WARE_TECH213': 5,
        # Rudder
        'SS_WARE_TECH246': 3,
        }
    Set_Ware_Pricing(name_price_dict = tuning_relative_value_dict)


# TODO: dynamic ware file check based on the item being modified.
@File_Manager.Transform_Wrapper('types/TWareT.txt')
def Set_Ware_Pricing(
    # Dict of ware names and their relative values to use.
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
    # Loop over the tech wares.
    for this_dict in File_Manager.Load_File('types/TWareT.txt'):

        # Check if this ware is one of the ones affected.
        if this_dict['name'] in name_price_dict:
            value = name_price_dict[this_dict['name']]
            # Loop over the fields being edited, for npc and player pricing.
            for field in ['relative_value_npc','relative_value_player']:
                this_dict[field] = str(int(value))

        # Do multiplier second.        
        if this_dict['name'] in name_price_factor_dict:
            # Loop over the fields being edited, for npc and player pricing.
            for field in ['relative_value_npc','relative_value_player']:
                # Get the value, multiply, and put back.
                value = int(this_dict[field])
                value *= name_price_factor_dict[this_dict['name']]
                this_dict[field] = str(int(value))

    return

# Transform to set relative value the same for player and npcs, essentially
#  to remove the player factory advantage.
# Can either set player to npc (player factories less efficient, and throws
#  off existing complex calculators), or set npc to player (better npc
#  factories; less penalty allowing npcs to build weapons to them purchase).
# Go with the latter. This will impact many ware files, as well as lasers,
#  missiles, maybe some others.
# TODO: rethink this; weed/booze are easier for player to produce, but
#  lasers/etc. are often harder.  Want to consider in more detail what
#  side effects may be for changing this, and update the description
#  to be more accurate.
#  Could maybe tune these adjustments based on the value:credit ratio
#  of the ware type, in some smart way, to ensure factories are still
#  profitable.
# At the moment, it looks like the only way this would work well is if
#  the value:credit ratios could be normalized somehow,
#  since the player/npc production rate differences are
#  often driven by value ratio differences (eg. missiles have half
#  the ratio of lasers, and players produce missiles twice as fast
#  as npcs).
# -Removing transform for now; it doesn't seem the problems are solvable
#  when value:credit ratios are hardcoded.
# @File_Manager.Transform_Wrapper('types/TWareT.txt', 'TWareF.txt', 'TWareB.txt', 
#                     'TLaser.txt', 'TShields.txt', 'TMissiles.txt')
# def Normalize_Player_And_NPC_Production_Rates(
#     match_player_to_npc = False
#     ):
#     '''
#     Edits wares to ensure the NPC and player production rates are
#     matched. This is an experimental transform, while side effects
#     are worked out.
# 
#     * match_player_to_npc:
#       - If True, the player production rate is matched to the
#         NPC rate. If False (default), the NPC rate is matched
#         to the player rate.
#     '''
#     #Loop over the files that have been observed to have pricing
#     # differences.
#     for file_name in ['types/TWareT.txt', 'TWareF.txt', 'TWareB.txt', 
#                     'TLaser.txt', 'TShields.txt', 'TMissiles.txt']:
#         #Loop over the wares.
#         for this_dict in File_Manager.Load_File(file_name):
#             #Set one to the other, depending on the input arg.
#             #If these are already matched, this will change nothing.
#             if match_player_to_npc:
#                 this_dict['relative_value_player'] = this_dict['relative_value_npc']
#             else:
#                 this_dict['relative_value_npc'] = this_dict['relative_value_player']
# 
#     return

# Quick dummy transform, to help the File_Manager recognize these as files
#  that may be changed.
@File_Manager.Transform_Wrapper(
    'types/TWareT.txt', 'types/TLaser.txt', 'types/TShields.txt',
    'types/TMissiles.txt', 'types/TFactories.txt', 'types/TDocks.txt',
    'types/TWareF.txt', 'types/TWareB.txt', 'types/TWareE.txt',
    'types/TWareM.txt',  'types/TWareN.txt')
def _dummy():
    return

# No predetermined dependency on this one; check it live.
@File_Manager.Transform_Wrapper()
def Change_Ware_Size(
    ware_name = None,
    new_size = None,
    ware_file = None):
    '''
    Change the cargo size of a given ware.

    * ware_name:
      - String, the name of the ware, eg. 'SS_WARE_WARPING' for jumpdrive.
        This may include lasers, factories, etc.
    * new_size:
      - Integer for the ware size. Exact meaning of the integers depends on
        any mods in use. In vanilla AP, 1-5 are small through ST. In XRM,
        0-5 are small through ST, where 4 is XXL.
    * ware_file:
      - Optional string to help identify the ware file to look in, eg. 'TWareT'
        or 'TLaser'.
        If not given, ware files will be searched in order, skipping those not
        found in the source folder.
    '''
    # Get the ware files to search.
    if ware_file == None:
        # Try everything, but in rough order of expected need to search.
        ware_file_list = [
            'types/TWareT.txt', 'types/TLaser.txt', 'types/TShields.txt',
            'types/TMissiles.txt', 'types/TFactories.txt', 'types/TDocks.txt',
            'types/TWareF.txt', 'types/TWareB.txt', 'types/TWareE.txt',
            'types/TWareM.txt',  'types/TWareN.txt', ]
    else:
        # Pack in a list to match formatting, with a txt suffix.
        ware_file_list = [ware_file + '.txt']

    # Loop over the file  names.
    for file_name in ware_file_list:

        # Try to load it; skip if not found.
        line_dict_list = File_Manager.Load_File(file_name)
        if line_dict_list == None:
            continue

        # Loop over the wares.
        for this_dict in line_dict_list:
            # Search for a name match.
            if this_dict['name'] == ware_name:

                # Apply the change and return.
                this_dict['cargo_size'] = str(new_size)
                return

    # If here, the ware wasn't found.
    print('Change_Ware_Size error: ware {}'
         ' not found in searched files.'.format(ware_name))
    return

    
def Get_Ware_Cost(ware_list):
    '''
    Returns the estimated cost of wares in a given list.
    All wares should be in TWaresT.
    Cost is given as estimated credits.
    '''
    total_cost = 0
    for this_dict in File_Manager.Load_File('types/TWareT.txt'):
        if this_dict['name'] in ware_list:
            total_cost += int(this_dict['relative_value_npc'])
    # Apply scaling and return.    
    return total_cost * Flags.Value_to_credits_ratio_dict['TWareT']