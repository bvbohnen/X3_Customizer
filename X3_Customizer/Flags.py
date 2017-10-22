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


import collections
def Unpack_Flags(flag_bit_to_name_dict, packed_flags_value):
    '''
    Unpacks a 1-hot packed_flags_value into an ordereddict.
    Keys are flag names where known, else bit indices where the flag was found.
    flag_bit_to_name_dict is the dict keying flag name to bit index, where 
     index 0 is the lowest bit (value 1).
    Length of the returned dict is set by either the highest defined flag bit, or
     highest flag bit found in packed_flags.
    '''
    flags_dict = collections.OrderedDict()
    #Convert input to an int if a string was given.
    if isinstance(packed_flags_value, str):
        packed_flags_value = int(packed_flags_value)

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

#Convenience call functions for the different t files.
def Unpack_Tbullets_flags(packed_flags_value):
    return Unpack_Flags(TBullets_flag_bits, packed_flags_value)
def Unpack_Tmissiles_flags(packed_flags_value):
    return Unpack_Flags(TMissiles_flag_bits, packed_flags_value)
    
import itertools
def Pack_Flags(flags_dict):
    '''
    Packs an ordereddict of flags into a 1-hot value.
    The first dict entry will be the lowest flag bit, proceeding upwards.
    Returns as a string.
    '''
    running_value = 0
    #Loop over the entries, start to end. Keys don't matter for this.
    for entry, index in zip(flags_dict.values(), itertools.count()):
        #The value to set the bit for this flag will be based on the index.
        #First flag at index = 0 corresponds to bit 1, requiring a value of 1.
        #Second flag at index = 1 is bit 2, requiring a value of 2.
        #Third flag needs a value of 4.
        if entry:
            #Can just do a shift for the right value to add.
            running_value += (1 << index)
    return str(running_value)
