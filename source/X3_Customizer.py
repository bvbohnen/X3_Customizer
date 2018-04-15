'''
X3 Customizer
------------------

This tool will read in source files from X3, perform transforms on them,
and write the results back out. Transforms will often perform complex
or repetitive tasks succinctly, avoiding the need for hand editing of
source files. Many transforms will also do analysis of game files, to
intelligently select appropriate edits to perform.

Source files will generally support any prior modding. Nearly all transforms 
support input arguments to set parameters and adjust behavior, according 
to user preferences. Most transforms will work on an existing save.

This tool is written in Python, and tested on version 3.6.
As of customizer version 3, an executable may be generated for users
who do not wish to run the Python source code directly.

This tool is designed for Albion Prelude v3.3. Most transforms will
support prior versions of AP. TC is not directly supported currently
due primarily to some path assumptions.

Source code is hosted on github:
https://github.com/bvbohnen/X3_Customizer
Announcements are primarily made on the Egosoft forum:
https://forum.egosoft.com/viewtopic.php?t=396158

Usage:

 * "X3_Customizer.bat [path to user_transform_module.py]"
   - Call from the command line.
   - Runs the customizer, using the provided python control module
     which will declare the path to the X3 directory and the
     transforms to be run.
   - Call with '-h' to see any additional arguments.
 * "source\X3_Customizer.py [path to user_transform_module.py]"
   - As above, running the python source code directly.
   - Supports general python imports in the control module.
   - If the scipy package is available, this has additional
     features omitted from the executable due to file size.
 * "source\Make_Documentation.py"
   - Generates updated documentation for this project, as markdown
     formatted files README.md and Documentation.md.
 * "source\Make_Executable.py"
   - Generates a standalone executable and support files, placed
     in the bin folder. Requires the PyInstaller package be available.
 * "source\Make_Patches.py"
   - Generates patch files for this project from some select modified
     game scripts. Requires the modified scripts be present in the
     patches folder; these scripts are not included in the repository.
 * "source\Make_Release.py"
   - Generates a zip file with all necessary binaries and source files
     for general release.

Setup and behavior:

  * Transforms will operate on source files (eg. tships.txt) which
  are either provided as loose files, or extracted automatically from the
  game's cat/dat files.

  * Source files are searched for in this priority order, where .pck
    versions of files take precedence:
    - From an optional user specified source folder, with a folder
      structure matching the X3 directory structure (without 'addon' path).
      Eg. [source_folder]/types/TShips.txt
    - From the normal x3 folders.
    - From the incrementally indexed cat/dat files in the 
      'addon' folder.
    - From the incrementally indexed cat/dat files in the base
      x3 folder.
    - Note: any cat/dat files in the 'addon/mods' folder will be
      ignored, due to ambiguity on which if any might be selected
      in the game launcher.

  * The user controls the customizer using a command script which will
  set the path to the X3 installation to customize (using the Set_Path
  function), and will call the desired transforms with any necessary
  parameters. This script is written using Python code, which will be
  executed by the customizer.
  
  * The key command script sections are:
    - "from Transforms import *" to make all transform functions available.
    - Call Set_Path to specify the X3 directory, along with some
      other path options. See documentation below for parameters.
    - Call a series of transform functions, as desired.
  
  * The quickest way to set up a command script is to
  copy and edit the input_scripts/User_Transforms_Example.py file.
  Included in the repository is User_Transforms_Mine, the author's
  personal set of transforms, which can be checked for futher examples
  of how to use most transforms available.

  * Transformed output files will be generated in an unpacked form
  in the x3 directories, or to a custom output direction set
  using Set_Path. Already existing files will be renamed,
  suffixing with '.x3c.bak', if they do not appear to have been
  created by the customizer on a prior run. A json log file will be
  written with information on which files were created or renamed.

  * Warning: this tool will attempt to avoid unsafe behavior, but
  the user should back up irreplaceable files to be safe against
  bugs such as accidental overwrites of source files with
  transformed files.
  
'''
# TODO: maybe remove version tag from title, just leave in change log.
# Note: the above comment gets printed to the markdown file, so avoid
#  having a 4-space indent because text will get code blocked.
# -Need to also avoid this 4-space group across newlines, annoyingly.
# -Spaces in text being put into a list seems okay.
# -In general, check changes in markdown (can use Visual Studio plugin)
#  to verify they look okay.

'''
TODO transforms:

-Add a start customizer, selecting name, age, ship, location, etc.
-Add option for salvage command software mod to disable the extra 
 content (invincible repair stations and such).
-Add option for xrm bounties to not spam the player log with messages.
'''

# Note: for organization, some files were moved into subfolders and
#  set up as packages.
# Because visual studio isn't very smart with package imports, and since
#  this project is not expected to be imported as a package by any
#  external tools, and since the entry function shares a name with the
#  main project folder, the top level is not packaged.
# Subpackages should be found naturally without having to mess around
#  with sys paths, since they are directly under this folder.
# Imports of the packages can just be done directly, not relative, relying
#  on them being found early in the search paths (avoiding conflicts with
#  any standard packages and such).

import sys, os

# Load up the file manager.
import File_Manager
# Load up the settings.
from Common.Settings import Settings
import argparse
import Change_Log

def Run():
    '''
    Run the customizer.
    This expect a single argument: the name of the .py file to load
    which specifies file paths and the transforms to run.
    '''
    
    # Set up command line arguments.
    argparser = argparse.ArgumentParser(
        description='Main function for running X3 Customizer version {}.'.format(
            Change_Log.Get_Version()
            ),
        # Special setting to add default values to help messages.
        # -Removed; doesn't work on positional args.
        #formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        )

    argparser.add_argument(
        'user_module',
        help = 'Python module setting up paths and specifying'
               ' transforms to be run.'
               ' Example in input_scripts/User_Transforms_Example.py.'
               )

    # Flag to clean out old files.
    argparser.add_argument(
        '-clean', 
        action='store_true',
        help = 'Cleans out any files created on the prior run,'
               ' and undoes any file renamings back to their original names.'
               'Files in the user source folders will be moved to the game'
               ' folders without modifications.'
               'Still requires a user_transform file which specifies'
               ' the necessary paths, but transforms will not be run.')
    
    # Flag to ignore loose files in the game folders.
    argparser.add_argument(
        '-ignore_loose_files', 
        action='store_true',
        help = 'Ignores files loose in the game folders when looking'
               ' for sources; only files in the user source folder or'
               ' the cat/dat pairs are considered.')
    
    # Flag to add source paths to the message log.
    argparser.add_argument(
        '-write_source_paths', 
        action='store_true',
        help = 'Prints the paths used for each sourced file to the'
               ' general message log.')
    

    # Run the parser on the sys args.
    args = argparser.parse_args()

    
    # The arg should be a python module.
    # This may include pathing, though is generally not expected to.
    user_module_name = args.user_module

    if not user_module_name.endswith('.py'):
        print('Error: expecting the name of a python module, ending in .py.')
        return

    # Check for file existence.
    if not os.path.exists(user_module_name):
        print('Error: {} not found.'.format(user_module_name))
        return
    
    # Check for the clean option.
    if args.clean:
        print('Enabling cleanup mode; transforms will be skipped.')
        # Apply this to the settings, so that all transforms get
        #  skipped early.
        Settings.skip_all_transforms = True

    if args.ignore_loose_files:
        print('Ignoring existing loose game files.')
        Settings.ignore_loose_files = True

    if args.write_source_paths:
        print('Adding source paths to the message log.')
        Settings.write_file_source_paths_to_message_log = True

    print('Attempting to run {}'.format(user_module_name))
      
    # Attempt to load the module.
    # This will kick off all of the transforms as a result.
    import importlib        
    module = importlib.machinery.SourceFileLoader(
        # Provide the name sys will use for this module.
        # Use the basename to get rid of any path, and prefix
        #  to ensure the name is unique (don't want to collide
        #  with other loaded modules).
        'user_module_' + os.path.basename(user_module_name), 
        user_module_name
        ).load_module()


    # If cleanup/writeback not disabled, run them.
    # These are mainly disabled by the patch builder.
    if not Settings.disable_cleanup_and_writeback:
        # Run any needed cleanup.
        File_Manager.Cleanup()
        
        # Everything should now be done.
        # Can open most output files in X3 Editor to verify results.
        File_Manager.Write_Files()

    print('Transforms complete')
    
if __name__ == '__main__':
    Run()
