'''
Add new or modified scripts.

This module will include a shared Add_Script transform, and some
convenience transforms for select scripts.
Modified scripts will tend to be handled with patches, while original
scripts will just be moved to the scripts folder.
'''
from File_Manager import *
import os
import shutil
from File_Patcher import *

#TODO: script to switch drone factories to using the food of their
# race, instead of all using split food. Same for satellites and
# majaglit.

    
#Quick dummy transform, to help the File_Manager recognize these as files
# that may be changed.
#Patched files should go here, else they get pulled from pck files every
# time (not a huge problem, but unnecessary).
#TODO: maybe find better solution; problem is that the source folder search
# routine ignores files not in a dependency list somewhere. Alternative
# might be to just grab everything, even user backup files that may
# be present (also huge problem, just makes unnecessary copies).
@Check_Dependencies(
    '!fight.war.protectsector.xml', 
    'plugin.com.agent.main.xml',
    '!move.follow.template.xml',
    '!plugin.acp.fight.attack.object.xml',
    '!lib.fleet.shipsfortarget.xml',
    #'!ship.cmd.attack.std.xml',
    'plugin.gz.CmpClean.crunch.xml',
    'plugin.gz.CmpClean.Main.xml',
    )
def _dummy():
    return


# No dependencies here; this only mucks around in the script folder.
@Check_Dependencies()
def Add_Script(
        script_name = None,
        remove = False
    ):
    '''
    Add a script to the addon/scripts folder. If an existing xml version
    of the script already exists, it is overwritten. If an existing pck
    version of the script already exists, it is renamed with suffix
    '.x3c.bak'. Note: this is only for use with full scripts, not those
    defined by diffs from existing scripts.

    * script_name:
      - String, the name of the script to add. This should be present
        in the /scripts directory of this program. The name does not
        need to include the '.xml' suffix, though it may.
    * remove:
      - Bool, if True then instead of adding the given script, it will
        be removed if present from a prior transform, and any backed
        up pck version will be restored.
    '''
    # Add the .xml extension if needed.
    if not script_name.endswith('.xml'):
        script_name += '.xml'
        
    # Copy the script to the scripts directory, to make it available.
    # Do this here to share the path with cleanup, which runs early.
    dest_path = os.path.join('scripts', script_name)
    # The pck version would just be the same path with a different
    # extension.
    pck_path = dest_path.replace('.xml', '.pck')
    # The backup pck is similar, with a longer extension.
    pck_backup_path = pck_path + '.x3c.bak'

    # The file is present here in scripts, so can reuse the dest_path.
    this_dir = os.path.normpath(os.path.dirname(__file__))
    source_path = os.path.join(this_dir, 'source', script_name)
    
    # Continue based on if removal is being done or not.
    if not remove:
        
        # Error if the file is not found locally.
        if not os.path.exists(source_path):
            print('Add_Script error: file {} not found at {}.'.format(
                script_name, source_path))
            return

        # Perform the copy of the xml; this overwrites any existing xml
        # version.
        shutil.copy(source_path, dest_path)

        # Check if a pck version exists.
        # If it does, it needs to be renamed to ensure the xml script
        # will get loaded by the game instead of the pck version.
        if os.path.exists(pck_path):
            os.rename(pck_path, pck_backup_path)

    else:
        # Check if the xml file exists from a prior run.
        if os.path.exists(dest_path):
            # Remove the xml file.
            os.remove(dest_path)
            # Check if a backed up pck exists.
            if os.path.exists(pck_backup_path):

                # Something odd if the standard pck also exists.
                if os.path.exists(pck_path):
                    # Print a warning and skip the rename.
                    print('Add_Script warning: when removing file {}, a .pck'
                         'version and a .pck.x3c.bak version were discovered;'
                         'backup restoration will be skipped.'.format(script_name))
                else:
                    # Rename it back to .pck.
                    os.rename(pck_backup_path, pck_path)

    return
    

@Check_Dependencies()
def Disable_OOS_War_Sector_Spawns(
    ):
    '''
    Disables spawning of dedicated ships in the AP war sectors which attack
    player assets when the player is out-of-sector. By default, these ships
    scale up with player assets, and immediately respawn upon being killed.
    This patches '!fight.war.protectsector'.
    '''
    # Can pass the _cleanup flag straight through as the remove field.
    # Add_Script('!fight.war.protectsector', remove = _cleanup)
    # Update: this will work on a file diff, to avoid having to keep the
    # full original egosoft source around.
    Apply_Patch('!fight.war.protectsector.xml')

    
@Check_Dependencies()
def Allow_CAG_Apprentices_To_Sell(
    ):
    '''
    Allows Commercial Agents to sell factory products at pilot
    rank 0. May require CAG restart to take effect.
    '''
    Apply_Patch('plugin.com.agent.main.xml')
    
    
@Check_Dependencies()
def Fix_OOS_Laser_Missile_Conflict(
    ):
    '''
    Allows OOS combat to include both missile and laser fire
    in the same attack round. In vanilla AP, a ship firing a 
    missile will not fire its lasers for a full round, generally 
    causing a large drop in damage output.
    With the change, adding missiles to OOS ships will not hurt
    their performance.
    '''
    Apply_Patch('!plugin.acp.fight.attack.object.xml')
    

@Check_Dependencies()
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
    Apply_Patch('!lib.fleet.shipsfortarget.xml')


@Check_Dependencies()
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
    Apply_Patch('!move.follow.template.xml')

    # Can now grab the T file and do a replacement in its text.
    source_t_file = Load_File('!move.follow.template.xml', 
                              return_t_file = True)
    source_t_file.text = (source_t_file.text
            .replace('3011', str(small_range))
            .replace('4011', str(medium_range))
            .replace('7011', str(long_range)))
    

@Check_Dependencies()
def Convert_Attack_To_Attack_Nearest(
        _cleanup = False
    ):
    '''
    Modifies the Attack command when used on an owned asset to instead
    enact Attack Nearest. In vanilla AP, such attack commands are quietly
    ignored. Intended for use when commanding groups, where Attack is 
    available but Attack Nearest is not.
    This replaces '!ship.cmd.attack.std'.
    '''
    Add_Script('!ship.cmd.attack.std', remove = _cleanup)

    
@Check_Dependencies()
def Add_CLS_Software_To_More_Docks(
        _cleanup = False
    ):
    '''
    Adds Commodity Logistics Software, internal and external, to all
    equipment docks which stock Trade Command Software Mk2.
    This is implemented as a setup script which runs on the game
    loading. Once applied, this transform may be disabled to remove
    the script run time. This change is not reversable.
    '''
    Add_Script('setup.x3customizer.add.cls.to.docks', remove = _cleanup)

        
    
@Check_Dependencies()
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
    Apply_Patch('plugin.gz.CmpClean.Main.xml', reformat_xml = True)

    
    
@Check_Dependencies()
def Complex_Cleaner_Use_Small_Cube(
        # Note: no cleanup needed, as above.
    ):
    '''
    Forces the Complex Cleaner to use the smaller cube model always
    when combining factories.
    Patches plugin.gz.CmpClean.crunch.xml.
    '''
    Apply_Patch('plugin.gz.CmpClean.crunch.xml', reformat_xml = True)

    

@Check_Dependencies()
def _Include_Script_To_Update_Ship_Variants(
        # Set this to be ignored when making documentation.
        # It exists mainly to ensure proper behavior between the
        # two ship variants transforms, so that if either runs then
        # this script will be included, but if neither runs then
        # this script will be cleaned out.
        _cleanup = False
    ):
    '''
    Adds the 'x3customizer.add.variants.to.shipyards' script to the
    game, which will update shipyards with any added or removed
    variants after calls to Add_Ship_Variants and Remove_Ship_Variants.
    This is called automatically by the above transforms, and is not
    intended for general direct calls.
    The script must be manually called from the ingame script editor
    currently, and will may take many seconds to complete an update.
    '''
    Add_Script('x3customizer.add.variants.to.shipyards.xml', remove = _cleanup)
    
    # If an older script name is present, clean it out.
    # This is not a big deal; can leave it in place for a version or two,
    # then remove it.
    # Update: removed as of version 2.17.
    # old_script_name = 'a.x3customizer.add.variants.to.shipyards.xml'
    # Add_Script(old_script_name, remove = True)

    

@Check_Dependencies()
def _Include_Script_To_Update_Factory_Sizes(
        _cleanup = False
    ):
    '''
    Adds the 'x3customizer.add.factories.to.shipyards' script to the
    game, which will update shipyards with any added factory sizes
    after a call to Add_More_Factory_Sizes.
    This is called automatically by the above transform, and is not
    intended for general direct calls.
    The script must be manually called from the ingame script editor
    currently.
    '''
    Add_Script('x3customizer.add.factories.to.shipyards.xml', remove = _cleanup)
    