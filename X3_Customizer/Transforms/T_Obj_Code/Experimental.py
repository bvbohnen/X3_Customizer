'''
This will hold experimental obj code transforms, which were found not
to work to satisfaction due to whatever reasons.
'''
from ... import File_Manager
from ... import Common
Settings = Common.Settings
from .Obj_Shared import *


@File_Manager.Transform_Wrapper('L/x3story.obj')
def _Disable_Friendly_Fire():
    '''
    Disables friendly fire between ships with the same owner.
    Experimental; not working in testing.
    '''
    '''
    Code to edit is in SHIP.Hit.

    Relatively early on, a check is made for if the attacker is the same
    owner as the victim.  Normally this skips over some notoriety hit
    code, but could be changed to return instead, skipping the damage
    update.

    The jump can be redirected to the end of the function, which has
    the same stack depth (3).

    Test result: no change in damage application when shooting another
    owned ship.  Suggests this bit of code isn't actually used normally.
    '''
    patch = Obj_Patch(
            #offsets = [0x000C01C0],
            # Code section starting with the jump address to the ship
            #  damage code.
            ref_code =  '000C02E5'
                        '0D' '0001'    
                        '0E' '0008'    
                        '5B'         
                        '34' '000C0211'
                        '01'         
                        '0E' '0008'    
                        '85' '0000298C',
            # Address of a pre-return stack pop.
            new_code = '000C04D0',
            )
    Apply_Obj_Patch(patch)

    return


# Underscore this name; it isn't really for general use due to
#   missing titles.
@File_Manager.Transform_Wrapper('L/x3story.obj')
def _Show_Pirate_Yaki_Nororiety():
    '''
    Adds pirates and yaki to the displayed list of faction notorieties.
    Due to missing text linkages, titles are not currently available and
    only progress to the next rank is shown.
    '''
    '''
    Code to edit is in MENU_PLAYER.SpecialUpdate.

    When races are looped over, they are checked against a 0006023Eh mask.
    This includes the main races, terrans, atf, and goners.
    To add pirates and yaki, switch to 000E033Eh.

    Result:
        Works as far as it goes, but the lack of text titles prevents this
        from being very useful.
        At a glance, there appears to be no way to add in titles, since they
        are seemingly hard coded to certain text pages through a global
        function (not in the KC), where page numbers do not follow any
        exploitable pattern.

        The mod at https://forum.egosoft.com/viewtopic.php?t=307436
        works around this by adding pirates/yaki to the generic mission
        based rankings using the MD, setting up cues that constantly
        copy over pirate/yaki rep to the mission side title for display.
        Such titles are set through an MD command that specifies the
        page text (with a bit of implicit offset based on rank).

        For now, sideline this but leave it here in case any ideas strike.
    '''
    patch = Obj_Patch(
            #offsets = [0x0013DAC6],
            # Code starts off with the pushing the mask.
            ref_code =  '07' '0006023E'
                        '53'
                        '01'
                        '5B'
                        '34' '........'
                        '24'
                        '32' '........',
            # Replace the pushed value.
            new_code = '07' '000E033E',
            )
    Apply_Obj_Patch(patch)

    return


@File_Manager.Transform_Wrapper('L/x3story.obj')
def _Disable_Modified_Tag():
    '''
    Disables the modified tag on a save, allowing for achievements
    to be gained.
    '''
    '''
    Obj_205.IsAuthorized is generally checked as part of the achievement
    unlock progress.  It in turn calls CLIENT.GetModified, preventing
    unlocks on modified games.  CLIENT.GetModified can be edited to
    always return a 0.

    Result:
        Appears to have unwanted side effects.  The SCS mod kept
        opening a glitchy menu (within half second of closing it).
        May have something to do with the script editor unlock,
        which normally sets the modified tag, and may rely on that
        tag to work properly.

    Attempt 2: Selective edits of GetModified call locations.
        Obj_205.IsAuthorized
        - Edit to unlock achievements.
        MENU_PLAYER.SpecialUpdate
        - Edit to remove the modified tag.
        
        The other places it is called are when exporting statistics,
        and when filling out the artificial life plugins menu.
        It is unclear on why either of those would cause a problem
        observed above.
        GetModified may also get called in the executable.

    Result:
        Removal of the "modified" tag was succesful.
        Achievement unlocks didn't appear to work.  The achievement
        menu lists them, and Xenon kills were counting up, though
        attempts to unlock the 2 billion credits one, or destroy
        a solar power plant, did not go through.

        TODO: look into other possible reasons for failure.
        The success with the achievements menu indicates that the
        edited code is being used, at least.
    '''
    #-Failed version that modified CLIENT.GetModified.
    #patch = Obj_Patch(
    #        #offsets = [00014D00],
    #        # Original code enters the function, looks up a modified
    #        #  flag, and returns it.  Following ops then return a 0,
    #        #  though are unreachable normally.
    #        ref_code =  '6E 0001'
    #                    '0F 000E'
    #                    '83     '
    #                    '       '
    #                    '01     '
    #                    '83     '
    #                    # Some extra for matching.
    #                    '6E 0007'
    #                    '02     '
    #                    '16 000E'
    #                    '24     '
    #                    '0F 000E',
    #        # Can just insert nops so that the following return-0 is
    #        #  used instead.
    #        new_code = '.. ....' + NOP*4,
    #        )
    
    patch_list = [
        # Change Obj_205.IsAuthorized.
        Obj_Patch(
            #offsets = [00021F62],
            ref_code =  (
                # This code performs the call, and returns early on a 1.
                # Note: stack is depth 0 here.
                '01         '
                '06 0096    '
                '86 ........'
                '64         '
                '83         '
                # This is the default return-0.
                # Don't want this; want to return 1.
                '01         '
                '83         '
                # Extra for matching.
                '6E 0002    '
                '0D 0004    '
                '02         '
                '82 ........'
                '83         '
                '           '
                '01         '
                '83         '),                        
                        
            # Replace with returning 1, plus nops (optional, since
            #  unreachable).
            new_code = PUSH_1 + RETURN + NOP * 9
            ),

        # Change MENU_PLAYER.SpecialUpdate.
        Obj_Patch(
            #offsets = [0013E1ED],
            ref_code =  (
                # This calls SpecialUpdate and jumps if 0.
                '01         '
                '06 0096    '
                '86 ........'
                '34 ........'
                # Extra match code.
                # This deals with the modified tag, and could potentially
                #  be nop'd (would need some more, though).
                '01         '
                '88 ........'
                '24         '
                '01         '
                '88 ........'
                '34 ........'
                '03         '
                '0F 003E    '
                '06 0081    '
                '0E 0000    '
                '0B ........'),               
                        
            # Swap the call to just pushing a 0 (not modified).
            new_code = (
                PUSH_0
                + NOP * 8
                )
            ),
       ]

    Apply_Obj_Patch_Group(patch_list)

    return