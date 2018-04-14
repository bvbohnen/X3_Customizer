'''
Development file to build patches from diffs between modified files
and source files, eg. for script edits.
This behaves similar to a transform file, requiring path setup to
find the source files being edited.

TODO: add a transform file to rebuild the source scripts from patches,
if needed.
'''
# Import all transform functions.
from Transforms import *
from File_Manager.File_Patcher import *
from Common import *

Set_Path(
    path_to_addon_folder = r'D:\Steam\SteamApps\common\x3 terran conflict\addon',
    source_folder = 'patch_source'
)
# Don't need to do normal game file writes.
# Not too important to have this here, but if not here then
# normal transforms will need to be rerun, which can be
# unexpected.
Settings.disable_cleanup_and_writeback = True

# Lay out the modified files here.
# These should all be in the patches folder.
# Verify the reverse direction patch application generates the
# modified file properly.

Make_Patch('scripts/!fight.war.protectsector.xml', verify = True)
Make_Patch('scripts/plugin.com.agent.main.xml', verify = True)
Make_Patch('scripts/!move.follow.template.xml', verify = True)
Make_Patch('scripts/!plugin.acp.fight.attack.object.xml', verify = True)
Make_Patch('scripts/!lib.fleet.shipsfortarget.xml', verify = True)

# Note: these patches are on original xml files, not pck.
# Also, they lack the sourcecodetext section and have line numbers,
# so reformatting should help reduce patch size.
Make_Patch('scripts/plugin.gz.CmpClean.crunch.xml', verify = True, reformat_xml = True)
Make_Patch('scripts/plugin.gz.CmpClean.Main.xml', verify = True, reformat_xml = True)


# Can leave the attack command mod as a standalone script, since it
# is fairly simple.
#Make_Patch('!ship.cmd.attack.std.xml', verify = True)
