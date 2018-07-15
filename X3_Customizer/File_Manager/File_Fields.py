'''
Specify the fields for various file types that are field based.
Generally, this covers T files.
'''
'''
Note on relative value fields:

    These are split into a basic 'relative value' and an 
    alternate 'relative value player'.

    This represents how many seconds it takes to produce or consume
    one item, for a factory running at 1x speed.
    Eg. if the product value is 10, input is 5, then over 10 seconds
    the factory will consume 2 inputs, produce 1 output.

    Player factories use the player term, npc factories the normal term.
    Commonly the player term is lower for end products, though not 
    for intermediate goods.

    Example: e-cells may have relval of 4 for npc and player, but mosquito
    missiles have relval of 6 for npc, 4 for player.
    As a result, a player produced mosquito consumes 33% fewer e-cells,
    since in 24 seconds an npc factory is [+4 mosquitos, -6 ecells]
    while a player factory is [+6 mosquitos, -6 ecells].

    Secondary resource consumption rates are stated to be 1/3 normal
    rate by egosoft, implying their relval is boosted 3x. Factories do
    not require secondary resources to run, though the factory does
    appear to need to run to use secondary resources (in brief checks).


    Relval is also used to determine consumption at trading posts and
    equipment docks, though the formula used is somewhat complex.

        This post has a code snippet:
        https://forum.egosoft.com/viewtopic.php?t=113932

        int use =((current_timestep / SA_GetTypeRelValue(m, s)) 
                * (percentage / 100) 
                * (BESTSTORE / BESTSTORE_SECONDARY) );

        if (use == 0) {
            int invuse = ((SA_GetTypeRelValue(m, s) / current_timestep) 
                * (100 / percentage) 
                * (BESTSTORE_SECONDARY / BESTSTORE) );
            if (!invuse || !SE_Random(invuse)) {
                use = (current_timestep / 20) + 1;
            }
            else {
                use = 0;
            }
        } 

        The first part appears to calculate the amount of wares consumed
        in a given time period.  current_timestep in seconds from the last
        evaluation, relvalue is seconds/unit, so this gives the base
        unit consumption at 1x rate.  The percentage is 6% or 12% for
        tech or non-tech respectively, a reduction in consumption rate.
        The beststore terms appear to be constants, and evaluate to 1/2.

        When the first term was floored to 0, it gets calculated in an 
        inverse manner.  According to the post, the next if() statement
        will fire with a (1/use) chance.  Logically, the inner statement
        here should just set use=1, but the timestep contribution
        will add some excess (1 unit per 20 seconds, regardless of type).

        This suggests the consumption rate at docks is 6% the normal rate
        for most wares, 3% for tech wares, being most accurate for low
        value wares, reducing consumption somewhat for medium value
        wares (rounded down), increasing consumption for high value
        wares (hits the 1/20s term).

        Personal testing on food items came out around 1/20th rate, which
        is in rough agreement with the above.

        Timestep is stated to be 5-300 seconds, and is presumably longer
        when the player is not watching.  With this, can determine the
        relval that will commonly round to 0 and trigger the alternate
        calculation.
            use = <1 = 300 / relval * [0.06,0.12] * 1/2
                     = [9,18] /relval
        Hence, a relval of >9 for tech goods, >18 for other goods, should
        round to 0.  This would cover just about all tech goods except
        for super cheap missiles (explaining why mosquitos tend to fill
        up at docks).

        At 300 seconds, the consumption rate inflation for these high
        value goods would be (300/20 +1) = 16x.  When a tech good
        is originally at a 3% consumption rate, it will actually be
        at a 48% rate.

        In summary:
            Low value goods are consumed at a ~5% rate.
            High value goods are consumed at a ~50% rate.


    Prices are based on the npc relative value, combined with a hidden
    multiplier that varies by item type. Some of these multipliers are
    calculated and placed in Flags.py.

    The price_modifier_1/2 fields are percentage changes in a ware's
    base price to allow based on factory storage utilization, where
    _1 is for primary resources, _2 for secondary resources.


Note on scene files:
    These can be a string (path from the objects folder) or an integer
    (implicitly path from objects/v folder, presumably).

'''

# T file names, and named fields of interest.
# The original files contain semicolon delimited lines; the index to each field
#  is given a string name here for easier reference.
# This dict will be keyed by a T file name, with an inner dict keyed by
#  field name and the index of the field.
# This will also define the min number of entries per line, to help identify which
#  lines hold data and which are headers. Equivelent to number of ';' +1.
T_file_name_field_dict_dict = {
    'Globals.txt' : {
        # Global lines are short, just 2 values and newline.
        'min_data_entries': 3,
        0  : 'name',
        1  : 'value',
        },
    'TBullets.txt' : {
        'min_data_entries': 5,
        0  : 'model_file',
        7  : 'shield_damage',     
        8  : 'energy_used',        
        9  : 'impact_sound',      
        # TODO: launch delay, maybe used in weapon charging.
        10 : 'lifetime',           #In milliseconds
        11 : 'speed',              #In meters per 500 seconds (divide by 500 for m/s)
        12 : 'flags',              #Special 1-hot flags.  
        16 : 'box_width',          #Float, size of the bullet hitbox, often 0.1-4 or so.
        17 : 'box_height',         #Float, size of the bullet hitbox. Generally same as width.
        18 : 'box_length',         #Float, size of the bullet hitbox. Given with 1 decimal place.
        20 : 'impact_effect',     
        21 : 'launch_effect',    
        22 : 'hull_damage',   
        33 : 'fragment_bullet',   #Integer index in Tbullets for a fragment bullet to create on explode  
        37 : 'shield_damage_oos', 
        38 : 'hull_damage_oos',   
        39 : 'ammo_type',         #Integer, the item type to consume as ammo.
        -2 : 'name',               #Name is 'SS_BULLET_'+suffix
        },
    'TFactories.txt' :{
        'min_data_entries': 5,
        0  : 'model_file',   #Int
        1  : 'picture_id',   #Int
        2  : 'rotation_x',   #0
        3  : 'rotation_y',   #0
        4  : 'rotation_z',   #0
        5  : 'subtype',    #String, eg. 'SG_FAC_SHIP'
        6  : 'name_id',    #Int
        7  : 'flyby_sound', #Int
        8  : 'docking_distance', #Float, may be negative.
        9  : 'rendezvous_distance', #Int, may be negative; 3 and -3 observed.
        10 : 'sound_volume', #Int
        11 : 'scene', #String
        12 : 'internal_scene', #Int
        13 : 'race', #Int
        14 : 'explosion_effect', #Int
        15 : 'body_explosion_definition', #Int
        16 : 'shield_recharge_rate', #Int
        17 : 'factory_size', #Int, production rate, 1/2/5/10.
        18 : 'icon',   #String, eg. 'ICON_TRG_ST_SHIPYARD'
        19 : 'volume',    #Int
        20 : 'relative_value_npc',
        21 : 'price_modifier_1',
        22 : 'price_modifier_2',
        23 : 'cargo_size',
        24 : 'relative_value_player',
        25 : 'minimum_notoriety',
        26 : 'video_id',
        27 : 'skin_index',
        -2 : 'name',               #Name is 'SS_FAC_'+suffix

        },
    'TLaser.txt' : {
        'min_data_entries': 5,
        0  : 'model_file',   #Int
        1  : 'picture_id',   #Int
        2  : 'rotation_x',     #rpm = 60 * this value. May be turret rpm.
        3  : 'rotation_y',
        4  : 'rotation_z',    #Appears to be 0 normally.
        5  : 'subtype',    #String, eg. 'SG_LASER_IRE'
        6  : 'name_id',    #Int
        7  : 'fire_delay', #In milliseconds
        8  : 'sound',      #Int
        9  : 'bullet',     #Integer index in tbullets of the bullet to create
        10 : 'max_energy', #Energy stored in weapon at 100% charge
        11 : 'charge_rate', #Rate the weapon charges up
        12 : 'icon',      #String, eg. 'ICON_LASER_IRE'
        13 : 'volume',    #Int
        14 : 'relative_value_npc',
        15 : 'price_modifier_1',
        16 : 'price_modifier_2',
        17 : 'cargo_size',
        18 : 'relative_value_player',
        19 : 'minimum_notoriety',
        20 : 'video_id',
        21 : 'skin_index',
        -2 : 'name', #Name is 'SS_LASER_'+suffix
        },
    'TMissiles.txt' : {
        'min_data_entries': 5,
        # 37 fields total
        0  : 'model_scene',    #String or int
        2  : 'rotation_x',     #rpm = 60 * this value
        3  : 'rotation_y',
        4  : 'rotation_z',    #Appears to be 0 normally.
        5  : 'subtype',       #Category of missile, eg. 'SG_MISSILE_LIGHT'.
        6  : 'name_id',
        7  : 'speed',        #In meters per 500 seconds, or 1/500 meters per second.
        8  : 'acceleration', #In meters per 500 seconds per second
        9  : 'launch_sound',     #Int, an index
        10 : 'ambient_sound',    #Int, an index
        11 : 'collision_type',   #Int, appears to be 1 or 2.
        12 : 'damage',
        13 : 'blast_radius',  #In 1/500ths of meters.
        14 : 'lifetime',      #In milliseconds
        15 : 'trail_effect',     #Int, an index
        16 : 'glow_effect',      #Int, an index
        17 : 'explosion_sound',  #Int, an index
        18 : 'sound_volume_min', #Int, appears max is 255 (probably 8-bit)
        19 : 'sound_volume_max', #Int, appears max is 255 (probably 8-bit)
        20 : 'impact_effect',    #Int, an index
        21 : 'explosion_effect', #Int, an index
        22 : 'particle_effect',  #Engine trail; Int.
        23 : 'flags',         #Special 1-hot flags.
        24 : 'fire_delay',    #In milliseconds
        25 : 'icon',          #String, name of the icon to use.
        26 : 'scene',         #String, a scene file name.
        27 : 'volume',
        28 : 'relative_value_npc',
        29 : 'price_modifier_1',
        30 : 'price_modifier_2',
        31 : 'cargo_size',
        32 : 'relative_value_player',
        33 : 'minimum_notoriety',
        34 : 'video_id',
        35 : 'skin_index',
        -2 : 'name',
        },
    'TShips.txt' : {
        'min_data_entries': 5,
        0  : 'model_file',  #Int.
        1  : 'picture_id',
        # Dynamic number of fields, seemingly due to turret or other variation.
        # Positive indices will count forward, negatives will count backwards.
        2 : 'yaw',  #rpm = 60 * this value
        3 : 'pitch',
        4 : 'roll',
        # Ship category, eg. 'SG_SH_TS' for transport ship.
        # This is different than the ship class (as used in the obj code).
        # Unknown effects; perhaps this affects the display icon?
        5 : 'subtype',      
        6 : 'name_id',      #Int, the id of the in-game ship name.
        7 : 'speed',        #In meters per 500 seconds
        8 : 'acceleration', #In meters per 500 seconds per second
        9 : 'engine_sound', #Int
        11 : 'engine_effect_color', #Int
        12 : 'engine_effect_glow', #Int
        # Power for recharging shields.
        # Exact recharge rate also depends on shield types and number.
        13 : 'shield_power',
        14 : 'sound_volumne_min',
        15 : 'sound_volumne_max',
        16 : 'ship_scene',    #String or int
        17 : 'cockpit_scene', #String or int
        18 : 'laser_compatibility_flags', #32-bit 1-hot flags for lasers equippable, signed.
        # Total weapon energy storable.
        # Called kW, even though that is not a unit of energy...
        20 : 'weapon_energy', 
        # Float, multiplier on weapon_energy to determine recharge rate.
        #  eg. 0.01 on transports, 0.025 on fighters.
        21 : 'weapon_recharge_factor', 
        22 : 'shield_type', #Integer, 0-5, where 0 is 1mj and 5 is 2gj
        23 : 'max_shields', #Integer, typically 1-5
        24 : 'missile_compatibility_flags', #16-bit 1-hot flats for missiles
        26 : 'speed_tunings',
        27 : 'rudder_tunings', #Note: may actually have 27/28 reversed.
        28 : 'cargo_min',
        29 : 'cargo_max',
        30 : 'ware_list', #Integer, index in warelists.txt for built-in wares.
        43 : 'docking_slots', #Int
        44 : 'cargo_size', #Int, 0-5, the size of cargo that can be held.
        45 : 'race',  #Int, the race this ship type is associated with.
        46 : 'hull_strength',
        47 : 'explosion_effect', #Int
        48 : 'body_explosion_effect', #Int
        49 : 'particle_effect', #Integer, corresponds to particles3 file?, engine trail
        50 : 'variation_index', #Int, the variation type of the ship, eg. 1 for vanguard.
        51 : 'angular_acceleration',
        # Ship alternate category, eg. 'OBJ_SHIP_TL' for transport ship.
        # This appears to match up to class type in the obj code, and is
        #  called 'class' in x3 editor.
        # Eg. a spacefly is 'OBJ_SPACEFLY' here, but 'SG_SH_M5' for its
        #  subtype.
        52 : 'class',
        #  Note: 53-X (96?) appear to be cockpits/turrets/guns.
        -11: 'volume', #Int; often 1, but may be related to marine capacity according to a forum post.
        -10: 'relative_value_npc',
        -9 : 'price_modifier_1',
        -8 : 'price_modifier_2',
        -7 : 'cargo_size_unused', #Int, cargo size for a ship ware; meaningless, always 0.
        -6 : 'relative_value_player',
        -5 : 'minimum_notoriety',
        -4 : 'video_id',
        -3 : 'skin_index',
        # Name is the last field before the newline.
        -2 : 'name',
        },
    'TShields.txt': {
        'min_data_entries': 5,
        0 : 'model_file',  #Int.
        1 : 'picture_id',
        2 : 'rotation_x',  #Always 0.
        3 : 'rotation_y',
        4 : 'rotation_z',
        5 : 'subtype',  #Int, appears to go from 0 for 1MJ to 5 for 2GJ.
        6 : 'name_id',    #Int
        7 : 'power_drain', #Int, the power draw of the shield, in kW. eg. 33 to 2500.
        8 : 'capacity', #Int, the size of the shield in kW, eg. 1000 for 1MJ.
        9 : 'hit_effect', #Int, always 1.
        10: 'efficiency', #Float, recharge efficiency of the shield, eg. 0.85.
        11 : 'volume',
        12 : 'relative_value_npc',
        13 : 'price_modifier_1',
        14 : 'price_modifier_2',
        15 : 'cargo_size',
        16 : 'relative_value_player',
        17 : 'minimum_notoriety',
        18 : 'video_id',
        19 : 'skin_index',
        -2: 'name',
        },
    # Catchall for the TWare files; individual links filled in further below.
    'TWare_.txt':{
        'min_data_entries': 5,
        0  : 'model_file',  #Int.
        1  : 'picture_id',
        2  : 'rotation_x',  #Always 0.
        3  : 'rotation_y',
        4  : 'rotation_z',
        5  : 'subtype',    #Int, varies, but not sure on meaning.
        6  : 'name_id',    #Int
        7  : 'volume',
        8  : 'relative_value_npc',    #Int, production time/ratio, seconds.
        9  : 'price_modifier_1',      #Int, percent primary resource price variation.
        10 : 'price_modifier_2',      #Int, percent secondary resource price variation.
        11 : 'cargo_size',
        12 : 'relative_value_player', #Int, production time/ratio, seconds.
        13 : 'minimum_notoriety',
        14 : 'video_id',
        15 : 'skin_index',
        -2: 'name',
        },
    'TGates.txt' : {
        'min_data_entries': 5,
        7 : 'model_scene', #String, int, or -1
        -2: 'name',
        },
    'TSpecial.txt' : {
        'min_data_entries': 5,
        0 : 'model_scene', #String, int, or -1
        -2: 'name',
        },
    'TBackgrounds.txt' : {
        'min_data_entries': 5,
        7 : 'image', #String, possibly background image
        11: 'fog1', #Integer, maybe goes to a fog code?
        12: 'fog2',
        13: 'fog3',
        14: 'fog4',
        15: 'fog5',
        16: 'fog6',
        17: 'fog7',
        18: 'fog8',
        19: 'fog_density',   #Integer, 0 to 50 observed, may be higher is thicker.
        24: 'fadeout_start', #Integer, in 1/500 meters (divide by 500 for meters), distance fade begins
        25: 'fadeout_end',   #Integer, in 1/500 meters, distance fade ends (past this, invisible)
        26: 'num_particles', #Integer, 0 or 100 seen, may be particles outside ship window
        -2: 'name',
        },
    'WareLists.txt':{
        # Empty entries may just be a count (0) and their slash_index (includes newline).
        # Note that this is small enough to match the header, so expect the
        #  header line to be returned to any calling code.
        'min_data_entries': 2,
        # Int, the number of wares in the list, prior to the index.
        # Adjust this if changing ware count.
        0 : 'ware_count',
        # String, a forward slash followed by the integer index, and then a
        #  newline (combined, since there is no semicolon at the end like with
        #  other files). May include a random comment before the newline, and
        #  is probably just a comment in general.
        #  Indices appear to always be in order, starting from 0.
        -1: 'slash_index_comment',  
        },
    # Note: it appears the jobs file has two formats, one (maybe for ap)
    #  which has 4 more fields inserted somewhere and throwing off later flags.
    # The AP new fields are at: [70,105,123,128], and will shift down
    #  the TC values correspondingly.
    # These offsets will be for the short/TC form (which xrm uses and seems
    #  to work okay), and the fluff entries will be noted and used when
    #  parsing if needed to shift entry names.
    # Set an initial empty dict for the ap fields; build it further below.
    'Jobs.txt.ap' : {
        'min_data_entries': 5,
        },
    'Jobs.txt' : {
        'min_data_entries': 5,
        'lines_tc': 130,
        'lines_ap': 134,
        # Provide the replacement dict to use in the ap case.
        'ap_name' : 'Jobs.txt.ap',
        0 : 'id',                   #Integer
        1 : 'name',                 #String, name of the job entry
        2 : 'max_jobs',             #Integer
        3 : 'max_jobs_in_sector',   #Integer
        4 : 'script',               #String
        5 : 'script_config',        #String
        6 : 'name_id',              #Integer; the in-game displayed name.
        # Int; if not 0, the override name to use.
        #  Unclear on relation to name_id.
        8 : 'override_name',       
        # These fields affect display and announcement name, being
        #  prefixed or suffixed to the name_id text/voice.
        9 : 'show_race',           #0 or 1; for display name in game.
        10: 'show_corperation',    #0 or 1; for display name in game.
        11: 'show_ship_type',      #0 or 1; for display name in game.
        12: 'show_variant',        #0 or 1; for display name in game.
        13: 'job_wing_index',      #Int; entry in JobWings.txt with subjobs to act as wingmen.
        14: 'ware_list_index',     #Int; wares associated with this job (eg to trade)
        15: 'job_jump_range',      #Int. Note: not 100% verified. Missing in x3 editor.
        16: 'idle_rate',           #Int, generally 0-10 or so.
        17: 'respawn_time',        #Integer, appears to be in seconds.
        18: 'ship_type_name',  #String, optional name of ship to spawn. -1 if unused.
        # Ship types to allow, given as standard type name for coding convenience.
        19: 'SG_SH_M1', #0 or 1
        20: 'SG_SH_M2', #0 or 1
        21: 'SG_SH_M3', #0 or 1
        22: 'SG_SH_M4', #0 or 1
        23: 'SG_SH_M5', #0 or 1
        24: 'SG_SH_M6', #0 or 1
        25: 'SG_SH_M7', #0 or 1
        26: 'SG_SH_M8', #0 or 1
        27: 'SG_SH_TP', #0 or 1
        28: 'SG_SH_TS', #0 or 1
        29: 'SG_SH_TL', #0 or 1
        30: 'special_tl_ts_flag', #0 or 1, unknown use.
        31: 'manufacturer_argon',  #0 or 1; probably used in ship selection.
        32: 'manufacturer_boron', 
        33: 'manufacturer_split', 
        34: 'manufacturer_paranid', 
        35: 'manufacturer_teladi', 
        36: 'manufacturer_xenon', 
        37: 'manufacturer_pirates', 
        38: 'manufacturer_khaak', 
        39: 'manufacturer_goner', 
        40: 'manufacturer_atf', 
        41: 'manufacturer_terran', 
        42: 'manufacturer_yaki', 
        43: 'variant_basic',       #0 or 1
        44: 'variant_vanguard',
        45: 'variant_sentinel',
        46: 'variant_raider',
        47: 'variant_hauler',
        48: 'variant_miner',
        49: 'variant_super_freighter',
        50: 'variant_tanker',
        51: 'variant_mk1',
        52: 'variant_9',
        53: 'variant_10',
        54: 'variant_11',
        55: 'variant_12',
        56: 'variant_13',
        57: 'variant_tanker_xl',
        58: 'variant_super_freighter_xl',
        59: 'variant_advanced',
        # Hue/saturation are generally -1, sometimes 0, and may be unused.
        # The spray shop supports 0-360 hue, -256 to 256 saturation.
        # Could consider playing with this at some point, maybe randomizing,
        #  though given ships of a job will always be the same, and variation
        #  would only be across jobs.
        60: 'hue',
        61: 'saturation',
        63: 'select_owners_sector',     #0 or 1
        67: 'select_not_enemy_sector',
        64: 'select_core_sector',
        68: 'select_border_sector',
        65: 'select_shipyard_sector',
        66: 'select_owner_station_sector',
        69: 'limit_to_x_universe_races',
        70: 'invert_sector_flags', #Never seen used; unclear on effect.
        71: 'sector_x', #Int, sector coordinates. -1,-1 used for dont case seemingly.
        72: 'sector_y',
        73: 'create_in_shipyard',
        74: 'create_in_gate',
        75: 'create_inside_sector',
        76: 'create_outside_sector',
        77: 'create_null',         #Never seen used.
        78: 'docked_chance',       #Int, 0-100, percentage.
        80: 'freight_extensions',  #Int, 0 to 100.
        81: 'engine_tunings',      #Int, 0 to 100.
        82: 'rudder_tunings',      #Int, 0 to 100.
        83: 'rotation_acceleration_limit', #Int, 0 or -20 seen (on idle TLs)
        84: 'owner_argon',         #0 or 1
        85: 'owner_boron', 
        86: 'owner_split', 
        87: 'owner_paranid', 
        88: 'owner_teladi', 
        89: 'owner_xenon', 
        90: 'owner_khaak', 
        91: 'owner_goner', 
        92: 'owner_atf', 
        93: 'owner_terran', 
        94: 'owner_yaki', 
        95: 'owner_pirates',  #Oddly, different ordering from manufacturer
        96: 'shield_level',  #Int, 0 to 100.
        97: 'laser_level',   #Int, 0 to 100.
        116: 'aggression',   #Int, 0 to 100.
        117: 'moral',        #Int, 0 to 100.
        118: 'fight_skill',  #Int, 0 to 100. May affect missile loadout.
        120: 'set_invincible',
        121: 'set_as_hidden_pirate',
        122: 'destroy_out_of_sector',
        123: 'rebuild_in_new_sector',
        124: 'fly_average_speed',
        125: 'classification_military',  #0 or 1
        126: 'classification_trader',
        127: 'classification_civilian',
        128: 'classification_fighter',
        # 129 is the last entry, seen to be a 0 with newline generally.
        },
}

# Fill in the TWare file entries.
for tware_name in [
    'TWareB.txt',
    'TWareE.txt',
    'TWareF.txt',
    'TWareM.txt',
    'TWareN.txt',
    'TWareT.txt',
    ]:
    T_file_name_field_dict_dict[tware_name] = T_file_name_field_dict_dict['TWare_.txt']
    
# Build an ap-specific dict for the jobs file, with inserted lines.
for tc_line_number, field in T_file_name_field_dict_dict['Jobs.txt'].items():
    # Skip special entries.
    if isinstance(tc_line_number, str):
        continue
    # Get the line number offset adjustment for ap.
    ap_line_number = tc_line_number + sum(
        # This will sum up all of the AP lines that the tc_line_number
        #  has reached. Eg. on tc reaching 70, an offset of 1 is applied;
        #  on tc reaching 105, an offset of 2 is applied.
        [1 for x in [70,105,123,128] if tc_line_number >= x])
    T_file_name_field_dict_dict['Jobs.txt.ap'][ap_line_number] = field
    

    
# Table capturing all known global names and their defaults.
# Names taken from the x3:ap executable version 3.3.
# Defaults taken from vanilla AP globals.txt, or from misc
# online searches, or from guesses.
# Default is None when completely unknown.
# Note: distance units are generally in 1/500 meters.
# Where interesting comments are in the globals.txt, they are quoted here.
Global_Defaults = {

    # Unclear. 85 m/s.  Could this be a strafe replacement or similar?
    'SG_AVRSPEED'                           : 42500,
    
    # Values related to ship steering.
    'SG_CURSORSTEERING_DAMPING'             : 30,
    # "max cursor firing angle, must be < 90"
    'SG_CURSORSTEERING_MAXFIREANGLE'        : 30,

    # Unknown. Could increasing this affect draw ranges, or when
    # a detailed model swaps in for the low-poly distant models?
    'SG_DETAILVISIBLE_MINDIST'              : 0,

    # Appearance related factors, presumably.
    'SG_HUEMODIFIER_MAX_ARGON'              : 30,
    'SG_HUEMODIFIER_MAX_BORON'              : 0,
    'SG_HUEMODIFIER_MAX_GONER'              : 0,
    'SG_HUEMODIFIER_MAX_KHAAK'              : 0,
    'SG_HUEMODIFIER_MAX_PARANID'            : 20,
    'SG_HUEMODIFIER_MAX_PIRATE'             : 0,
    'SG_HUEMODIFIER_MAX_RACE1'              : 359,
    'SG_HUEMODIFIER_MAX_RACE2'              : 359,
    'SG_HUEMODIFIER_MAX_SPLIT'              : 0,
    'SG_HUEMODIFIER_MAX_TELADI'             : 20,
    'SG_HUEMODIFIER_MAX_TERRAN'             : 0,
    'SG_HUEMODIFIER_MAX_XENON'              : 20,
    'SG_HUEMODIFIER_MAX_YAKI'               : 0,
    'SG_HUEMODIFIER_MIN_ARGON'              : 340,
    'SG_HUEMODIFIER_MIN_BORON'              : 0,
    'SG_HUEMODIFIER_MIN_GONER'              : 0,
    'SG_HUEMODIFIER_MIN_KHAAK'              : 0,
    'SG_HUEMODIFIER_MIN_PARANID'            : 340,
    'SG_HUEMODIFIER_MIN_PIRATE'             : 0,
    'SG_HUEMODIFIER_MIN_RACE1'              : 0,
    'SG_HUEMODIFIER_MIN_RACE2'              : 0,
    'SG_HUEMODIFIER_MIN_SPLIT'              : 0,
    'SG_HUEMODIFIER_MIN_TELADI'             : 340,
    'SG_HUEMODIFIER_MIN_TERRAN'             : 0,
    'SG_HUEMODIFIER_MIN_XENON'              : 340,
    'SG_HUEMODIFIER_MIN_YAKI'               : 0,
    'SG_HUE_ZEROPOS_ARGON'                  : -26,
    'SG_HUE_ZEROPOS_BORON'                  : 0,
    'SG_HUE_ZEROPOS_GONER'                  : 0,
    'SG_HUE_ZEROPOS_KHAAK'                  : 0,
    'SG_HUE_ZEROPOS_PARANID'                : 0,
    'SG_HUE_ZEROPOS_PIRATE'                 : 0,
    'SG_HUE_ZEROPOS_RACE1'                  : 0,
    'SG_HUE_ZEROPOS_RACE2'                  : 0,
    'SG_HUE_ZEROPOS_SPLIT'                  : 0,
    'SG_HUE_ZEROPOS_TELADI'                 : 130,
    'SG_HUE_ZEROPOS_TERRAN'                 : 0,
    'SG_HUE_ZEROPOS_XENON'                  : 0,
    'SG_HUE_ZEROPOS_YAKI'                   : 0,
    'SG_SATMODIFIER_DEFAULT_ARGON'          : 65536,
    'SG_SATMODIFIER_DEFAULT_BORON'          : 65536,
    'SG_SATMODIFIER_DEFAULT_GONER'          : 65536,
    'SG_SATMODIFIER_DEFAULT_KHAAK'          : 65536,
    'SG_SATMODIFIER_DEFAULT_PARANID'        : 65536,
    'SG_SATMODIFIER_DEFAULT_PIRATE'         : 65536,
    'SG_SATMODIFIER_DEFAULT_RACE1'          : 65536,
    'SG_SATMODIFIER_DEFAULT_RACE2'          : 65536,
    'SG_SATMODIFIER_DEFAULT_SPLIT'          : 65536,
    'SG_SATMODIFIER_DEFAULT_TELADI'         : 65536,
    'SG_SATMODIFIER_DEFAULT_TERRAN'         : 65536,
    'SG_SATMODIFIER_DEFAULT_XENON'          : 65536,
    'SG_SATMODIFIER_DEFAULT_YAKI'           : 65536,
    'SG_SATMODIFIER_SPECIAL_ARGON'          : 65536,
    'SG_SATMODIFIER_SPECIAL_BORON'          : 65536,
    'SG_SATMODIFIER_SPECIAL_GONER'          : 65536,
    'SG_SATMODIFIER_SPECIAL_KHAAK'          : 65536,
    'SG_SATMODIFIER_SPECIAL_PARANID'        : 65536,
    'SG_SATMODIFIER_SPECIAL_PIRATE'         : 65536,
    'SG_SATMODIFIER_SPECIAL_RACE1'          : 65536,
    'SG_SATMODIFIER_SPECIAL_RACE2'          : 65536,
    'SG_SATMODIFIER_SPECIAL_SPLIT'          : 65536,
    'SG_SATMODIFIER_SPECIAL_TELADI'         : 65536,
    'SG_SATMODIFIER_SPECIAL_TERRAN'         : 65536,
    'SG_SATMODIFIER_SPECIAL_XENON'          : 65536,
    'SG_SATMODIFIER_SPECIAL_YAKI'           : 65536,

    # May be related to how much a ship drifts on turns.
    'SG_MAXGLIDESPEED'                      : 100,

    # Various hull values.
    # May need to look these up in game for defaults.
    'SG_MAXHULL_ASTEROID'                   : None,
    'SG_MAXHULL_BOARDINGPOD'                : None,
    'SG_MAXHULL_CELESTIAL'                  : None,
    'SG_MAXHULL_CONTAINER'                  : None,
    'SG_MAXHULL_DEBRIS'                     : None,
    'SG_MAXHULL_DOCK'                       : None,
    'SG_MAXHULL_FAC_BIO'                    : None,
    'SG_MAXHULL_FAC_COMPLEX'                : None,
    'SG_MAXHULL_FAC_DEFAULT'                : None,
    'SG_MAXHULL_FAC_FOOD'                   : None,
    'SG_MAXHULL_FAC_MINE'                   : None,
    'SG_MAXHULL_FAC_POWER'                  : None,
    'SG_MAXHULL_FAC_SHIP'                   : None,
    'SG_MAXHULL_FAC_STORAGE'                : None,
    'SG_MAXHULL_FAC_TECH'                   : None,
    'SG_MAXHULL_SPECIAL'                    : None,
    'SG_MAXHULL_WARPGATE'                   : None,
    'SG_MAXHULL_WRECK'                      : None,

    # Missile hull values from here:
    # https://forum.egosoft.com/viewtopic.php?t=316886&start=68
    'SG_MAXHULL_MISSILE'                    : 5,
    'SG_MAXHULL_MISSILE_AF'                 : 5,
    'SG_MAXHULL_MISSILE_BOMBER'             : 2700,
    'SG_MAXHULL_MISSILE_DMBF'               : 5,
    'SG_MAXHULL_MISSILE_HEAVY'              : 2000,
    'SG_MAXHULL_MISSILE_KHAAK'              : 200,
    'SG_MAXHULL_MISSILE_LIGHT'              : 50,
    'SG_MAXHULL_MISSILE_MEDIUM'             : 90,
    # This one could not be found anywhere on google.
    # At a guess, may be the same as base missile, at 5.
    'SG_MAXHULL_MISSILE_SWARMPCT'           : 5, # Guess
    'SG_MAXHULL_TORPEDO'                    : 4000,
    # Swarm missile related fields.
    'SG_MISSILE_SWARM_COUNT'                : 8,
    # "time for a full rotation in ms, 0 stops rotation"
    'SG_MISSILE_SWARM_ROT_TIME'             : 15000,
    # "random position variance, 65536/missilecount is a good base"
    'SG_MISSILE_SWARM_WIGGLE_FACTOR'        : 8192,
    

    # Strafe factors may be unused. TODO: test.
    # About 52 and 98 m/s respectively.
    'SG_MAXSTRAFEFACTOR_BIGSHIP'            : 26214,
    'SG_MAXSTRAFEFACTOR_SMALLSHIP'          : 49152,

    # These units are in meters.
    'SG_MAX_DISTANCE_BEAMING'               : 5000,
    'SG_MAX_DISTANCE_BUILDCOMPLEX'          : 20000,
    'SG_MAX_DISTANCE_COMM'                  : 25000,
    # This distance is to nearest vertex of the dock target.
    'SG_MAX_VERTEXDIST_DOCKCOMPUTER'        : 4000,

    # Field of view limits.
    'SG_MIN_FOV'                            : 70,
    'SG_MAX_FOV'                            : 100,

    # Related to generic missions.
    'SG_MISSION_QUOTA_BUILD'                : 4,
    'SG_MISSION_QUOTA_FIGHT'                : 4,
    'SG_MISSION_QUOTA_THINK'                : 4,
    'SG_MISSION_QUOTA_TRADE'                : 4,

    # Unknown. Tuning values for something.
    # At a guess: mobile mining yield per pickup and energy to
    # break down rocks.
    'SG_MM_BULLET_ENERGY'                   : 10000,
    'SG_MM_DESTRUCTION_RANGE'               : 100000,
    'SG_MM_EMPTY_DIVISOR'                   : 1,
    'SG_MM_EMPTY_MULTIPLIER'                : 1,
    'SG_MM_EMPTY_PERCENTAGE'                : 30,
    'SG_MM_FIXED_MINIMUM'                   : 1,
    # "0:fixed, 1-4:formulae"
    'SG_MM_METHOD'                          : 1,
    'SG_MM_RANDOM_MINIMUM'                  : 2,
    'SG_MM_RANDOM_RANGE'                    : 0,
    'SG_MM_RELVALUE_BASE'                   : 100,
    # "0:none, 1:random, 2:fixed"
    'SG_MM_RELVALUE_TYPE'                   : 1,
    'SG_MM_YIELD_DIVISOR'                   : 30,
    'SG_MM_YIELD_MULTIPLIER'                : 1,
    # "0:none, 1:random, 2:fixed"
    'SG_MM_YIELD_TYPE'                      : 1,
    # "0:none, 1:normal"
    'SG_MM_YIELD_ZERO'                      : 0,
    
    # Storage space multipliers for docks/hub.
    'SG_DOCK_STORAGE_FACTOR'                : 3,
    'SG_HUB_STORAGE_FACTOR'                 : 6,
    'SG_NPC_DOCK_STORAGE_FACTOR'            : 1,
    'SG_NPC_HUB_STORAGE_FACTOR'             : 6,
    # Unknown. Maybe these increase storage based on wares
    # being large or high price, to get around the low limit
    # on high end goods like PPCs and such.
    'SG_DOCK_STORAGE_PRICE_FACTOR'          : None,
    'SG_DOCK_STORAGE_VOL_FACTOR'            : None,
    # Hub gate realignment settings.
    'SG_GATE_REALIGNMENT_ENERGY'            : 10000,
    # Time to complete a relink.
    'SG_GATE_REALIGNMENT_LINK'              : 300,
    # Cooldown between relinks.
    'SG_GATE_REALIGNMENT_WAIT'              : 7200,

    # Unknown. Suggests alternate OOS combat mechanics, maybe
    # a 0 gives TC/Reunion style mechanics instead of the
    # updated AP ones.
    'SG_OOS_FIGHT_MODE'                     : 1,
    
    # Ranges of various scanners.
    'SG_SCANNER_RANGE_FREIGHTSCANNER'       : 2000000,
    'SG_SCANNER_RANGE_ORBITALLASER'         : 1250000,
    'SG_SCANNER_RANGE_SATELLITE'            : 11000000,
    'SG_SCANNER_RANGE_SATELLITE2'           : 17500000,
    'SG_SCANNER_RANGE_SHIP'                 : 5000000,
    'SG_SCANNER_RANGE_SHIP_UPGRADE2'        : 10000000,
    'SG_SCANNER_RANGE_SHIP_UPGRADE3'        : 15000000,
    # Nebula were in x2; this could be leftover from then.
    'SG_SCANNER_RANGE_SO_NEBULA'            : 750000,
    'SG_SCANNER_RANGE_STATION'              : 5000000,

    # Unknown.
    'SG_STRICT_EQUIP_LIMIT'                 : None,
    
    # Possibly the number of blue brackets put around various
    # object types.
    'SG_TRACKER_NUM_ASTEROIDS'              : 3,
    'SG_TRACKER_NUM_BEACON'                 : 2,
    'SG_TRACKER_NUM_CIVILIAN'               : 2,
    'SG_TRACKER_NUM_CONTAINER'              : 2,
    'SG_TRACKER_NUM_ENEMYSHIP'              : 8,
    'SG_TRACKER_NUM_GATES'                  : 16,
    'SG_TRACKER_NUM_HUGEENEMYSHIP'          : 8,
    'SG_TRACKER_NUM_HUGEPLSHIP'             : 10,
    'SG_TRACKER_NUM_HUGESHIP'               : 10,
    'SG_TRACKER_NUM_INMISSILE'              : 2,
    'SG_TRACKER_NUM_MINES'                  : 4,
    'SG_TRACKER_NUM_OTHER'                  : 3,
    'SG_TRACKER_NUM_PLSHIP'                 : 16,
    'SG_TRACKER_NUM_SHIP'                   : 10,
    'SG_TRACKER_NUM_STATION'                : 8,

    # Tractor beam values.
    # In meters.
    'SG_TRACTOR_BREAK_DIST'                 : 1332,
    'SG_TRACTOR_SPEED_LIMIT'                : 80,
    # "fixed point spring constant"
    'SG_TRACTOR_SPRING_CONST'               : 4369,
    'SG_TRACTOR_SPRING_DIST'                : 777,
    
    # AP war values.
    'SG_WAR_SCORE_HULL_DIVISOR'             : 2000,
    'SG_WAR_SCORE_MD_MULTIPLIER'            : 1,
    'SG_WAR_SCORE_PLAYER_MULTIPLIER'        : 20,
    'SG_WAR_SCORE_RELVAL_DIVISOR'           : 1000,
    }