'''
Make edits to the T_Shields file.
This is mainly aimed at adjusting shield recharge rates, since changing
size is completely unintuitive considering shields are named
after their sizes.
'''
from File_Manager import *
import Flags
import math


@Check_Dependencies('TShields.txt')
def Adjust_Shield_Regen(
    scaling_factor = 1
    ):
    '''
    Adjust shield regeneration rate by changing efficiency values.
    
    * scaling_factor:
      - Multiplier to apply to all shield types.
    '''
    for this_dict in Load_File('TShields.txt'):
        if scaling_factor != 1:
            #Grab the shield efficiency, as a float.
            value = float(this_dict['efficiency'])
            new_value = value * scaling_factor
            #Put it back, with 1 decimal place.
            this_dict['efficiency'] = str('{0:.1f}'.format(new_value))

