'''
Edits made to the .obj files which contain compiled game KC code.
These are generally based on reading the dissassembled assembly code,
selecting constants of interest (eg. max seta multiplier), determining
their location in the original obj file, and defining a patch to apply.

This will not use the File_Patcher, since direct edits should be
reasonably safe.

Initial focus will be on x3story. Much of the code is copied at 
different offset in x3galedit, which may be added if needed.
'''
from File_Manager import *
# This function will convert hex strings to bytes objects.
from binascii import unhexlify as hex2bin

class Obj_Patch:
    '''
    Patch to apply to the .obj file.
    Members:
        file
            String, name of the obj file being edited, without .obj extension.
        offset
            Int, byte offset into the obj file to begin the edit.
            This will match the obj file labelling, and does not need to
            account for the file header.
        ref_code
            Byte string, the code starting at the offset which is being replaced.
            Used for verification.
        new_code
            Byte string, the replacement code.
            Length of this doesn't need to match ref_code.
            Replacements will be on a 1:1 basis with existing bytes.
            Overall code will remain the same length.
    '''
    def __init__(s, file, offset, ref_code, new_code):
        s.file = file
        s.offset = offset
        s.ref_code = ref_code
        s.new_code = new_code


def Apply_Obj_Patch(patch):
    '''
    Patch an obj file using the defined patch.
    Prints a message and skips if ref_code doesn't match.
    '''
    file_contents = Load_File(patch.file + '.obj')

    # Look up how long the file header is.
    # This will be used to translate the code offset to the file
    # offset, which is slightly larger due to the header.
    header_length = {
        'x3story' : 20,
        # TODO: x3galedit offset.
        }[patch.file]

    # Calculate the actual offset.
    offset = patch.offset + header_length

    # Grab the slice matching the ref code.
    ref_code_slice = file_contents.binary[offset : offset + len(patch.ref_code)]
    # Error check.
    if ref_code_slice != patch.ref_code:
        print('Error: Obj patch reference code mismatch.')
        return

    # Do the insertion, building a new byte string.
    new_binary = (file_contents.binary[0 : offset] 
                  + patch.new_code 
                  + file_contents.binary[offset + len(patch.new_code) : ])

    # Verify length match.
    assert len(new_binary) == len(file_contents.binary)
    # Update the binary.
    file_contents.binary = new_binary


    
@Check_Dependencies('x3story.obj')
def Adjust_Max_Seta(
        speed_factor = 10
    ):
    '''
    Changes the maximum SETA speed multiplier. Higher multipliers than
    the game default of 10 may cause oddities.
    
    * speed_factor
      - Int, the multiplier to use. At least 2, currently limited to 50,
        the debug mode maximum.
    '''
    # Make sure the input is an int, not float.
    try:
        speed_factor = int(speed_factor)
    except:
        print('Adjust_Max_Seta error: non-integer speed_factor')
        return
    # Check the range on the input.
    if not (2 <= speed_factor <= 50):
        print('Adjust_Max_Seta error: speed_factor unsupported.')
        return

    # Convert the input into a byte string, hex.
    # Always big endian (required by function, doesn't matter for 1 byte though).
    seta_hex = speed_factor.to_bytes(1, byteorder = 'big')

    # Construct the patch.
    # Unfortunately, this is mostly the result of hand analysis of the
    # code. Notes may be uploaded elsewhere at some point.
    # There are a couple places in need of patching.
    patch_list = [

        # Change the menu cap. Unclear on when this is called exactly.
        Obj_Patch(
            file = 'x3story',
            offset = 0x001152BF,
            # Existing code is 'pushb 10d', or b'050A'.
            # Check an extra couple bytes.
            ref_code = hex2bin('050A1600'),
            # Swap to something larger.
            new_code = hex2bin('05')+seta_hex,
            ),

        # Change the max check when clicking the buttons.
        Obj_Patch(
            file = 'x3story',
            offset = 0x001157C1,
            # Existing code is 'pushb 10d', or b'050A'.
            # Check an extra couple bytes.
            ref_code = hex2bin('050A5C34'),
            # Swap to something larger.
            new_code = hex2bin('05')+seta_hex,
            ),
        Obj_Patch(
            file = 'x3story',
            offset = 0x00115812,
            ref_code = hex2bin('050A1600'),
            new_code = hex2bin('05')+seta_hex,
            ),
    ]

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return



@Check_Dependencies('x3story.obj')
def Adjust_Max_Speedup_Rate(
        scaling_factor = 1
    ):
    '''
    Changes the rate at which SETA turns on. By default, it will accelerate
    by (selected SETA -1)/10 every 250 milliseconds. This transform will reduce
    the delay between speedup ticks.
    
    * scaling_factor
      - Float, the amount to boost the speedup rate by. Eg. 2 will reduce
        the delay between ticks to 125 ms. Practical limit may be set
        by game frame rate, eg. approximately 15x at 60 fps.
    '''
    # Change the 250 ms delay.
    new_delay = int(250 / scaling_factor)
    # Safety floor.
    new_delay = max(1, new_delay)

    # Convert this into a byte string, hex.
    # Always big endian.
    # This is a wide int, eg. 16-bits.
    delay_hex = new_delay.to_bytes(2, byteorder = 'big')

    # Construct the patch.
    # Unfortunately, this is mostly the result of hand analysis of the
    # code. Notes may be uploaded elsewhere at some point.
    patch = Obj_Patch(
            file = 'x3story',
            offset = 0x00013994,
            # Existing code is 'pushw 250d', or b'0600FA'.
            # Check an extra couple bytes.
            ref_code = hex2bin('0600FA5D34'),
            # Add the delay bytes.
            new_code = hex2bin('06')+delay_hex,
            )
    Apply_Obj_Patch(patch)

    return


@Check_Dependencies('x3story.obj')
def Stop_Events_From_Disabling_Seta(
        on_missile_launch = False,
        on_receiving_priority_message = False,
        on_collision_warning = False,
    ):
    '''
    Stop SETA from being turned off automatically upon certain events,
    such as missile attacks.
    
    * on_missile_launch
      - If True, Seta will not turn off when a missile is fired at the
        player ship.
    * on_receiving_priority_message
      - If True, Seta will not turn off when a priority message is
        received, such as a police notice of being scanned.
    * on_collision_warning
      - If True, Seta will not turn off when a near collision occurs.
    '''

    # This will work by finding the places where a call is made to
    # CLIENT.StopFastForward, and replace them with something
    # benign, like a call to CLIENT.IsFastForward.
    # Predefine the call hex values here, to reuse in patches.
    # call86     CLIENT.StopFastForward
    original_call = hex2bin('8600015770')
    # call86     CLIENT.IsFastForward
    new_call      = hex2bin('86000157A9')


    # Construct the patches.
    patch_list = []
   
    if on_missile_launch:
        patch_list.append( Obj_Patch(
            file = 'x3story',
            offset = 0x00017BEE,
            # Check an extra couple bytes.
            ref_code = original_call + hex2bin('246F'),
            new_code = new_call,
            ))
    if on_receiving_priority_message:
        patch_list.append( Obj_Patch(
            file = 'x3story',
            offset = 0x00015DCA,
            # Check an extra couple bytes.
            ref_code = original_call + hex2bin('240D'),
            new_code = new_call,
            ))
    if on_collision_warning:
        patch_list.append( Obj_Patch(
            file = 'x3story',
            offset = 0x00017F22,
            # Check an extra couple bytes.
            ref_code = original_call + hex2bin('2424'),
            new_code = new_call,
            ))
        

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return



@Check_Dependencies('x3story.obj')
def Set_Max_Marines(
        tm_count = 8,
        tp_count = 40,
        m6_count = 8,
        capital_count = 20,
        sirokos_count = 30,
    ):
    '''
    Sets the maximum number of marines that each ship type can carry.
    These are byte values, signed, so max is 127.
    
    * tm_count
      - Int, marines carried by TMs.
    * tp_count
      - Int, marines carried by TPs.
    * m6_count
      - Int, marines carried by M6s.
    * capital_count
      - Int, marines carried by capital ships: M1, M2, M7, TL.
    * sirokos_count
      - Int, marines carried by the Sirokos, or whichever ship is located
        at entry 263 in Tships (when starting count at 1).
        Note: XRM does not use this slot in Tships.
    '''
    # Make input args ints, limit to 1 to max_count.
    max_count = 127
    tm_count = max(1, min(int(tm_count), max_count))
    tp_count = max(1, min(int(tp_count), max_count))
    m6_count = max(1, min(int(m6_count), max_count))
    capital_count = max(1, min(int(capital_count), max_count))
    sirokos_count = max(1, min(int(sirokos_count), max_count))


    # These are generally just going to be integer value edits.
    # Entries generally are doubled, one const is used in a comparison,
    # second copy is used on one comparison path, so 2 patches per
    # marine count changed.
    # Defaults should leave things unchanged.

    # Create a short version of the key patch fields.
    # These are groups of [offset, ref_code, new_code].
    patch_fields = [
        # Sirokos. Special case of SHIP.
        # Only one value to patch.
        [0x000A876E, '051E8301', sirokos_count],

        # TM. Inherits from SHIP_BIG.
        [0x000CFA1C, '05085D34', tm_count],
        [0x000CFA2C, '05081400', tm_count],
        
        # Capitals, inherit from Obj_2019.
        [0x000D58EE, '05145D34', capital_count],
        [0x000D58FE, '05141400', capital_count],
        
        # M6. Uses SHIP_M6.
        [0x000D68DB, '05085D34', m6_count],
        [0x000D68EB, '05081400', m6_count],
        
        # TP. Uses SHIP_TP.
        [0x000D9537, '05285D34', tp_count],
        [0x000D9547, '05281400', tp_count],
        ]

    # Construct the patches.
    patch_list = []
    for offset, ref_code, count in patch_fields:
        patch_list.append( Obj_Patch(
            file = 'x3story',
            offset = offset,
            # Convert these to binary strings.
            ref_code = hex2bin(ref_code),
            new_code = hex2bin('05') + count.to_bytes(1, byteorder = 'big'),
        ))
   
    #-Removed; only half of the patches, and too verbose.
    ## Sirokos. Special case of SHIP.
    #patch_list.append( Obj_Patch(
    #    file = 'x3story',
    #    offset = 0x000A876E,
    #    # Check an extra couple bytes.
    #    ref_code = hex2bin('051E8301'),
    #    new_code = hex2bin('05') + sirokos_count.to_bytes(1, byteorder = 'big'),
    #    ))
    #
    ## TM. Inherits from SHIP_BIG.
    #patch_list.append( Obj_Patch(
    #    file = 'x3story',
    #    offset = 0x000CFA1C,
    #    # Check an extra couple bytes.
    #    ref_code = hex2bin('05085D34'),
    #    new_code = hex2bin('05') + tm_count.to_bytes(1, byteorder = 'big'),
    #    ))
    #
    ## Capitals, inherit from Obj_2019.
    #patch_list.append( Obj_Patch(
    #    file = 'x3story',
    #    offset = 0x000D58EE,
    #    # Check an extra couple bytes.
    #    ref_code = hex2bin('05145D34'),
    #    new_code = hex2bin('05') + capital_count.to_bytes(1, byteorder = 'big'),
    #    ))
    #
    ## M6. Uses SHIP_M6.
    #patch_list.append( Obj_Patch(
    #    file = 'x3story',
    #    offset = 0x000D68DB,
    #    # Check an extra couple bytes.
    #    ref_code = hex2bin('05085D34'),
    #    new_code = hex2bin('05') + m6_count.to_bytes(1, byteorder = 'big'),
    #    ))
    #
    ## TP. Uses SHIP_TP.
    #patch_list.append( Obj_Patch(
    #    file = 'x3story',
    #    offset = 0x000D9537,
    #    # Check an extra couple bytes.
    #    ref_code = hex2bin('05285D34'),
    #    new_code = hex2bin('05') + tp_count.to_bytes(1, byteorder = 'big'),
    #    ))
        

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return