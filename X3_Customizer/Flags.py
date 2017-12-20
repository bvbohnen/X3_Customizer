'''
Methods to handle packed flag fields.
This will also hold some misc values, for lack of a better place
to put them.
'''

#How many game updates occur per minute, used to define fire delays in real time.
Game_Ticks_Per_Minute = 1000*60

#Name of the file holding coefficients for the curve fit on laser speed.
#(This is unused; the complex curve fit did not work well. TODO: comment out.)
Laser_Speed_Coefs_File_Name = 'X3_laser_speed_coefs.pickle'

#The size of each shield type, where type is an integer, size is the MJ value.
Shield_type_size_dict = {
    0: 1,
    1: 5,
    2: 25,
    3: 200,
    4: 1000,
    5: 2000,
    }

#The races associated with the race tags in tships and maybe elsewhere.
Race_code_name_dict = {
    #Give some default for 0, an unspecified race.
    0  : 'None',
    1  : 'Argon',
    2  : 'Boron',
    3  : 'Split',
    4  : 'Paranid',
    5  : 'Teladi',
    6  : 'Xenon',
    7  : 'Khaak',
    8  : 'Pirates',
    9  : 'Goner',
    10 : 'Player',
    11 : 'Enemy Race',
    12 : 'Neutral Race',
    13 : 'Friendly Race',
    14 : 'Unknown',
    15 : 'Race 1',
    16 : 'Independent',
    17 : 'ATF',
    18 : 'Terran',
    19 : 'Yaki',
    }
#Convenience reverse direction lookup dict.
Race_name_code_dict = {x:y for y,x in Race_code_name_dict.items()}


#Price adjustments, from relative value to credits.
#This might vary by item type; organize by tfile.
#Note: this is the mechanism by which factoreis can be made profitable,
# since eg. if a factory consumes 3 inputs and produces 1 output,
# the inputs need to average a value:credits ratio 1/3 that of the output,
# since the factory consumes and produces value for all wares at an
# equal rate.
#The general trend here is each tier being ~30% more than the prior tier(s)
# it is constructed from (ecells to bio, ecells+bio to food/minerals, etc.).
# Some special handling is done for lasers/shields, however.
Value_to_credits_ratio_dict = {
    'TWareE'    : 4,      #Ecells.
    'TWareB'    : 5.33,   #Bio.
    'TWareM'    : 5.33,   #Minerals.
    'TWareF'    : 12,     #Food
    'TWareT'    : 28,     #Various tech (microchips, warheads, etc.)
    'TMissiles' : 28,
    'TLaser'    : 64.9,
    'TShields'  : 64.9,
    'TShips'    : 66, #An old comment elsewhere said 81 here; needs retest maybe.
    'TWareN'    : 4,      #Misc items (artefacts, etc.), all base value.
    }
#Side notes for profit expectation:
# Player shields produce at 80/130 efficiency 
#  (eg. as if 39.9 credits/value, or 39.9/(12+5.33+4) = +87% profit).
# Player lasers produce at 72/96 efficiency
#  (eg. as if 48.6 credits/value, or +127% profit).
# Player missiles produce at 2x efficiency
#  (eg. as if 48 credits/value, or +125% profit).



#Known flags in the 1-hot flag values for some t files.
#Key is the bit position, value is the field name.
TBullets_flag_bits = {
    #Value 2 = beam, hence bit 1
    1: 'beam',
    #Value 4 = zigzag (ion disruptor jump between targets)
    2: 'zigzag',
    #8 is areal (eg. plasma burst generator)
    3: 'areal',
    #Presumed; only set on IonD.
    4: 'disable_shields',
    #Value 32 = ignore shields (mass driver)
    5: 'ignore_shields',
    #Value 64 = ammo usage, hence bit 6
    6: 'use_ammo',
    #Repair beams
    7: 'repair',
    #256 for flak
    8: 'flak',
    #Presumed 9-11
    9: 'reduce_speed',
    10: 'drain_weapons',
    11: 'damage_over_time',
    #Value 4096 = fragmentation, hence bit 12
    12: 'fragmentation',
    #Value 8192 = charged
    13: 'charged',
    }
TMissiles_flag_bits = {
    #4 is fragmentation/swarm
    2: 'fragmentation',
    #16 is multiwarhead (unused by vanilla missiles)
    4: 'multiwarhead',
    #32 is proximity
    5: 'proximity',
    }
#Lasers are categorized into hardcoded named groups.
#In tlasers the names are used; in tships a flag mask is used
# with a fixed mapping.
#TODO: fill this out if ever needed, eg. adding repair lasers and
# such compatibilities. Names filled in for now.
#Note: the encoded flags are 32-bit signed, so the Kyon weapons
# created a negative number. This is true in vanilla tships as well
# as those out of x3_editor.
#Note: 27, 30 unused.  Only 30 of 32 categories.
Tships_laser_subtype_flag_bits = {
     0  : 'SG_LASER_IRE'          ,
     1  : 'SG_LASER_PAC'          ,
     2  : 'SG_LASER_MASS'         ,
     3  : 'SG_LASER_ARGON_LIGHT'  ,
     4  : 'SG_LASER_TELADI_LIGHT' ,
     5  : 'SG_LASER_PARANID_LIGHT',
     6  : 'SG_LASER_HEPT'         ,
     7  : 'SG_LASER_BORON_LIGHT'  ,
     8  : 'SG_LASER_PBE'          ,
     9  : 'SG_LASER_PIRATE_LIGHT' ,
    10  : 'SG_LASER_TERRAN_LIGHT' ,
    11  : 'SG_LASER_CIG'          ,
    12  : 'SG_LASER_BORON_MEDIUM' ,
    13  : 'SG_LASER_SPLIT_MEDIUM' ,
    14  : 'SG_LASER_TERRAN_MEDIUM',
    15  : 'SG_LASER_TELADI_AF'    ,
	16  : 'SG_LASER_ARGON_AF'     ,
    17  : 'SG_LASER_SPLIT_AF'     ,
    18  : 'SG_LASER_PARANID_AF'   ,
    19  : 'SG_LASER_TERRAN_AF'    ,
    20  : 'SG_LASER_PPC'          ,
    21  : 'SG_LASER_BORON_HEAVY'  ,
    22  : 'SG_LASER_TELADI_HEAVY' ,
    23  : 'SG_LASER_PIRATE_HEAVY' ,
    24  : 'SG_LASER_TERRAN_HEAVY' ,
    25  : 'SG_LASER_ARGON_BEAM'   ,
    26  : 'SG_LASER_PARANID_BEAM' ,
    #27 unused.
    28  : 'SG_LASER_SPECIAL'      ,
    29  : 'SG_LASER_UNKNOWN1'     ,
    #30 unused.
    31  : 'SG_LASER_KYON'         ,
    }
#Missiles work the same way with category names in tmissiles.
Tships_missile_subtype_flag_bits = {
     0 : 'SG_MISSILE_LIGHT'          ,
     1 : 'SG_MISSILE_MEDIUM'         ,
     2 : 'SG_MISSILE_HEAVY'          ,
     3 : 'SG_MISSILE_TR_LIGHT'       ,
     4 : 'SG_MISSILE_TR_MEDIUM'      ,
     5 : 'SG_MISSILE_TR_HEAVY'       ,
     6 : 'SG_MISSILE_KHAAK'          ,
     7 : 'SG_MISSILE_BOMBER'         ,
     8 : 'SG_MISSILE_TORP_CAPITAL'   ,
     9 : 'SG_MISSILE_AF_CAPITAL'     ,
    10 : 'SG_MISSILE_TR_BOMBER'      ,
    11 : 'SG_MISSILE_TR_TORP_CAPITAL',
    12 : 'SG_MISSILE_TR_AF_CAPITAL'  ,
    13 : 'SG_MISSILE_BOARDINGPOD'    ,
    14 : 'SG_MISSILE_DMBF'           ,
    #Note: this flag does not appear to be used (and hence the
    # total value may be signed). Instead, it is treated as
    # true if any other flag is true, giving mosquitos to any
    # ship which can fire missiles.
    15 : 'SG_MISSILE_COUNTER'        ,
    }


#Convenience call functions for the different t files.
#These will take a line dict and grab the correct field.
def Unpack_Tbullets_Flags(bullet_dict):
    return Unpack_Flags(TBullets_flag_bits, 
                        bullet_dict['flags'])

def Unpack_Tmissiles_Flags(missile_dict):
    return Unpack_Flags(TMissiles_flag_bits, 
                        missile_dict['flags'])

#Tships laser field is 32-bit signed.
def Unpack_Tships_Laser_Flags(ship_dict):
    return Unpack_Flags(Tships_laser_subtype_flag_bits, 
                        ship_dict['laser_compatibility_flags'], 
                        negative_bit = 31)

def Unpack_Tships_Missile_Flags(ship_dict):
    return Unpack_Flags(Tships_missile_subtype_flag_bits, 
                        ship_dict['missile_compatibility_flags'])
    
#Similar functions for calling Pack_Flags with the right options.
#Most of these use unsigned numbers, so are handled the same way.
#These will take the line dict and pack the correct field.
def Pack_Tbullets_Flags(bullet_dict, flags_dict):
    packed_flags = Pack_Flags(flags_dict)
    bullet_dict['flags'] = packed_flags

def Pack_Tmissiles_Flags(missile_dict, flags_dict):
    packed_flags = Pack_Flags(flags_dict)
    missile_dict['flags'] = packed_flags

#Tships laser field is 32-bit signed.
def Pack_Tships_Laser_Flags(ship_dict, flags_dict):
    packed_flags = Pack_Flags(flags_dict, negative_bit = 31)
    ship_dict['laser_compatibility_flags'] = packed_flags

def Pack_Tships_Missile_Flags(ship_dict, flags_dict):
    packed_flags = Pack_Flags(flags_dict)
    ship_dict['missile_compatibility_flags'] = packed_flags


import collections
def Unpack_Flags(flag_bit_to_name_dict, 
                 packed_flags_value, 
                 negative_bit = None):
    '''
    Unpacks a 1-hot packed_flags_value into an ordereddict.
    Keys are flag names where known, else bit indices where the flag was found.
    flag_bit_to_name_dict is the dict keying flag name to bit index, where 
     index 0 is the lowest bit (value 1).
    If negative_bit != None, this is the sign bit of a signed number at
    the input, and will be used to determine the unsigned conversion.
    Length of the returned dict is set by either the highest defined flag bit, or
     highest flag bit found in packed_flags.
    '''
    flags_dict = collections.OrderedDict()
    #Convert input to an int if a string was given.
    if isinstance(packed_flags_value, str):
        packed_flags_value = int(packed_flags_value)
    #If there is a negative bit, make an adjustment.
    if negative_bit != None:
        #The value of the sign bit can be obtained with a shift.
        #Eg. if the sign bit is 3 (4-bit signed number), this is -8.
        sign_value = (1 << negative_bit) * -1
        #If the input value is negative, can subtract the sign value
        # twice to flip the value positive.
        #The first sign_value negates the existing one, the second puts
        # the bit back in as positive.
        if packed_flags_value < 0:
            packed_flags_value += sign_value *2

    #Start from bit 0 and go upward.
    bit_index = 0
    while 1:

        #Approach will be to use AND mask operations to determine if any given bit
        # is set in packed_flags_value.
        this_flag_value = 1 << bit_index

        #Is this bit set?
        if packed_flags_value & this_flag_value:
            this_flag = True
            #Remove this flag from packed_flags_value, to help with knowing when done.
            packed_flags_value -= this_flag_value
        else:
            this_flag = False

        #Is this flag named?
        if bit_index in flag_bit_to_name_dict:
            #Record with the name as key.
            flags_dict[flag_bit_to_name_dict[bit_index]] = this_flag
        else:
            #Record with the index as key.
            flags_dict[bit_index] = this_flag

        #Done when packed_flags_value == 0 and bit_index is the highest entry in
        # the flag name dict (to ensure all named flags get an entry in the output).
        if packed_flags_value == 0 and bit_index >= max(flag_bit_to_name_dict.keys()):
            break
        
        #Prepare for the next bit.
        bit_index += 1
        
    return flags_dict


def Pack_Flags(flags_dict, negative_bit = None):
    '''
    Packs an ordereddict of flags into a 1-hot value.
    The first dict entry will be the lowest flag bit, proceeding upwards.
    If negative_bit given, it is the bit position to be treated as
    negative. Set this to the top bit for signed numbers, ignore for
    unsigned numbers.
    Returns as a string.
    '''
    running_value = 0
    #Loop over the entries, start to end. Keys don't matter for this.
    for index, entry in enumerate(flags_dict.values()):
        #The value to set the bit for this flag will be based on the index.
        #First flag at index = 0 corresponds to bit 1, requiring a value of 1.
        #Second flag at index = 1 is bit 2, requiring a value of 2.
        #Third flag needs a value of 4.
        if entry:
            #Can just do a shift for the right value.
            value = (1 << index)
            #Normally this will add in, but might subtract for the sign bit.
            if index != negative_bit:
                running_value += value
            else:
                running_value -= value
    return str(running_value)
