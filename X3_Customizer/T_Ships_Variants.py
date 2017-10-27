'''
Split off file from T_Ships, holding the variant ship generation code.

TODO: make more robust across mods that play with the variants, since
this is mostly tuned for xrm. Perhaps use a pre-config block that
can swap out variant names and indices, as well as variants to ignore
and other such flags, tuned to a particular mod setup.
At the very least, remove the xl tank/freighter from the defaults,
since those are xrm variants only.
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
    25: explorer, in xrm, special addition. Vanilla AP stops at 20.
        There is a gap in text strings from 21-24, so supporting above
        20 would be messy here (eg. an ingame script to read suffixes
        would need to be conditionalized on not finding a suffix).

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
    8 : tug, mk 1 in xrm.
    9 : luxury cruiser, xrm overwrites this suffix in the 0001 text file 
                          to have no suffix.
    10 : slave transport, empty in xrm.
    11 : military transporter, maybe empty in xrm.
    12 : XL, maybe empty in xrm.
    13 : extended, empty in xrm.
    14 : tanker xl
    15 : super freighter xl
    16 : vanguard, used by Hyperion and kite (an actual variant of base kite).
    17 : sentinel, unused?
    18 : raider, unused?
    19 : hauler (used for griffon, panther, colossus; editor recognizes this 
         as adding the hauler suffix, though it never has stat variation from
         a base type (griffon/panther have no base, colossus has same stats)).
         This may need some special handling in the case of the griffon, but
         the panther/colossus are generally not part of the game.
         If a hauler is auto-added for tag 4, it will have the same name as
         with tag 19.
    20?: advanced

These seem to correspond with the 0001 language file, where ids 10001 to
10019 match to variants, and have suffixes. The above are filled in from
there for defaults.

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
        **kwargs
        ):
    '''
    Adds combat variants for combat ships. This is a convenience function
    which calls Add_Ship_Variants with variants [vanguard, sentinel, raider,
    hauler], for ship types [M0-M8]. See Add_Ship_Variants documentation
    for other parameters.
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
        **kwargs
        )
    
@Check_Dependencies('TShips.txt', 'WareLists.txt', 'TWareT.txt')
def Add_Ship_Trade_Variants(
        **kwargs
        ):
    '''
    Adds trade variants for trade ships. This is a convenience function
    which calls Add_Ship_Variants with variants [hauler, miner, tanker (xl),
    super freighter (xl)], for ship types [TS,TP,TM,TL]. See Add_Ship_Variants 
    documentation for other parameters.    
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
            'super freighter',
            'tanker xl',
            'super freighter xl',
            ],
        **kwargs
        )

    
#Set up a dict matching variant names to their indices in tships.
#This is used to parse transform input args; most logic should use
# indices to stay generic.
variant_name_index_dict = {
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
    #TODO: maybe include other variants from the base files, but
    # they are not common enough to really generate ships for.
    }
#For convenience, build the reverse lookup dict. -Removed.
variant_index_type_dict = {x:y for y,x in variant_name_index_dict.items()}


#Keep a global dict with the varient modifiers.
#This is only calculated on the first call, to avoid generated variants
# from being seen in the analysis in later calls.
variant_id_field_ratios_dict_dict = None


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
        price_multiplier = 1,
        blacklist = None,
        #Set the variants to ignore.
        #These will not be used in analysis, will not be used as base ships,
        # and will generally be skipped.
        variant_indices_to_ignore = [
            #Avoid mk 1 ships, so as not to make variants of them, as that
            # gets confusing. Eg. 'colossus mk 1' becomes 'colossus raider'
            # because the variant flag gets overwritten.
            #This is mostly for xrm.
            8,
            ],
        include_advanced_ships = True,
        add_mining_equipment = True,
        print_variant_modifiers = False,
        print_variant_count = False,
        prepatch_ship_variant_inconsistencies = True,
        _cleanup = False
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

    After variants are created, a script may be manually run in game from the
    script editor which will add variants to all shipyards that sell the base
    ship. Run 'a.x3customizer.add.variants.to.shipyards.xml', no input args.
    Note: this will add all stock variants as well, as it currently has no
    way to distinguish the new ships from existing ones.

    * ship_types:
      - List of ship names or types to add variants for,
        eg. ['SS_SH_OTAS_M2', 'SG_SH_M1'].
    * variant_types:
      - List of variant types to add. Variant names are given as strings or
        as integers (1-19). The default list, with supported names and
        corresponding integers in parentheses, is:
           ['vanguard' (1),
            'sentinel' (2),
            'raider' (3),
            'hauler' (4),
            'miner' (5),
            'super freighter' (6),
            'tanker' (7) ,
            'tanker xl' (14),
            'super freighter xl' (15)
            ]
    * price_multiplier:
      - Float, extra scaling to apply to pricing for the new variants,
        on top of standard variant modifiers.
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
    * variant_indices_to_ignore:
      - List of integers, any existing variants to be ignored for analysis
        and variant generation. Default list includes 8, XRM Mk.1 ships.
    * add_mining_equipment:
      - Bool, if True mining equipment will be added to Miner variants. 
        Default True.
    * prepatch_ship_variant_inconsistencies:
      - Bool, if True then Patch_Ship_Variant_Inconsistencies will be run
        prior to this transform, to avoid some spurious variant generation.
        Default True with XRM fixes enabled; this should be safe to apply
        to vanilla AP.
    * print_variant_count:
      - Bool, if True then the number of new variants added will be printed.
    * print_variant_modifiers:
      - Bool, if True then the calculated attributes used for variants will 
        be printed, given as multipliers on base attributes for various ship
        attributes. Default False.
    '''
    if prepatch_ship_variant_inconsistencies:
        #Include the xrm fixes as well, by default.
        Patch_Ship_Variant_Inconsistencies(include_xrm_fixes = True)

    #To add the variants to shipyards in game, a script has been set
    # up for running from the game script editor.
    #Copy the script to the scripts directory, to make it available.
    #Do this here to share the path with cleanup, which runs early.
    import shutil
    dest_path = os.path.join('scripts','a.x3customizer.add.variants.to.shipyards.xml')
    #The file is present here in scripts, so can reuse the dest_path.
    this_dir = os.path.normpath(os.path.dirname(__file__))
    source_path = os.path.join(this_dir, dest_path)
    shutil.copy(source_path, dest_path)
    
    #If in cleanup mode, check for the file and delete it if found.
    if _cleanup:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return


    #Make an empty blacklist list if needed.
    if blacklist == None:
        blacklist = []


    #Translate the input variant names to indices.
    for index, input_arg in enumerate(variant_types):
        error = False

        #Check for a string.
        if isinstance(input_arg, str):
            #Error if this is not a name in the table.
            if input_arg not in variant_name_index_dict:
                error = True
            else:
                #Replace with the table value.
                variant_types[index] = variant_name_index_dict[input_arg]

        else:
            #Verify this is in the 1-19 range.
            if not isinstance(input_arg , int) or input_arg < 1 or input_arg > 19:
                error = True

        #Common error catch.
        if error:
            print('Add_Ship_Variants Error, variant type {} not understood.'.format(
                input_arg))
            return

    #Rename to clarify these as indices.
    variant_indices_to_generate = variant_types


    #Suffixes to use for generated ship naming.
    #This is just laid out manually, to make it clear and tweak the
    # xl entries to distinguish them, while keeping suffixes short
    # and expressive.
    #Names are generally uppercase, so maintain that here.
    #Limitations on ship names are unknown; there seems to be room
    # for a moderate number of letters.  Try to limit to ~6 here.
    #Stick an underscore, since that is common in existing names.
    #These should cover all possible variants 1-19, in case mods
    # add new ones in that range.
    variant_index_suffix_dict = {
        #Set up some nice names for basic variants.
        variant_name_index_dict['basic']              : '_BASIC',
        variant_name_index_dict['vanguard']           : '_VAN',
        variant_name_index_dict['sentinel']           : '_SENT',
        variant_name_index_dict['raider']             : '_RAID',
        variant_name_index_dict['hauler']             : '_HAUL',
        variant_name_index_dict['miner']              : '_MINE',
        variant_name_index_dict['super freighter']    : '_SFR',
        variant_name_index_dict['tanker']             : '_TANK',
        variant_name_index_dict['tanker xl']          : '_TANKXL',
        variant_name_index_dict['super freighter xl'] : '_SFRXL',
    }
    #Fill out with generics for the rest.
    for i in range(20):
        if i not in variant_index_suffix_dict:
            variant_index_suffix_dict[i] = '_VAR{}'.format(i)

    #Set up a list of mining equipment to add to mining variants.
    #Goal is to correct the cost adjustment to subtract off mining gear,
    # then add it back later.
    #TODO: look this up dynamically, in case mods swap miners around,
    # or other custom equipment needs to be captured.
    # For now, miners are a special case.
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
    #redundant_variant_indices = [
    #    16, #Vanguard
    #    19, #Hauler
    #    ]
    #Update: this is not consistent across mods. Switch to just allowing
    # any ship not in the user variant list to be selected as a new
    # base (with preference for variant 20).


    #Set the ship types that will be used for analysis of each
    # variant type.
    #The main goal here is to omit some outliers, such as the sentinel
    # varients in xrm for transports and corvettes which involves heavy
    # modifications to turrets/etc. which aren't easily captured.
    #Note: this isn't super safe across heavy modding, but it is 
    # probably good for the general case to improve results, 
    # eg. have more reasonable sentinels.
    #TODO: maybe swap to checking which ship type is most common
    # for each variant, and using that instead (or maybe the
    # 2 most common). This might backfire for eg. xrm sentinels,
    # though, if they are more numerous than any individual
    # fighter type, so fighters would need to be lumped together.
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
        variant_name_index_dict['vanguard']           : analysis_combat_ship_types,
        variant_name_index_dict['sentinel']           : analysis_combat_ship_types,
        variant_name_index_dict['raider']             : analysis_combat_ship_types,
        #Hauler will compare against combat and/or trade ships.
        #In practice, trade ships in xrm have too big a buff from
        # the hauler suffix (mostly in massive shield boosts), which
        # doesn't map well to combat ships (where shields get super
        # important).
        #Scale using only combat ships for this, which feels much
        # better (balanced and thematic, with haulers getting more
        # cargo and a small shield buff for penalties most elsewhere).
        variant_name_index_dict['hauler']             : analysis_combat_ship_types,
        variant_name_index_dict['miner']              : analysis_trade_ship_types,
        variant_name_index_dict['super freighter']    : analysis_trade_ship_types,
        variant_name_index_dict['tanker']             : analysis_trade_ship_types,
        variant_name_index_dict['tanker xl']          : analysis_trade_ship_types,
        variant_name_index_dict['super freighter xl'] : analysis_trade_ship_types,
        }


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
    # Eg. all standard Mercury variants use the same name_id, despite
    # having different internal names, so this will gather all Mercuries 
    # together.
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
        #This will only prune out the 20 variant.
        #-Removed, unnecessary, skipping is handled later.
        #if not include_advanced_ships and variation_index == 20:
        #and variation_index not in variant_index_type_dict):
        #    continue

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
    global variant_id_field_ratios_dict_dict
    if variant_id_field_ratios_dict_dict == None:

        #Note that some variant ship lists may be very sparse, maybe
        # only one entry for special cases. This code should work in
        # those cases regardless.
    
        #Goal is to build a list of ratios for each variant type and each
        # variant field. Eg. ['raider']['speed'] = [1.1, 1.15], from
        # which averages can be calculated later.
        #Populate this with initial entries for all variants.
        variant_id_field_ratios_list_dict_dict = defaultdict(lambda: defaultdict(list))

        #Loop over the ship names and their variants.
        for ship_name, variant_id_ship_dict_dict in name_variant_id_ship_dict_dict_dict.items():

            #If there is no base variant to compare against, skip.
            #This occurs for heavy ships or similar.
            if 0 not in variant_id_ship_dict_dict:
                continue
            basic_dict = variant_id_ship_dict_dict[0]
            

            #Loop over all variants, not just those being added.
            #Since this is only run once, it needs to gather everything
            # needed for any future transform calls.
            #Cover everything from 1-19.
            for variant_index in range(1,20):

                #Skip if this ship type is not being used in analysis of this
                # variant type.
                #When a type list is not available, all types are allowed.
                if variant_index in variant_analysis_ship_type_list_dict:
                    if basic_dict['subtype'] not in variant_analysis_ship_type_list_dict[variant_index]:
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
                    variant_id_field_ratios_list_dict_dict[variant_index][field].append(ratio)

                #TODO:
                #Gather ship ware lists, and look for differences.
                #Eg. miner variants should have extra mining equipment.


        #From the lists, can now calculate average ratios.
        variant_id_field_ratios_dict_dict = {}
        #Loop over the variants.
        for variant_index, field_ratios_list_dict in variant_id_field_ratios_list_dict_dict.items():
            #Set up a dict for this variant.
            variant_id_field_ratios_dict_dict[variant_index] = {}

            #Prune any outliers.
            #XRM, for instance, has sentinel versions of transports that
            # have very large ratios on weapon energy (>200x or so).
            #Anything that varies by more than 10x, either direction, will
            # get pruned. Some super freighters and such can vary by
            # 6x or so on shields or cost.
            outlier_max = 10
            outlier_min = 1/outlier_max

            #To determine the ships to ignore, get the indices, so that
            # all field lists can skip the right entries.
            indices_to_skip = set()
            #Loop over the fields and ratios to check them.
            for field, ratio_list in field_ratios_list_dict.items():

                #Special case: allow price outliers.
                if field == 'price':
                    continue

                for ratio_index, ratio in enumerate(ratio_list):
                    #Skip if this is an outlier.
                    if ratio > outlier_max or ratio < outlier_min:
                        indices_to_skip.add(ratio_index)


            #Loop over the fields and ratio lists again.
            for field, ratio_list in field_ratios_list_dict.items():
                #Get all entries that are not being skipped.
                ratios_to_average = [x 
                                     for i,x in enumerate(ratio_list) 
                                     if i not in indices_to_skip]
                ratio = sum(ratios_to_average) / len(ratios_to_average)
                variant_id_field_ratios_dict_dict[variant_index][field] = ratio



        #Apply a special fix for cargo min/max, unifying the ratios so
        # that adjustments can be made safely to all ships (eg. those with
        # min and max set the same).
        #These changes could be averaged, but that may lead to oddities,
        # eg. if min changes a lot and max does not, this will result in
        # an excessive boost to max.
        #For now, just apply the max ratio to the min.
        for field_ratios_dict in variant_id_field_ratios_dict_dict.values():
            #cargo_ratio = field_ratios_dict['cargo_min'] + field_ratios_dict['cargo_max']/2
            field_ratios_dict['cargo_min'] = field_ratios_dict['cargo_max']
                

    #Print these out if desired.
    if print_variant_modifiers:
        print('Variant modifiers:')
        for variant_id, field_ratios_dict in sorted(variant_id_field_ratios_dict_dict.items()):
            print('  Variant {} ({})'.format(
                variant_id,
                #Give the variant name as well, if known.
                variant_index_type_dict[variant_id] 
                if variant_id in variant_index_type_dict 
                else ''
                ))
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

        #If not allowing advanced ships to act as a base, skip variants
        # for this ship.
        elif not include_advanced_ships:
            continue

        #Favor the 20 case as an alternative.
        elif 20 in variant_id_ship_dict_dict:
            #Do not need to reclassify this as variant 0; it shouldn't
            # have a suffix (the 0001 test file doesn't go high enough
            # for a 20 suffix).
            basic_dict = variant_id_ship_dict_dict[20]

        #Two options here: find any existing variant, or try to find
        # a variant not being added in this call.
        #The latter might work, and was tried before, but the former is
        # probably more straightforward.
        else:
            #Pick the highest variant index in general.
            basic_dict = None
            for test_index in range(19,0,-1):
                if test_index in variant_id_ship_dict_dict:
                    basic_dict = variant_id_ship_dict_dict[test_index]
                    break

            #If here, it is possible a mod added ships with higher
            # variants, eg. explorers in xrm being variant 25.
            #Just skip these cases.
            if basic_dict == None:
                continue
                
            #Reclassify this as variant 0, the base.
            #This will also stip off redundant suffixes from some ships.
            #Eg. if basing off Hyperion Vanguard, change it to Hyperion
            # before making variants.
            basic_dict['variation_index'] = str(0)
            #Update the variant_id_ship_dict_dict to reflect this change,
            # in case it matters ever.
            del(variant_id_ship_dict_dict[test_index])
            variant_id_ship_dict_dict[0] = basic_dict


        #-Removed; this method tried to find a ship not having a variant
        # generated to use as the base.
        ##Looking up non-standard variants is kinda tricky to do programmatically.
        ##Can convert the variant type keys into sets, and look for difference.
        #elif set(variant_id_ship_dict_dict) - set(variant_index_type_dict):
        #
        #    #Find the first non-standard variant.
        #    #To ensure this is the same on every run (in case there are
        #    # several to pick from), sort by variant index.
        #    basic_dict = None
        #    for variant_index, basic_dict in sorted(variant_id_ship_dict_dict.items()):
        #        if variant_index not in variant_index_type_dict:
        #            break
        #    #Error check.
        #    assert basic_dict != None
        #    #This shouldn't occur unless advanced ships were included.
        #    assert include_advanced_ships
        #
        #    #If this has a redundant variant index, can assign it to 0 to
        #    # avoid a generated variant having overlap with the redundant
        #    # name, or possibly to 20 to clarify it as special.
        #    # Go with 0 for now.
        #    #Eg. if basing off Hyperion Vanguard, change it to Hyperion
        #    # before making variants.
        #    if int(basic_dict['variation_index']) in redundant_variant_indices:
        #        basic_dict['variation_index'] = str(0)
        #        del(variant_id_ship_dict_dict[variant_index])
        #        variant_id_ship_dict_dict[0] = basic_dict
        #
        #else:
        #    #Nothing was found for the base type.
        #    #Here, a base will need to be generated be downscaling an existing
        #    # variant.
        #    #TODO. Just print a quick warning for now and skip ahead.
        #    # This did not come up during testing, but may occur for some
        #    # mod combo out there.
        #    print('Warning, no basic version found for {}, skipping'.format
        #          (name_id))
        #    continue


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
        #The other problem is that in some cases the variant is excessively
        # powerful and probably best ignored if possible, eg. with the kite
        # vanguard.
        #For now, just allow redundancies.
        

        #Skip if this is not a ship type to modify.
        if (basic_dict['subtype'] not in ship_types
        and basic_dict['name'] not in ship_types):
            continue


        #With the base type selected, can now start filling in the variants.
        #Loop over the variants being added.
        for variant_index in variant_indices_to_generate:

            #Can skip this if the variant already exists.
            if variant_index in variant_id_ship_dict_dict:
                continue

            #Need to skip if there is no scaling information for the
            # requested variant.
            if variant_index not in variant_id_field_ratios_dict_dict:
                continue

            #Make a copy of the basic_dict.
            #Shallow copy should be fine for this, but deep copy to be
            # safe in case of future code changes that might add annotation
            # fields or similar.
            new_ship_dict = copy.deepcopy(basic_dict)

            #Need to edit the name.
            #Add the predefined suffix for the variant type.
            new_name = new_ship_dict['name'] + variant_index_suffix_dict[variant_index]
            #Toss an error if the name is taken; it shouldn't be, but be safe.
            if new_name in ship_names_list:
                raise Exception('Variant name {} already taken.'.format(new_name))
            new_ship_dict['name'] = new_name

            #Record the variant index for this ship, for recognition in game
            # and also in future transform calls.
            new_ship_dict['variation_index'] = str(variant_index)

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
                ratio = variant_id_field_ratios_dict_dict[variant_index]['shielding']

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
            for field, ratio in variant_id_field_ratios_dict_dict[variant_index].items():

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

                    #Support an additional scaling on price.
                    elif field in ['production_value_npc','production_value_player']:
                        value *= ratio * price_multiplier

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
            #TODO: maybe generalize this to record variants per type, and
            # then in a later step add in generic wares.
            if variant_index == variant_name_index_dict['miner']:
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
    if add_mining_equipment:
        Add_Ship_Equipment(
            ship_types = [x['name'] for x in new_miners_list],
            equipment_list = mining_equipment )


    return

'''
Phase 2 is to generate a script which will add the new variants to the
shipyards for an ongoing game.

Through a callable script:
    A script would be manually called by the player when needing to
    update shipyards. This may be bothersome if something like the xrm
    roaming shipyards need the script rerun each time they move.

    Page ~62 on the msci scripting code reference has station commands.
    The main commands of interest are:
        <RetVar/IF><RefObj> uses ware <Var/Ware> as product
        <RefObj> add product to factory or dock: <Var/Ware>
        <RetVar> = get station array: of race <Var/Race> class/type =<Value>
        <RetVar> = get station array: product =<Var/Ware> include empty =<Var/Boolean>

    The thread has a simple example of using a couple of the above, once the
    ship and station are selected:
        https://forum.egosoft.com/viewtopic.php?p=3671990

    The general approach could be to:
    -For every base ship + variants (many expand out)
        -Get array of stations producing a given base ship.
        -Add every generated variant as factory products.

    The base ship loop might be hundreds of ships, leading to a large
    generated line count.

    X scripts are stored in a compiled form, where raw text, semi-encoded
    text, and compiled nodes are all dropped into sections of the xml.
    Auto-generating raw text is easy, but the encoded and compiled versions
    get to be much more of a mess.

    One possible option is to code up the shell manually, with the outer
    loops and a manually done test ship + variants added.
    The code lines for the ship+variants could then be analyzed, pattern
    found, and then repeated across all ships actually being handled.

    This is a bit clumsy, but workable.


    Alternatively, base ships and variants can be put in a file somehow,
    read in in-game, and parsed by a generic script looping over them.
    This avoids the hassle of special encoding/compilation, since the
    base script is written once.

    The file could be one of the xml language t files, holding the
    ship information needed, with counts for how many ships or similar.
    This would require requesting a reserved t file number, but that
    shouldn't be a big deal (check the mod forum for free numbers).
    Such files need to be made for every language supported, which is
    rather meh.

    There appears to be no other method for general file loading.


    Another alternative is to write a generic script that can pull all
    ship variants from the game files.
    The goal would be to find all shipyards, loop over all ships offered,
    get the name_id, then loop over all ships in existence filtering for
    those with the matched name_id, and adding those to the shipyard.
    It would be a lot of loops, but might be fine for a 1-shot script.


Through the mission director:
    Could be set to autocall itself once, though once the cue has fired
    it will need to reset it somehow.  A timed reset and rerun would be
    clumsy.
    Perhaps have two cues and alternate them, each one clearing the other,
    swapping between cues on runs of the customizer, but this will mean
    redundant calls on the next game load when variants have not changed.

    File formatting is easy, though, with the director approach, and the
    user could potentially manually call the director script by mucking
    around in-game with cues (note: this option hasn't been explored).

    Command to find shipyards:
    <find_station group="CUE_name.Shipyards" class="shipyard"/>
    ?

    There appears to be no way to add wares to an existing station.
    Creation of a new station is possible, but this would be a
    horrible solution, unless custom stations are added just for
    selling the new variant ships.

    While use custom stations is an interesting thought, it is generally
    clumsy, doesn't mesh well with mods that might organize ship sell
    locations (eg. xrm with trade ships at different docks), requires
    excessive stations to make variants as accessible as normal ships,
    etc.


Testing:
    Attempts to use the command:
     <RetVar> = get station array: product =<Var/Ware> include empty =<Var/Boolean>

        Some oddities involved.  Primary problem: no good way to specify
        the produce ware.
        The game heavily relies on using a ship name for the
        ingame editor (IE), or the ship race+name+name_id in exscriptor (EX).
        IE doesn't even offer ships as inputs, only EX does.

        Test with an Atlas, and printing the result to the player logbook,
        prints null.
        Trying with 1GJ shield, it prints out an ARRAY() of stations, so it
        seems this command doesn't work with ships, at least not the way
        exscriptor specifies ships.
        In the compiled code, 1GJ shield is just 589828, which doesn't have
        any apparent meaning (the shield id is SS_SHIELD_E, name_id is 7853).
        For comparison, a Buster is 458769.

        In general, this is confusing.


    The ship browser mod has some reference code that might be useful.

        It uses a generic ship type lookup command:
            $ship.array = get ship type array: maker race=null class=$$wanted.class

            Though that script has null for race, in game testing of this command
            required race to be filled in, and class (object type M2 or similar)
            alone wasn't sufficient.
            Class isn't needed for the command, though.
            Potentially, all ship types can be obtained by running this command
            on each individual race.
            This appears to return actual live ships, though, not classes.

        Ship class may be obtained with:
            $ship.array = get ship type array: maker race=null class=$wanted.class
            If doing this, the printed array is of recognizable ship class names,
            albeit with suffixes added for variants.

        Stations are looked up by race as well.
            $station.list = get station array: of race $ship.race class/type={Shipyard 2037}
            There is a slight caveat that terran stations can sell atf ships,
            but that might not matter if brute forcing checks on all races.

        Arrays are joined like so:
            $station.list = [THIS]->call script '!lib.array.join' : a.arr1=$station.list  a.arr2=$station.list.2

        Using these, can get a full array of all ship types, and a full array
        of all shipyards.

        A station's product list is gotten with:
            $station.product.list = $station->get tradeable ware array from station
        Can search for a given ship at the station with:
            if find $ship.ware in array: $station.product.list
            

    For variant filling, can use these commands:
        
        <RetVar> get ship variation: subtype =<Var/Number> 
            On ship type: 
                works correctly (mercury tanker returns 7)
            On ship:
                returns 0

        <RetVar> = <RefObj> get ship variation 
            On ship type: 
                returns 0
            On ship:
                works correctly (mercury tanker returns 7)

        https://forum.egosoft.com/viewtopic.php?t=396298 has an example
        of using the command. Maybe look into it.

        Even with variant detection, if there is no way to match variants
        of a given ship with each other, this doesn't help.
        Eg. how to match Titans or similar.
        

    One possibility would be to create a ship, run some of these commands
    on it, then destroy the ship, but this is not expected to be too useful,
    at most giving a string name of the ship that should be obtainable by
    other methods and isn't language safe anyway.


    Other commands tried:

        <RetVar> = <RefObj> get ID code
            On ship type, tested on Mammoth: 
                ID code is CLASS458752, presumably an awkward prefix and the
                actual class code of interest.
            On ship:
                ID code is the in-game generated id.

        <RetVar> = <RefObj> get name
            On ship type, tested on Mammoth: 
                Name is an invalid readtext gibberish line, and not useful.
            On ship:
                Name is the full in-game name, eg. Jonferco Security Buster Mk. 1.
                For created ships, this is the default name, eg. Mercury Tanker.
                
        <RetVar/IF><RefObj> get object class
            On ship type:
                Returns null
            On ship:
                Returns general class, eg. TS, which is not too useful.


        <RetVar/IF><RefObj> get ware type code of object
            On ship type:
                Returns unknown object
            On ship:
                Returns eg. Mercury Tanker, presumably the ship type.
                Not too useful, since a ship was generated from a type.

        <RetVar> get ship class from subtype: <Var/Number>
            On ship type:
                Returns general class, eg. TS, which is not too useful.
            On ship:
                Note tried.


    From these tests, the only useful bits are:
        -Obtain a ship type variant code.
        -Obtain a ship type name with variant suffix.
    Want to know the base name without the variant, if possible.

    If the variant suffix can be read from a language file, it can potentially
    be removed from the name using:
        <RetVar> = substitute in string <Var/String>: pattern <Var/String> with <Var/String>
    This mod may have an example of pulling the variant names:
        https://forum.egosoft.com/viewtopic.php?t=307684
    The above didn't help, though a simple check of 0001-l044.xml found it:
    
    <page id="300017" title="Boardcomp. objects" descr="" voice="yes">
        <t id="10001">Vanguard</t>
        <t id="10002">Sentinel</t>
        <t id="10003">Raider</t>
        <t id="10004">Hauler</t>
        <t id="10005">Miner</t>
        <t id="10006">Super Freighter</t>
        <t id="10007">Tanker</t>
        <t id="10012">XL</t>

    General approach to get a ship base name:
        Look up the variant type.
        Get the variant suffix from the text file, adding spaces and XL.
        Convert the ship type to a string name (has suffix).
        Replace the suffix with an empty string.
    The above is tested and works.

    One pass over a list of ship types can generate an annotation array
    with the base names.
    By pulling ship types from a shipyard, and getting their base names,
    can then compare that name to all those in the above array, pulling
    out the index to know the corresponding ship types, and then add
    those types to the shipyard.

    Further work done in the script file, found in /scripts.
    In general, it is working well, though had some oddities.
        
'''