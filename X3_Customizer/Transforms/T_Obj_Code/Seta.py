
from ... import File_Manager
from ... import Common
from .Obj_Shared import *

@File_Manager.Transform_Wrapper('L/x3story.obj')
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
    lu_text_file = File_Manager.Load_File(file_name = 't/8383-L044.xml',
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
            # Edits Obj_2259.Input.
            Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x001152BF],
                # Existing code is 'pushb 10d', or b'050A'.
                ref_code = '05' '0A' '16' '0054' '24' '0F' '0054',
                # Swap to something larger.
                new_code = '05' + seta_hex,
                ),

            # Change the max check when clicking the buttons.
            # Edits Obj_2259.ChangeValue.
            Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x001157C1],
                # Existing code is 'pushb 10d', or b'050A'.
                # Check an extra couple bytes.
                ref_code = '05' '0A' '5C' '34' '........' '0F' '0055' '02',
                # Swap to something larger.
                new_code = '05' + seta_hex,
                ),

            # Edits Obj_2259.ChangeValue (a little below the above spot).
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



@File_Manager.Transform_Wrapper('L/x3story.obj')
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


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
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
    replacement = NOP * 10


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

