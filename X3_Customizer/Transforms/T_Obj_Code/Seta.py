
from ... import File_Manager
from ... import Common
Settings = Common.Settings
from .Obj_Shared import *

# TODO: update for FL
@File_Manager.Transform_Wrapper('L/x3story.obj', TC = False)
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
    '''
    Notes made when looking into seta speed:
    
	TI_SetTimeWarpFactor and TI_GetTimeWarpFactor appear to deal with Seta.
		
		TI_SetTimeWarpFactor is defaulted in some places to 65536, 0x10000, 
        such as in dialogue handling or when playing cutscenes, indicating 
        this sets the timescale back to 1x.
			
		DEBUG.IncreaseTimeWarp checks the current value against 0x10000 and 
        does nothing if >= to that, else doubles the current value.
			This implies the TimeWarpFactor is a 32-bit integer where the 
            lower 16-bits are fractional scaling.
			Capping at 0x10000 is a 10x speed multiplier.
		DEBUG.DecreaseTimeWarp checks against 0x1000 and does not drop below 
        that, else halves the current value.
			
		X_AUDIO.SpeakArrayWithPriorityAndFaceAndDurationWithSubtitle and 
        SpeakArrayWithPriorityAndFaceAndDuration change the timewarp, 
        though it is unclear on the value changed to 
        (lots of stack manipulation).
			
		CAMERA.CutEvent and CLIENT.StopFastForward and 
        MENU_DIALOG.SpeakQuestionWithDuration set the timewarp to 0x10000.
		CLIENT.Vbi sets it in an  unclear way, but after calls to cl_FastForward.
			
		There is no clear indicator this deals with Seta, though; 
        may be a more generic time factor.
			
	FastForward is another name to look at.
		Var: CLIENT.cl_FastForwardTime
			-Initialized to 6.
			-Appears to be the menu selection for seta speed.
		Var: CLIENT.cl_FastForward
			-Appears to be the current seta speed.
		Var: CLIENT.cl_FastForwardStep
			-Appears to be a temp var to track the time since the last seta increment.
			-Used to time out 250ms updates.
		CLIENT.StartFastForward
			-Plays a sound.
			-Does some sort of key check to exit early.
			-Does not call TI_SetTimeWarpFactor, only sets vars.
			-Edits cl_TargetNextKey, cl_FastForward, cl_FastForwardStep, cl_LastNotifyPlanet.
		CLIENT.StopFastForward
			-Plays a sound
			-Calls TI_SetTimeWarpFactor set back to 0x10000.
			-This is commonly called by other methods to disable Seta.
			-Can potentially track down those other methods and muck with their
             call to stop a ship being dropped out of seta automatically.
			-Returns 0 on the stack; consumes no inputs. To disable, need to 
             replace with some harmless function which will return a single 
             item on the stack, while taking no input args.
			-IsFastForward might work as a replacement; nearby (easier to 
             remember), and just a quick value lookup, though it doesn't 
             return 0 (shouldn't matter).
		CLIENT.ToggleFastForward
			-Calls StartFastForward or StopFastForward.
			-Has a NotifyNoEquipment call, maybe after checking for Seta software.
		CLIENT.Vbi
			-Does some time variable stuff, unclear on details.
			-Does compare cl_FastForward to 10, which could be the max seta check.
			-Appears to have a 250ms timer, and increments cl_FastForward by 1, 
             suggesting this is the mechanic that slowly increases seta.
			-Succesfully changed to speed up seta turn-on rate.
		CLIENT.SetWarpFactor
			-Updates cl_FastForwardTime.
			-Called in Obj_2259.Input.
		Var: Obj_2259.var_2259_1
			-Gets initialized with CLIENT.GetWarpFactor.
			-If above returned 0, this defaults to 6.
			-This appears to be the temp var for the menu item, converted to a 
             string elsewhere.
		Obj_2259.Input
			-Appears to deal with menu items.
			-Label L00114EF2 sets the minimum seta value to 2.
			-Label L001152BF sets the maximum to 10?
					-Unclear on why this would force it to 10.
					-Code block is only called from a switch statement, 
                     apparently based on button press, but there is no 
                     expected comparison to 10 here.
			-Label L001157C1 checks against 10 and calls L001157D9, 
             which rolls it over to 2?
			-Label L00115812 also has a 10 value.
			-When cheat mode is active, it appears the max may be 50 instead of 10.
				
		Conclusion: Editing the above 3 locations in Obj_2259.Input succesfully increased SETA speed.
		Editing the CLIENT.Vbi delay (250 ms) down succesfully speeds up SETA turn-on rate.

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
        #root_node = lu_text_file.Get_XML_Tree().getroot()
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

        # The addresses of vars differ between AP and FL.
        if Settings.Target_Is_AP():
            var1 = '0054'
            var2 = '0055'
        else: # FL
            var1 = '0065'
            var2 = '0066'

        # Construct the patch.
        # Unfortunately, this is mostly the result of hand analysis of the
        # code. Notes may be uploaded elsewhere at some point.
        # There are a couple places in need of patching.
        patch_list = [

            # Change the menu cap. Unclear on when this is called exactly.
            # Edits Obj_2259.Input.
            # Just prior to CLIENT.SetWarpFactor.
            Obj_Patch(
                #offsets = [0x001152BF],
                # Existing code is 'pushb 10d', or b'050A'.
                ref_code = '05' '0A' '16' +var1+ '24' '0F' +var1+ '02' '06' '0096',
                # Swap to something larger.
                new_code = '05' + seta_hex,
                ),

            # Change the max check when clicking the buttons.
            # Edits Obj_2259.ChangeValue.
            Obj_Patch(
                #offsets = [0x001157C1],
                # Existing code is 'pushb 10d', or b'050A'.
                # Check an extra couple bytes.
                ref_code = '05' '0A' '5C' '34' '........' '0F' +var2+ '02',
                # Swap to something larger.
                new_code = '05' + seta_hex,
                ),

            # Edits Obj_2259.ChangeValue (a little below the above spot).
            # This is also prior to CLIENT.SetWarpFactor.
            Obj_Patch(
                #offsets = [0x00115812],
                ref_code = '05' '0A' '16' +var2+ '24' '0F' +var2+ '16' +var1,
                new_code = '05' + seta_hex,
                ),
        ]

        # Apply the patches.        
        Apply_Obj_Patch_Group(patch_list)

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
            #offsets = [0x00017BEE],
            ref_code = original_call + '6F' '33' '........' '05' '14',
            new_code = replacement,
            ))

    if on_receiving_priority_message:
        # Edit in CLIENT.ReceiveMessageWithPriority.
        patch_list.append( Obj_Patch(
            #offsets = [0x00015DCA],
            ref_code = original_call + '0D' '0004' '0D' '0006' '03',
            new_code = replacement,
            ))

    if on_collision_warning:
        # Edit in CLIENT.NotifyCollisionWarn.
        patch_list.append( Obj_Patch(
            #offsets = [0x00017F22],
            ref_code = original_call + '24' '01' '83' '6E' '0009' '0F' '0006',
            new_code = replacement,
            ))
        
    if on_frame_input:
        # Edit in Obj_501.PerFrameInput.
        patch_list.append( Obj_Patch(
            #offsets = [0x0001C40C],
            ref_code = original_call + '32' '........' '79' '0006' '0000',
            new_code = replacement,
            ))        
        

    # Apply the patches.    
    Apply_Obj_Patch_Group(patch_list)

    return

