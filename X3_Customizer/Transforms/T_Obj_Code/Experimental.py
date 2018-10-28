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

