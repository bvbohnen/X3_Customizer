from ... import File_Manager
from ... import Common
Settings = Common.Settings
from .Obj_Shared import *


@File_Manager.Transform_Wrapper('L/x3story.obj')
def Hide_Lasertowers_Outside_Radar():
    '''
    Prevents lasertowers and mines from showing up on sector maps
    when outside the radar ranges of player ships.
    '''
    '''
    Added by request.

    Code to edit is in MENU_SECTOR.FindMapObjects.

    Lasertowers, Mines, and Satellites (and beacons) are sublcasses
    of class 2135.  The code for determining if an object is visible
    will normally do a radar range check on player owned assets, but for
    class 2135 will only check the result of a GetUnknown call.

    To preserve this behavior for jump beacons while hiding laser towers,
    the class code can be swapped to 2079, the class code for satellites
    and beacons.
    '''
    patch = Obj_Patch(
            #offsets = [0x00132C15],
            # Code starts off with the 2135 class code check.
            ref_code =  '06' '0857'
                        '0D' '0002'
                        '03'
                        '82' '........'
                        '64'
                        '0D' '0002'
                        '03'
                        '88' '........'
                        '33' '........'
                        '01'
                        '32' '........',
            # Replace start with 2011 check.
            new_code = '06' '081F',
            )
    Apply_Obj_Patch(patch)

    return



##############################################################################
# Following code originally written by rovermicrover.

@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False, TC = False)
def Set_LaserTower_Equipment(
        lasertower_laser_type = 25,
        lasertower_laser_count = 1,
        lasertower_shield_type = 4,
        lasertower_shield_count = 1,
        orbital_laser_laser_type = 25,
        orbital_laser_laser_count = 2, 
        orbital_laser_shield_type = 4,
        orbital_laser_shield_count = 1,
    ):
    '''
    Sets laser and shield type and count that are auto equipped for
    lasertowers and Terran orbital lasers. May need corresponding
    changes in Tships to enable equipment compatibility (not included here).
    
    * lasertower_laser_type
      - Int, argon lasertower laser type.
    * lasertower_laser_count
      - Int, argon lasertower laser count.
    * lasertower_shield_type
      - Int, argon lasertower shield type.
    * lasertower_shield_count
      - Int, argon lasertower shield count.
    * orbital_laser_laser_type
      - Int, terran orbital laser laser type.
    * orbital_laser_laser_count
      - Int, terran orbital laser laser count.
    * orbital_laser_shield_type
      - Int, terran orbital laser shield type.
    * orbital_laser_shield_count
      - Int, terran orbital laser shield count.
    '''
    # Make input args ints, limit to 1 to max_count.
    max_count = 127
    lasertower_laser_type      = max(1, min(int(lasertower_laser_type), max_count))
    lasertower_laser_count     = max(1, min(int(lasertower_laser_count), max_count))
    lasertower_shield_type     = max(1, min(int(lasertower_shield_type), max_count))
    lasertower_shield_count    = max(1, min(int(lasertower_shield_count), max_count))
    orbital_laser_laser_type   = max(1, min(int(orbital_laser_laser_type), max_count))
    orbital_laser_laser_count  = max(1, min(int(orbital_laser_laser_count), max_count))
    orbital_laser_shield_type  = max(1, min(int(orbital_laser_shield_type), max_count))
    orbital_laser_shield_count = max(1, min(int(orbital_laser_shield_count), max_count))

    # Convert to hex strings, 1 byte each.
    lasertower_laser_type      = Int_To_Hex_String(lasertower_laser_type, 1)
    lasertower_laser_count     = Int_To_Hex_String(lasertower_laser_count, 1)
    lasertower_shield_type     = Int_To_Hex_String(lasertower_shield_type, 1)
    lasertower_shield_count    = Int_To_Hex_String(lasertower_shield_count, 1)
    orbital_laser_laser_type   = Int_To_Hex_String(orbital_laser_laser_type, 1)
    orbital_laser_laser_count  = Int_To_Hex_String(orbital_laser_laser_count, 1)
    orbital_laser_shield_type  = Int_To_Hex_String(orbital_laser_shield_type, 1)
    orbital_laser_shield_count = Int_To_Hex_String(orbital_laser_shield_count, 1)

    patch_fields = [
        # Edits ORBITALLASER.EquipOnEject, the standard laser tower.
        [
            '6E' '0004' '..'
            '05' '..'
            '03' '88' '000B09F0'
            '24' '..'
            '05' '..'
            '03' '88' '000B0BBA' '24' '01' '83'
            '6E' '0003' '0D' '0004' '02' '88' '000AF243',

            '..' '....'+lasertower_shield_count+
            '..'+lasertower_shield_type+
            '..' '..' '........'
            '..'+lasertower_laser_count+
            '..'+lasertower_laser_type+
            '..' '..' '........' '..' '..' '..'
            '..' '....' '..' '....' '..' '..' '........'
        ],
        
        # Edits Obj_2149.EquipOnEject, the Terran laser tower.
        [
            '6E' '0001' '07' '00100071' '83' '01' '83'
            '6E0004' '..'
            '05' '..'
            '03' '88' '000B09F0' 
            '24' '..' 
            '05' '..' 
            '03' '88' '000B0BBA' '24' '01' '83',

            '..' '....' '..' '........' '..' '..' '..'
            '......'+orbital_laser_shield_count+
            '..'+orbital_laser_shield_type+
            '..' '..' '........'
            '..'+orbital_laser_laser_count+
            '..'+orbital_laser_laser_type+
            '..' '..' '........' '..' '..' '..'
        ],
    ]
    
    # Construct the patches.
    patch_list = []
    for ref_code, replacement in patch_fields:
        patch_list.append( Obj_Patch(
            #offsets = [offset],
            ref_code = ref_code,
            new_code = replacement,
        ))
   

    # Apply the patches.
    Apply_Obj_Patch_Group(patch_list)

    return
