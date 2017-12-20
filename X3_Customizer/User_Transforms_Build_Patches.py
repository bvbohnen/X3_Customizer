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
from File_Patcher import *

Set_Path(
    path_to_addon_folder = r'D:\Steam\SteamApps\common\x3 terran conflict\addon',
    source_folder = 'patch_source'
)

# Lay out the modified files here.
# These should all be in the patches folder.
# Verify the reverse direction patch application generates the
# modified file properly.
Make_Patch('!fight.war.protectsector.xml', verify = True)
# Can leave the attack command mod as a standalone script, since it
# is fairly simple.
#Make_Patch('!ship.cmd.attack.std.xml', verify = True)
