'''
Transforms aimed at finding the problem with excessive game load and
gate traversal (and quit) times when there is a big player complex
somewhere in the galaxy.
'''
'''
See threads:
https://forum.egosoft.com/viewtopic.php?t=399008 (newer)
https://forum.egosoft.com/viewtopic.php?t=387073 (older, benchmark saves)
'''
from ... import File_Manager
from ... import Common
from .Obj_Shared import *

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

    Test result:
        Massive fps slowdown when joining an older 256 stack factory
        to a new one.
        Theory: connectors are responsible for determining which factories
        will not have collision detection with each other. With no
        connections, the factory stack was calculating collision.
        Similar fps drop (and similar amount) was noticed when destroying
        the complex as well, leaving the factories loose but still stacked
        on top of each other.

        Updated theory: SA_CreateFactoryConnections may only
        return key information such as tube subtype and positioning,
        and doesn't create any objects.
        Also, complex based slowdown was later tracked to SA_CleanUpObjects;
        see further below.

        TODO: look into complex Activation code, so that it will update
        factory links even when no tube connections are present, to see
        if this helps.

        TODO: one fps problem is dealt with, try building a large complex
        with this applied and see if there is progressive delay added
        to gate traversal time.
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




@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False, TC = False)
def _Benchmark_Gate_Traversal_Time():
    '''
    Experimental.
    Disable calls to SA_CleanUpObjects or SA_FreeAllBodies when passing gates.
    '''
    '''
    Code to edit is in CLIENT.WarpToSector.
    At 0001666B is the SA_CleanUpObjects call.
    At 00016672 is the SA_FreeAllBodies call.
    A second instance is elsewhere, in CLIENT.QuickWarp, which can also
    be modified.

    Can replace with nops.

    Test results, using 1x256 factory complex:
        - Traversing gate between empty sectors, benchmark default.
        - Baseline: 14 seconds.
            - Note: early hops were 11 seconds; indicates something slows
              down after some game loads.
        - Removing SA_CleanUpObjects: near instant travel.
        - Removing SA_FreeAllBodies:  no change.

    Test results, using 2x256 factory complex:
        - Baseline: 75 seconds.
        - Removing SA_CleanUpObjects: near instant travel.

    Performed a ~1 hour test in XRM on a 10 day old save, flying around
    sectors, fighting, etc., with this applied.
    No oddities were observed; objects were cleaned up just fine, save
    file size was stable, game memory usage appeared the same as without
    this edit (eg. starts at a base of 1.8 GB, climbs up to ~3.5 GB and then
    does some sort of flush back down to ~1.8).

    TODO: get more playtime in with this transform to establish higher
    confidence of stability, and release for general use.

    '''
    remove_SA_CleanUpObjects = True
    remove_SA_FreeAllBodies  = False

    ref_code = [
        # Push 0, call SA_CleanUpObjects, pop.
        '01'
        '82' '00004C33'
        '24'
        # Again for SA_FreeAllBodies.
        '01'
        '82' '00004C45'
        '24'
        ]

    # Fill in new code based on which functions are being replaced.
    new_code = []
    if remove_SA_CleanUpObjects:
        new_code += [
            NOP * 7, # First call
            ]
    else:
        new_code += [
            '..'
            '..' '........'
            '..'
            ]
        
    if remove_SA_FreeAllBodies:
        new_code += [
            NOP * 7, # Second call
            ]
    else:
        new_code += [
            '..'
            '..' '........'
            '..'
            ]

    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0001666C],
            ref_code = ''.join(ref_code),
            new_code = ''.join(new_code),
            expected_matches = 2,
            )
    Apply_Obj_Patch(patch)

    return



