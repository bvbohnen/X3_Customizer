'''
Add new or modified scripts.

This module will include a shared Add_Script transform, and some
convenience transforms for select scripts.
Modified scripts will tend to be handled with patches, while original
scripts will just be moved to the scripts folder.

TODO: quiet xrm bounty messages.
'''
from .. import File_Manager
from ..File_Manager.File_Patcher import *

#TODO: script to switch drone factories to using the food of their
# race, instead of all using split food. Same for satellites and
# majaglit.


@File_Manager.Transform_Wrapper('scripts/!fight.war.protectsector.xml', 
                                LU = False, TC = False)
def Disable_OOS_War_Sector_Spawns(
    ):
    '''
    Disables spawning of dedicated ships in the AP war sectors which attack
    player assets when the player is out-of-sector. By default, these ships
    scale up with player assets, and immediately respawn upon being killed.
    This patches '!fight.war.protectsector'.
    '''
    Apply_Patch('scripts/!fight.war.protectsector.xml')

    
@File_Manager.Transform_Wrapper('scripts/plugin.com.agent.main.xml', 
                                LU = False, TC = False)
def Allow_CAG_Apprentices_To_Sell(
    ):
    '''
    Allows Commercial Agents to sell factory products at pilot
    rank 0. May require CAG restart to take effect.
    '''
    Apply_Patch('scripts/plugin.com.agent.main.xml')
    
    
@File_Manager.Transform_Wrapper('scripts/!plugin.acp.fight.attack.object.xml', 
                                LU = False, TC = False)
def Fix_OOS_Laser_Missile_Conflict(
    ):
    '''
    Allows OOS combat to include both missile and laser fire
    in the same attack round. In vanilla AP, a ship firing a 
    missile will not fire its lasers for a full round, generally 
    causing a large drop in damage output.
    With the change, adding missiles to OOS ships should not hurt
    their performance.
    '''
    Apply_Patch('scripts/!plugin.acp.fight.attack.object.xml')
    

@File_Manager.Transform_Wrapper('scripts/!lib.fleet.shipsfortarget.xml', 
                                LU = False, TC = False)
def Fleet_Interceptor_Bug_Fix(
    ):
    '''
    Apply bug fixes to the Fleet logic for selecting ships to launch
    at enemies. A mispelling of 'interecept' causes M6 ships to be
    launched against enemy M8s instead of interceptors.
    Patches !lib.fleet.shipsfortarget.xml.
    '''
    # Fix bug in !lib.fleet.shipsfortarget.pck at line 12, mispelled intercept,
    # which does not have matching mispell in !lib.fleet.getship.role.pck,
    # with the effect that enemy bombers should have an interceptor sent
    # at them, but will actually have a corvette sent.
    Apply_Patch('scripts/!lib.fleet.shipsfortarget.xml')


@File_Manager.Transform_Wrapper('scripts/!move.follow.template.xml', 
                                LU = False, TC = False)
def Increase_Escort_Engagement_Range(
    small_range  = 3000,
    medium_range = 4000,
    long_range   = 7000,
    ):
    '''
    Increases the distance at which escort ships will break and
    attack a target. In vanilla AP an enemy must be within 3km
    of the escort ship. This transform will give custom values 
    based on the size of the escorted ship, small, medium (m6), 
    or large (m7+).
    
    * small_range:
      - Int, distance in meters when the escorted ship is not 
        classified as a Big Ship or Huge Ship.
        Default 3000.
    * medium_range:
      - Int, distance in meters when the escorted ship is classified
        as a Big Ship but not a Huge Ship, eg. m6.
        Default 4000.
    * long_range:
      - Int, distance in meters when the escorted ship is classified
        as a Huge Ship, eg. m7 and larger.
        Default 7000.
    '''
    # Start by applying the patch.
    # This will fill in these default values, which should be
    # unique in the whole script:
    # small_range  = 3011
    # medium_range = 4011
    # long_range   = 7011
    Apply_Patch('scripts/!move.follow.template.xml')

    # Can now grab the T file and do a replacement in its text.
    source_file = File_Manager.Load_File('scripts/!move.follow.template.xml', 
                              return_game_file = True)
    source_file.Update_From_Text(source_file.Get_Text()
            .replace('3011', str(small_range))
            .replace('4011', str(medium_range))
            .replace('7011', str(long_range)))
    

# TODO: check if these script copies work okay in TC.
@File_Manager.Transform_Wrapper()
def Convert_Attack_To_Attack_Nearest():
    '''
    Modifies the Attack command when used on an owned asset to instead
    enact Attack Nearest. In vanilla AP, such attack commands are quietly
    ignored. Intended for use when commanding groups, where Attack is 
    available but Attack Nearest is not.
    This replaces '!ship.cmd.attack.std'.
    '''
    File_Manager.Copy_File(
        'scripts/!ship.cmd.attack.std.xml')

    
@File_Manager.Transform_Wrapper()
def Add_CLS_Software_To_More_Docks():
    '''
    Adds Commodity Logistics Software, internal and external, to all
    equipment docks which stock Trade Command Software Mk2.
    This is implemented as a setup script which runs on the game
    loading. Once applied, this transform may be disabled to remove
    the script run time. This change is not easily reversable.
    '''
    File_Manager.Copy_File(
        'scripts/setup.x3customizer.add.cls.to.docks.xml')

        
    
@File_Manager.Transform_Wrapper('scripts/plugin.gz.CmpClean.Main.xml', LU = False)
def Complex_Cleaner_Bug_Fix(
        # Note: no cleanup needed, since the unmodified script should
        # be present in the source_folder and it will just be moved
        # back to the scripts folder unchanged.
    ):
    '''
    Apply bug fixes to the Complex Cleaner mod. Designed for version
    4.09 of that mod. Includes a fix for mistargetted a wrong hub
    in systems with multiple hubs, and a fix for some factories
    getting ignored when crunching.
    Patches plugin.gz.CmpClean.Main.xml.
    '''
    Apply_Patch('scripts/plugin.gz.CmpClean.Main.xml', reformat_xml = True)

    
    
@File_Manager.Transform_Wrapper('scripts/plugin.gz.CmpClean.crunch.xml', LU = False)
def Complex_Cleaner_Use_Small_Cube(
        # Note: no cleanup needed, as above.
    ):
    '''
    Forces the Complex Cleaner to use the smaller cube model always
    when combining factories.
    Patches plugin.gz.CmpClean.crunch.xml.
    '''
    Apply_Patch('scripts/plugin.gz.CmpClean.crunch.xml', reformat_xml = True)
        

#-Removed; mission director used instead of standalone script.
#@File_Manager.Transform_Wrapper()
#def _Include_Script_To_Update_Ship_Variants():
#    '''
#    Adds the 'x3customizer.add.variants.to.shipyards' script to the
#    game, which will update shipyards with any added or removed
#    variants after calls to Add_Ship_Variants and Remove_Ship_Variants.
#    This is called automatically by the above transforms, and is not
#    intended for general direct calls.
#    The script must be manually called from the ingame script editor
#    currently, and will may take many seconds to complete an update.
#    '''
#    File_Manager.Copy_File(
#        'scripts/x3customizer.add.variants.to.shipyards.xml')
#        
#
#@File_Manager.Transform_Wrapper()
#def _Include_Script_To_Update_Factory_Sizes():
#    '''
#    Adds the 'x3customizer.add.factories.to.shipyards' script to the
#    game, which will update shipyards with any added factory sizes
#    after a call to Add_More_Factory_Sizes.
#    This is called automatically by the above transform, and is not
#    intended for general direct calls.
#    The script must be manually called from the ingame script editor
#    currently.
#    '''
#    File_Manager.Copy_File(
#        'scripts/x3customizer.add.factories.to.shipyards.xml')
    