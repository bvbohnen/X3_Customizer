'''
Main function for the X3_Customizer.
'''
import os
import sys
from pathlib import Path
import argparse

# To support packages cross-referencing each other, set up this
#  top level as a package, findable on the sys path.
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

import X3_Customizer

def Run(*args):
    '''
    Run the customizer.
    This expect a single argument: the name of the .py file to load
    which specifies file paths and the transforms to run.
    '''
    
    # Rename the settings for convenience.
    Settings = X3_Customizer.Common.Settings
    
    # Set up command line arguments.
    argparser = argparse.ArgumentParser(
        description='Main function for running X3 Customizer version {}.'.format(
            X3_Customizer.Change_Log.Get_Version()
            ),
        # Special setting to add default values to help messages.
        # -Removed; doesn't work on positional args.
        #formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        )

    argparser.add_argument(
        'user_module',
        help = 'Python module setting up paths and specifying'
               ' transforms to be run.'
               ' Example in input_scripts/Example_Transforms.py.'
               )

    # Flag to clean out old files.
    argparser.add_argument(
        '-clean', 
        action='store_true',
        help = 'Cleans out any files created on the prior run,'
               ' and reverts any file renamings back to their original names.'
               ' Files in the user source folder will be moved to the game'
               ' folders without modifications.'
               ' Still requires a user_transform file which specifies'
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
    
    argparser.add_argument(
        '-dev', 
        action='store_true',
        help =  'Enables developer mode, which makes some changes to'
                ' exception handling.')
    
    argparser.add_argument(
        '-quiet', 
        action='store_true',
        help =  'Quiets some extra status messages.')
    
    argparser.add_argument(
        '-allow_path_error', 
        action='store_true',
        help =  'Allows the customizer to attempt to run if the x3/addon'
                ' path appears incorrect; may be used if the source folder'
                ' contains all needed files, though generated files'
                ' need to be moved manually to the x3 directory.')
    
    # TODO: maybe update this; currently scipy is default enabled, but
    # could be force disabled for users with scipy installed but who don't
    # want to use it.
    #argparser.add_argument(
    #    '-use_scipy', 
    #    action='store_true',
    #    help =  'Allows the scipy package to be used when generating'
    #            ' smoothing functions; only supported when running the'
    #            ' python source code with the scipy package installed.')
        
    argparser.add_argument(
        '-test_run', 
        action='store_true',
        help =  'Performs a test run of the transforms, behaving like'
                ' a normal run but not writing out results.')
        
    
    # Run the parser on the sys args.
    args = argparser.parse_args(args)

    
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
        if not args.quiet:
            print('Enabling cleanup mode; transforms will be skipped.')
        # Apply this to the settings, so that all transforms get
        #  skipped early.
        Settings.skip_all_transforms = True

    if args.ignore_loose_files:
        if not args.quiet:
            print('Ignoring existing loose game files.')
        Settings.ignore_loose_files = True

    if args.write_source_paths:
        if not args.quiet:
            print('Adding source paths to the message log.')
        Settings.write_file_source_paths_to_message_log = True

    if args.dev:
        if not args.quiet:
            print('Enabling developer mode.')
        Settings.developer = True
        
    if args.quiet:
        # No status message here, since being quiet.
        Settings.verbose = False
           
    if args.test_run:
        if not args.quiet:
            print('Performing test run.')
        # This uses the disable_cleanup flag.
        Settings.disable_cleanup_and_writeback = True
                
    if not args.quiet:
        print('Attempting to run {}'.format(user_module_name))
      
    try:
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

    except Exception as ex:
        # Make a nice message, to prevent a full stack trace being
        #  dropped on the user.
        print('Exception of type "{}" encountered.\n'.format(
            type(ex).__name__))
        ex_text = str(ex)
        if ex_text:
            print(ex_text)

        # In dev mode, reraise the exception.
        if Settings.developer:
            raise ex
        #else:
        #    print('Enable developer mode for exception stack trace.')

    # If cleanup/writeback not disabled, run them.
    # These are mainly disabled by the patch builder.
    if not Settings.disable_cleanup_and_writeback:
        # Run any needed cleanup.
        X3_Customizer.File_Manager.Cleanup()
        
        # Everything should now be done.
        # Can open most output files in X3 Editor to verify results.
        X3_Customizer.File_Manager.Write_Files()
    else:
        print('Skipping file writes.')

    #print('Run complete')
    

if __name__ == '__main__':
    Run(*sys.argv[1:])
