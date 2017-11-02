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
        for super cheap missiles.

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

#T file names, and named fields of interest.
#The original files contain semicolon delimited lines; the index to each field
# is given a string name here for easier reference.
#This dict will be keyed by a T file name, with an inner dict keyed by
# field name and the index of the field.
#This will also define the min number of entries per line, to help identify which
# lines hold data and which are headers. Equivelent to number of ';' +1.
T_file_name_field_dict_dict = {
    'Globals.txt' : {
        #Global lines are short, just 2 values and newline.
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
    'TLaser.txt' : {
        'min_data_entries': 5,
        2 : 'rotation_x',     #rpm = 60 * this value. May be turret rpm.
        3 : 'rotation_y',
        4 : 'rotation_z',    #Appears to be 0 normally.
        7 : 'fire_delay', #In milliseconds
        9 : 'bullet',     #Integer index in tbullets of the bullet to create
        10 : 'max_energy', #Energy stored in weapon at 100% charge
        11 : 'charge_rate', #Rate the weapon charges up
        14 : 'production_value_npc',
        18 : 'production_value_player',
        -2 : 'name', #Name is 'SS_LASER_'+suffix
        },
    'TMissiles.txt' : {
        'min_data_entries': 5,
        #37 fields total
        0  : 'model_scene',    #String or int
        2  : 'rotation_x',     #rpm = 60 * this value
        3  : 'rotation_y',
        4  : 'rotation_z',    #Appears to be 0 normally.
        5  : 'subtype',       #Specific if eg. 'SG_MISSILE_LIGHT'.
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
        28 : 'relative_value',   #Int, production time/ratio, seconds.
        29 : 'price_modifier_1', #Int, percent primary resource price variation.
        30 : 'price_modifier_2', #Int, percent secondary resource price variation.
        -2 : 'name',
        },
    'TShips.txt' : {
        'min_data_entries': 5,
        #Dynamic number of fields, seemingly due to turret or other variation.
        #Positive indices will count forward, negatives will count backwards.
        2 : 'yaw',  #rpm = 60 * this value
        3 : 'pitch',
        4 : 'roll',
        5 : 'subtype',      #Specific if eg. 'SG_SH_TS' for transport ship
        6 : 'name_id',      #Int, the id of the in-game ship name.
        7 : 'speed',        #In meters per 500 seconds
        8 : 'acceleration', #In meters per 500 seconds per second
        #Power for recharging shields.
        #Exact recharge rate also depends on shield types and number.
        13 : 'shield_power',
        18 : 'laser_compatibility_flags', #32-bit 1-hot flags for lasers equippable, signed.
        #Total weapon energy storable.
        #Called kW, even though that is not a unit of energy...
        20 : 'weapon_energy', 
        #Float, multiplier on weapon_energy to determine recharge rate.
        # eg. 0.01 on transports, 0.025 on fighters.
        21 : 'weapon_recharge_factor', 
        22 : 'shield_type', #Integer, 0-5, where 0 is 1mj and 5 is 2gj
        23 : 'max_shields', #Integer, typically 1-5
        24 : 'missile_compatibility_flags', #16-bit 1-hot flats for missiles
        26 : 'speed_tunings',
        27 : 'rudder_tunings', #Note: may actually have 27/28 reversed.
        28 : 'cargo_min',
        29 : 'cargo_max',
        30 : 'ware_list', #Integer, index in warelists.txt for built-in wares.
        44 : 'cargo_size', #Int, 0-5, the size of cargo that can be held, 0 for S, 5 for ST.
        45 : 'race',  #Int, the race this ship type is associated with.
        46 : 'hull_strength',
        49 : 'particle_effect', #Integer, corresponds to particles3 file?, engine trail
        50 : 'variation_index', #Int, the variation type of the ship, eg. 1 for vanguard.
        51 : 'angular_acceleration',
        #Production values are a little unclear.
        #Often these are set to the same number.
        #Ship price appears to be roughly 81 * production_value_npc in sampling,
        # but may depend on other fields to determine this.
        -10: 'production_value_npc',
        -6 : 'production_value_player',
        #Name is the last field before the newline.
        -2 : 'name',
        },
    'TShields.txt': {
        'min_data_entries': 5,
        0 : 'model_file',  #Int.
        5 : 'subtype',  #Int, appears to go from 0 for 1MJ to 5 for 2GJ.
        7 : 'power_drain', #Int, the power draw of the shield, in kW. eg. 33 to 2500.
        8 : 'capacity', #Int, the size of the shield in kW, eg. 1000 for 1MJ.
        10: 'efficiency', #Float, recharge efficiency of the shield, eg. 0.85.
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
    'TWareT.txt':{
        'min_data_entries': 5,
        7 : 'volume',
        8 : 'relative_value_npc',    #Int, production time/ratio, seconds..
        9 : 'price_modifier_1',      #Int, percent primary resource price variation.
        10: 'price_modifier_2',      #Int, percent secondary resource price variation.
        12: 'relative_value_player', #Int, production time/ratio, seconds..
        -2: 'name',
        },
    'WareLists.txt':{
        #Empty entries may just be a count (0) and their slash_index (includes newline).
        #Note that this is small enough to match the header, so expect the
        # header line to be returned to any calling code.
        'min_data_entries': 2,
        #Int, the number of wares in the list, prior to the index.
        #Adjust this if changing ware count.
        0 : 'ware_count',
        #String, a forward slash followed by the integer index, and then a
        # newline (combined, since there is no semicolon at the end like with
        # other files). May include a random comment before the newline, and
        # is probably just a comment in general.
        # Indices appear to always be in order, starting from 0.
        -1: 'slash_index_comment',  
        },
    #Note: it appears the jobs file has two formats, one (maybe for ap)
    # which has 4 more fields inserted somewhere and throwing off later flags.
    #The AP new fields are at: [70,105,123,128], and will shift down
    # the TC values correspondingly.
    #These offsets will be for the short/TC form (which xrm uses and seems
    # to work okay), and the fluff entries will be noted and used when
    # parsing if needed to shift entry names.
    #Set an initial empty dict for the ap fields; build it further below.
    'Jobs.txt.ap' : {
        'min_data_entries': 5,
        },
    'Jobs.txt' : {
        'min_data_entries': 5,
        'lines_tc': 130,
        'lines_ap': 134,
        #Provide the replacement dict to use in the ap case.
        'ap_name' : 'Jobs.txt.ap',
        0 : 'id',                   #Integer
        1 : 'name',                 #String, name of the job entry
        2 : 'max_jobs',             #Integer
        3 : 'max_jobs_in_sector',   #Integer
        4 : 'script',               #String
        5 : 'script_config',        #String
        6 : 'name_id',              #Integer; the in-game displayed name.
        17: 'respawn_time',        #Integer, appears to be in seconds.
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
        43: 'variant_vanguard',
        43: 'variant_sentinel',
        43: 'variant_raider',
        43: 'variant_hauler',
        43: 'variant_miner',
        43: 'variant_super_freighter',
        43: 'variant_tanker',
        43: 'variant_mk1',
        43: 'variant_9',
        43: 'variant_10',
        43: 'variant_11',
        43: 'variant_12',
        43: 'variant_13',
        43: 'variant_tanker_xl',
        43: 'variant_super_freighter_xl',
        43: 'variant_advanced',
        #Hue/saturation are generally -1, sometimes 0, and may be unused.
        #The spray shop supports 0-360 hue, -256 to 256 saturation.
        #Could consider playing with this at some point, maybe randomizing,
        # though given ships of a job will always be the same, and variation
        # would only be across jobs.
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
        #129 is the last entry, seen to be a 0 with newline generally.
        },
}

#Build an ap-specific dict for the jobs file, with inserted lines.
for tc_line_number, field in T_file_name_field_dict_dict['Jobs.txt'].items():
    #Skip special entries.
    if isinstance(tc_line_number, str):
        continue
    #Get the line number offset adjustment for ap.
    ap_line_number = tc_line_number + sum(
        #This will sum up all of the AP lines that the tc_line_number
        # has reached. Eg. on tc reaching 70, an offset of 1 is applied;
        # on tc reaching 105, an offset of 2 is applied.
        [1 for x in [70,105,123,128] if tc_line_number >= x])
    T_file_name_field_dict_dict['Jobs.txt.ap'][ap_line_number] = field
    


