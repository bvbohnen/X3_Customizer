'''
Loads and stores source files to be modified, and writes them
out when finished.

TODO: rename this to be different than the package.
'''

import os
from collections import OrderedDict
import inspect
import shutil

from .. import Common
Settings = Common.Settings
from .File_Fields import *
from .Source_Reader import *
from .File_Types import *
from .Logs import *

    
# Make a set of all transform file names that may be used by transforms,
#  used in filtering the source files tracked.
# This gets filled in by decorators, which should all get processed before
#  the first call to Init (through a call to Load_File) occurs and uses
#  this set.
# Update: may no longer be used.
Transform_required_file_names = set()

# Record a set of all transforms.
# This is filled in by the decorator at startup.
Transform_list = []

# Record a set of transforms that were called.
# Transforms not on this list at the end of a run may need to do
#  cleanup of older files generated on prior runs.
# This is filled in by the decorator.
Transforms_names_run = set()


# On the first call to Load_File from any transform, do some extra
#  setup.
First_call = True
def Init():
    'Initialize the file manager.'
    # Safety check for First_call already being cleared, return early.
    global First_call
    if not First_call:
        return
    First_call = False

    # The file paths should be defined at this point. Error if not.
    Settings.Verify_Setup()

    # Read any old log file.
    Log_Old.Load()

    # Do some version patching as needed.
    Version_Patch()

    # Initialize the file system, now that paths are set in settings.
    Source_Reader.Init()
    
    #-Removed for now.
    ## Generate an initial dummy file for all page text overrides.
    #game_file = Page_Text_File(
    #    virtual_path = Settings.Get_Page_Text_File_Path(),
    #    )
    #Add_File(game_file)

    return


# Dict to hold file contents, as well as specify their full path.
# Keyed by virtual path for the file.
# This gets filled in by transforms as they load the files.
# T files will generally be loaded into lists of dictionaries keyed by field
#  name or index, with each list entry being a separate line.
# XML files will generally be loaded as a XML_File object holding
#  the encoding and raw text.
# These are Game_File objects, and will record their relative path
#  to be used during output.
File_dict = {}

def Add_File(game_file):
    '''
    Add a Game_File object to the File_dict, keyed by its virtual path.
    '''
    File_dict[game_file.virtual_path] = game_file


# Decorator function for transforms to check if their required
#  files are found, and have nice handling when not found.
# The args will be the file names.
# This is implemented as a two-stage decorator, the outer one handling
#  the file check, the inner one returning the function.
# Eg. decorators have one implicit input argument, the following object,
#  such that "@dec func" is like "dec(func)".
# To support input args, a two-stage decorator is used, such that
#  "@dec(args) func" becomes "dec(args)(func)", where the decorator
#  will return a nested decorator after handling args, and the nested
#  decorator will accept the function as its arg.
# To get the wrapped function's name and documentation preserved,
#  use the 'wraps' decorator from functools.
# Update: this will also support a keyword 'category' argument, which
#  will be the documentation transform category override to use when
#  the automated category is unwanted.
# TODO: move to a different module, maybe, since this has grown beyond
#  just being a file thing.
from functools import wraps
def Transform_Wrapper(
        *file_names, 
        category = None, 
        Vanilla = True,
        XRM = True,
        LU = True,
        TC = True,
    ):
    '''
    Wrapper function for transforms.

    * file_names (args)
      - Loose args should be names of required transform files, given
        in the cat path format (forward slashes, etc.).
    * category
      - String, category of the transform; if not given, category
        is set to the name of the containing module without the 'T_'
        prefix and set to singular instead of plural.
      - Subpackages of transforms should set this explicitly for now.
    * Vanilla
      - Bool, if True then the transform should be compatable with
        vanilla x3.
    * XRM
      - Bool, if True then the transform should be compatable with
        XRM modded x3.
    * LU
      - Bool, if True then the transform should be compatable with
        LU modded x3.
    * TC
      - Bool, if True then the transform should be compatable with
        basic vanilla TC (without AP).
    '''

    # Record the required file names to a set for use elsewhere.
    Transform_required_file_names.update(file_names)

    # Make the inner decorator function, capturing the wrapped function.
    def inner_decorator(func):

        # Attach the required file_names to the wrapped function,
        #  since they are only available on function definition at the
        #  moment, and will be checked at run time.
        func._file_names = file_names

        # Attach the override category to the function.
        if category != None:
            func._category = category
        else:

            # Fill a default category from the module name.
            func._category = func.__module__

            # The module may have multiple package layers in it, so
            #  get just the last one.
            func._category = func._category.split('.')[-1]

            # Remove a 'T_' prefix.
            if func._category.startswith('T_'):
                func._category = func._category.replace('T_','')

            # Drop the ending 's' if there was one (which was mostly present to
            #  mimic the X3 source file names, eg. 'tships').
            if func._category[-1] == 's':
                func._category = func._category[0:-1]
            # Special fix for 'Factorie' (after 's' removal).
            if func._category == 'Factorie':
                func._category = 'Factory'


        # Record the version compatability flags.
        # Keep this ordered for easy documentation generation.
        func._compatabilities = OrderedDict([
            ('Vanilla', Vanilla),
            ('XRM'    ,  XRM),
            ('LU'     ,  LU),
            ('TC'     ,  TC),
            ])

        # Record the transform function.
        Transform_list.append(func)

        # Set up the actual function that users will call, capturing
        #  any args/kwargs.
        @wraps(func)
        def wrapper(*args, **kwargs):

            # On the first call, do some extra setup.
            # Init normally runs earlier when the paths are set up,
            #  but if a script forgot to set paths then init will end
            #  up being called here.
            if First_call:
                Init()

            # Check if the settings are requesting transforms be
            #  skipped, and return early if so.
            if Settings.skip_all_transforms:
                return

            # Note this transform as being seen.
            Transforms_names_run.add(func.__name__)
            
            # Loop over the required files.
            for file_name in func._file_names:
                # Do a test load; if succesful, the file was found.
                try:
                    Load_File(file_name)
                # Catch file problems.
                except Common.File_Missing_Exception:
                    print('Skipped {}, required file {} not found or is empty.'.format(
                        func.__name__,
                        file_name
                        ))
                    # Return nothing and skip the call.
                    return
                # Catch gzip problems.
                except Common.Gzip_Exception:
                    print('Skipped {}, required file {} failed during unzipping.'.format(
                        func.__name__,
                        file_name
                        ))
                    # Return nothing and skip the call.
                    return
                except Exception as ex:
                    # Dev mode will reraise the exception.
                    if Settings.developer:
                        raise ex
                    else:
                        print('Skipped {}, unhandled exception.'.format(
                            func.__name__,
                            file_name
                            ))
                    return

            # Call the transform function, looking for exceptions.
            # This will be the generally clean fallback when anything
            #  goes wrong, so that other transforms can still be
            #  attempted.
            try:
                results = func(*args, **kwargs)

                # If here, ran successfully.
                # (This may not be the case in dev mode, but that will
                #  have other messages to indicate the problem.)
                if Settings.verbose:
                    print('Successfully ran {}'.format(
                        func.__name__
                        ))

                # If the function is supposed to return anything, return it
                #  here, though currently this is expected to always be None.
                return results

            except Exception as ex:
                # When set to catch exceptions, just print a nice message.
                if not Settings.developer:
                    # Give the exception name.
                    print('Skipped {} due to a {} exception.'.format(
                        func.__name__,
                        type(ex).__name__
                        ))
                else:
                    # Reraise the exception.
                    raise ex

            return

        # Return the callable function.
        return wrapper

    # Return the decorator to handle the function.
    return inner_decorator


def Set_Transform_Category(function, category):
    '''
    Sets the documentation category for the given function, similar
    to when the decorator is called.
    '''
    # If a correct transform func was given, it will have the
    #  appropriate category field.
    assert hasattr(function, '_category')
    function._category = category


def Load_File(file_name,
              # TODO: rename this to be more generic.
              return_game_file = False, 
              return_text = False,
              error_if_not_found = True):
    '''
    Returns the contents of the given file, either raw text for XML
     or a dictionary for T files.
    If the file has not been loaded yet, reads from the expected
     source file.

    * file_name
      - Name of the file, using the cat_path style (forward slashes,
        no 'addon' folder).
      - For the special text override file to go in the addon/t folder,
        use 'text_override', which will be translated to the correct
        name according to Settings.
    * error_if_not_found
      - Bool, if True and the file is not found, raises an exception,
        else returns None.
    * return_game_file
      - Bool, if True, returns the Game_File object, else returns
        the result of the Read_Data method of the file.
      - Some file types will always return themselves.
    * return_text
      - Bool, if True, returns the raw text of the loaded file,
        without any edits from prior transforms applied.
    '''
    # Special replacement: if the file_name is 'text_override', swap
    #  to the name indicated by settings.
    # -Removed for now.
    #if file_name == 'text_override':
    #    file_name = Settings.Get_Page_Text_File_Path()

    # If the file is not loaded, handle loading.
    if file_name not in File_dict:

        # Get the file using the source_reader, maybe pulling from
        #  a cat/dat pair.
        # Returns a Game_File object, of some subclass, or None
        #  if not found.
        game_file = Source_Reader.Read(file_name, error_if_not_found = False)

        # Problem if the file isn't found.
        if game_file == None:
            if error_if_not_found:
                raise Common.File_Missing_Exception(
                    'Could not find file {}, or file was empty'.format(file_name))
            return None
        
        # Store the contents in the File_dict.
        Add_File(game_file)


    # Return the file contents.
    if return_game_file:
        return File_dict[file_name]
    elif return_text:
        return File_dict[file_name].Get_Text()
    else:
        return File_dict[file_name].Read_Data()

          
def Cleanup():
    '''
    Handles cleanup of old transform files, undoing all file renames
     and deleting prior outputs.
    This is done blindly for now, regardless of it this run intends
     to follow up by applying another renaming and writing new files
     in place of the ones removed.
    This should preceed a call to any call to Write_Files, though can
     be run standalone to do a generic cleaning.
    Preferably do this late in a run, so that files from a prior run
     are not removed if the new run had an error during a transform.
    '''
    # Find all files generated on a prior run, that still appear to be
    #  from that run (eg. were not changed externally), and remove
    #  them.
    for path in Log_Old.Get_File_Paths_From_Last_Run():
        if os.path.exists(path):
            os.remove(path)

    # Find all renamed files, and name them back to their standard
    #  form, which should normally be free after the deletions from above.
    # If the standard form is occupied, it is likely it was overwritten
    #  externally between runs; in this case the backup should not be
    #  restored.
    for original_path, renamed_path in Log_Old.Get_Renamed_File_Paths():
        # Skip if the renamed file doesn't exist anymore for some reason.
        if not os.path.exists(renamed_path):
            continue
        # Skip if the original file name is taken for some reason.
        if os.path.exists(original_path):
            continue
        os.rename(renamed_path, original_path)
            

def Add_Source_Folder_Copies():
    '''
    Adds Misc_File objects which copy files from the user source
     folders to the game folders.
    This should only be called after transforms have been completed,
     to avoid adding a copy of a file that was already loaded and
     edited.
    '''
    # Some loose files may be present in the user source folder which
    #  are intended to be moved into the main folders, whether transformed
    #  or not, in keeping with behavior of older versions of the customizer.
    # These will do direct copies.
    for virtual_path, sys_path in Source_Reader.source_file_path_dict.items():
        # Skip files already written.
        if virtual_path in File_dict:
            continue

        # TODO:
        # Skip files which do not match anything in the game cat files,
        #  to avoid copying any misc stuff (backed up files, notes, etc.).
        # This will need a function created to search cat files without
        #  loading from them.

        # Read the binary.
        with open(sys_path, 'rb') as file:
            binary = file.read()

        # Create the game file.
        Add_File(Misc_File(binary = binary, virtual_path = virtual_path))

                
def Write_Files():
    '''
    Write output files for all source file content used or
     created by transforms.
    Existing files which may conflict with the new writes will be renamed,
     including files of the same name as well as their .pck versions.
    '''
    # Add copies of leftover files from the user source folder.
    # Do this before the proper writeout, so it can reuse functionality.
    Add_Source_Folder_Copies()

    # TODO: do a pre-pass on all files to do a test write, then if all
    #  look good, do the actual writes and log updates, to weed out
    #  bugs early.
    # Maybe could do it Clang style with gibberish extensions, then once
    #  all files, written, rename then properly.

    # Loop over the files that were loaded.
    for file_name, file_object in File_dict.items():

        # Skip if not modified.
        if not file_object.modified:
            continue

        # Look up the output path.
        file_path = file_object.Get_Output_Path()
        
        # In case the target directory doesn't exist, such as on a
        #  first run, make it.
        folder_path, _ = os.path.split(file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Rename any conflicting files, of same name or pck version.
        # These should never be old versions of the customize output,
        #  since the Cleanup call handled them.
        file_path_pck = Unpacked_Path_to_Packed_Path(file_path)
        for conflict_path in [file_path, file_path_pck]:

            # Skip if no such file exists.
            if not os.path.exists(conflict_path):
                continue

            # Get the backup path name.
            backup_path = Get_Backed_Up_Sys_Path(conflict_path)
            # Delete any old backup (this should be more or less safe,
            #  hopefully, if other checks were good.)
            if os.path.exists(backup_path):
                os.remove(backup_path)
            # Do the rename.
            os.rename(conflict_path, backup_path)

            # Record this to the log.
            Log_New.Record_File_Path_Renamed(conflict_path, backup_path)
            
            # Note: it is possible something will fail during a file write,
            #  in which case some files will have been written but not others,
            #  which can confuse any older logs (with old hashes).
            # As a clumsy workaround, the log will be written out freshly
            #  after every single written or renamed file for now.
            Log_New.Store()

        # Write out the file, using the object's individual method.
        file_object.Write_File(file_path)

        # Add this to the log, post-write for correct hash.
        Log_New.Record_File_Path_Written(file_path)

        # As above, refresh the log file.
        Log_New.Store()
        

    return


def Copy_File(
        source_virtual_path,
        dest_virtual_path = None
    ):
    '''
    Suport function to copy a file from a source folder under this project, 
     to a dest folder. Typically used for scripts, objects, etc.

    * source_virtual_path
      - Virtual path for the source file, which matches the folder
        structure in the project source folder.
    * dest_virtual_path
      - Virtual path for the dest location.
      - If None, this defaults to match the source_virtual_path.
    '''
    # Normally, the dest will just match the source.
    if dest_virtual_path == None:
        dest_virtual_path = source_virtual_path

    # Get the path for where to find the source file, and load
    #  its binary.
    with open(Virtual_Path_to_Project_Source_Path(source_virtual_path), 'rb') as file:
        source_binary = file.read()

    # Create a generic game object for this, using the dest path.
    Add_File(Misc_File(virtual_path = dest_virtual_path, 
                       binary = source_binary))

    return


def Version_Patch():
    '''
    Make any necessary changes to files and such when switching
    customizer versions.
    '''
    # If there is no log of the last version run, this is either the
    #  first run or the first in 2.23+.
    # In this case, clean out some old files from prior versions which
    #  used .x3c.bak as their renamed file suffix.
    if Log_Old.version == None or int(Log_Old.version.split('.')[0]) < 3:
        pass

        #-Removed; x3c.bak is used again, to avoid problem of the game
        # trying to read files with an xml extension automatically.
        #old_backup_suffix = '.x3c.bak'
        #
        ## Traverse the scripts folder.
        #for dir_path, folder_names, file_names in os.walk(
        #    os.path.join(Settings.Get_Addon_Folder(), 'scripts')):
        #
        #    # Loop over the file names.
        #    for file_name in file_names:
        #
        #        # Skip those without the looked for suffix.
        #        if not file_name.endswith(old_backup_suffix):
        #            continue
        #
        #        path = os.path.join(dir_path, file_name)
        #        original_path = path.replace(old_backup_suffix, '')
        #
        #        # There should be no non-suffixed version of the file,
        #        #  since it was a pck that was moved to avoid conflict.
        #        if os.path.exists(original_path):
        #            # Toss a warning and otherwise skip ahead.
        #            # (Note: currently, this will only get printed on the
        #            #  first run, so the file might linger around in later
        #            #  runs with no notices, but it should be okay as just
        #            #  a loose file.)
        #            print(('Warning: could not undo renaming of "{}"'
        #                  ' from older version due to "{}" being occupied').format(
        #                path, original_path))
        #            continue
        #
        #        # Do the rename.
        #        os.rename(path, original_path)


def Unpack_Pck_Scripts():
    '''
    Small script to unpack gzipped pck files in the current directory.
    Outputs are placed in scripts_pck_unpacked under this dir.
    TODO: touch up and integrate nicely; this was originally just written
    as a standalone to aid in grepping through packed scripts.
    '''
    from pathlib import Path
    import gzip

    output_path = Path('scripts_pck_unpacked')
    # Assumes the output_path exists.
    assert output_path.exists()

    for pck_file_name in Path('.').glob('*.pck'):
        print('Unpacking: ', pck_file_name)
    
        with open(pck_file_name, 'rb') as file:
            unpacked_binary = gzip.decompress(file.read())
        with open(output_path / pck_file_name.with_suffix('.xml'), 'wb') as file:
            file.write(unpacked_binary)