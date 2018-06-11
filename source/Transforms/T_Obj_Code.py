'''
Edits made to the .obj files which contain compiled game KC code.
These are generally based on reading the dissassembled assembly code,
selecting constants of interest (eg. max seta multiplier), determining
their location in the original obj file, and defining a patch to apply.

This will not use the File_Patcher, since direct edits should be
reasonably safe.

Initial focus will be on x3story. Much of the code is copied at 
different offset in x3galedit, which may be added if needed.

Note: current patch offsets are based on AP version 3.3.

Update:
    Want more dynamic code which can generate these patches without
    exact pointers, to be resiliant against game patches.
    
    This will require extended matching regions, likely with wildcards
    for the pointers, and will not support replacing pointers (since
    picking out the new pointer is a hassle, though possible with
    some separate pointer search function).

    Eg. instead of matching '06 00FA 5D 34 00014313 02', which includes
    a full 32-bit pointer, can instead match '06 00FA 5D 34 ???????? 02'

    The replacement strings can have similar wildcards, which represent
    sections to leave as-is.

    The most convenient way to do this is to use the regex package,
    presuming it does not add much compiled code overhead (in quick
    test it seems to only add ~100kB).

    Code updates are complete and pass initial testing.
    
'''
from File_Manager import *
from Common import *
import inspect
# This function will convert hex strings to bytes objects.
from binascii import unhexlify as hex2bin
from binascii import hexlify as bin2hex
import re

OPCODE_NOP = '0C'
OPCODE_POP = '24'

class Obj_Patch:
    '''
    Patch to apply to the .obj file.

    Attributes:
    * file
      - String, name of the obj file being edited.
    * ref_code
      - String, the code starting at the offset which is being replaced.
      - Used for verification and for offset searching.
      - Use '.' for any wildcard match.
      - Will be converted to a regex pattern, though the string should
        not be formatted as a regex pattern.
    * new_code
      - Byte string, the replacement code.
      - Length of this doesn't need to match ref_code.
      - Replacements will be on a 1:1 basis with existing bytes, starting
        at a matched offset and continuing until the end of the new_code.
      - Overall obj code will remain the same length.
    '''
    def __init__(s, file, ref_code, new_code):
        s.file = file
        s.ref_code = ref_code
        s.new_code = new_code


def _String_To_Bytes(string, add_escapes = False):
    '''
    Converts the given string into bytes.
    Strings should either be hex representations (2 characters at a time)
    or wildcards given as '.' (also in pairs, where .. matches a single
    wildcard byte).

    * add_escapes
      - Bool, if True then re.escape will be called on the non-wildcard
        entries.
      - This should be applied if the bytes will be used as a regex pattern.
    '''
    # Make sure the input is even length, since hex conversions
    #  require 2 chars at a time (to make up a full byte).
    assert len(string) % 2 == 0

    new_bytes = b''

    # Loop over the pairs, using even indices.
    for even_index in range(0, len(string), 2):
        char_pair = string[even_index : even_index + 2]
        
        # Wildcards will be handled directly.
        if char_pair == '..':
            # Encode as a single '.' so this matches one byte.
            new_bytes += str.encode('.')
        # Everything else should be strings representing hex values.
        else:
            # Note: for low values, this tends to produce a special
            #  string in the form '\x##', but for values that can map
            #  to normal characters, it uses that character instead.
            # However, that character could also be a special regex
            #  character, and hence direct mapping is not safe.
            # As a workaround, aim to always put an escape character
            #  prior to the encoded byte; however, this requires that
            #  the escape be a byte also (a normal python escape will
            #  escape the / in /x## and blows up). Hopefully regex
            #  will unpack the byte escape and work fine.
            # Use re.escape for this, since trying to do it manually
            #  is way too much effort (get 'bad escape' style errors
            #  easily).
            this_byte = hex2bin(char_pair)
            if add_escapes:
                this_byte = re.escape(this_byte)
            new_bytes += this_byte

    return new_bytes


def Int_To_Hex_String(value, byte_count):
    '''
    Converts an int into a hex string, with the given byte_count
    for encoding. Always uses big endian.
    Eg. Int_To_Hex_String(62, 2) -> '003e'
    '''
    # Convert this into a byte string, hex, then back to string.
    # Always big endian.
    # Kinda messy: need to encode the int to bytes, then go from the
    #  byte string to a hex string, then decode that back to unicode.
    return bin2hex(value.to_bytes(byte_count, byteorder = 'big')).decode()
    

def Apply_Obj_Patch(patch):
    '''
    Patch an obj file using the defined patch.
    This will search for the ref_code, using regex, and applies
    the patch where a match is found.
    Error if 0 or 2+ matches found.
    '''
    file_contents = Load_File(patch.file)

    # Get a match pattern from the ref_code, using a bytes pattern.
    # This needs to convert the given ref_code into a suitable
    #  regex pattern that will match bytes.
    ref_bytes = _String_To_Bytes(patch.ref_code, add_escapes = True)
    pattern = re.compile(ref_bytes)

    # Get all match points.
    # Need to use finditer for this, as it is the only one that will
    #  return multiple matches.
    # Note: does not capture overlapped matches; this is not expected
    #  to be a problem.
    matches = [x for x in re.finditer(pattern, file_contents.binary)]
    
    # Look up the calling transform's name for any debug printout.
    try:
        caller_name = inspect.stack()[1][3]
    except:
        caller_name = '?'

    # Do the error check, as in the older patch style.
    if not matches or len(matches) > 1:
        # Can raise a hard or soft error depending on mode.
        # Message will be customized based on error type.
        if Settings.developer and not matches:
            print('Error: Obj patch reference code found 0 matches'
                 ' in {}.'.format(caller_name))
        elif Settings.developer and len(matches) > 1:
            print('Error: Obj patch reference code found multiple matches'
                 ' in {}.'.format( caller_name))
        else:
            raise Obj_Patch_Exception()
        return
    

    # Grab the offset of the match.
    offset = matches[0].start()
    #print(hex(offset))

    # Get the wildcard char, as an int (since the loop below unpacks
    #  the byte string into ints automatically, and also pulls ints
    #  from the original binary).
    wildcard = str.encode('.')[0]

    # Quick verification of the ref_code, to ensure re was used correctly.
    # This will not add escapes, since they confuse the values.
    for index, ref_byte in enumerate(_String_To_Bytes(patch.ref_code)):

        # Don't check wildcards.
        if ref_byte == wildcard:
            continue

        # Check mismatch.
        original_byte = file_contents.binary[offset + index]
        if ref_byte != original_byte:
            if Settings.developer:
                print('Error: Obj patch regex verification mismatch'
                     ' in {}.'.format(caller_name))
                return
            else:
                raise Obj_Patch_Exception()


    # Apply the patch, leaving wildcard entries unchanged.
    # This will edit in place on the bytearray.
    new_bytes = _String_To_Bytes(patch.new_code)
    for index, new_byte in enumerate(new_bytes):
        if new_byte == wildcard:
            continue
        file_contents.binary[offset + index] = new_byte

    return


    
@Transform_Wrapper('L/x3story.obj')
def Adjust_Max_Seta(
        speed_factor = 10,
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

    # Note:
    # LU swaps out all of the seta code sections with reading one of
    #  the text files (page 68 id 200) and decoding the value there.
    # As such, a text override would be needed for LU instead of an
    #  obj edit.
    # Can detect the LU installation by the presence of the 8383-L044.xml
    #  t file.
    # TODO: redirect this to a call to a module with t file edits, if
    #  one is ever added.
    lu_text_file = Load_File(file_name = 't/8383-L044.xml',
                          error_if_not_found = False,
                          return_game_file = True)
    if lu_text_file != None:

        #-Removed; while this works, it deletes all comments due
        # to elementtree being dumb about them, so a raw text replacement
        # should work just as well.
        ## A proper way to do this is with xml editing.
        ## Note: the top node is the language node, so searches
        ##  should start below it.
        #root_node = lu_text_file.Get_XML_Node()
        #
        ## Use xpath to do the node lookup.
        #seta_node = root_node.find(
        #    './page[@id="68"]/t[@id="200"]' )
        #assert seta_node != None
        #
        ## It should have a string in the 'text' attribute.
        #assert seta_node.text == '10'
        #seta_node.text = str(speed_factor)
        #
        ## Update the lu_text_file, since it tracks text and not xml
        ##  (for now).
        #lu_text_file.Update_From_XML_Node(root_node)

        text = lu_text_file.Get_Text()
        original_text = '<t id="200">10</t>'
        assert text.count(original_text) == 1
        text = text.replace(original_text,
                     '<t id="200">{}</t>'.format(speed_factor))
        lu_text_file.Update_From_Text(text)


    else:
        # Convert the input into a byte string, hex.
        # Always big endian (required by function, doesn't matter
        #  for 1 byte though).
        seta_hex = Int_To_Hex_String(speed_factor, 1)

        # Construct the patch.
        # Unfortunately, this is mostly the result of hand analysis of the
        # code. Notes may be uploaded elsewhere at some point.
        # There are a couple places in need of patching.
        patch_list = [

            # Change the menu cap. Unclear on when this is called exactly.
            Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x001152BF],
                # Existing code is 'pushb 10d', or b'050A'.
                ref_code = '05' '0A' '16' '0054' '24' '0F' '0054',
                # Swap to something larger.
                new_code = '05' + seta_hex,
                ),

            # Change the max check when clicking the buttons.
            Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x001157C1],
                # Existing code is 'pushb 10d', or b'050A'.
                # Check an extra couple bytes.
                ref_code = '05' '0A' '5C' '34' '........' '0F' '0055' '02',
                # Swap to something larger.
                new_code = '05' + seta_hex,
                ),

            Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x00115812],
                ref_code = '05' '0A' '16' '0055' '24' '0F' '0055' '16' '0054',
                new_code = '05' + seta_hex,
                ),
        ]

        # Apply the patches.
        for patch in patch_list:
            Apply_Obj_Patch(patch)

    return



@Transform_Wrapper('L/x3story.obj')
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

    # Convert this into a hex string.
    # This is a wide int, eg. 16-bits.
    delay_hex = Int_To_Hex_String(new_delay, 2)

    # Construct the patch.
    # This edits CLIENT.Vbi, which internally has a timer that it compares
    #  to 250 (ms), the value to replace.
    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x00013994, 0x00014304],
            # Existing code is 'pushw 250d', or b'0600FA'.
            ref_code = '06' '00FA' '5D' '34' '........' '02' '32' '........' '01',
            # Replaced the delay bytes.
            new_code = '06' + delay_hex,
            )
    Apply_Obj_Patch(patch)

    return


@Transform_Wrapper('L/x3story.obj', LU = False)
def Stop_Events_From_Disabling_Seta(
        on_missile_launch = False,
        on_receiving_priority_message = False,
        on_collision_warning = False,
        on_frame_input = False,
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
    * on_frame_input
      - If True, the PerFrameInput function will not turn off seta,
        allowing menus to be opened.
    '''

    '''
    This will work by finding the places where a call is made to
    CLIENT.StopFastForward, and replace them with nops.

    Initial locations to edit:
        CLIENT.NotifyMissileAlert
        CLIENT.ReceiveMessageWithPriority
        CLIENT.NotifyCollisionWarn
        Obj_501.PerFrameInput (related to menu opening)

    Possible future locations to edit:
        CLIENT.PlayMessageWithPrioAndFaceAndNoise
        CLIENT.PlayMessageWithPrioAndFace
        MONITORCONTROL.ClickInfoPanel

    Note on LU:
        These triggers are removed already in LU.
        LU disables seta on user controls; may indicate this is part
        of the runtime code and not in the KC.

    Predefine the call hex values here, to reuse in patches.
       push       0
       pushw      150d ; 96h
       call86     CLIENT.StopFastForward
       pop
    
    Note:
     The call is preceeded by 2 commands to push arguments.
     The call itself consumes 2 args, and returns 1.
     The followup pop removes that 1.

    The replacement should be stack neutral, so replace all of these
     with nops, or else replace the call and pop twice then fill with
     nops.
    '''
    original_call = '01' '06' '0096' '86' '........' '24'
    replacement = OPCODE_NOP * 10


    # Construct the patches.
    patch_list = []
   
    if on_missile_launch:
        # Edit in CLIENT.NotifyMissileAlert.
        # Note: this code isn't in LU.
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x00017BEE],
            ref_code = original_call + '6F' '33' '........' '05' '14',
            new_code = replacement,
            ))

    if on_receiving_priority_message:
        # Edit in CLIENT.ReceiveMessageWithPriority.
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x00015DCA],
            ref_code = original_call + '0D' '0004' '0D' '0006' '03',
            new_code = replacement,
            ))

    if on_collision_warning:
        # Edit in CLIENT.NotifyCollisionWarn.
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x00017F22],
            ref_code = original_call + '24' '01' '83' '6E' '0009' '0F' '0006',
            new_code = replacement,
            ))
        
    if on_frame_input:
        # Edit in Obj_501.PerFrameInput.
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001C40C],
            ref_code = original_call + '32' '........' '79' '0006' '0000',
            new_code = replacement,
            ))        
        

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return



@Transform_Wrapper('L/x3story.obj', LU = False)
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

    # Convert to hex strings, 1 byte each.
    tm_count      = Int_To_Hex_String(tm_count, 1)
    tp_count      = Int_To_Hex_String(tp_count, 1)
    m6_count      = Int_To_Hex_String(m6_count, 1)
    capital_count = Int_To_Hex_String(capital_count, 1)
    sirokos_count = Int_To_Hex_String(sirokos_count, 1)

    '''
    These are generally just going to be integer value edits of
    the GetMaxMarines functions (base and overloads).

    Entries generally are doubled, one const is used in a comparison,
    second copy is used on one comparison path, so 2 patches per
    marine count changed.

    Sirokos is a special case, with an ship subtype id comparison and
    early return of 30.

    For now, all locations are edited, but arg defaults
    should leave things unchanged.

    Note on LU:
        This removes most of the overloads and just has the base function
        look up the ware volume of the ship, and hence the marine count
        is set through tships instead.
        TODO: add support for this alternate style of marine changes.
    '''

    # Create a short version of the key patch fields.
    # These are groups of [offset, ref_code, new_count].
    # Note: for cleaner matching, keep a prefix 05 in the ref, but leave
    #  it off the new_code here and add it below.
    #patch_fields = [
    #    # Sirokos. Special case of SHIP.
    #    # Only one value to patch.
    #    [0x000A876E, '051E8301', sirokos_count],
    #
    #    # TM. Inherits from SHIP_BIG.
    #    [0x000CFA1C, '05085D34', tm_count],
    #    [0x000CFA2C, '05081400', tm_count],
    #    
    #    # Capitals, inherit from Obj_2019.
    #    [0x000D58EE, '05145D34', capital_count],
    #    [0x000D58FE, '05141400', capital_count],
    #    
    #    # M6. Uses SHIP_M6.
    #    [0x000D68DB, '05085D34', m6_count],
    #    [0x000D68EB, '05081400', m6_count],
    #    
    #    # TP. Uses SHIP_TP.
    #    [0x000D9537, '05285D34', tp_count],
    #    [0x000D9547, '05281400', tp_count],
    #    ]
    
    # Lay out the replacement region, capturing both values (otherwise
    #  ambiguity problems crop up).
    patch_fields = [
        # Sirokos. Special case of SHIP.
        # Only one value to patch.
        ['05'  '1E'  '83''01''83''01''83''6E''0005''0F''0062', 
         '..'+sirokos_count],

        # TM. Inherits from SHIP_BIG.
        ['05'  '08'    '5D''34''........''0D''0001''32''........'
         '05'  '08'    '14''0002''24''83''24''01''83''6E''0006''01', 
         '..'+tm_count+'..''..''........''..''....''..''........'
         '..'+tm_count],
        
        # Capitals, inherit from Obj_2019.
        ['05'  '14'         '5D''34''........''0D''0001''32''........'
         '05'  '14'         '14''0002''24''83''24''01''83''6E''0007''0D', 
         '..'+capital_count+'..''..''........''..''....''..''........'
         '..'+capital_count],
        
        # M6. Uses SHIP_M6.
        ['05'  '08'    '5D''34''........''0D''0001''32''........'
         '05'  '08'    '14''0002''24''83''24''01''83''6E''0007''05', 
         '..'+m6_count+'..''..''........''..''....''..''........'
         '..'+m6_count],
        
        # TP. Uses SHIP_TP.
        ['05'  '28'    '5D''34''........''0D''0001''32''........'
         '05'  '28'    '14''0002''24''83''24''01''83''6E''0007''0D', 
         '..'+tp_count+'..''..''........''..''....''..''........'
         '..'+tp_count],
        ]

    # Construct the patches.
    patch_list = []
    for ref_code, replacement in patch_fields:
        patch_list.append( Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [offset],
            ref_code = ref_code,
            new_code = replacement,
        ))
   

    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)

    return


@Transform_Wrapper('L/x3story.obj', LU = False)
def Disable_Combat_Music(
    ):
    '''
    Turns off combat music, keeping the normal environment musc playing
    when nearing hostile objects. If applied to a saved game already in
    combat mode, combat music may continue to play for a moment.
    The beep on nearing an enemy will still be played.
    '''
    '''
    This will edit the CLIENT.NotifyAlert function
    The arg to the function is a flag to enable or disable combat mode.
    CLIENT.cl_Alert is an existing flag indicating if already in
    combat mode or not.

    Near entry, the code can be edited so that when
    called to turn on combat mode, and checking to see if already
    in combat mode and return early, it will instead return early
    if not in combat mode (skipping the combat mode enable code).

    To deal with cases where this transform is applied and combat
    mode is already on, the turn-on code will be edited to turn
    off combat mode instead.

    Both of these changes are next to each other, and can be done
    with one patch.

    Example:
    L00017889: push       SP[3] ; arg1
            ; Jumps to turning off combat
            if SP[0]=0 then jump L000178AE     
            read       CLIENT.cl_Alert ; [7]
            if SP[0]=0 then push 1 else push 0
            ; Jumps to return if already in combat
            if SP[0]=0 then jump L000178A9
            ; Turns on combat and music
            push       1
            write      CLIENT.cl_Alert ; [7]
            ...

    Replacement will look like:
    L00017889: push       SP[3] ; arg1
            ; Jumps to turning off combat
            if SP[0]=0 then jump L000178AE     
            read       CLIENT.cl_Alert ; [7]
            if SP[0]=0 then push 1 else push 0
            ; Jumps to return if not in combat
            if SP[0]!=0 then jump L000178A9    <-edit
            ; If here, then arg1 requested combat, and combat flag
            ;  is set, so turn off the flag.
            ; Turns off combat
            push       0                       <-edit
            write      CLIENT.cl_Alert ; [7]
            ; Continue to turning on combat music for now;
            ;  next check should switch the path that clears combat fully.
            ...

    Note on LU:
        The code is mostly the same, but for some reason cl_Alert is
        swapped to cl_Verbose (different offset code), and near the
        start CLIENT.cl_Killed is swapped to CLIENT.cl_GameFeatures.

        It is unclear at a glance what this is meant to accomplish.
        TODO: look into this, maybe after getting LU music to work
        so that changes can be tested.
    '''

    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x00017895],
            # Existing code is 
            # 'if SP[0]=0 then jump L000178A9'
            # 'push       1'
            # 'write      CLIENT.cl_Alert'
            ref_code = '34' '........' '02' '16' '0007' '24' '01' '06' '00C8',
            # Switch to 'if SP[0] != 0' and 'push 0'.
            new_code = '33' '........' '01',
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

@Transform_Wrapper('L/x3story.obj')
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
    '''
    The related function has a lot of complex code in it, mostly
    broken into two major analysis sections followed by some other
    script calls.

    The two sections, and their related Event calls, could be
    bypassed, but the simplest approach turned out to leverage some
    code in the sector analysis loop which allows some sectors
    to be skipped, perhaps for some special sectors (like M148).
    '''

    #-Removed unused patch style to reduce code maintanance.
    ## Pick the patching style.
    ## Both work in testing, though the general sector skipper is
    ## simpler to maintain.
    #patch_style = 1
    #
    #if patch_style == 0:
    #    # To disable individual events:
    #    # Event type 1:
    #    # A particular 'if' equivelent flag check can be tuned so that
    #    # a given factory doesn't count as full/starved, whatever path
    #    # its analysis took, since both paths will now write a 0.
    #    patch = Obj_Patch(
    #            file = 'L/x3story.obj',
    #            offsets = [0x0017F560],
    #            # Change the 'push 1' to 'push 0'.
    #            # Verify the following instruction.
    #            ref_code = hex2bin('02'+'320017F567'),
    #            new_code = hex2bin('01'),
    #            )
    #    Apply_Obj_Patch(patch)
    #
    #    # Event type 2:
    #    # Edit the code near L0017FC6B, which decided if a non-existent
    #    # object gets removed from the list. Replace the jump with a
    #    # pop and some nops, so that all list items get removed. The later
    #    # check for an empty list will then skip to the next sector.
    #    patch = Obj_Patch(
    #            file = 'L/x3story.obj',
    #            offsets = [0x0017FC59],
    #            ref_code = hex2bin('340017FC6B'),
    #            new_code = hex2bin(OPCODE_POP + OPCODE_NOP * 4),
    #            )
    #    Apply_Obj_Patch(patch)
    
    # Skip the sector before any factory analysis.
    # When the sector is checking for its 'SetNoEvents' flag to be skipped,
    # ensure both result paths will skip the sector.
    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0017EEEB],
            # Swap 'push 0' to 'push 1'.
            ref_code = '01' '32' '........' '02' '34' '........' 
                        '23' '0002' '32' '........' '02' '02' '82',
            new_code = '02',
            )
    Apply_Obj_Patch(patch)

    return


@Transform_Wrapper('L/x3story.obj', LU = False)
def Disable_Asteroid_Respawn(
    ):
    '''
    Stops any newly destroyed asteroids from being set to respawn.
    This can be set temporarily when wishing to clear out some
    unwanted asteroids.
    It is not recommended to leave this transform applied long term,
    without some other method of replacing asteroids.
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

    Note: does not apply to LU, which already has the respawn code removed.
    '''
    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0008F9EB],
            # Replace with nops.
            ref_code = '2E' '02' '06' '012F' '86' '........' '24' '0F' '0001' '34',
            new_code = OPCODE_NOP * 11,
            )
    Apply_Obj_Patch(patch)

    return


@Transform_Wrapper('L/x3story.obj', LU = False)
def Allow_Valhalla_To_Jump_To_Gates(
    ):
    '''
    Removes a restriction on the Valhalla, or whichever ship is at
    offset 211 in tships, from jumping to gates. This should only
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

    Note: LU trims away all of this extra code already.
    '''
    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x000CED11],
            # This pushes 0, returns, and checks a few later commands
            #  for verification.
            ref_code = '01' '83' '32' '........' '78' '0001' '000000D3'
                        '........' '........' '02' '83',
            # Swap push 0 to push 1
            new_code = '02',
            )
    Apply_Obj_Patch(patch)

    return

# TODO: asteroid/station respawn time edits.