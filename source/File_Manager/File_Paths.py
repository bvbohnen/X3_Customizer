'''
General place to put support code for path constructors.

In general, there are three types of paths:
* virtual_path:
  - Uses forward slash separators and does not include any 'addon' folder.
  - Matches game internal file system.
* cat_path:
  - Similar to virtual_path, but includes the 'addon' folder for some
    categories of files.
* sys_path:
  - Real system path to where a file should be located.
  - Default is in the game directory where it can be found.
  - Some paths are relative to the user source folder or project
    source/patches folders.

Some care will be needed to ensure virtual path lookups will work
when there may be case discrepencies, as case shouldn't really matter
but it is not easy to do caseless matching in python without just
blindly lowercasing everything (which will be avoided due to
ugliness of written result).
'''
import os
from Common.Settings import Settings

# Preset the directory where the customizer resides, which
#  is one level up from here.
_customizer_dir = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..'))

def Virtual_Path_to_System_Path(virtual_path):
    '''
    Convert a virtual path to an absolute system path to the base x3
     or 'addon' folder, where the game will read it.
    Virtual paths will use forward slash separators, and match
     to the game's internal file system (without addon folder).
    '''
    # Convert to a cat path first, to prefix with 'addon'.
    cat_path = Virtual_Path_to_Cat_Path(virtual_path)

    # Swap to standard os separators; this is still relative to
    #  the x3 base folder.
    sys_path = os.path.join(*cat_path.split('/'))

    # Append the path to the x3 base folder.
    return os.path.join(Settings.Get_X3_Folder(), sys_path)


def Virtual_Path_to_Output_Path(virtual_path):
    '''
    Convert a virtual path to an absolute system path specified
     for capturing output files.
    '''
    # Similar to above, but the base folder will be different.
    cat_path = Virtual_Path_to_Cat_Path(virtual_path)
    sys_path = os.path.join(*cat_path.split('/'))
    return os.path.join(Settings.Get_Output_Folder(), sys_path)


def Virtual_Path_to_User_Source_Path(virtual_path):
    '''
    Convert a virtual path to an absolute system path for the
     user specified source folder.
    '''
    # Similar to above, but do not prefix with 'addon', and append to
    #  the source folder.
    sys_path = os.path.join(*virtual_path.split('/'))
    return os.path.join(Settings.Get_Source_Folder(), sys_path)


def Virtual_Path_to_Project_Patch_Path(virtual_path):
    '''
    Convert a virtual path to an absolute system path for the
     project patch folder.
    '''
    # Similar to above, but the folder is located in this project.
    # Placed up an extra level, for sharing with an exe.
    sys_path = os.path.join(*virtual_path.split('/'))
    return os.path.join(_customizer_dir, '..', 'patches', sys_path)


def Virtual_Path_to_Project_Source_Path(virtual_path):
    '''
    Convert a virtual path to an absolute system path for the
     project source folder, holding some general files to
     be copied from for some transforms which do blind overwrites.
    '''
    # Similar to above, but the folder is located in this project.
    sys_path = os.path.join(*virtual_path.split('/'))
    return os.path.join(_customizer_dir, '..', 'game_files', sys_path)


def Cat_Path_to_Virtual_Path(cat_path):
    '''
    Convert a cat path (forward slashes, with 'addon' folder) to
     a virtual path (forward slashes, no 'addon' folder).
    '''    
    # Separate on forward slashes.
    path_split = cat_path.split('/')

    # Drop a starting 'addon' folder, to normalize to the
    #  source folder setup (which doesn't distinguish 'addon').
    # ('addon' should always be followed by something, so don't
    #  worry about that being the only item in the list.)
    if path_split[0] == 'addon':
        path_split = path_split[1:]

    # Rejoin and return.
    return '/'.join(path_split)


def Virtual_Path_to_Cat_Path(virtual_path):
    '''
    Convert a virtual path (forward slashes, no 'addon' folder) to
    a cat path (forward slashes, possible addon folder).
    '''
    # This may or may not have 'addon' prefixed, depending on the
    #  path structure.
    # Note the starting folder.
    path_start_folder = virtual_path.split('/')[0]
    # Default cat path to match virtual path, for when 'addon' not needed.
    cat_path = virtual_path
        
    # Get the folders that should be in the addon directory.
    # These are just the first folders, in case of nesting, though
    #  no nesting expected for any files expected to be transformed,
    #  it can happen (eg. directory/images).
    # Note: comparison should be case insensitive.
    for test_folder in [
            'cutscenes',
            'director',
            'maps',
            't',
            'types',
            'scripts',
        ]:
        # On a match, prefix with the addon folder.
        if path_start_folder.lower() == test_folder:
            cat_path = 'addon/' + virtual_path
            break
        
    return cat_path


def System_Path_to_Virtual_Path(sys_path):
    '''
    Convert a system path to a virtual path.
    The system path should be absolute, and will be considered relative
     to the source folder (if under the source folder), else the 'addon'
     folder (if under the addon folder), else the base X3 folder.
    '''
    # Verify the input is absolute, to avoid amgibuity in case
    #  working directory ever changes.
    assert os.path.isabs(sys_path)

    # Determine which folder to consider this path relative to, to
    #  get the correct virtual path.
    # Can loop over the folders (in priority order), and break when
    #  a match found.
    for relative_folder in [
        Settings.Get_Source_Folder(),
        Settings.Get_Addon_Folder(),
        Settings.Get_X3_Folder(),
        ]:
        if sys_path.startswith(relative_folder):
            break

    # Isolate the relative part of the path.
    relative_path = os.path.relpath(sys_path, relative_folder)

    # Swap out the separators from system default to standardized forward
    #  slashes.
    virtual_path = relative_path.replace(os.path.sep, '/')

    return virtual_path


def System_Path_to_Relative_Path(path):
    '''
    Convert a full system path to a standardized relative path.
    The standard will be relative to the x3 base folder.
    '''
    return os.path.relpath(path, Settings.Get_X3_Folder())
    

def Relative_Path_to_System_Path(path):
    '''
    Convert a standardized relative path to a full system path.
    The standard will be relative to the x3 base folder.
    '''
    # Error if the path is already absolute.
    assert not os.path.isabs(path)
    return os.path.join(Settings.Get_X3_Folder(), path)


def Unpacked_Path_to_Packed_Path(path):
    '''
    Converts a path for an unpacked file to a packed file, for
    any path type (sys_path, virtual_path, cat_path).
    '''
    # All path types end with an extension, so can just split it
    #  off and replace with .pck.
    return path.rsplit('.',1)[0] + '.pck'


def Get_Backed_Up_Sys_Path(sys_path):
    '''
    Returns the path for a backed up version of a file specified
    by sys_path. This can be used when creating backups, or when looking
    for prior backups.
    '''
    # Suffix with .x3c.bak.
    # While the replaces the normal file suffix, which can be bothersome
    #  for editing, in some cases it is important to stop the game
    #  from reading the file (eg. all xml files in the director folder
    #  get read by the game).
    return sys_path + '.x3c.bak'
