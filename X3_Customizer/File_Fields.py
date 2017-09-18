'''
Specify the fields for various file types that are field based.
Generally, this covers T files.
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
        0: 'name',
        1: 'value',
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
        0  : 'model_scene',
        2  : 'rotation_x',     #rpm = 60 * this value
        3  : 'rotation_y',
        4  : 'rotation_z',    #Appears to be 0 normally.
        7  : 'speed',        #In meters per 500 seconds
        8  : 'acceleration', #In meters per 500 seconds per second
        9  : 'launch_sound',     #Int, an index
        10 : 'ambient_sound',    #Int, an index
        11 : 'collision_type',   #Int, appears to be 1 or 2.
        12 : 'damage',
        13 : 'blast_radius',  #Likely in meters
        14 : 'lifetime',      #In milliseconds
        15 : 'trail_effect',     #Int, an index
        16 : 'glow_effect',      #Int, an index
        17 : 'explosion_sound',  #Int, an index
        18 : 'sound_volume_min', #Int, appears max is 255 (probably 8-bit)
        19 : 'sound_volume_max', #Int, appears max is 255 (probably 8-bit)
        20 : 'impact_effect',    #Int, an index
        21 : 'explosion_effect', #Int, an index
        23 : 'flags',         #Special 1-hot flags.
        24 : 'fire_delay',    #In milliseconds
        25 : 'icon',          #String, name of the icon to use.
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
        7 : 'speed',        #In meters per 500 seconds
        8 : 'acceleration', #In meters per 500 seconds per second
        #Power for recharging shields.
        #Exact recharge rate also depends on shield types and number.
        13 : 'shield_power',
        #Total weapon energy storable.
        #Called kW, even though that is not a unit of energy...
        20 : 'weapon_energy', 
        #Float, multiplier on weapon_energy to determine recharge rate.
        # eg. 0.01 on transports, 0.025 on fighters.
        21 : 'weapon_recharge_factor', 
        22 : 'shield_type', #Integer, 0-5, where 0 is 1mj and 5 is 2gj
        23 : 'max_shields', #Integer, typically 1-5
        26 : 'speed_tunings',
        27 : 'rudder_tunings', #Note: may actually have 27/28 reversed.
        28 : 'cargo_min',
        29 : 'cargo_max',
        46 : 'hull_strength',
        49 : 'particle_effect', #Integer, corresponds to particles3 file?, engine trail
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
    'TGates.txt' : {
        'min_data_entries': 5,
        7: 'model_scene',
        -2: 'name',
        },
    'TBackgrounds.txt' : {
        'min_data_entries': 5,
        7: 'image', #String, possibly background image
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
    'Jobs.txt' : {
        'min_data_entries': 5,
        0: 'id',                   #Integer
        1: 'name',                 #String, name of the job entry
        2: 'max_jobs',             #Integer
        3: 'max_jobs_in_sector',   #Integer
        4: 'script',               #String
        5: 'script_config',        #String
        6: 'name_id',              #Integer; this appears to relate to the in-game displayed name.
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
        125: 'classification_military',  #0 or 1
        126: 'classification_trader',
        127: 'classification_civilian',
        128: 'classification_fighter',
        },
    'TWareT.txt':{
        'min_data_entries': 5,
        7 : 'volume',
        8 : 'relative_value_npc',
        9 : 'price_modifier_1',
        10: 'price_modifier_2',
        12: 'relative_value_player',
        -2: 'name',
        },
}




