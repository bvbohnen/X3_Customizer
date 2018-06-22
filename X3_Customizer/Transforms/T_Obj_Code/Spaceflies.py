'''
Edits aimed at dealing with excessive spacefly counts.
'''
'''
Motivating example:
    10 day old XRM game, 134 factories, 200 ships.
    15k scripts active, 3.7k of them spaceflies (241 idle, rest followers).
    Testing seta speedup in Harmony of Perpetuity:
		With spacefly scripts running:
			1 real minute : 5 game minutes
			2 real minutes: 9 game minutes
		With spacefly scripts killed off (5000% seta limit):
			1 real minute : 28 game minutes
			2 real minutes: 59 game minutes
		6.5x speedup with dead spaceflies.
'''

'''
Relevent forum thread:
https://forum.egosoft.com/viewtopic.php?t=398200

A lot of thought was put into how to do this, but in short, the existing
spacefly scripts are cached and spaceflies themselves are recorded
as special object in the null sector (typically), and so cannot
be killed directly by other scripts nor by edits to the base
spacefly scripts.

To kill them, the "is disabled" script command will be edited,
relying on this only being called inside the spacefly script.
The command will either Return (to end the script) or kill
the spacefly, or some mixture of those.

Unfortunately, this approach will be obj file specific, since
it involves editing pointers instead of logic.


Option 1)

    Some background:
        Each script command is encoded to an integer opcode, which
        matches those in the t file on page 2003.

        In the script handling part of the obj code, there is a
        large jump table which uses the opcode to determine which
        code section to jump to for executing the command.

        By editing this table, one command can be redirected to
        the handler code for another command.

        All commands appear to enter and exit at the same stack depth,
        so the main issue in swapping between commands would be that
        they might assume different formats/sizes of the commands
        attached codearray (which holds the target, args, return value).

    The Return command returns the %0 item; while IsDisabled operates
    on %0 (target object) and %1 (return value or branch code).
    So, redirecting to Return is expected to return [THIS], which hopefully
    won't matter if nothing uses the return value.

    This will be based on AP 1.03 for now.
    If succesful, maybe an LU version can be added.

    Test result:
        Idle spacefly scripts stops, Follow scripts kept running,
        since those appear to be stuck on an Escort command.
    
Option 2)
    Maybe less safe approach: replace with Destruct.
    This should hopefully work.
    IsDisabled has args:
        %0 : [THIS]
        %1 : some branch code
    Destruct takes args
        %0 : target (This is desired here).
        %1 : show explosion (if comparison to 1, may be okay if this
                            checks the branch code)

    Test result:
        Spaceflies died, but savegame list got corrupted, indicating
        there are probably more errors.
            
Option 3)
    Edit the IsDisabled command to internally call SelfDestruct and
    follow up with something safe.
    This requires a lot of manual code and careful stack management,
    but is potentially doable.

    The SelfDestruct call will be taken from SECTOR.Deactivate when
    removing spaceflies (same reason code and such).

    If the begin_critical section fails, this should be failsafe,
    so that case will redirect to the IsDocked command handler,
    which has the same args and return value as IsDisabled and
    should hopefully be compatible (both fill stack 17,18,19).

    The above code uses up all available space, so the explicit
    Return will be left out, relying on the dead spacefly to
    kill off the script.  This means the SelfDestruct will
    always be followed by IsDocked.

    Note: adding a spacefly class type check would add ~17 bytes,
    maybe more, so that would be tough to fit.

    Test result:
        Behaves the same as (2); problem may specifically be with
        a script killing its owner.  A forum response suggests
        others have had the same problem.

Option 4)
    As (3), but skip the IsDocked and just do a return.
    Other code that destructs ships doesn't seem to care if the
    critical section does not execute, so maybe this patch shouldn't
    care either.

    Test result:
        As before, dead spaceflies but bad savegame list.
            
Option 5)
    On the theory that IsDisabled is being called somehow from
    elsewhere, perhaps some bit of assembly manually building
    script commands and running them, and that it is being
    used to look at Quests which also have an IsDisabled method,
    the script code will need to be left alone.

    Edit the SHIP.IsDisabled command to call JumpOutOfExistence,
    which wraps SelfDestruct and takes no args (small footprint).
    The SelfDestruct call, with args and critical section, is too
    large to fit.
        
    Test result:
        As before, dead spaceflies but bad savegame list.
        Indicates the problem is not a Quest.IsDisabled call or
        something like that, but specific to ships.

Option 6)
    Similar to 3-4, but include a class id check to verify a spacefly
    before using JumpOutOfExistence (to save on bytes). Aim to fill
    in with IsDocked or similar again when not dealing with spaceflies.
        
    Test result:
        As before, dead spaceflies but bad savegame list.
        Indicates the problem must be with deleting spaceflies, somehow,
        unless IsDocked redirection is a problem.

Update:
    On the assumption the patches are fine and something external
    is going wrong, the spacefly problem was tracked down to
    both Improved Races 2.0 and XRM generating the lingering
    spaceflies when a game is loaded (accumulating them across
    saves/loads).

    The bad-saves-list problem was not observed in a game without
    these mods installed.

    These mods appear to sometimes generate a ship (striding through
    tships), pull some data, then destroy the ship.
    However, create_ship for a spacefly will also spawn a swarm,
    which is not getting destroyed.

Option 7)
    Modification on (6) that will instead assume a spacefly
    target (like 3-4), keep the short code of JumpOutOfExistence,
    and add on a delay to the kill.

    Around a ~10 second delay should be enough (hopefully) for
    any other scripts to spawn a spacefly, collect information on
    it, and destroy it themselves.
        
    Test result:
        Success!
        Spaceflies take a little longer to die, but the delay avoids
        a mod messing up the save game list.


Note on LU:
    The spacefly killing patch is heavily dependent on call addresses,
    so will not be portable as-is.

    The swarm suppression patch further below should work okay.
'''


from ... import File_Manager
from ... import Common
from .Obj_Shared import *

@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False)
def Kill_Spaceflies():
    '''
    Kills active spaceflies by changing their "is disabled" script
    command to make them self destruct .
    Intended for use with games that have accumulated many stale
    spacefly swarms generated by Improved Races 2.0 or XRM
    or other mods, which add spacefly swarms each time a game is
    loaded, causing accumulating slowdown (eg. 85% SETA slowdown after
    200 loads).
    Use Prevent_Accidental_Spacefly_Swarms to stop future spacefly
    accumulation, and this transform to clean out existing spaceflies.

    Deaths are delayed by 10 seconds so that mods generating and
    killing the spaceflies have time to record their information.
    It may take a minute for accumulated spaceflies to die.
    Progress can be checked in the script editor by watching the
    active spacefly script counts.
    '''
    # 1,2,3,4,5,6 have issues with the problematic mods.
    # Testing 7.
    option = 7

    if option in [1,2]:
        patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x000777B5],
            # Give the original IsDisabled handler, and a few following ones.
            ref_code =  '0004EFF2'
                        '0004F091'
                        '0004F1B1'
                        '00076D54'
                        '00076D54',
            new_code = (
                # Retarget to the Return handler. Option 1.
                '00039599' if option == 1
                # Retarget to the Destruct handler. Option 2.
                else '0004F25C'
                ),          
            )
    
    elif option in [3,4]:
        # Note: code bits broken out of the patch definition due to a VS
        #  lockup bug when mousing over it (cannot deal with 50+ line
        #  arg lists when making its annoying popup?).

        # This code starts the section in IsDisabled right after
        #  reading the input args (a spacefly target in the desired
        #  case, but maybe not always).
        # The code does some pushes onto the deeper stack to capture
        #  the return arg.
        ref_code = (
                    # Push something to the deeper stack.
                    '14' '0006'
                    '24'         
                    '05' '04'
                    # Push something to the deeper stack.
                    '14' '0005'    
                    '24'         
                    '01'         
                    '0D' '0002'
                    # IsDisabled call.
                    '85' '00007143'
                    # Push IsDisabled flag to the deeper stack.
                    '14' '0004'
                    '24'         
                    '23' '0002'
                    '32' '000785F1'
                    )

        new_code = [
            # At this point, the stack is 22 deep.
            # 19 of the items are from IsDisabled entry, which means
            #  3 were generated locally.
            # These 3 appear to be:
            #  SP[2]: loc20 : global.TGlobal_48 or something similar ?
            #  SP[1]: loc21 : spacefly target ?
            #  SP[0]: loc22 : ?
        
            # Match format for SelfDestruct calls commonly used,
            #  that wraps the call in a critical section, skipping to
            #  after the call if the begin_critical returned a non-0.
            begin_critical,
        
            # Be careful with this value, to retarget to after the
            #  return call. (Verify this after patching.)
            '33' '0004F086',
        
            # Call to SelfDestruct.
            # This will feed args (16,0) for (reason?, killer), which
            #  matches the SelfDestruct call used in SECTOR.Deactivate
            #  when removing spaceflies.
            PUSH_0,
            '05' '10',
            PUSH_2,
        
            # Push a stack item, the spacefly target.
            # At this point, it should be at SP[4], which is encoded
            #  at offset+1 in this Push command.
            # TODO: look at this; first test has idle spaceflies
            #  stop, but they don't seem to get destroyed, with follower
            #  scripts still alive.
            '0D' '0005',
        
            # Call SelfDestruct (should pick out the spacefly version
            #  from the target type).
            # This consumes 4 stack items, returns 1 item (a 0).
            '85' '00004EF4',
            # Pop the return arg to standardize stack.
            POP,
            # End critical section.
            end_critical,
            
        
            # Jump the is_critical check to here on failure.
        
            # Pop items off the stack and call IsDocked to fill in the
            #  expected return args (at stack 17-19).
            # Alternatively, call Return directly.
            # Stack is now 22 deep.
            '23' '0003',
            # Pick just one of these.
            '32',
            ('00038982' if option == 3 # IsDocked, option 3
                else '00039599' # Return, option 4
                ),                   
            
            # Code after this point can be ignored, as it should be
            #  unreachable, though for explicitness it will be
            #  replaced with nops.
            # 31 old bytes, ~28 new bytes, -2 nops.
            NOP * 3,
        ]    
        new_code = ''.join(new_code)

        patch = Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x0004F072],
                ref_code = ref_code,
                new_code = new_code,
                )
            

    elif option == 5:
        # Edit SHIP.IsDisabled.

        ref_code = (
            # This will replace the code right after the 'enter' node.
            # Note: the 'enter' command indicates 0 args, but a max
            #  stack of 2 (watch out for this).
            '6E' '0002'
            # This reads SHIP.var_2004_0, masks by 0x0400, and returns
            #  1 if that bit is set, else 0.
            # Note: this returns twice, perhaps with a default 'ret 0'
            #  placed at the end of all methods that don't have that,
            #  which gives a couple extra bytes to play with.
            '0F' '000C'
            '06' '0400'
            '53'
            '01'
            '5A'
            '83'
            # Can leave the dummy return in place for now, since these
            #  bytes aren't needed.
            #'01'
            #'83' 
            )

        new_code = [
            # Keep the max stack at 2 for now.
            '6E' '0002',
            # There is not enough room to put in a spacefly class code
            #  check, so just go straight to the JumpOutOfExistence
            #  call. This will take 1 input, the number of args (0).
            PUSH_0,
            # Unsure on call type, but call87 makes the disassembler
            #  happy, while call88 does not.
            CALL87 + '0000B2AA',
            # Can probably return its value directly, but be consistent
            #  with the normal form and pop the result, then push 0.
            POP,
            PUSH_0,
            RETURN,
            ]
        new_code = ''.join(new_code)

        # Fill in with nops.
        # Can get count by string length difference, 1 nop per 2 chars.
        nop_count = (len(ref_code) - len(new_code)) // 2
        assert nop_count >= 0
        new_code += NOP * nop_count

        patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x000AE85F],
            ref_code =  ref_code,
            new_code =  new_code,         
            )

        
    elif option in [6]:
        # Some of this is similar to 3-4, but with scattered edits.

        # Unlike 3-4, this will start a little earlier, at the
        #  point where various arg read paths join up, just before
        #  the code does an array lookup.
        # On rereading, that code chunk can probably be dropped.
        ref_code = (
            # Do an array lookup, getting loc16[3].
            '04'
            '0D' '0007'
            '10'
            # Push loc16[3] to loc17.
            '14' '0006'
            '24'
            # Push value 4 to the deeper stack, loc18.
            '05' '04'
            '14' '0005'                    
            '24'
            # Call IsDisabled, 0 args, on loc21 as target object.
            '01'
            '0D' '0002'
            '85' '00007143'
            # Push IsDisabled flag to the deeper stack, loc19.
            '14' '0004'
            # Pops and jump to post-command code.
            '24'         
            '23' '0002'
            '32' '000785F1'
            )
        # The ref_code has 36 bytes freed up.
        
        # This will switch to calling JumpOutOfExistence for a shorter
        #  code setion, and use the saved bytes to do a spacefly
        #  class code check. When not a spacefly, call IsDocked.
        new_code = [
            # At this point, the stack is 21 deep.
            # 19 of the items are from IsDisabled entry, which means
            #  2 were generated locally.
            # These 2 appear to be:
            #  SP[1]: loc20 : global.TGlobal_48 or something similar ?
            #  SP[0]: loc21 : spacefly (or ship) target

            # Push the spacefly class code, 2070.
            PUSHW + '0816',
            # Push the spacefly target object, SP[1].
            PUSH + '0002',
            # Do a call to SE_IsClass with 2 args.
            PUSH_2,
            CALLASM + '00000228',
            # Do a conditional jump if != 1 (mismatch), to the
            #  non-spacefly code a bit below.
            JUMP_IF_0 + '0004F088',

            # Stack is at 21 again.
            # Call JumpOutOfExistence on the spacefly.
            # 0 args.
            PUSH_0,
            # Spacefly target, SP[1].
            PUSH + '0002',
            CALL85 + '0000B2AA',
            # Pop result.
            POP,

            # 27 bytes used so far.

            # Earlier jump should go to here.
            # Pop items off the stack and call IsDocked to fill in the
            #  expected return values (at stack 17-19).
            # TODO: maybe manually fill return values if figuring out
            #  what should be in loc17 with dummies, if there is enough
            #  room (stack pushes cost 3 bytes each, plus need to load
            #  the values).
            # Stack is 21 here. Pop 2.
            '23' '0002',
            '32' '00038982',

            # Should have 1 byte left over.
            ]
        new_code = ''.join(new_code)
        # Fill in with nops.
        # Can get count by string length difference, 1 nop per 2 chars.
        nop_count = (len(ref_code) - len(new_code)) // 2
        assert nop_count >= 0
        assert nop_count == 1
        new_code += NOP * nop_count

        patch = Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x0004F06D],
                ref_code = ref_code,
                new_code = new_code,
                )
        


    elif option in [7]:
        # Similar to 6, but removing spacefly check to instead put
        #  in a kill delay.

        ref_code = (
            # Do an array lookup, getting loc16[3].
            '04'
            '0D' '0007'
            '10'
            # Push loc16[3] to loc17.
            '14' '0006'
            '24'
            # Push value 4 to the deeper stack, loc18.
            '05' '04'
            '14' '0005'                    
            '24'
            # Call IsDisabled, 0 args, on loc21 as target object.
            '01'
            '0D' '0002'
            '85' '00007143'
            # Push IsDisabled flag to the deeper stack, loc19.
            '14' '0004'
            # Pops and jump to post-command code.
            '24'         
            '23' '0002'
            '32' '000785F1'
            )
        # The ref_code has 36 bytes freed up.
        

        # This will switch to calling JumpOutOfExistence for a shorter
        #  code setion.
        # Assumes a spacefly is given, but still uses IsDocked for
        #  good form.
        new_code = [
            # At this point, the stack is 21 deep.
            # 19 of the items are from IsDisabled entry, which means
            #  2 were generated locally.
            # These 2 appear to be:
            #  SP[1]: loc20 : global.TGlobal_48 or something similar ?
            #  SP[0]: loc21 : spacefly (or ship) target

            # Add a delay.
            # This calls TI_Delay with 1 arg, time in milliseconds.
            # Aim for 10000 ms (10 s).
            PUSHW + '2710',
            PUSH_1,
            CALLASM + '00002A99',
            POP,

            # Call JumpOutOfExistence on the spacefly.
            # 0 args.
            PUSH_0,
            # Spacefly target, SP[1].
            PUSH + '0002',
            CALL85 + '0000B2AA',
            # Pop result.
            POP,

            # 20 bytes used so far.

            # Earlier jump should go to here.
            # Pop items off the stack and call IsDocked to fill in the
            #  expected return values (at stack 17-19).
            # TODO: maybe manually fill return values if figuring out
            #  what should be in loc17 with dummies, if there is enough
            #  room (stack pushes cost 3 bytes each, plus need to load
            #  the values).
            # Stack is 21 here. Pop 2.
            '23' '0002',
            '32' '00038982',

            # Should have 8 bytes left over.
            ]
        new_code = ''.join(new_code)

        # Fill in with nops.
        # Can get count by string length difference, 1 nop per 2 chars.
        nop_count = (len(ref_code) - len(new_code)) // 2
        assert nop_count >= 0
        assert nop_count == 8
        new_code += NOP * nop_count

        patch = Obj_Patch(
                file = 'L/x3story.obj',
                #offsets = [0x0004F06D],
                ref_code = ref_code,
                new_code = new_code,
                )

    Apply_Obj_Patch(patch)

    return



@File_Manager.Transform_Wrapper('L/x3story.obj')
def Prevent_Accidental_Spacefly_Swarms(
    ):
    '''
    Prevents spaceflies from spawning swarms when created by a
    script using the 'create ship' command.
    Aimed at mods such as Improved Races 2.0 and XRM which create
    all ships, record data, and then destroy the ships, leaving
    behind the spacefly swarm, with swarms accumulating across
    game loads and slowing the game down.
    '''

    '''
    To carry this out, the script command code for 'create ship'
    will be edited. This code internally has a jump table based on
    the class id of the ship created, with a special section for
    spaceflies.

    The spacefly section is a short block at 0004AE74 which will
    call SPACEFLY.CreateSwarm instead of SPACEFLY.Create.

    The edit will be to redirect to SPACEFLY.Create, which appears
    to have the same call signature (args [x,y,z,environment], returns
    self).

    Note on LU:
        This appears to have the exact same code, and its Create
        method is at the same lookup offset in the str file, so
        this patch should work on LU just fine with enough of
        a pattern to match.
    '''

    patch = Obj_Patch(
            file = 'L/x3story.obj',
            #offsets = [0x0004AE92],
            # TODO: extend this to not need exact addresses, maybe.
            ref_code =  '85' '........'
                        '14' '0002'
                        '24'
                        '32' '........'
                        '0D' '000C'
                        '0D' '0004'
                        '0D' '0006'
                        '06' '01F4'
                        '50'
                        '0D' '0009'
                        '06' '01F4'
                        ,
            # Replace just the call.
            new_code = '85' '00000081'
            )
    Apply_Obj_Patch(patch)

    return
