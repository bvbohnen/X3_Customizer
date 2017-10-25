'''
Split off file from T_Ships, holding the variant ship generation code.
'''
from File_Manager import *
import Flags
import math
from collections import defaultdict
import copy
from T_Ships import *
from T_Wares import *


'''
Notes on adding new ship variants:

Varients are distinguished by a variation_index field.
From looking at random ships in xrm:
    0: base
    1: vanguard
    2: sentinel
    3: raider
    4: hauler
    9: unknown, used by heavy centaur.
    13: unknown, used by griffon.
    19: unknown, used by notus hauler.
    20: unknown, used by heavy centaur prototype, enhanced elite.
        https://forum.egosoft.com/viewtopic.php?p=4221390 suggests this means
        a heavy version of a ship, m3+, m2+, etc., but this doesn't seem to
        match the XRM files very consistently. Vanilla files somewhat match
        this, however.

The jobs file seems to clean this up a bit, with check boxes having various
labels (some being unlabelled).
    0 : basic
    1 : vanguard
    2 : sentinel
    3 : raider
    4 : hauler
    5 : miner
    6 : super freighter
    7 : tanker
    8 : mk 1
    9 : unlabelled, couger in xrm
    10 : unlabelled, hyperion in xrm, also a hand-named 'medusa vanguard' which
                     may need blacklisting.
    11 : unlabelled, talon in xrm
    12 : unlabelled
    13 : unlabelled
    14 : tanker xl
    15 : super freighter xl
    16 : vanguard, used by Hyperion and kite (an actual variant of base kite).
    19 : hauler (used for griffon, panther, colossus; editor recognizes this 
         as adding the hauler suffix, though it never has stat variation from
         a base type (griffon/panther have no base, colossus has same stats)).
         This may need some special handling in the case of the griffon, but
         the panther/colossus are generally not part of the game.
         If a hauler is auto-added for tag 4, it will have the same name as
         with tag 19.
    20?: advanced

If adding new variants programmatically, some issues to consider:

    -How to parse the existing ships to find variants and the base ship
    they map to?
    One commonality appears to be the name index, which is always the same
    between variants, suggesting the variant name prefix is added automatically.
    Can sort all ships by name index, and check that all ships for a given
    name are disjoint variants.

    -How to select adjustments for each variation, eg. shields, hull, etc.?
    Once existings variants are found, can gather their variations in a select
    group of fields:
        laser gen, 
        shield gen, 
        speed, 
        turning, 
        total shields, 
        hull, 
        cargo, 
        price
    Other fields, eg. missile compatibility or cargo size, can be ignored,
    since it is rare for them to change (eg. a falcon hauler that can carry xl wares).

    -How to add variants to an existing game?
    The jobs file may select variants automatically (randomly), partially populating
    the universe.
    Making variants available for purchase would require adding them manually to
    shipyards.
    If added through x3_universe, any shipyard with a base variant can have all
    new variants added, but that may only work on a new game.
     
    -How to ignore non-ships that are in tships, like drones and weapon platforms?
    These cases appear to have 0 speed extensions generally.
    Advanced space suit in xrm does have extensions, but no cargo space.
    Normal space suit has 1 cargo, some speed extensions, no rudder extensions.
    Others, like freight drones, have cargo but not speed extensions.
    Can require modified ships have both cargo and both extension types.

    -How to capture built in wares, eg. ore collector for miner variants.
    TODO: think about this.

'''

@Check_Dependencies('TShips.txt', 'WareLists.txt', 'TWareT.txt')
def Add_Ship_Combat_Variants(
        include_advanced_ships = True,
        print_variant_modifiers = False,
        print_variant_count = False,
        blacklist = None,
        ):
    '''
    Adds combat variants for combat ships. This is a convenience function
    which calls Add_Ship_Variants with variants [vanguard, sentinel, raider,
    hauler], for ship types [M0-M8].

    * blacklist:
      - List of names of ships not to generate variants for.
    * include_advanced_ships:
      - Bool, if True then existing heavy ships (variation 20) and other 
        non-basic ships will have variants added. This may result in some
        redundancies, eg. variants of Mercury and Advanced Mercury.
        In some cases, the existing ship will be reclassified as a basic
        version, eg. Hyperion Vanguard will become a base Hyperion from
        which a vanguard and other variants are generated.
        Default True.
    * print_variant_count:
      - Bool, if True then the number of new variants added will be printed.
    * print_variant_modifiers:
      - Bool, if True then the calculated attributes used for variants will 
        be printed, given as multipliers on base attributes for various ship
        attributes. Default False.
    '''
    Add_Ship_Variants(
        ship_types = [
            'SG_SH_M0',
            'SG_SH_M1',
            'SG_SH_M2',
            'SG_SH_M3',
            'SG_SH_M4',
            'SG_SH_M5',
            'SG_SH_M6',
            'SG_SH_M7',
            'SG_SH_M8',
            ],
        variant_types = [
            'vanguard',
            'sentinel',
            'raider',
            'hauler',
            ],
        blacklist = blacklist,
        include_advanced_ships = include_advanced_ships,
        print_variant_modifiers = print_variant_modifiers,
        print_variant_count = print_variant_count
        )
    
@Check_Dependencies('TShips.txt', 'WareLists.txt', 'TWareT.txt')
def Add_Ship_Trade_Variants(
        include_advanced_ships = True,
        print_variant_modifiers = False,
        print_variant_count = False,
        blacklist = None,
        ):
    '''
    Adds trade variants for trade ships. This is a convenience function
    which calls Add_Ship_Variants with variants [hauler, miner, tanker (xl),
    super freighter (xl)], for ship types [TS,TP,TM,TL].
    
    * blacklist:
      - List of names of ships not to generate variants for.
    * include_advanced_ships:
      - Bool, if True then existing heavy ships (variation 20) and other 
        non-basic ships will have variants added. This may result in some
        redundancies, eg. variants of Mercury and Advanced Mercury. Default True.
    * print_variant_count:
      - Bool, if True then the number of new variants added will be printed.
    * print_variant_modifiers:
      - Bool, if True then the calculated attributes used for variants will 
        be printed, given as multipliers on base attributes for various ship
        attributes. Default False.
    '''
    Add_Ship_Variants(
        ship_types = [
            'SG_SH_TS',
            'SG_SH_TP',
            'SG_SH_TM',
            'SG_SH_TL',
            ],
        variant_types = [
            'hauler',
            'miner',
            'tanker',
            'tanker xl',
            'super freighter',
            'super freighter xl',
            ],
        blacklist = blacklist,
        include_advanced_ships = include_advanced_ships,
        print_variant_modifiers = print_variant_modifiers,
        print_variant_count = print_variant_count
        )

    
#Set up a dict matching variant names to their indices in tships.
variant_type_index_dict = {
    'basic'              : 0,
    'vanguard'           : 1,
    'sentinel'           : 2,
    'raider'             : 3,
    'hauler'             : 4,
    'miner'              : 5,
    'super freighter'    : 6,
    'tanker'             : 7,
    'tanker xl'          : 14,
    'super freighter xl' : 15,
    }
#For convenience, build the reverse lookup dict.
variant_index_type_dict = {x:y for y,x in variant_type_index_dict.items()}


#Keep a global dict with the varient modifiers.
#This is only calculated on the first call, to avoid generated variants
# from being seen in the analysis in later calls.
variant_field_ratios_dict_dict = None


@Check_Dependencies('TShips.txt', 'WareLists.txt', 'TWareT.txt')
def Add_Ship_Variants(
        ship_types = [
            'SG_SH_M0',
            'SG_SH_M1',
            'SG_SH_M2',
            'SG_SH_M3',
            'SG_SH_M4',
            'SG_SH_M5',
            'SG_SH_M6',
            'SG_SH_M7',
            'SG_SH_M8',
            'SG_SH_TS',
            'SG_SH_TP',
            'SG_SH_TM',
            'SG_SH_TL',
            ],
        variant_types = [
            'vanguard',
            'sentinel',
            'raider',
            'hauler',
            'miner',
            'tanker',
            'tanker xl',
            'super freighter',
            'super freighter xl',
            ],
        race_types = None,
        blacklist = None,
        include_advanced_ships = True,
        print_variant_modifiers = False,
        print_variant_count = False,
    ):
    '''
    Adds variants for various ships.  The new variant ships may be spawned
    by jobs where they match the job criteria.  New ships are added to
    shipyards in the x3_universe file, though require a new game to show
    up.
    Variant attribute modifiers are based on the average differences between
    existing variants and their basic ship, where only M3,M4,M5 are
    analyzed for combat variants, and only TS,TP are analyzed for trade variants,
    with Hauler being considered both a combat and trade variant.
    Special attributes, such as turret count and weapon compatibitities, are not
    considered.
    Variants are added base on ship name and race; pirate variants are handled
    separately from standard variants.
    Ships without extensions or cargo are ignored (eg. drones, weapon platforms).

    * ship_types:
      - List of ship names or types to add variants for,
        eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].
    * variant_types:
      - List of variant types to add. Variant names are given as strings, and
        support the following list:
           ['vanguard',
            'sentinel',
            'raider',
            'hauler',
            'miner',
            'tanker',
            'tanker xl',
            'super freighter',
            'super freighter xl']
    * blacklist:
      - List of names of ships not to generate variants for.
    * race_types:
      - List of race names whose ships will have variants added. By default,
        the following are included: [Argon, Boron, Split, Paranid, Teladi, 
        Xenon, Khaak, Pirates, Goner, ATF, Terran, Yaki].
    * include_advanced_ships:
      - Bool, if True then existing heavy ships (variation 20) and other 
        non-basic ships will have variants added. This may result in some
        redundancies, eg. variants of Mercury and Advanced Mercury.
        In some cases, the existing ship will be reclassified as a basic
        version to remove their suffix, eg. Hyperion Vanguard will become 
        a base Hyperion from which a vanguard and other variants are generated.
        Default True.
    * print_variant_count:
      - Bool, if True then the number of new variants added will be printed.
    * print_variant_modifiers:
      - Bool, if True then the calculated attributes used for variants will 
        be printed, given as multipliers on base attributes for various ship
        attributes. Default False.
    '''

    #Make an empty blacklist list if needed.
    if blacklist == None:
        blacklist = []


    #Suffixes to use for generated ship naming.
    #This is just laid out manually, to make it clear and tweak the
    # xl entries to distinguish them, while keeping suffixes short
    # and expressive.
    #Names are generally uppercase, so maintain that here.
    #Avoid ever changing these, since they will break ships in an
    # existing save game using the old name.
    #Limitations on ship names are unknown; there seems to be room
    # for a moderate number of letters.  Try to limit to ~6 here.
    #Stick an underscore, since that is common in existing names.
    variant_suffix_dict = {
        'basic'              : '_BASIC',
        'vanguard'           : '_VAN',
        'sentinel'           : '_SENT',
        'raider'             : '_RAID',
        'hauler'             : '_HAUL',
        'miner'              : '_MINE',
        'super freighter'    : '_SFR',
        'tanker'             : '_TANK',
        'tanker xl'          : '_TANKXL',
        'super freighter xl' : '_SFRXL',
        }

    #Set up a list of mining equipment to add to mining variants.
    #TODO: look this up dynamically, to also account for its value when
    # checking ship cost adjustments.
    #Goal is to correct the cost adjustment to subtract off mining gear,
    # then add it back later.
    mining_equipment = [
        #For now, hardcode these.
        'SS_WARE_ORECOLLECTOR',
        'SS_WARE_TECH275', #Mineral scanner.
        'SS_WARE_SW_SPECIAL_1', #Special command software
        ]

    #Get the cost of equipment for miners.
    #-Not needed; equipment cost is not part of ship base price, but gets
    # added at purchase time, so don't worry about it here.
    #miner_cost_adjustment = Get_Ware_Cost(mining_equipment)

    #Note the variation indices belonging to some of the redundantly
    # suffixed ships, eg. hyperion vanguard and notus hauler.
    #These can get replaced with 0 when no basic version is available
    # and the base ship used had one of that variant ids.
    #The main goal is to avoid having eg. two Hyperion Vaguard ships,
    # one with id 16 and one with the normal id.
    redundant_variant_indices = [
        16, #Vanguard
        19, #Hauler
        ]


    #Set the ship types that will be used for analysis of each
    # variant type.
    #The main goal here is to omit some outliers, such as the sentinel
    # varients in xrm for transports and corvettes which involves heavy
    # modifications to turrets/etc. which aren't easily captured.
    analysis_combat_ship_types = [
        #Focus on fighters, the main ship type with variants.
        'SG_SH_M3',
        'SG_SH_M4',
        'SG_SH_M5',
        ]
    analysis_trade_ship_types = [
        'SG_SH_TS',
        #Could ignore TPs, but hauler is a common variant.
        'SG_SH_TP',
        ]
    #Build a convenience dict matching variants to ship types.
    variant_analysis_ship_type_list_dict = {
        'vanguard'           : analysis_combat_ship_types,
        'sentinel'           : analysis_combat_ship_types,
        'raider'             : analysis_combat_ship_types,
        #Hauler will compare against combat and trade ships.
        'hauler'             : analysis_combat_ship_types + analysis_trade_ship_types,
        'miner'              : analysis_trade_ship_types,
        'super freighter'    : analysis_trade_ship_types,
        'tanker'             : analysis_trade_ship_types,
        'tanker xl'          : analysis_trade_ship_types,
        'super freighter xl' : analysis_trade_ship_types,
        }

    #Set the variants to ignore.
    #These will not be used in analysis, will not be used as base ships,
    # and will generally be skipped.
    variant_indices_to_ignore = [
        #Avoid mk 1 ships, so as not to make variants of them, as that
        # gets confusing. Eg. 'colossus mk 1' becomes 'colossus raider'
        # because the variant flag gets overwritten.
        8,
        ]

    #Define the race ships which will be analyzed for setting modifiers.
    races_for_modifiers = [
        'Argon', 
        'Boron', 
        'Split', 
        'Paranid', 
        'Teladi', 
        'Xenon', 
        'Khaak', 
        'Pirates', 
        'Goner', 
        'ATF', 
        'Terran', 
        'Yaki',
        ]
    #If a race_list wasn't given, set it to the above.
    if race_types == None:
        race_types = races_for_modifiers


    #Build a list of all ship names.
    #This is used later to ensure generated names have no conflicts
    # with existing names.
    ship_names_list = []
    for ship_dict in Load_File('TShips.txt'):
        ship_names_list.append(ship_dict['name'])

    
    #Build a (name,race) : variant index : ship_list dictionary.
    #The stored ships will use their line dicts, for easier analysis.
    #Variant index is used instead of type, since some indices may not
    # be named above (eg. heavy/advanced variants).
    #To distinguish ships of the same general type, the name_id will be used,
    # and race is appended to distinguish pirate variants from others.
    # Eg. all Mercury variants use the same name_id, despite having different
    # internal names, so this will gather all Mercuries together (maybe 
    # ignoring the advanced mercury).
    name_variant_id_ship_dict_dict_dict = defaultdict(dict)
    for ship_dict in Load_File('TShips.txt'):

        #Skip those without cargo.
        if int(ship_dict['cargo_min']) == 0:
            continue
        #Skip those without extensions.
        if int(ship_dict['speed_tunings']) == 0:
            continue
        if int(ship_dict['rudder_tunings']) == 0:
            continue
        #Skip those not of a standard race.
        race_type = Flags.Race_code_name_dict[int(ship_dict['race'])]
        if race_type not in races_for_modifiers:
            continue
        #Skip those blacklisted.
        if ship_dict['name'] in blacklist:
            continue
        
        #Grab the variant index.
        variation_index = int(ship_dict['variation_index'])

        #If this is an index to ignore, skip it.
        if variation_index in variant_indices_to_ignore:
            continue

        #If not including advanced/misc variants as base, ignore
        # them here.
        if (not include_advanced_ships 
        and variation_index not in variant_index_type_dict):
            continue

        #Determine the name tuple for this ship.
        #Combine name_id with race.
        key = (ship_dict['name_id'], race_type)

        #Error if a ship with this key already found somehow, eg. the
        # same race has another ship of the same name and variant.
        assert variation_index not in name_variant_id_ship_dict_dict_dict[key]
        
        #Everything else should be fairly safe to add in.
        name_variant_id_ship_dict_dict_dict[key][variation_index] = ship_dict


    
    #Define the fields being modified.
    #Aim to use existing field names where reasonable, though shielding will
    # need special handling to deal with cases where shield type changes.
    fields_to_modify = [
        'yaw',
        'pitch',
        'roll',
        'speed',
        'acceleration',
        'shield_power',
        'weapon_energy',
        'weapon_recharge_factor',
        #To be safe, check speed/rudder extensions, since these appear to
        # vary on some pirate variants.
        #It may be best to wrap these into speed/turning directly.
        #-Removed, handled with speed and turning.
        #'speed_tunings',
        #'rudder_tunings',
        #It is possible that cargo min may get boosted on average more
        # than cargo max, which for select ships could make the min
        # overtake the max.  Fix that below at some point.
        'cargo_min',
        'cargo_max',
        'hull_strength',
        'angular_acceleration',
        #Both values should be the same, but easier to modify separately
        # to avoid a special case.
        'production_value_npc',
        'production_value_player',
        #Shielding will be a special case, relying on both
        # shield_type and max_shields.
        'shielding',
        #To handle tankers in xrm, also track ware size changes.
        #Without reducing this, tankers are overpowered a bit.
        'cargo_size',
        ]

    
    #Can now gather the variation statistics.
    #Check if the global dict has these already.  If not, need to calculate
    # them on the first call.
    global variant_field_ratios_dict_dict
    if variant_field_ratios_dict_dict == None:
    
        #Goal is to build a list of ratios for each variant type and each
        # variant field. Eg. ['raider']['speed'] = [1.1, 1.15]
        #Populate this with initial entries for all variants.
        variant_field_ratios_list_dict_dict = defaultdict(lambda: defaultdict(list))

        #Loop over the ship names.
        #Each gets considered separately.
        for variant_id_ship_dict_dict in name_variant_id_ship_dict_dict_dict.values():

            #If there is no base variant to compare against, skip.
            #This occurs for heavy ships or similar.
            if variant_type_index_dict['basic'] not in variant_id_ship_dict_dict:
                continue
            basic_dict = variant_id_ship_dict_dict[variant_type_index_dict['basic']]

            #Skip if the basic variant was an added ship.

            #Loop over all variants, not just those being added.
            #Since this is only run once, it needs to gather everything
            # needed for any future transform calls.
            for variant_type in variant_type_index_dict:
                #Skip the basic variant.
                if variant_type == 'basic':
                    continue
                #Get the index of this variant type.
                variant_index = variant_type_index_dict[variant_type]

                #Skip if this ship type is not being used in analysis of this
                # variant type.
                if basic_dict['subtype'] not in variant_analysis_ship_type_list_dict[variant_type]:
                    continue

                #Skip if this variant not present for this ship.
                if variant_index not in variant_id_ship_dict_dict:
                    continue
                variant_dict = variant_id_ship_dict_dict[variant_index]

                #Can now grab ratios, since both the variant and the base
                # ship exist.
                #Loop over the fields of interest.
                for field in fields_to_modify:

                    #Grab the value for the base ship and the variant.
                    #Special handling on shields.
                    if field == 'shielding':
                        #Calculate shielding for basic and variant.
                        #This has some copy/paste, but not worth trying to
                        # set up code sharing on this.
                        basic_shield_slots = int(basic_dict['max_shields'])
                        basic_shield_size  = Flags.Shield_type_size_dict[
                                int(basic_dict['shield_type'])]
                        basic_value = basic_shield_slots * basic_shield_size
                    
                        variant_shield_slots = int(variant_dict['max_shields'])
                        variant_shield_size  = Flags.Shield_type_size_dict[
                                int(variant_dict['shield_type'])]
                        variant_value = variant_shield_slots * variant_shield_size

                    #Special handling on speed tuning related values.
                    elif field in ['speed', 'acceleration']:
                        #Wrap tunings into the values, to capture their variation
                        # at the same time.
                        basic_value   = (int(basic_dict[field]) 
                                         * (1 + int(basic_dict['speed_tunings'])/10))
                        variant_value = (int(variant_dict[field]) 
                                         * (1 + int(variant_dict['speed_tunings'])/10))
                    

                    #Special handling on rudder tuning related values.
                    #TODO: Should angular acceleration be included here?
                    elif field in ['yaw', 'pitch', 'roll']:
                        #Wrap tunings into the values, to capture their variation
                        # at the same time.
                        basic_value   = (float(basic_dict[field]) 
                                         * (1 + int(basic_dict['rudder_tunings'])/10))
                        variant_value = (float(variant_dict[field]) 
                                         * (1 + int(variant_dict['rudder_tunings'])/10))


                    #-Removed; equipment is not part of base cost, so no special
                    # adjustment needed here for miners.
                    ##Special handling on value/cost, if this is a miner.
                    #elif (field in ['production_value_npc', 'production_value_player']
                    #and variant_type == 'miner'):
                    #    #Get the normal values.
                    #    basic_value   = int(basic_dict[field])
                    #    variant_value = int(variant_dict[field])
                    #    #Subtract off the mining equipment pricing from
                    #    # the variant.
                    #    ...


                    else:
                        #Grab the field values directly.
                        #Might be int or float, try both.
                        #TODO: think about how to put back correctly.
                        try:
                            basic_value   = int(basic_dict[field])
                            variant_value = int(variant_dict[field])
                        except ValueError:
                            basic_value   = float(basic_dict[field])
                            variant_value = float(variant_dict[field])

                    #This could be 0 in the special case of cargo size.
                    #Manually handle that case.
                    if basic_value == 0:
                        ratio = 1
                    else:
                        ratio = variant_value / basic_value

                    #Some debug checks for oddball cases.
                    if field == 'speed_tunings' and ratio != 1:
                        stop = 1
                    if field == 'rudder_tunings' and ratio != 1:
                        stop = 1
                    #There may be an odd outlier on one of the metrics.
                    if ratio > 20:
                        stop = 1

                    #Calculate the ratio and store it.
                    variant_field_ratios_list_dict_dict[variant_type][field].append(ratio)


        #From the lists, can now calculate average ratios.
        #This is kinda clumsy with dict comprehensions, but try it out.
        variant_field_ratios_dict_dict = {
            #Outer dict needs to make an inner dict.
            variant : {
                #Calculate the average.
                field : sum(ratio_list) / len(ratio_list) 
                for field, ratio_list in field_ratios_list_dict.items()
                }
            for variant, field_ratios_list_dict in variant_field_ratios_list_dict_dict.items()
            }


        #Apply a special fix for cargo min/max, unifying the ratios so
        # that adjustments can be made safely to all ships (eg. those with
        # min and max set the same).
        #These changes could be averaged, but that may lead to oddities,
        # eg. if min changes a lot and max does not, this will result in
        # an excessive boost to max.
        #For now, just apply the max ratio to the min.
        for field_ratios_dict in variant_field_ratios_dict_dict.values():
            #cargo_ratio = field_ratios_dict['cargo_min'] + field_ratios_dict['cargo_max']/2
            field_ratios_dict['cargo_min'] = field_ratios_dict['cargo_max']
                

    #Print these out if desired.
    if print_variant_modifiers:
        print('Variant modifiers:')
        for variant, field_ratios_dict in variant_field_ratios_dict_dict.items():
            print('  Variant {}'.format(variant))
            for field, ratio in field_ratios_dict.items():
                print('    {: <30} : {:.3f}'.format(field, ratio))



    #Now that the modifiers are known, need to determine the base ships to
    # add variants for.
    #Keep a list of the new ships being created.
    new_ships_list = []
    #Keep a list of the new miner variants, which will have an ore collector
    # and mineral scanner and special command software added as built-in equipment.
    #TODO: These should also have the mobile drilling system added as a compatibility
    # if possible, though that can be kicked down the road.
    new_miners_list = []

    #Loop over the ship names.
    #Each gets considered separately.
    for name_id, variant_id_ship_dict_dict in name_variant_id_ship_dict_dict_dict.items():

        #The base variant will either be the actual base, or potentially
        # a non-standard variant (eg. heavy/20 or special hauler/19).
        if 0 in variant_id_ship_dict_dict:
            basic_dict = variant_id_ship_dict_dict[0]

        #Looking up non-standard variants is kinda tricky to do programmatically.
        #Can convert the variant type keys into sets, and look for difference.
        elif set(variant_id_ship_dict_dict) - set(variant_index_type_dict):

            #Find the first non-standard variant.
            #To ensure this is the same on every run (in case there are
            # several to pick from), sort by variant index.
            basic_dict = None
            for variant_index, basic_dict in sorted(variant_id_ship_dict_dict.items()):
                if variant_index not in variant_index_type_dict:
                    break
            #Error check.
            assert basic_dict != None
            #This shouldn't occur unless advanced ships were included.
            assert include_advanced_ships

            #If this has a redundant variant index, can assign it to 0 to
            # avoid a generated variant having overlap with the redundant
            # name, or possibly to 20 to clarify it as special.
            # Go with 0 for now.
            #Eg. if basing off Hyperion Vanguard, change it to Hyperion
            # before making variants.
            if int(basic_dict['variation_index']) in redundant_variant_indices:
                basic_dict['variation_index'] = str(0)
                del(variant_id_ship_dict_dict[variant_index])
                variant_id_ship_dict_dict[0] = basic_dict

        else:
            #Nothing was found for the base type.
            #Here, a base will need to be generated be downscaling an existing
            # variant.
            #TODO. Just print a quick warning for now and skip ahead.
            # This did not come up during testing, but may occur for some
            # mod combo out there.
            print('Warning, no basic version found for {}, skipping'.format
                  (name_id))
            continue


        #TODO:
        #Consider pruning out any redundant_variant_indices somehow, perhaps
        # converting them to standard indices if there was a proper base
        # version of the ship.
        #Eg. vanilla has a kite and kite vanguard (index 16), where the vanguard
        # could be swapped to index 1 to fill the role of the standard vanguard,
        # blocking generation of a new one.
        #In this case, only the swap in the variant_id_ship_dict_dict is
        # needed; the ship itself can remain 16.
        #The problem with this is that some of these special variants don't
        # actually exist in game, resulting in a gap in the generated
        # variants needlessly, eg. with the colossus hauler.
        #For now, just allow redundancies.
        

        #Skip if this is not a ship type to modify.
        if (basic_dict['subtype'] not in ship_types
        and basic_dict['name'] not in ship_types):
            continue


        #With the base type selected, can now start filling in the variants.
        #Loop over the variants being added.
        for variant_type in variant_types:
            varient_index = variant_type_index_dict[variant_type]

            #Can skip this if the variant already exists.
            if varient_index in variant_id_ship_dict_dict:
                continue

            #Make a copy of the basic_dict.
            #Shallow copy should be fine for this, but deep copy to be
            # safe in case of future code changes that might add annotation
            # fields or similar.
            new_ship_dict = copy.deepcopy(basic_dict)

            #Need to edit the name.
            #Add the predefined suffix for the variant type.
            new_name = new_ship_dict['name'] + variant_suffix_dict[variant_type]
            #Toss an error if the name is taken; it shouldn't be, but be safe.
            if new_name in ship_names_list:
                raise Exception('Variant name {} already taken.'.format(new_name))
            new_ship_dict['name'] = new_name

            #Record the variant index for this ship, for recognition in game
            # and also in future transform calls.
            new_ship_dict['variation_index'] = str(varient_index)

            #For modifiers, shields should be edited first, since the amount of
            # shielding actually modified will be used to adjust the speed
            # modifier for this ship.
            #Indent this just for clarity.
            if 1:
                #Preference here is to modify the number of shield slots,
                # but it will be important to also be able to swap shield
                # type for better accuracy, since some cases may have base
                # ships with only a single shield slot (eg. 1x1GJ), which
                # can't be downscaled for raider variants without changing
                # type.
                #This should only need to search 1 step up/down at most, and
                # should try to avoid having an excess shield count.
                # The typical high shield counts are around 6 in game.

                #Grab the shield ratio.
                ratio = variant_field_ratios_dict_dict[variant_type]['shielding']

                #Look up the starting slots and size.
                shield_slots = int(new_ship_dict['max_shields'])
                shield_type = int(new_ship_dict['shield_type'])
                shield_size  = Flags.Shield_type_size_dict[shield_type]

                #Calculate the starting and target shield values.
                start_value = shield_slots * shield_size
                target_value = start_value * ratio

                #Make a small support function.
                #This will add or remove shields until a min error
                # has been found.
                def Find_min_error(shield_size):
                    'Returns (error, shield_slots to use)'

                    #Start from 1 shield, go up.
                    shield_slots = 1

                    #Calc the initial error.
                    error = abs(target_value - shield_slots * shield_size)

                    #Loop until error gets worse.
                    #TODO: maybe try to limit adjustment so that the
                    # new shield value is between the original shield value
                    # and the target (eg. if target is +20%, keep in the
                    # 0-20% range, don't go to 25%). This probably doesn't
                    # make much difference, though, and might be more
                    # interesting to allow overshoot.
                    while 1:
                        #Add a shield.
                        new_shield_slots = shield_slots + 1

                        #Calculate the shielding at this step.
                        new_shielding = new_shield_slots * shield_size
                        #Calc error.
                        new_error = abs(target_value - new_shielding)

                        #If error got worse, done.
                        if new_error > error:
                            break

                        #Record this point and loop.
                        error = new_error
                        shield_slots = new_shield_slots

                    return error, shield_slots


                #Get the error at the start size.
                shield_type_0 = shield_type
                shield_size_0 = shield_size
                error_0, shield_slots_0 = Find_min_error(shield_size_0)

                #Try +1
                shield_type_1 = shield_type + 1
                #Skip if there is no +1, eg. this was already 2GJ.
                if shield_type_1 in Flags.Shield_type_size_dict:
                    shield_size_1 = Flags.Shield_type_size_dict[shield_type_1]
                    error_1, shield_slots_1 = Find_min_error(shield_size_1)
                else:
                    #Just set error as higher so this doesn't get used.
                    error_1 = error_0 +1

                #Try -1
                shield_type_2 = shield_type - 1
                #Check this as above.
                if shield_type_2 in Flags.Shield_type_size_dict:
                    shield_size_2 = Flags.Shield_type_size_dict[shield_type_2]
                    error_2, shield_slots_2 = Find_min_error(shield_size_2)
                else:
                    error_2 = error_0 +1


                #Now need to pick the best that didn't go over the
                # shield count limit.
                #8 is the highest seen in xrm for a semi-normal ship,
                # though 7 is the typical max.
                #Be lenient here and allow 8 for better matching.
                shield_slots_limit = 8
                #Start with same shield size.
                best_type = shield_type_0
                best_size = shield_size_0
                best_slots = shield_slots_0
                best_error = error_0
                #Swap to +1 if it was better.
                if error_1 < best_error and shield_slots_1 <= shield_slots_limit:
                    best_type = shield_type_1
                    best_size = shield_size_1
                    best_slots = shield_slots_1
                    best_error = error_1
                #Swap to -1 if it was better.
                if error_2 < best_error and shield_slots_2 <= shield_slots_limit:
                    best_type = shield_type_2
                    best_size = shield_size_2
                    best_slots = shield_slots_2
                    best_error = error_2

                #Can now apply the new shield type.
                new_ship_dict['max_shields'] = str(best_slots)
                new_ship_dict['shield_type'] = str(best_type)


                #The final shield value may be significantly off from the
                # targetted value.
                #To avoid a ship with a too-high shield being too strong,
                # or a too-low shield being too weak, can rescale the ship
                # speed value based on the error here.
                #Eg. and overshielded raider will lose some of its speed
                # boost.
                #Calculate the actual ratio applied to shielding.
                actual_ratio = best_size * best_slots / start_value
                
                #If this ratio is too high, the ship is overshielded and
                # needs a speed reduction.
                #If this ratio is too low, the ship is undershielded and
                # needs a speed buff.
                #In either case, the speed adjustment will not match the
                # shielding error, since shield does not transfer 1:1 to
                # speed.
                #The best approach is maybe to apply the ratio of ratios
                # to the speed ratio used elsewhere.
                # For instance, if only half the shield adjustment were
                # applied, then only half the speed adjustment should be
                # applied.
                #Eg. if the shield was supposed to be -20%, and was actually
                # -15%, it has a (1-.85)/(1-.8) = .75 factor on this adjustment,
                # and can apply a .75 factor to the speed % change; if the
                # speed ratio was 1.1, it would become ((1.1-1)*.75)+1 = 1.075.
                #Does this also work for the increased-shield case?
                # Eg. +15% applied of +20%: (1-1.15)/(1-1.2) = .75 still.
                # It should be fine in both cases.
                #Calculate the shield part of it here, speed part of it later.
                #Also do an error check if ratio == 1 (and avoid /0 error).
                if ratio == 1:
                    assert actual_ratio == 1
                    amount_of_shield_ratio_applied = 1
                else:
                    amount_of_shield_ratio_applied = (1-actual_ratio) / (1-ratio)


            #Loop over the modifiers.
            for field, ratio in variant_field_ratios_dict_dict[variant_type].items():

                #Skip shielding; it was already handled.
                if field == 'shielding':
                    continue

                #May be float or int. Use try/except to catch this.
                try:
                    value = int(new_ship_dict[field])

                    #If this is speed/acceleration, handle it specially.
                    if field in ['speed','acceleration']:
                        #Determine how much of the ratio to apply.
                        #Basically, take difference from 1, scale that diff
                        # by how much of the shield diff was applied, and
                        # then add back the 1.
                        actual_ratio = (ratio -1) * amount_of_shield_ratio_applied +1
                        value *= actual_ratio

                    else:
                        #Direct ratio application.
                        value *= ratio

                    #Round it.
                    #Some special cases will have a coarse rounding.
                    #Cargo is probably the most important to refine right
                    # now, and maybe hull; others can be tweaked later.
                    if field in ['cargo_min','cargo_max']:
                        if value > 10000:
                            value = math.ceil(value/1000)*1000
                        elif value > 1000:
                            #Nearest 50 is common for cargo.
                            value = math.ceil(value/50)*50
                        elif value > 500:
                            value = math.ceil(value/10)*10
                        else:
                            value = round(value)
                            
                    elif field == 'cargo_size':
                        #Need to bound cargo size to the 0-5 range, just in
                        # case a scout tanker tried to reduce it.
                        value = max(0, value)
                        value = min(5, value)
                        #It is probably safe to round this.
                        #One special falcon increases cargo size, but not enough
                        # to pull up the average ratio where cargo size will
                        # be increased ever.
                        #Tankers in xrm reduce cargo size, commonly enough that
                        # the ratio should drop the size here by 1 tick.
                        #Can check these in game to make sure there are no
                        # oddities for now.
                        value = round(value)

                    elif field == 'hull':
                        #Hull scaling copied from the hull transform above.
                        if value > 10000:
                            value = math.ceil(value/1000)*1000
                        elif value > 1000:
                            value = math.ceil(value/100)*100
                        else:
                            value = math.ceil(value/10)*10
                    else:
                        #Others get simple rounding.
                        value = round(value)

                    #Put it back.
                    new_ship_dict[field] = str(int(value))

                except ValueError:
                    #Floats will not have as complicated rounding, since
                    # they don't get displayed directly in game.
                    value = float(new_ship_dict[field]) * ratio
                                                
                    #Put it back.
                    #Aim for no more than 7 decimal places.
                    #Use 6, as in the tunings transform.
                    new_ship_dict[field] = str('{0:.6f}'.format(value))


            #Name is updated and modifiers applied, so the new ship
            # should be ready.
            new_ships_list.append(new_ship_dict)
            #Record miners.
            if variant_type == 'miner':
                new_miners_list.append(new_ship_dict)


    #All new ships will be put at the bottom of the tships dict_list.
    #This will require that the header be modified to account for the
    # new lines.
    t_file = Load_File('TShips.txt', return_t_file = True)

    #Add the new ships.
    #These need to go in both the data and line lists, data for future
    # visibility to this and other transforms, lines to be seen at
    # writeout.
    t_file.data_dict_list += new_ships_list
    t_file.line_dict_list += new_ships_list

    #Find the header line.
    for line_dict in t_file.line_dict_list:
        #Looking for the first non-comment line; it should have
        # 3 entries (with newline).
        if not line_dict[0].strip().startswith('/') and len(line_dict) == 3:
            #The second field is the ship count.
            #It was labelled as 'name', to match normal data lines.
            line_dict['name'] = str(int(line_dict['name']) + len(new_ships_list))
            break
            
        #Error if hit a data line.
        assert line_dict is not t_file.data_dict_list[0]

    #Note how many ships were added.
    if print_variant_count:
        print('Number of new variants added: {}'.format(len(new_ships_list)))


    #Add miner equipment.
    Add_Ship_Equipment(
        ship_types = [x['name'] for x in new_miners_list],
        equipment_list = mining_equipment )

    return

