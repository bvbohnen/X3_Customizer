'''
X3 Customizer v2.10
------------------

This tool will read in source files from X3, perform transforms on them,
and write the results back out. Transforms will often perform complex
or repetitive tasks succinctly, avoiding the need for hand editing of
source files. Many transforms will also do analysis of game files, to
intelligently select appropriate edits to perform.
Source files will generally support any prior modding. Nearly all transforms 
support input arguments to set parameters and adjust behavior, according 
to user preferences. Most transforms will work on an existing save.

This tool is written in Python, and tested on version 3.6. To run this
script, the user will need to install Python.

Usage:
 * "X3_Customizer <user_transform_module.py>"
   - Runs the customizer, using the provided control module which
     will specify the path to the AP directory, the folder
     containing the source files to be modified, and the transforms
     to be run. See User_Transforms_Example.py for an example.
     Defaults to running 'User_Transforms.py' if an argument is 
     not provided.
 * "Make_Documentation.py"
   - Generates documentation for this project, as markdown
     supporting files README.md and Documentation.md.

Setup:
  * Transforms will operate on source files (eg. tships.txt) which
  need to be set up prior to running this tool. Source files can be
  extracted using X3 Editor 2 if needed. Source files may be provided
  after any other mods have been applied.

  * Source files need to be located in a folder underneath the 
  specified AP addon directory, and will have an internal folder
  structure matching that of the files in the normal addon directory.

  * The user must write a Python script which will specify paths
  and control the customizer by calling transforms.

  * Output files will be generated in the addon directory matching
  the folder structure in the source folder. Non-transformed files
  will generate output files. Files which do not have a name matching
  the requirement of any transform will be ignored and not copied.
  In some cases, files may be generated one directory up, in the
  presumed Terran Conflict folder.

  * Warning: Generated output will overwrite any existing files.

  Example directory:
  <code>
    <path to X3 installation>
        addon
            source_folder
                maps
                    x3_universe.xml
                types
                    TBullets.txt
                    TLaser.txt
                    TShips.txt
                    TShips_backup.txt
  </code>
   This will write to the following files, overwriting any
   existing ones:   
  <code>
    <path to X3 installation>
        addon
            maps
                x3_universe.xml
            types
                TBullets.txt
                TLaser.txt
                TShips.txt
  </code>

'''
#TODO: maybe remove version tag from title, just leave in change log.
#Note: the above comment gets printed to the markdown file, so avoid
# having a 4-space indent because text will get code blocked.
#-Need to also avoid this 4-space group across newlines, annoyingly.
#-Spaces in text being put into a list seems okay.
#-In general, check changes in markdown (can use Visual Studio plugin)
# to verify they look okay.

'''
General transform ideas:

-Add larger factories (may be tricky to get naming right on suffixes).
-Add a start customizer, selecting name, age, ship, location, etc.
'''

import sys, os
#Load up the file manager.
import File_Manager

def Run(args):
    '''
    Run the customizer.
    This expect a single argument: the name of the .py file to load
    which specifies file paths and the transforms to run.
    '''
    #If only one arg available, it is the autofilled file name,
    # so user gave nothing.
    if len(args) == 1:
        #Set the module to User_Transforms.py by default.
        args.append('User_Transforms.py')

        #Print some semi-informative message.
        #-Removed in favor of default.
        #print('Please provide the name of a transform specification module.')

    if len(args) > 2:
        print('Error: expecting 1 argument, 2 were given.')

    #Check for a help request.
    elif args[1] == '-help':
        help_lines = [
            '',
            'Usage: X3_Customizer user_transform_module.py',
            '',
            '\tPlease provide the name of a python module in this directory',
            '\twhich will declare the path to the AP directory, the folder ',
            '\tcontaining the source files to be modified, and the transforms ',
            '\tto be run.',
            '\tSee User_Transforms_Example.py for an example.'
            ]
        print('\n'.join(help_lines))

    else:
        #The arg should be a python module.
        #This may include pathing, though is generally not expected to.
        user_module_name = args[1]

        if not user_module_name.endswith('.py'):
            print('Error: expecting the name of a python module, ending in .py.')
            return

        #Check for file existence.
        if not os.path.exists(user_module_name):
            print('Error: {} not found.'.format(user_module_name))
            return

        print('Attempting to run {}'.format(user_module_name))
      
        #Attempt to load the module.
        #This will kick off all of the transforms as a result.
        import importlib        
        module = importlib.machinery.SourceFileLoader(
            #Provide the name sys will use for this module.
            #Use the basename to get rid of any path, and prefix
            # to ensure the name is unique.
            'user_module_' + os.path.basename(user_module_name), 
            user_module_name
            ).load_module()

    #Run any needed cleanup.
    File_Manager.Cleanup()
        
    #Everything should now be done.
    #Can open most output files in X3 Editor to verify results.
    File_Manager.Write_Files()

    print('Transforms complete')
    
if __name__ == '__main__':
    Run(sys.argv)

