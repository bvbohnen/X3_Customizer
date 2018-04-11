'''
Support for reading source files, including unpacking from cat/dat files.
Includes File_Missing_Exception for when a file is not found.
Import as:
    from Source_Reader import *
'''
import os
from Common.Settings import Settings
from collections import OrderedDict
from .File_Types import *
from .Cat_Reader import *
import gzip

class File_Missing_Exception(Exception):
    '''Exception raised when Load_File doesn't find the file.'''
    pass


class Source_Reader_class:
    '''
    Class used to find and read the highest priority source files.

    The general search order is:
    * Source folder defined in the settings.
    * Scripts folder, if a script is being looked up.
    * Cat files in the addon folder numbered 01 through the highest
      contiguous 2-digit number, higher number taking precedence.
    * Cat files in the base X3 directory, treated similarly to the
      addon folder.

    Note: the addon/mods folder is ignored, due to ambiguity on which
    mod located there might be in use for a given game session.

    Loose source files in the game folders are ignored at this time,
    as these are assumed to be leftovers from prior runs of the
    customizer.

    Cat files will be parsed as they are reached in the search order,
    not before, to avoid excessive startup time when deeper cat files
    may never be needed.

    Attributes:
    * source_file_path_dict
      - Dict, keyed by file name (without path), holding the relative path
        for where the file is located, for files in the source folder
        specified in the Settings.
      - Path is relative to the source folder, and matches the virtual
        path except using system separators instead of forward slash.
    * script_file_path_dict
      - Dict, keyed by script name (without path), holding the full path
        for a script in the addon/scripts folder.
      - pending development.
    * catalog_file_dict
      - OrderedDict of Catalog_File objects, keyed by file path, organized
        by priority, where the first entry is the highest priority cat.
      - Early catalogs are from the addon folder, later catalogs are from
        the base x3 folder.
      - Dict entries are initially None, and get replaced with Catalog_Files
        as the cats are searched.
    '''
    def __init__(s):
        s.source_file_path_dict = {}
        s.catalog_file_dict = OrderedDict()


    def Init(s, transform_required_file_names = None):
        '''
        Initializes the file system by finding files in the source folder,
         and finding all cat files in priority order.
        This should be run after paths have been set up in Settings.

        * transform_required_file_names
          - List of strings, names of source files required by any transform.
          - Files with other names in the source folder will be ignored.
          - If None, all files in the source folder are included.
        '''
        # Error if the source folder isn't set yet.
        source_folder = Settings.Get_Source_Folder()
        assert source_folder != None
        
        # Dynamically find all files in the source folder.
        # These will all be copied at final writeout, even if not modified,
        #  eg. if a transform was formerly run on a file but then commented
        #  out, need to overwrite the previous results with a non-transformed
        #  version of the file.
        # Uses os.walk to go through the source folder and all subfolders.
        # Note: dir_path is the relative dir from the source folder, including
        #  the source folder. This could be removed by doing a nested walk
        #  from each folder in the source_folder, though this wouldn't work if
        #  the user just wanted to give a basic list of files to transform and
        #  manually handle moving around outputs.
        #  Edits to the path can remove the first folder, though are clumsy
        #  to implement.
        #  The working directory could be moved to the source directory
        #  temporarily for this, though starting walk using '.' will have
        #  that as the start of the path still (which might be fine).
        original_cwd = os.getcwd()
        os.chdir(source_folder)

        for dir_path, folder_names, file_names in os.walk('.'):
            # Loop over the file names.
            for file_name in file_names:

                # Skip misc files not required by transforms.
                # This is mainly intended to allow stuff like notes.txt
                #  to be sitting around at multiple points in the source
                #  folder without triggering a warning.
                # Only check this if a list of transform files was provided,
                #  otherwise include everything.
                if (transform_required_file_names != None
                    and file_name not in transform_required_file_names):
                    continue

                # Warn if the file already seen.
                if file_name in s.source_file_path_dict:
                    # Just print a message and continue.
                    print(('Warning: source file {} seen on multiple paths;'
                           ' defaulting to path {}')
                        .format(
                            file_name, 
                            os.path.join(
                                source_folder, 
                                s.source_file_path_dict[file_name])))
                    continue
                
                # Record the absolute path, with name.
                s.source_file_path_dict[file_name] = os.path.abspath(
                    os.path.join(dir_path, file_name))

        # Restore the working directory.
        os.chdir(original_cwd)
         
        
        # Search for cat files the game will recognize.
        # These start at 01.cat, and count up as 2-digit values until
        #  the count is broken.
        # For convenience, the first pass will fill in a list with low
        #  to high priority, then the list can be reversed at the end.
        cat_dir_list_low_to_high = []

        # Loop over the base x3 folder and the addon folder, doing x3
        #  first since it is lower priority.
        for path in [Settings.Get_X3_Folder(), Settings.Get_Addon_Folder()]:

            # Loop until a cat index not found.
            cat_index = 1
            while 1:
                # Error if hit 100.
                assert cat_index < 100
                cat_name = '{:02d}.cat'.format(
                    cat_index
                    )
                cat_path = os.path.join(path, cat_name)

                # Stop if the cat file is not found.
                if not os.path.exists(cat_path):
                    break

                # Record the path and increment for the next cat.
                cat_dir_list_low_to_high.append(cat_path)
                cat_index += 1
               

        # Note on the mods folder:
        # One cat/dat pair in the addon/mods folder can be selected for
        #  use by the game.  At this time, no effort has been put into
        #  knowing which pair a user might have selected, so mods applied
        #  in that way will be ignored for now.

        # Fill in dict entries with the list paths, in reverse order.
        for path in reversed(cat_dir_list_low_to_high):
            s.catalog_file_dict[path] = None

        return


    def Record_New_Source_File(s, file_name, file_path):
        '''
        Records a new file in the source folder, placed there after init.
        The provided path should be absolute.
        '''
        s.source_file_path_dict[file_name] = file_path


    #def Get_Source_File_Path(s, file_name):
    #    '''
    #    Returns the path to the given source file_name, from the addon
    #     directory.
    #    Path will be relative to the AP/addon/source directory, or
    #     equivelently that of the x3 internal path (such as for files
    #     found in the cat/dat files).
    #    If a path isn't known, returns None.
    #    '''
    #    # Check the source folder first.
    #    if file_name in s.source_file_path_dict:
    #        # Look up the path from the source folder, and add it to the
    #        #  path to the source folder.
    #        return os.path.join(Settings.Get_Source_Folder(), 
    #                            File_path_dict[file_name], 
    #                            file_name)
    #    return None


    def Read(s, 
             file_name,
             error_if_not_found = True,
             copy_to_source_folder = False
             ):
        '''
        Returns a Game_File including the contents read from the
         source folder or unpacked from a cat file.
        Contents may be binary or text, depending on the Game_File subclass.
        This will search for packed versions as well, automatically unzipping
         the contents.

        * file_name
          - Name of the file, optionally including relative path.
          - For files which may be gzipped into a pck file, give the
            expected non-zipped extension (.xml, .txt, etc.).
          - If path included, it should be the format of the cat files,
            using forward slashes, and will be used to help resolve the
            lookup incase multiple files share names on different paths.
        * error_if_not_found
          - Bool, if True an exception will be thrown if the file cannot
            be found, otherwise None is returned.
        * copy_to_source_folder
          - Bool, if True and the file is read from a cat/dat pair, then
            a copy of the data will be placed into the source folder.
          - The copy is made after any unzipping is applied.
          - Pending development.
        '''
        # First step is to get the binary for the file, wherever it
        #  comes from.
        file_binary = None

        # Grab the extension.
        file_extension = file_name.rsplit('.',1)[1]
        # Determine the name for a possibly packed version.
        file_name_pck = file_name.rsplit('.',1)[0] + '.pck'
        # Flag to indicate if the binary was loaded from a pck file, and
        #  needs unzipping.
        file_binary_is_zipped = False

        # Record either a path to a source file on the hard disk, or
        #  a path in the cat/dat structure, depending on where the
        #  file is found.
        source_path_name = None
        cat_path_name = None


        # Check the source folder for a simple name match.
        # TODO: consider supporting full path matches for this.
        # Pck takes precedence over other files when X3 loads them.
        for test_file_name in [file_name_pck, file_name]:
            # Skip if not found.
            if test_file_name not in s.source_file_path_dict:
                continue

            # Open the file and grab the binary data.
            # If this needs to be treated as text, it will be
            #  reinterpretted elsewhere.
            with open(s.source_file_path_dict[test_file_name], 'rb') as file:
                file_binary = file.read()
                # If it was pck, clarify as zipped.
                file_binary_is_zipped = test_file_name.endswith('.pck')
                # Record the path used.
                source_path_name = s.source_file_path_dict[test_file_name]
                
            # Don't check the other suffix after a match is found.
            break


        # TODO: find files in the script folder, or other bare files.
        # (This may need to mess around with checking for backed up
        #  versions, which were renamed to avoid getting overwritten
        #  on prior customizer runs.)
        #if file_binary == None:
        #    if file_name in s.script_file_path_dict:
        #        pass

        # If still no binary found, check the cat/dat pairs.
        if file_binary == None:
            # Loop over them in priority order.
            for cat_path, cat_reader in s.catalog_file_dict.items():

                # If the reader hasn't been created, make it.
                if cat_reader == None:
                    cat_reader = Cat_Reader(cat_path)
                    s.catalog_file_dict[cat_path] = cat_reader

                # Loop over the pck and standard versions.
                # Note: this is done in the inner loop, check each cat
                #  for a pck or non-pck before moving on to the next.
                # (It is unclear on how the game handles this, though it
                #  should be fine since the cats are expected to not
                #  mix packed and unpacked versions.)
                for test_file_name in [file_name_pck, file_name]:

                    # Check the cat for the file.
                    file_binary = cat_reader.Read(test_file_name)
                    if file_binary == None:
                        continue

                    # If it returned something, then it matched, so can
                    #  stop searching.
                    # If it was pck, clarify as zipped.
                    file_binary_is_zipped = test_file_name.endswith('.pck')
                    # Record the path used in the cat file.
                    cat_path_name = cat_reader.Get_Path(test_file_name)
                    if file_name.startswith('Jobs'):
                        print('Found Jobs.pck in cat {}'.format(cat_reader.cat_path))
                    break

                # Stop looping over cats once a match found.
                if file_binary != None:
                    break


        # If no binary was found, error.
        if file_binary == None:
            if error_if_not_found:
                raise File_Missing_Exception(
                    'Could not find a match for file {}'.format(file_name))
            return None


        # Decompress if needed.
        if file_binary_is_zipped:
            file_binary = gzip.decompress(file_binary)
            # Normalize the path name used to always be uncompressed.
            if source_path_name:
                source_path_name = source_path_name.replace('.pck', '.'+file_extension)
            if cat_path_name:
                cat_path_name = cat_path_name.replace('.pck', '.'+file_extension)

        # Convert the binary into a Game_File object.
        # The object constructors will handle parsing of binary data,
        #  so this just checks file extensions and picks the right class.
        if file_extension == 'xml':
            game_file_class = XML_File         
        elif file_extension == 'obj':
            game_file_class = Obj_File
        elif file_extension == 'txt':
            game_file_class = T_File
        else:
            raise Exception('File type for {} not understood.'.format(file_name))

        # Construct the game file.
        # These will also record the path used, to help know where to place
        #  an edited file in the folder structure.
        game_file = game_file_class(
            file_binary = file_binary,
            source_path_name = source_path_name,
            cat_path_name = cat_path_name
            )
        
        return game_file


# Single, global copy of the reader.
# TODO: make a copy part of a File_System or similar object, instead
#  of keeping one here.
Source_Reader = Source_Reader_class()