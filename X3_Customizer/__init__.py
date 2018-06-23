'''
X3 Customizer
-----------------

This tool will read in source files from X3, modify on them based on
user selected transforms, and write the results back to the game directory.
Transforms will often perform complex or repetitive tasks succinctly,
avoiding the need for hand editing of source files. Many transforms
will also do analysis of game files, to intelligently select appropriate
edits to perform.  Some transforms carry out binary code edits, allowing
for options not found elsewhere.

Source files will generally support any prior modding. Nearly all transforms 
support input arguments to set parameters and adjust behavior, according 
to user preferences. Most transforms will work on an existing save.

This tool is written in Python, and tested on version 3.6.
As of customizer version 3, an executable may be generated for users
who do not wish to run the Python source code directly.

This tool is designed primarily for Albion Prelude v3.3. Most transforms
will support prior or later versions of AP. TC is not supported currently
due to some path assumptions.

When used alongside the X3 Plugin Manager, run X3 Customizer second,
after the plugin manager is closed, since the plugin manager generates a
TWareT.pck file when closed that doesn't capture changes in TWareT.txt.

Usage:

 * "Launch_X3_Customizer.bat [path to user_transform_module.py]"
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
  copy and edit the input_scripts/Example_Transforms.py file.
  Included in the repository is Authors_Transforms, the author's
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

# Note:
# For convenient user use, this will import the transforms and some
#  select items flatly.
# For general good form, this will also import subpackages and top
#  level modules
# The Main and various Make_* modules will be left off; those are
#  desired to be called directly from a command line.

# Subpackages/modules.
from . import Common
from . import Transforms
from . import File_Manager
from . import Change_Log

# Convenience items for input scripts to import.
from .Transforms import *
from .File_Manager import Set_Path
from .Common.Settings import Settings

