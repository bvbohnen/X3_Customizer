from ... import File_Manager
from ... import Common
Settings = Common.Settings
from .Obj_Shared import *

@File_Manager.Transform_Wrapper('L/x3story.obj')
def Disable_Combat_Music(
    ):
    '''
    Turns off combat music, keeping the normal environment music playing
    when nearing hostile objects. If applied to a saved game already in
    combat mode, combat music may continue to play for a moment.
    The beep on nearing an enemy will still be played.
    '''
    '''
    This will edit the CLIENT.NotifyAlert function.
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

        It is unclear at a glance what this is meant to accomplish,
        though it may simply be a situation where LU adds class variables,
        changing the offsets of cl_Alert and CLIENT.cl_Killed, but the
        disassembler is providing names based on the vanilla game.

        If the underlying functionality is the same just with adjusted
        offsets, this patch should work okay, but the reference code
        needs to wildcard the offsets.  (In testing, this seems to
        work fine.)
    '''

    patch = Obj_Patch(
            #offsets = [0x00017895],
            # Existing code is 
            # 'if SP[0]=0 then jump L000178A9'
            # 'push       1'
            # 'write      CLIENT.cl_Alert'
            ref_code =  '34' '........' '02' '16' '....' '24' '01' 
                        '06' '00C8' '86' '........' '24' '32',
            # Switch to 'if SP[0] != 0' and 'push 0'.
            new_code = '33' '........' '01',
            )
    Apply_Obj_Patch(patch)

    return


@File_Manager.Transform_Wrapper('L/x3story.obj')
def Disable_Docking_Music():
    '''
    Prevents docking music from playing when the player manually requests
    docking.
    '''
    '''
    Code to edit is in CLIENT.DockingAllowed, where music track 14 is
    called.
    
    Can convert the code section to nops:
           pushb      14d ; 0Eh
           push       1
           pushw      200d ; 0C8h
           call86     X_AUDIO.ChangeTrackMusic
           pop
    '''
    patch = Obj_Patch(
            #offsets = [0x000172AE],
            ref_code =  '05' '0E'
                        '02'
                        '06' '00C8'
                        '86' '........'
                        '24'
                        '6F'
                        '33' '........'
                        '02'
                        '06' '0503'
                        '05' '0D'
                        '28' '0002'
                        '03'
                        '06' '00C8',
            # Swap to 12 nops.
            new_code = NOP * 12,
            )
    Apply_Obj_Patch(patch)

    return
