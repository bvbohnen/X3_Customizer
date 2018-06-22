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
    

Note on verification:
    There is some danger of poorly constructed patches not being
    stack neutral. No easy way exists to check this here (without
    building a partial assembly parser to pick out the stack changes
    in replaced code).

    Verification can be done using the disassembler tool and taking
    the diff of the .out files with the original obj file.
    All changed locations should have the same stack count at the
    start and end of their code regions.

    Most recent check was done on: version 3.4.3.
    TODO: maybe set up a tool to autocheck this, perhaps as part
    of the release process.
'''
'''
TODO:
    Asteroid/station respawn time.
    Station tolerance to friendly fire.
      - Can reduce shield threshold before response from ~99% down to
        something lower, like 10% or 0% (require hull damage).

'''
from ... import File_Manager
from ... import Common
from .Obj_Shared import *
    

@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
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


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
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

@File_Manager.Transform_Wrapper('L/x3story.obj')
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
    #            new_code = hex2bin(POP + NOP * 4),
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


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
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
            new_code = NOP * 11,
            )
    Apply_Obj_Patch(patch)

    return


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
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


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
def Remove_Factory_Build_Cutscene(
    ):
    '''
    Removes the cutscene that plays when placing factories by shortening
    the duration to 0.  Also prevents the player ship from being stopped.
    May still have some visible camera shifts for an instant.
    '''
    '''
    Code to edit is in BUILD_FACTORY.Build for factories and 
    BUILD_FACTORY.BuildComplex for complexes.

    These animations appear to set up a rotating camera around the
    build ship then built complex, and then swap to the camera for a duration
    as it turns.

    Can potentially shorten camera duration, or somehow completely skip the
    code block (perhaps leverage code that tests if the player ship is
    in the same sector, to have it always appear False).
    The latter approach will be used where possible.

    Factory/complex intro cutscene:
        - Whole build function returns if the player is not in sector,
          seemingly, so that cannot be easily edited.
        - Edit delays for this one, 2 seconds and 1 second.
        - Both build functions share the same code for this.

    Factory/complex outro cutscene:
        - Again, code is shared.
        - There is a player presense check that skips over much of the
          animation code, but not all.
        - Stick to editing delays.

    Note: the factory code repeats the code section twice, so expecting
    a total of 3 repetitions.


    In addition to the cutscene, the ship-stop code can also be removed.
    This appears to run on both the builder ship and the player ship,
    and code is again shared across both build methods.
    There are two such code sections, where the build ship stop is a little
    further down.
    
    Note: preventing stop of the building ship doesn't seem to work in
    testing. Initial glance at decompiled code looks okay.
    Code logic seems like it might be calling StopCommand twice on
    the builder ship, which indicates neither worked for some reason.
    Looking at SHIP_TL.BuildStation, there is also a stop command there
    which would need to be overwritten. TODO: maybe handle that.

    TODO: maybe also edit the player sector check for factory building,
    to possibly allow builds from outside the sector.

    TODO: make this smoother, getting rid of the camera view shift
    entirely.

    TODO: maybe make speed customizable as a rate factor, so some
    cutscene is left in but sped up.
    '''
    patch_list = [
        # Factory and complex intro, shared code template.
        Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001B019, 0x0001BB91],
            # 06 01F4 is first fade time (500 ms)
            # 06 07D0 is the first delay (2000 ms)
            # 06 03E8 is second fade time (1000 ms)
            # 06 03E8 is second delay (1000 ms)
            ref_code =  '06' '01F4' '01' '03' '06' '0096' '86' '........'
                        '24' '06' '07D0' '02' '82' '........' '24' '06' '03E8'
                        '07' '........' '03' '06' '0096' '86' '........'
                        '24' '06' '03E8',
            # Reduce all apparent delay times.
            # Try 0 for now.
            # TODO: maybe keep a little animation.
            new_code =  '..' '0000' '..' '..' '..' '....' '..' '........'
                        '..' '..' '0000' '..' '..' '........' '..' '..' '0000'
                        '..' '........' '..' '..' '....' '..' '........'
                        '..' '..' '0000',
            expected_matches = 3,
            ),
        
        # Complex outro.
        Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001BDEB, 0x0001BE5F],
            # 06 03E8 is first fade time (1000 ms)
            # 06 0FA0 is the first delay (4000 ms)
            # 06 03E8 is second fade time (1000 ms)
            # 06 03E8 is second delay (1000 ms)
            ref_code =  '06' '03E8' '01' '03' '06' '0096' '86' '........'
                        '24' '06' '0FA0' '02' '82' '........' '24' '06' '03E8'
                        '07' '........' '03' '06' '0096' '86' '........'
                        '24' '06' '03E8',
            # Reduce all apparent delay times.
            # Try 0 for now.
            # TODO: maybe keep a little animation.
            new_code =  '..' '0000' '..' '..' '..' '....' '..' '........'
                        '..' '..' '0000' '..' '..' '........' '..' '..' '0000'
                        '..' '........' '..' '..' '....' '..' '........'
                        '..' '..' '0000',
            expected_matches = 3,
            ),

        # Outros also have a followup 500 ms fade.
        Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001B26A],
            # 06 03E8 is fade time (1000 ms)
            ref_code =  '06' '03E8' '01' '03' '06' '0096' '86' '........'
                        '24' '01' '02' '06' '01F4' '86' '........' '24' '02',
            # Reduce all apparent delay times.
            # Try 0 for now.
            # TODO: maybe keep a little animation.
            new_code =  '..' '0000',
            expected_matches = 3,
            ),

        # Ship stop logic.
        # Replace these with nops.
        Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001AE52],
            # The ........ fields will call, in order:
            #  SA_SetDesiredSpeed
            #  SA_SetSpeed
            #  StopCommand
            #  GetObjectID
            #  SA_SetDesiredSpeed
            #  SA_SetSpeed
            # The GetObjectID bit needs to be kept, since that stack value
            #  gets used later.
            ref_code =  '01' '0D' '0002' '03' '82' '........' '24' 
                        '01' '0D' '0002' '03' '82' '........' '24' 
                        '01' '0D' '0010' '85' '........' '24' 
                        # GetObjectID; keep this (note that it doesn't get
                        #  its response popped at the end).
                        '01' '0D' '0010' '85' '........'
                        '01' '0D' '0002' '03' '82' '........' '24'
                        '01' '0D' '0002' '03' '82' '........' '24',
            # Can replace this with two chunks of nops around the
            #  GetObjectID section.
            # Check after patch to verify nop count in edited section.
            new_code = ( NOP * (11+11+10) 
                        + '..' '..' '....' '..' '........'
                        + NOP * (11+11) 
                        ),
            expected_matches = 2,
            ),
        
        # Extra stop command further down for the builder.
        # The code for this diverges in stack pointers, and the surrounding
        #  code diverges too much for simple wildcards to match the
        #  desired locations and nowhere else, so use two patches.
        Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001AF74],
            # This does an SE_ObjectExists check and then a StopCommand.
            # Replace the StopCommand with nops, as above.
            ref_code =  '0D' '0015' '02' '82' '........' '34' '........'
                        # Replace this chunk.
                        '01' '0D' '0016' '85' '........' '24'
                        '0D' '0004' '0D' '0004' '10' '16',
            new_code = ('..' '....' '..' '..' '........' '..' '........'
                        + NOP * 10 ),
            ),
        Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001BAF8],
            # Slightly different version of above.
            ref_code =  '0D' '0011' '02' '82' '........' '34' '........'
                        # Replace this chunk.
                        '01' '0D' '0012' '85' '........' '24'
                        '06' '18A6' '16' '0001' '24' '02',
            new_code = ('..' '....' '..' '..' '........' '..' '........'
                        + NOP * 10 ),
            ),
        ]
    # Apply the patches.
    for patch in patch_list:
        Apply_Obj_Patch(patch)
    return


@File_Manager.Transform_Wrapper('L/x3story.obj')
def Keep_TLs_Hired_When_Empty():
    '''
    When a hired TL places its last station, it will remain hired until
    the player explicitly releases it instead of being automatically dehired.
    '''
    '''
    Code to edit is in SHIP_TL.BuildStation, near the bottom:
           pop
           push       0
           call88     SHIP_TL.GetNumWareStation
           push       0
           if SP[0]<>SP[1] then push 0 else push 1
           if SP[0]=0 then jump L000DAA94
           push       0
           push       1
           call88     SHIP.SetHired
           pop
    Can either replace the call with nops, or tweak the arg from 0 to 1.
    Both should work okay.  Nops might be safer in case there are
    side effects to setting a hired ship to hired again.
    '''
    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x000DAA8C],
            # Only this first bit is the SetHired call, with args and
            #  return pop.
            ref_code =  '01' '02' '88' '........' '24' 
                        '24' '70' '02' '14' '0003' '23' '0002' '83',
            # Swap to nops.
            new_code = NOP * 8,
            )
    Apply_Obj_Patch(patch)

    return


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
def _Prevent_Complex_Connectors():
    '''
    Experimental; avoid use for now (big frame hit on complexes).
    Prevents code which generates complex connectors, the tubes between
    factories.  Where normal tube removal mods simply drop a blank model
    for the tube (avoiding graphics and collision overhead), this will
    prevent computation and creation of the tube objects themselves
    in the underlying code.  Only applies when a new complex is formed.
    '''
    '''
    Code to edit is in Obj_2044.CreateConnections.
    Full analysis not given here, but in summary:
        - Obj_2044.var_2044_1 is where connectors are stored.
        - A call to SA_CreateFactoryConnections on complex creation will
          take the complex and factory list, and returns connector
          information that is used to populate Obj_2044.var_2044_1.
        - Tubes are created from this information.
        - By cutting out the SA_CreateFactoryConnections call and allowing
          code to continue with a blank connectors list, the tube
          overhead should be completely removed.

    Note: this transform is explored as a possible way to address
    massive game slowdown for large complexes, on the assumption there
    is a problem in the SA_CreateFactoryConnections call generating
    excess overhead the lasts after the call return.

    Code section of interest, around 000A2323:

        L000A2323: push       SP[1] ; loc2
                   push       1
                   callasm    SE_ArraySize
                   if SP[0]=0 then jump L000A2342
                   push       SP[1] ; loc2
                   read       GBODY.var_1000_3 ; [3]
                   push       2
                   callasm    SA_CreateFactoryConnections
                   jump       L000A2345

        L000A2342: create_array   0
        L000A2345: push       SP[0] ; loc4
                   if SP[0]=0 then push 1 else push 0
                   if SP[0]=0 then jump L000A2356
                   push       0
                   mov        SP[4],SP[0] ; loc1
                   popx       4
                   ret

    Aim is to skip SA_CreateFactoryConnections, and also to skip the
    code which returns early when no connectors exist (since this
    function has a bunch of other work to do in setting up factories,
    and this return point seems to just be error handling).

    1)  Replace the early nodes with nops and a 'push 1' and 'if SP[0]=0...',
        so that jump is always taken to L000A2342 to create a blank array.
        Note: apparently, cannot just 'push 0' into the conditional branch
        else things bugger up, so use the comparison in between (maybe
        converts to a bool type that acts specially?).
    2)  Change 'push SP[0]' to instead be 'push 1', so
        that the array looks populated and the return is skipped.

    So code will look like (with nops pruned):
    
        L000A2323: push       1
                   if SP[0]=0 then push 1 else push 0
                   if SP[0]=0 then jump L000A2342
                   push       SP[1] ; loc2
                   read       GBODY.var_1000_3 ; [3]
                   push       2
                   callasm    SA_CreateFactoryConnections
                   jump       L000A2345

        L000A2342: create_array   0
        L000A2345: push       1
                   if SP[0]=0 then push 1 else push 0
                   if SP[0]=0 then jump L000A2356
                   push       0
                   mov        SP[4],SP[0] ; loc1
                   popx       4
                   ret

    '''
    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x000A2323],
            ref_code =  '0D' '0002' '02' '82' '........'
                        '34' '........' '0D' '0002' '0F' '0003' '03'
                        '82' '........' '32' '........' '28' '0000'
                        '0D' '0001'
                        '64' '34' '........' '01' '14' '0005' '23' '0004' '83'
                        ,
            # First part swaps to nops, push 1, compare to 0.
            # Swap line 4 to a push 0 with nops.
            new_code =  NOP*7 + PUSH_1 + '64'
                        '..' '........' '..' '....' '..' '....' '..'
                        '..' '........' '..' '........' '..' '....'
                        + NOP*2 + PUSH_1 +
                        '..' '..' '........' '..' '..' '....' '..' '....' '..'
            )
    Apply_Obj_Patch(patch)

    return

