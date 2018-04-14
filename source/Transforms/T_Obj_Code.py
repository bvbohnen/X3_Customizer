'''
Edits made to the .obj files which contain compiled game KC code.
These are generally based on reading the dissassembled assembly code,
selecting constants of interest (eg. max seta multiplier), determining
their location in the original obj file, and defining a patch to apply.

This will not use the File_Patcher, since direct edits should be
reasonably safe.

Initial focus will be on x3story. Much of the code is copied at 
different offset in x3galedit, which may be added if needed.

Note: current patch offsets are based on AP version 3.4.

TODO:
Write more dynamic code which can generate these patches without
exact pointers, to be resiliant against game patches.
    -This will require extended matching regions, likely with wildcards
    for the pointers.
    -Where pointer values need to be used in the replacement, a similar
    wildcard match can be used, but which will return the value found
    in the wildcarded slice.
'''
from File_Manager import *
import inspect
# This function will convert hex strings to bytes objects.
from binascii import unhexlify as hex2bin

OPCODE_NOP = '0C'
OPCODE_POP = '24'

class Obj_Patch:
    '''
    Patch to apply to the .obj file.
    Members:
        file
            String, name of the obj file being edited.
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
    file_contents = Load_File(patch.file)

    # Look up how long the file header is.
    # This will be used to translate the code offset to the file
    # offset, which is slightly larger due to the header.
    header_length = {
        'L/x3story.obj' : 20,
        # TODO: x3galedit offset.
        }[patch.file]

    # Calculate the actual offset.
    offset = patch.offset + header_length

    # Grab the slice matching the ref code.
    ref_code_slice = file_contents.binary[offset : offset + len(patch.ref_code)]
    # Error check.
    if ref_code_slice != patch.ref_code:
        # Look up the calling transform's name for the printout.
        try:
            caller_name = inspect.stack()[1][3]
        except:
            caller_name = '?'
        print('Error: Obj patch reference code mismatch in {}.'.format(caller_name))
        return

    # Do the insertion, building a new byte string.
    new_binary = (file_contents.binary[0 : offset] 
                  + patch.new_code 
                  + file_contents.binary[offset + len(patch.new_code) : ])

    # Verify length match.
    assert len(new_binary) == len(file_contents.binary)
    # Update the binary.
    file_contents.binary = new_binary


    
@Check_Dependencies('L/x3story.obj')
def Adjust_Max_Seta(
        speed_factor = 10
    ):
    '''
    Changes the maximum SETA speed multiplier. Higher multipliers than
    the game default of 10 may cause oddities.
    
    * speed_factor
      - Int, the multiplier to use. At least 2. X3 debug mode allows
        up to 50. This transform will soft cap at 127, the max positive
        single byte value.
    '''
    # Make sure the input is an int, not float.
    try:
        speed_factor = int(speed_factor)
    except:
        print('Adjust_Max_Seta error: non-integer speed_factor')
        return
    # Check the range on the input.
    if not (2 <= speed_factor <= 127):
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
            file = 'L/x3story.obj',
            offset = 0x001152BF,
            # Existing code is 'pushb 10d', or b'050A'.
            # Check an extra couple bytes.
            ref_code = hex2bin('050A1600'),
            # Swap to something larger.
            new_code = hex2bin('05')+seta_hex,
            ),

        # Change the max check when clicking the buttons.
        Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x001157C1,
            # Existing code is 'pushb 10d', or b'050A'.
            # Check an extra couple bytes.
            ref_code = hex2bin('050A5C34'),
            # Swap to something larger.
            new_code = hex2bin('05')+seta_hex,
            ),
        Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x00115812,
            ref_code = hex2bin('050A1600'),
            new_code = hex2bin('05')+seta_hex,
            ),
    ]

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return



@Check_Dependencies('L/x3story.obj')
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
            file = 'L/x3story.obj',
            offset = 0x00013994,
            # Existing code is 'pushw 250d', or b'0600FA'.
            # Check an extra couple bytes.
            ref_code = hex2bin('0600FA5D34'),
            # Add the delay bytes.
            new_code = hex2bin('06')+delay_hex,
            )
    Apply_Obj_Patch(patch)

    return


@Check_Dependencies('L/x3story.obj')
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

    # Update: To simplify this code (and make it easier in the future
    # to update), use nop replacement instead.

    # Predefine the call hex values here, to reuse in patches.
    # call86     CLIENT.StopFastForward
    # pop
    original_call = hex2bin('8600015770'+'24')
    #-Removed
    # call86     CLIENT.IsFastForward
    #new_call      = hex2bin('86000157A9')
    new_call      = hex2bin(OPCODE_NOP * 6)


    # Construct the patches.
    patch_list = []
   
    if on_missile_launch:
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x00017BEE,
            # Check an extra couple bytes.
            ref_code = original_call + hex2bin('6F'),
            new_code = new_call,
            ))
    if on_receiving_priority_message:
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x00015DCA,
            # Check an extra couple bytes.
            ref_code = original_call + hex2bin('0D'),
            new_code = new_call,
            ))
    if on_collision_warning:
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x00017F22,
            # Check an extra couple bytes.
            ref_code = original_call + hex2bin('24'),
            new_code = new_call,
            ))
        

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return



@Check_Dependencies('L/x3story.obj')
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
            file = 'L/x3story.obj',
            offset = offset,
            # Convert these to binary strings.
            ref_code = hex2bin(ref_code),
            new_code = hex2bin('05') + count.to_bytes(1, byteorder = 'big'),
        ))
   

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return

#-Removed; the function edited appears to not be used for in-sector
# damage, and may be almost purely out of sector or special cases,
# which isn't so useful.
#@Check_Dependencies('L/x3story.obj')
#def Disable_Friendly_Fire(
#    ):
#    '''
#    Turns off friendly fire damage. This should also work against
#    collision damage. Friendly fire is defined aa an owner match
#    between the victim ship and the damage source object.
#    '''
#    # Construct the patch.
#    # This will edit the SHIP.Hit function where it does a matched
#    # owner check. Normally it will skip code for calling help, 
#    # player notoriety hit, etc. Now it will skip everything and
#    # jump to the function exit.
#    patch = Obj_Patch(
#            file = 'L/x3story.obj',
#            offset = 0x000C0172,
#            # Existing code is 'if SP[0]=0 then jump L000C02E5'.
#            # Check an extra couple bytes.
#            ref_code = hex2bin('34000C02E5'+'0F0001'),
#            # The exit block poped 3 from the stack, and there was
#            # 3 after the above jump, so everything should work okay.
#            new_code = hex2bin('34000C04D0'),
#            )
#    Apply_Obj_Patch(patch)
#
#    # Test patch:
#    # Above not working. Try shortcutting the whole function earlier,
#    # when it does the environment check.
#    patch = Obj_Patch(
#            file = 'L/x3story.obj',
#            offset = 0x000C0184,
#            # Existing code is 'if SP[0]=0 then jump L000C01A1'.
#            # Want to change to jumping on 1, an environment mismatch,
#            # so that environment match falls through and evenally returns.
#            # Check an extra couple bytes.
#            ref_code = hex2bin('34000C01A1'+'060812'),
#            # Change opcode to 33, for jump on not-0.
#            new_code = hex2bin('33000C01A1'),
#            )
#    Apply_Obj_Patch(patch)
#
#    # Above had no effect.
#    # Another test patch, changing a flag check which normally early
#    # returns on flag being 1, to use an OR instead of AND mask on
#    # the flag isolation, causing it to always see a non-0 result
#    # and return.
#    # Do this for ships and stations.
#    patch = Obj_Patch(
#            file = 'L/x3story.obj',
#            offset = 0x000C015D,
#            ref_code = hex2bin('53'+'34000C0165'),
#            # Opcode to 54, OR.
#            new_code = hex2bin('54'),
#            )
#    Apply_Obj_Patch(patch)
#
#    patch = Obj_Patch(
#            file = 'L/x3story.obj',
#            offset = 0x00098BEE,
#            ref_code = hex2bin('53'+'3400098BF6'),
#            # Opcode to 54, OR.
#            new_code = hex2bin('54'),
#            )
#    Apply_Obj_Patch(patch)
#
#    return


@Check_Dependencies('L/x3story.obj')
def Disable_Combat_Music(
    ):
    '''
    Turns off combat music, keeping the normal environment musc playing
    when nearing hostile objects. If applied to a saved game already in
    combat mode, combat music may continue to play for a moment.
    The beep on nearing an enemy will still be played.
    '''
    # Construct the patch.
    # This will edit the CLIENT.NotifyAlert function, such that when
    #  called to turn on combat mode, and checking to see if already
    #  in combat mode and return early, it will instead return early
    #  if not in combat mode (skipping the combat mode enable code).
    # To deal with cases where this transform is applied and combat
    #  mode is already on, the turn-on code will be edited to turn
    #  off combat mode instead.
    # Both of these changes are next to each other, and can be done
    #  with one patch.
    patch = Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x00017895,
            # Existing code is 
            # 'if SP[0]=0 then jump L000178A9'
            # 'push       1'
            # 'write      CLIENT.cl_Alert'
            ref_code = hex2bin('34000178A9'+'02'+'160007'),
            # Switch to 'if SP[0] != 0' and 'push 0'.
            new_code = hex2bin('33000178A9'+'01'),
            )
    Apply_Obj_Patch(patch)

    return



# Notes on the god engine station removal behavior:
'''
The primary sector and station analysis occurs in GODENGINE.InspectSectorTask.
Characteristics of this task:

    Infinite loop.
    Each loop randomly selects a sector, within 0-23 x, 0-19 y.
	    -Skips xenon/khaak/unclaimed sectors.
	    -Skips sectors flagged as 
	    -Skips sectors checked in the prior 10 hours.
    Analyzes one sector per 35 seconds or so (some random variation, with a 
        lot of scattered small waits).
	    -This is fast enough to traverse all sectors ~5 times in 10 hours.
	    -Probably spend most time doing ~15 second waits between skipped sectors.
	    -A sector with its 10 hours up will probably get visited within ~2 hours.
    In the sector, will loop over all factories.
    Loops over all resources, and records their overall fullness.
    Aims to capture factories that are lightly filled, and factories that are 
     starved (average <=7% full over 10 sampled fullness counts taken by the 
     factory at some inteverals.
    Also captures factories that are overfull (average >93% fill).

    If any such starved or stuffed factories found, an event will be spawned 
    for the sectors with those factories in a list, presumably to handle deletion.
	    -Some effort was spent on following the logic for how events work, but 
        the script calling was extremely obtuse.

    If the above deletion event not started, more logic is present to do further
    analysis, leading to a secondary event type.
	    -This was not explored in detail, and is not described here.
        -In testing, this logic chain appears to also perform station deletion.

    To stop station deletion, the code leading to the corresponding events need 
    to be modified. Two general options here:
        a)  Change code just prior to the Event creations to skip them, leaving
            the rest of the code intact in case of any important changes it might
            make.
        b)  Change the code prior to factory analysis to skip the sector
            entirely.
    In either case, the code for deleting wrecks should be left intact, so
    any edits should occur after there.
    
	Test results:
		1) Game started with god enabled, modded to skip first event type. Fail.
		2) Game started with all sectors skipped from start. Success.
		3) Game started with only the first event type skipped from start. Fail.
			-Suggest second event type also removes stations.
		4) Game started with both event types skipped from start. Success.
		4) Game started with god enabled, then modded to skip all sectors. Success.
'''

@Check_Dependencies('L/x3story.obj')
def Stop_GoD_From_Removing_Stations(
    ):
    '''
    Stops the GoD engine from removing stations which are nearly
    full on products or nearly starved of resources for extended
    periods of time.  This will not affect stations already removed
    or in the process of being removed.
    '''
    # Construct the patch.
    # This will edit GODENGINE.InspectSectorTask.

    # Pick the patching style.
    # Both work in testing, though the general sector skipper is
    # simpler to maintain.
    patch_style = 1

    if patch_style == 0:
        # To disable individual events:
        # Event type 1:
        # A particular 'if' equivelent flag check can be tuned so that
        # a given factory doesn't count as full/starved, whatever path
        # its analysis took, since both paths will now write a 0.
        patch = Obj_Patch(
                file = 'L/x3story.obj',
                offset = 0x0017F560,
                # Change the 'push 1' to 'push 0'.
                # Verify the following instruction.
                ref_code = hex2bin('02'+'320017F567'),
                new_code = hex2bin('01'),
                )
        Apply_Obj_Patch(patch)
    
        # Event type 2:
        # Edit the code near L0017FC6B, which decided if a non-existent
        # object gets removed from the list. Replace the jump with a
        # pop and some nops, so that all list items get removed. The later
        # check for an empty list will then skip to the next sector.
        patch = Obj_Patch(
                file = 'L/x3story.obj',
                offset = 0x0017FC59,
                ref_code = hex2bin('340017FC6B'),
                new_code = hex2bin(OPCODE_POP + OPCODE_NOP * 4),
                )
        Apply_Obj_Patch(patch)
    
    else:
        # Alterative: skip the sector before any factory analysis.
        # When the sector is checking for its 'SetNoEvents'
        # flag to be skipped, ensure both result paths
        # will skip the sector.
        # This will be used in general, being easier to maintain a
        # single patch.
        patch = Obj_Patch(
                file = 'L/x3story.obj',
                offset = 0x0017EEEB,
                # Swap 'push 0' to 'push 1'.
                ref_code = hex2bin('01'+'320017EEF2'),
                new_code = hex2bin('02'),
                )
        Apply_Obj_Patch(patch)

    return


@Check_Dependencies('L/x3story.obj')
def Disable_Asteroid_Respawn(
    ):
    '''
    Stops any newly destroyed asteroids from being set to respawn.
    This can be set temporarily when wishing to clear out some
    unwanted asteroids.
    It is not recommended to leave this transform applied long term.
    '''
    '''
    This one might be a little bit tricky.
    The best approach is to modify ASTEROID.Destruct to no longer
    make a call to REBUILD.RequestRebuild, but it needs to be
    done using a 1:1 replacement, and that call consumes 3
    stack items, so the replacement would need to work similarly.

    Can try out the nop instruction for this; though it hasn't
    been generally observed in existing code, it might be safe
    to used as an insert.

    Code to replace:
        get_object
        push       1
        pushw      303d ; 012Fh
        call86     REBUILD.RequestRebuild
        pop
    Byte count: 11
    '''
    # Construct the patch.


    # This will edit GODENGINE.InspectSectorTask.
    # At one point, an if/else block prior to the final station
    # creation event launcher will loop back to the next sector
    # if a particular table is empty. This change will ensure the
    # alternate path also jumps to the next sector, bypassing
    # the final code section.

    patch = Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x0008F9EB,
            # Replace with nops.
            ref_code = hex2bin('2E'+'02'+'06012F'+'8600085F30'+'24'),
            new_code = hex2bin( OPCODE_NOP * 11),
            )
    Apply_Obj_Patch(patch)

    return


@Check_Dependencies('L/x3story.obj')
def Allow_Valhalla_To_Jump_To_Gates(
    ):
    '''
    Removes a restriction on the Valhalla, or whichever ship is at
    offset 211 in tships, for jumping to gates. This should only
    be applied alongside another mod that either reduces the
    valhalla size, increases gate size, removes gate rings,
    or moves/removes the forward pylons, to avoid collision problems.
    '''
    '''
    Code to edit is in SHIP.CanMoveThroughGates, which is a somewhat
    convoluted function that returns 0 for ships of subtype 211,
    and 1 otherwise.  This uses a jump table with an xjump with an
    offset of 211, relying on all non-211 ships to be out of the
    table range and use the default jump target.

    Possible edits include:
        - Changing the xjump from "xjump 1, 211" to "xjump 1, -1", so that
        all ships will be out of range and use the default.
        - Changing the return value on the valhalla path from a 0
        to a 1.
        - Changing the jump table entries to always go to the return-1
        block.
        - etc.

    The simplest is probably just to change the return value.
    '''
    # Construct the patch.

    patch = Obj_Patch(
            file = 'L/x3story.obj',
            offset = 0x000CED11,
            # This pushes 0, returns, and checks a few later commands
            #  for verification.
            ref_code = hex2bin('01'+'83'+'32'+'000CED27'+'78'),
            # Swap push 0 to push 1
            new_code = hex2bin('02'),
            )
    Apply_Obj_Patch(patch)

    return

# TODO: asteroid/station respawn time edits.