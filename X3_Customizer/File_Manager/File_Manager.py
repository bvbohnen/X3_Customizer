'''
Loads and stores source files to be modified, and writes them
out when finished.
'''

from .File_Fields import *
import os
from collections import OrderedDict
import inspect
import shutil
from Common.Settings import Settings
from .Source_Reader import *
from .File_Types import *

# TODO: move this somewhere more convenient, eg. the Settings module.
def Set_Path(
        path_to_addon_folder,
        source_folder = 'x3_customizer_source_files',
        log_folder = 'x3_customizer_logs',
        summary_file = 'X3_Customizer_summary.txt',
        log_file = 'X3_Customizer_log.json',
    ):
    '''
    Sets the pathing to be used for file loading and writing.

    * path_to_addon_folder
      - Path to the X3 AP addon folder, containing the source_folder.
        Output files will be written relative to here.
      - If this is not the addon folder, a warning will be printed but
        operation will continue, writing files to this folder, though
        files will need to be moved to the proper addon folder to be
        applied to the game. Some generated files may be placed in
        the directory above this folder, eg. the expected TC directory.

    * source_folder
      - Subfolder in the addon directory containing unmodified files, 
        internally having the same folder structure as addon to be
        used when writing out transform results.
      - Folder will be created if it does not exist, and may be
        populated with any source files that can be extracted from
        the primary folders and are needed by transforms.
      - Defaults to 'x3_customizer_source_files'.
      - (eg. output to addon\types will source from input in
         addon\source_folder\types).

    * log_folder
      - String, the path to the folder to place any output logs in, or
        to read prior output logs from.
      - Defaults to 'x3_customizer_logs'.

    * summary_file
      - Name for where a summary file will be written, with
        any transform results, relative to the log folder.
      - Defaults to 'X3_Customizer_summary.txt'.

    * log_file
      - Name for where a json log file will be written,
        including a summary of files written.
      - This is also the file which will be read for any log from
        a prior run.
      - Defaults to 'X3_Customizer_log.json'.
    '''
    Settings.Set_Addon_Folder(path_to_addon_folder)
    Settings.Set_Source_Folder(source_folder)
    Settings.Set_Log_Folder(log_folder)
    Settings.Set_Message_File(summary_file)
    Settings.Set_Log_File(log_file)

    # Call to generic Init moved here, to ensure it is applied before
    # any transforms which may not use input files.
    Init()
    return


# Track the file object, to append to it on the fly.
Message_file = None
def Write_Summary_Line(line, no_newline = False):
    '''
    Write a line to the summary file.
    A newline is inserted automatically if no_newline == False.
    '''
    global Message_file
    # Open the file if needed.
    if Message_file == None:
        Message_file = open(Settings.Get_Message_File_Path(), 'w')
    Message_file.write(line + '\n' if not no_newline else '')
    

Flag_disable_cleanup_and_writeback = False
def Disable_Cleanup_and_Writeback():
    '''
    Set flag to disable cleanup and file writing at the end of the
    program. This is mainly for use with the patch builder and
    any related development transforms not intended to modify
    the game files.
    '''
    global Flag_disable_cleanup_and_writeback
    Flag_disable_cleanup_and_writeback = True

    
# Make a set of all transform file names that may be used by transforms,
#  used in filtering the source files tracked.
# This gets filled in by decorators, which should all get processed before
#  the first call to Init (through a call to Load_File) occurs and uses
#  this set.
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
    # TODO: remove this check, and remove all calls to Init except for that
    #  in Set_Path, which should always be called before anything else
    #  anyway.
    global First_call
    if not First_call:
        return
    First_call = False

    # The file paths should be defined at this point. Error if not.
    Settings.Verify_Setup()

    # Initialize the file system, now that paths are set in settings.
    Source_Reader.Init(Transform_required_file_names)
    
    # Set the working directory to the AP directory.
    # This makes it easier for transforms to generate any misc files.
    os.chdir(Settings.Get_Addon_Folder())

    return


# Dict to hold file contents, as well as specify their full path.
# Keyed by file name with path.
# This gets filled in by transforms as they load the files.
# T files will generally be loaded into lists of dictionaries keyed by field
#  name or index, with each list entry being a separate line.
# XML files will generally be loaded as a XML_File object holding
#  the encoding and raw text.
# These are Game_File objects, and will record their relative path
#  to be used during output.
File_dict = {}


def Add_File(file_name, game_file):
    '''
    Add a Game_File object to the File_dict.
    '''
    File_dict[file_name] = game_file


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
from functools import wraps
def Check_Dependencies(*file_names, category = None):
    # Record the required file names to a set for use elsewhere.
    Transform_required_file_names.update(file_names)

    # Make the inner decorator function, capturing the wrapped function.
    def inner_decorator(func):

        # Attach the required file_names to the wrapped function,
        #  since they are only available on function definition at the
        #  moment, and will be checked at run time.
        func._file_names = file_names
        # Attach the override category to the function.
        # TODO: maybe fill in the default category here, but for now
        #  it is done in Make_Documentation.
        func._category = category

        # Record the transform function.
        Transform_list.append(func)

        # Set up the actual function that users will call, capturing
        #  any args/kwargs.
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Note this transform as being seen.
            Transforms_names_run.add(func.__name__)
            
            # On the first call, do some extra setup.
            if First_call:
                Init()

            # Loop over the required files.
            for file_name in func._file_names:
                # Do a test load; if succesful, the file was found.
                try:
                    Load_File(file_name)
                except File_Missing_Exception:
                    print('Skipped {}, required file {} not found.'.format(
                        func.__name__,
                        file_name
                        ))
                    # Return nothing and skip the call.
                    return
            # Return the normal function call results.
            return func(*args, **kwargs)

        # Return the callable function.
        return wrapper

    # Return the decorator to handle the function.
    return inner_decorator


#def Get_Source_File_Path(file_name):
#    '''
#    Returns the path to the given source file_name, from the addon directory.
#    Path will be relative to the AP/addon/source directory.
#    If a path isn't known, returns None.
#    '''
#    if file_name in Source_Reader.source_file_path_dict:
#        # Look up the path from the source folder, and add it to the
#        #  path to the source folder.
#        return os.path.join(Settings.Get_Source_Folder(), 
#                            Source_Reader.source_file_path_dict[file_name], 
#                            file_name)
#    return None
#
#
#def Get_Output_File_Path(file_name):
#    '''
#    Returns the path to the given output file_name, from the addon directory.
#    Path will be relative to the AP/addon directory.
#    '''
#    if file_name in Source_Reader.source_file_path_dict:
#
#        # Special case: obj files need to go a higher level than the
#        #  addon directory.
#        if file_name.endswith('.obj'):
#            # Stick this one folder up, in the L folder.
#            folder_path = os.path.join('..', 'L')
#        else:
#            # Look up the path from the source folder, and add it to the
#            #  path to the AP/addon folder, eg. the working directory.
#            folder_path = Source_Reader.source_file_path_dict[file_name]
#
#        # Construct the full file path.
#        file_path = os.path.join(folder_path, file_name)
#
#        # Quick safety check: error if matches the source file path.
#        source_file_path = Get_Source_File_Path(file_name)
#        assert file_path != source_file_path
#
#        # In case the target directory doesn't exist, such as on a
#        #  first run, make it.
#        if not os.path.exists(folder_path):
#            os.mkdir(folder_path)
#        return file_path
#
#    # Shouldn't be here.
#    raise Exception('Failed to find output path for file {}'.format(file_name))
#    return


def Load_File(file_name,
              return_t_file = False, 
              return_text = False,
              error_if_not_found = True):
    '''
    Returns the contents of the given file, either raw text for XML
     or a dictionary for T files.
    If the file has not been loaded yet, reads from the expected
     source file.
    If the file is not found and error_if_not_found == True, 
     raises an exception, else returns None.
    If return_t_file == True, returns the T_File object instead of just
     the trimmed dict of data lines; does not work on xml files.
    If return_text == True, returns the raw text of the loaded file,
     without any edits from prior transforms applied.
    If the source file is not found, will attempt to find the file in
     a non-source folder and copy it to the source folder before proceeding;
     this will attempt to unpack script .pck files.
    '''
    # If the file is not loaded, handle loading.
    if file_name not in File_dict:

        # Get the file using the source_reader, maybe pulling from
        #  a cat/dat pair.
        # Returns a Game_File object, of some subclass, or None
        #  if not found.
        game_file = Source_Reader.Read(file_name, error_if_not_found = False)

        # Problem if the file isn't found.
        if game_file == None:

            # Do a fallback search to find the file in a primary folder
            #  and copy to the source folder, then try again.
            # This returns True if it made a copy; error if it fails
            #  to copy.
            # TODO: integrate this into the source_reader fully, and
            #  remove this code.
            if not Find_and_Copy_Source_File(file_name):
                if error_if_not_found:
                    raise File_Missing_Exception()
                return None
            # Try again; allow this to error this time, regardless of
            #  the arg flag, since this should always find the copied
            #  file.
            game_file = Source_Reader.Read(file_name)

        # Store the contents in the File_dict.
        Add_File(file_name, game_file)


    # Return the file contents.
    if return_t_file:
        return File_dict[file_name]
    elif return_text:
        return File_dict[file_name].text
    else:
        return File_dict[file_name].Read_Data()


# TODO: switch cleanup to being something that runs at program start,
#  getting rid of prior run files (recorded in a json or possibly with
#  annotation comments, but json is simplest), and renaming any
#  x3c.bak files to their original.
# While redundant somewhat, pre-cleanup is easier to work with, since
#  later code can ignore backups and such, simplifying it.            
def Cleanup():
    '''
    Handles cleanup of old transform files, generally aimed at transforms
    which were not run and which have a cleanup attribute.
    '''
    # Skip when not cleaning up.
    if Flag_disable_cleanup_and_writeback:
        return
    # Loop over the transforms.
    for transform in Transform_list:
        # Skip if this was run, since it should handle its own cleanup
        #  as needed based on input args.
        if transform.__name__ in Transforms_names_run:
            continue

        # Look up the arg names first (ignore the *args, **kwargs names).
        argspec = inspect.getargspec(transform)
        # Check if this transform has a cleanup method.
        if '_cleanup' in argspec.args:
            # Run the transform in cleanup mode.
            transform(_cleanup = True)

                
def Write_Files():
    '''
    Write output files for all source file content edited by transforms.
    Outputs will overwrite any existing files.
    Any .pck files with otherwise the same name and location will be
    renamed into .pck.x3c.bak; there is currently no code to rename
    these back to .pck, since source files are always assumed modified.
    '''
    # Skip when not cleaning up.
    if Flag_disable_cleanup_and_writeback:
        return

    # Keep a record of files written, to be placed in a json to know
    #  activities from run to run.
    # Just need paths for now.
    file_paths_written = []

    # Loop over the files that were loaded.
    for file_name, file_object in File_dict.items():

        # Look up the output path.
        file_path = file_object.Get_Output_Path()
        file_paths_written.append(file_path)
        
        # In case the target directory doesn't exist, such as on a
        #  first run, make it.
        folder_path, _ = os.path.split(file_path)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        # Handle T files.
        if isinstance(file_object, T_File):
            file_object.Write_File(file_path)

            # For some reason, TwareT has a pck version created sometimes,
            #  which ends up overriding the custom version.
            # (This may be from the mod manager program, which may cause
            #  oddities; TODO: look into this.)
            # If a pck file exists, rename it further below.
            pck_file_path = file_path.replace('.txt','.pck')


        # Handle xml files.
        elif isinstance(file_object, XML_File):
            pck_file_path = file_path.replace('.xml','.pck')
            file_object.Write_File(file_path)


        # Handle obj files.
        elif isinstance(file_object, Obj_File):
            # No pck files for these.
            pck_file_path = None
            file_object.Write_File(file_path)

        # Handle generic files.

        # Check for a pck version of the file.
        if pck_file_path and os.path.exists(pck_file_path):
            #Just stick a suffix on it, so it isn't completely gone.
            os.rename(pck_file_path, pck_file_path + '.x3c.bak')


    # Loop over the files that were not loaded. These may need to be included
    #  in case a prior run transformed them, then the transform was removed
    #  such that they weren't loaded but need to overwrite old changes.
    # These will do direct copies.
    # TODO: consider cases with a .pck.x3c.bak version exists, and rename
    #  that to .pck instead, though this may not be entirely safe if the
    #  version in the source folder is different than the pck version,
    #  so don't implement this for now.
    for file_name in Source_Reader.source_file_path_dict:
        # Skip the loaded files.
        if file_name in File_dict:
            continue

        # Look up the source path.
        source_file_path = Source_Reader.source_file_path_dict[file_name]

        # Create a basic Game_File object, with no data content, to
        #  reuse its path handling.
        game_file = Game_File(source_path_name = source_file_path)

        # Look up the output path.
        dest_file_path = game_file.Get_Output_Path()
        
        # Do the copy.
        shutil.copy(source_file_path, dest_file_path)
        file_paths_written.append(dest_file_path)


    # Write a record of which files were written.
    # This will be packed into a generic log, a dict with multiple
    #  entries where this is the first.
    log_dict = {
        'file_paths_written': file_paths_written
        }
    import json
    with open(Settings.Get_Log_File_Path(), 'w') as file:
        json.dump(log_dict, file, indent = 2)

    return


def Copy_File(
        source_path,
        dest_path,
        remove = False
    ):
    '''
    Suport function to copy a file from a source folder under this project, 
     to a dest folder. Typically used for scripts, objects, etc.
    The source_path will be based on this project directory.
    The dest_path will be based on the AP/addon directory.
    This handles removal of the copied file as well, for when the calling
     transform wasn't selected.
    If a file was already present at the destination, it will be overwritten.
    '''
    # Look up this project directory, and prefix the source_path.
    this_dir = os.path.normpath(os.path.dirname(__file__))
    source_path = os.path.join(this_dir, '..', source_path)
        
    # Continue based on if removal is being done or not.
    if not remove:        
        # Error if the file is not found locally.
        if not os.path.exists(source_path):
            print('Copy_File error: no file found at {}.'.format(source_path))
            return
        # Create the folder if needed.
        folder_path = os.path.dirname(dest_path)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        # Perform the copy.
        shutil.copy(source_path, dest_path)
    else:
        # Check if the file exists from a prior run.
        if os.path.exists(dest_path):
            # Remove the file.
            os.remove(dest_path)
    return


import gzip
def Find_and_Copy_Source_File(file_name):
    '''
    Attempts to find a given file_name in a primary folder in
     the addon directory. If found, the file is copied to the
     source_folder with an appropriate path.
    If a match is found in the script folder for a pck file,
     it will be unzipped and copied as an xml file.
    Currently, this only searches the script folder for pck files,
     though the file_name should end in .xml.
    Returns True if a file was copied over, else False
    '''
    # During development, if a file was forgotten in the transform
    # dependencies, it can end up getting copied on every run.
    # This is extra awkward for xml files, which get overwritten
    # after modification, then the edited version copied into the
    # source folder again.
    # To help catch these cases, check here if the file_name is
    # in the Transform_required_file_names, warn if not.
    if file_name not in Transform_required_file_names:
        raise Exception(
            'Error: file {} is not in Transform_required_file_names,'
            ' add it to a transform to avoid potential errors'.format(
                 file_name))

    folders_to_search = ['scripts']
    copy_made = False
    for folder in folders_to_search:
        if folder == 'scripts':

            # The file_name should end in xml; skip if it doesn't.
            if not file_name.endswith('.xml'):
                continue
            # Strip off the .xml for now.
            file_name_unsuffixed = file_name.replace('.xml','')

            # Look for a valid file path for the pck extentions.
            # This will also look for a backed up file from a prior run
            # of this manager.
            # In case a loose .xml file is the target, check for that as
            # well.
            file_path = None
            for extension in ['.pck', '.pck.x3c.bak', '.xml', '.xml.x3c.bak']:
                this_path = os.path.join(folder, file_name_unsuffixed + extension)
                if os.path.exists(this_path):
                    file_path = this_path
                    break

            # If no valid path found, skip.
            if file_path == None:
                continue
            
            # Note: in the xml source case, the original file will be
            # overwritten during writeback after all transforms are
            # finished. This should be safe overall, since the copy
            # of the file placed in the source folder will be unchanged.
            # The only danger is the source folder name being switched
            # without a clean run of the customizer to restore all files
            # from the prior folder name.
            # Treat this as an unlikely case and mostly ignore it for now,
            # but be a little safe and make a backup if there is none.
            if extension == '.xml':
                backup_path = os.path.join(folder, file_name_unsuffixed + '.xml.x3c.bak')
                if not os.path.exists(backup_path):
                    shutil.copy(file_path, backup_path)


            # Read the source text.
            # X3 pck files were compressed using gzip, so use that package
            # here to decompress.
            if '.pck' in extension:
                #try:
                # Gzip uses a generic 'r' tag, but returns binary.
                with gzip.open(file_path,'r') as file:
                    text = file.read()
                #except:
                #    continue
            else:
                # Explicitly read binary.
                with open(file_path,'rb') as file:
                    text = file.read()

            # This text can now be written out as xml.
            # Make sure the dest folder exists.
            dest_folder = os.path.join(Settings.Get_Source_Folder(), folder)
            if not os.path.exists(dest_folder):
                os.mkdir(dest_folder)

            # Write the file, as binary.
            dest_path = os.path.join(dest_folder, file_name)
            with open(dest_path, 'wb') as file:
                file.write(text)

            # Record the file and path in the File_path_dict, which did 
            # not see this file on the first run.
            Source_Reader.source_file_path_dict[file_name] = dest_path

            # Stop searching the folders.
            copy_made = True
            break

    return copy_made


# TODO: move this to a class method, which transforms are set
#  up to access.
def Add_Entries_To_T_File(t_file_name, new_entry_list):
    '''
    Convenience function to add new lines to a t file.
    t_file_name:
      Name of the tfile to edit, with .txt extension.
    new_entry_list:
      List of OrderedDict entries matching the tfile's line format.
    '''
    # Return early if the list is empty.
    if not new_entry_list:
        return

    # All new entries will be put at the bottom of the tfile dict_list.
    # This will require that the header be modified to account for the
    # new lines.
    t_file = Load_File(t_file_name, return_t_file = True)

    # Set how many columns are expected in the header line, based on
    # the t file name, along with which column/index holds the
    # entry counter.
    # Error when a new t file seen; this somewhat has to be done
    # manually.
    if t_file_name == 'TShips.txt':
        header_columns = 3
        index_with_count = 1
    elif t_file_name == 'TFactories.txt':
        header_columns = 3
        index_with_count = 1
    elif t_file_name == 'Globals.txt':
        header_columns = 2
        index_with_count = 0
    elif t_file_name == 'WareLists.txt':
        header_columns = 2
        index_with_count = 0
    else:
        raise Exception()

    # Add the new entries.
    # These need to go in both the data and line lists, data for future
    # visibility to this and other transforms, lines to be seen at
    # writeout.
    t_file.data_dict_list += new_entry_list
    t_file.line_dict_list += new_entry_list

    # Find the header line.
    for line_dict in t_file.line_dict_list:
            
        # To normalize handling when the dict could have indexed or named
        # keys, pull out the first key (for comment checks) and the key
        # with the counter.
        keys = list(line_dict.keys())
        first_key, count_key = keys[0], keys[index_with_count]

        # Looking for the first non-comment line; it should have
        # header_columns entries (with newline).
        if (not line_dict[first_key].strip().startswith('/') 
        and len(line_dict) == header_columns):
            # The second field is the entry count, to be updated.
            line_dict[count_key] = str(int(line_dict[count_key]) 
                                              + len(new_entry_list))
            # Can stop looping now.
            break

        # Error if hit a data line.
        if line_dict is t_file.data_dict_list[0]:
            raise Exception()

    return