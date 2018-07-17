'''
Support for reading source files, including unpacking from cat/dat files.
Includes File_Missing_Exception for when a file is not found.
Import as:
    from Source_Reader import *
'''
import os
from pathlib import Path # TODO: convert all from os to pathlib.
from ..Common.Settings import Settings
from .Logs import *
from collections import OrderedDict
from .File_Types import *
from .File_Paths import *
from .Cat_Reader import *
from .. import Common
import gzip

'''
Notes on X3 Plugin Manager generated TWareT.pck file:
    This file does not work with standard gzip, though does appear to
    open with X3 Editor 2.
    Exploration into reasons led down this path:
        - Look through X3 Editor source code (c#) to trace compression.
        - This uses x2fd.dll.
        - Look through x2fd source code (c++).
        - Find a file reading in catpck.cpp, function DecompressBuffer.

    The apparent decompression used is:
        magic_value = bytestream[0] ^ 0xC8
        file_binary_demagicked = bytestream[1:] ^ magic_value
        file_contents = gzip.decompress(file_binary_demagicked)

    This does not match up with the magic values or approaches used
    in the actual cat files (running magic value for cats, 0x33 for dats,
    no dropping of the first byte), and the standalone pck files in scripts
    are all plain gzipped.

    At any rate, if normal gzip fails, this decompression can be applied
    as a second pass to see if it works better.

'''


class Source_Reader_class:
    '''
    Class used to find and read the highest priority source files.

    The general search order is:
    * Source folder defined in the settings.
    * Loose folders, including scripts.
    * Cat files in the addon folder numbered 01 through the highest
      contiguous 2-digit number, higher number taking precedence.
    * Cat files in the base X3 directory, treated similarly to the
      addon folder.

    Note: the addon/mods folder is ignored, due to ambiguity on which
    mod located there might be in use for a given game session.

    Files which were generated on a prior customizer run (identified
    by matching a hash in the prior run's log) will be skipped.
    Files which were backed up on a prior run will be checked.
    
    Cat files will be parsed as they are reached in the search order,
    not before, to avoid excessive startup time when deeper cat files
    may never be needed.

    Attributes:
    * source_file_path_dict
      - Dict, keyed by virtual_path, holding the system path
        for where the file is located, for files in the source folder
        specified in the Settings.
    * script_file_path_dict
      - Dict, keyed by script name (without path), holding the full path
        for a script in the addon/scripts folder.
      - pending development.
    * catalog_file_dict
      - OrderedDict of Cat_Reader objects, keyed by file path, organized
        by priority, where the first entry is the highest priority cat.
      - Early catalogs are from the addon folder, later catalogs are from
        the base x3 folder.
      - Dict entries are initially None, and get replaced with Catalog_Files
        as the cats are searched.
    * file_to_cat_dict
      - Dict, keyed by file name, with the Cat_Reader object that holds
        the file with the highest priority.
      - Used for code result reuse, and is not an exhaustive list.
    * prior_customizer_cat_path
      - String, path for any catalog file from a prior customizer run.
      - The dat file has a matched path, changing extension.
      - This path may need to get replaced with an empty cat file if the
        user added more catalogs after the prior run, to maintain indexing
        order.
    * prior_customizer_cat_needs_dummy
      - Bool, if True then a dummy catalog should be generated using the
        prior_customizer_cat_path during file cleanup (after the prior
        cat is deleted normally).
      - Any new catalog file will always be at least 2 steps higher than
        the prior cat file in this case.
    '''
    def __init__(s):
        s.source_file_path_dict = {}
        s.catalog_file_dict = OrderedDict()
        s.file_to_cat_dict = {}
        s.prior_customizer_cat_path = None
        s.prior_customizer_cat_needs_dummy = False

    def Init(s):
        '''
        Initializes the file system by finding files in the source folder,
         and finding all cat files in priority order.
        This should be run after paths have been set up in Settings.
        '''
        # Look up the source folder.
        source_folder = Settings.Get_Source_Folder()
        
        # If it is not None, look into it.
        if source_folder != None:

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
                    # Record the absolute path.
                    s.Record_New_Source_File( os.path.abspath(
                        os.path.join(dir_path, file_name)))

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

                # Record the path if the cat is not from a prior run.
                if not Log_Old.File_Is_From_Last_Run(cat_path):
                    cat_dir_list_low_to_high.append(cat_path)

                    # If a prior cat file was found before this, then this
                    #  was added by the user since the last customizer run.
                    # If this cat file is not the highest priority,
                    #  toss a warning, since this indicates the user added
                    #  a higher numbered cat since the last customizer
                    #  run.
                    # Only print this warning once, by checking the dummy
                    #  flag.
                    if (s.prior_customizer_cat_path != None
                    and s.prior_customizer_cat_needs_dummy == False):
                        s.prior_customizer_cat_needs_dummy = True
                        print('Warning: cat file {} is from a prior'
                                ' Customizer run but is not the highest'
                                ' numbered cat file.'.format(
                                    s.prior_customizer_cat_path))
                else:
                    s.prior_customizer_cat_path = cat_path

                # Increment for the next cat.
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


    def Get_Next_Higher_Cat_Index(s):
        '''
        Returns a 2-digit string, the next catalog index, 1 higher than
        the existing highest index when ignoring any catalogs generated
        by prior runs. To be used if writing modified files to a catalog.
        '''
        # The first catalog_file_dict entry is the highest priority.
        # This will get the file path.
        # Convert to a Path for convenience.
        highest_index_path = Path(next(iter(s.catalog_file_dict.keys())))

        # Get the index.
        highest_index = int(highest_index_path.stem)

        # Increment and convert back to a 2-digit string.
        next_index_str = '{:02}'.format(highest_index + 1)
        assert len(next_index_str) == 2
        return next_index_str


    def Record_New_Source_File(s, sys_path):
        '''
        Records a new file in the source folder, placed there after init.
        The provided path should be absolute.
        '''
        virtual_path = System_Path_to_Virtual_Path(sys_path)
        s.source_file_path_dict[virtual_path] = sys_path
        

    def Decompress(s, file_binary, virtual_path):
        '''
        Decompress the given binary using gzip.
        This will attempt to decompress the binary as-is, and if failing,
        will decompress as if an x2 file (gzipped with an xor pass and
        prefix byte) to support X3 Plugin Manager generated pck files.

        * file_binary
          - Byte string or Bytearray with the original file binary data.
        * virtual_path
          - String, virtual path of the file to look up.
          - Only used for printouts.
        '''
        try:
            decompressed_binary = gzip.decompress(file_binary)
        except:
            # Print a nice message in dev mode to indicate this fallback
            #  code is being used. TODO: remove this if code seems robust.
            if Settings.developer:
                print('First gzip pass on {} failed, attempting to apply'
                     ' x2 style decompression.'\
                    .format(virtual_path))

            # Try method 2.  See notes way up above for what is
            #  going on, but in short, the first byte xors with 0xC8
            #  to get a magic value to Xor with all other bytes, then
            #  that is all decompressed with gzip.
            magic = file_binary[0] ^ 0xC8
            file_binary = bytearray(x ^ magic for x in file_binary)

            try:
                # Toss the first byte for this.
                decompressed_binary = gzip.decompress(file_binary[1:])
            except Exception as ex:
                if Settings.developer:
                    # Dev mode will give a little extra info.
                    print('Gzip error for file {}'.format(virtual_path))
                    raise ex
                else:
                    # Swap to a generic exception.
                    raise Common.Gzip_Exception()

        return decompressed_binary


    def Read(s, 
             virtual_path,
             error_if_not_found = True,
             copy_to_source_folder = False
             ):
        '''
        Returns a Game_File including the contents read from the
         source folder or unpacked from a cat file.
        Contents may be binary or text, depending on the Game_File subclass.
        This will search for packed versions as well, automatically unzipping
         the contents.
        If the file contents are empty, this returns None; this may occur
         for LU dummy files.
         
        * virtual_path
          - String, virtual path of the file to look up.
          - For files which may be gzipped into a pck file, give the
            expected non-zipped extension (.xml, .txt, etc.).
        * error_if_not_found
          - Bool, if True an exception will be thrown if the file cannot
            be found, otherwise None is returned.
        * copy_to_source_folder
          - Bool, if True and the file is read from a cat/dat pair, then
            a copy of the data will be placed into the source folder.
          - The copy is made after any unzipping is applied.
          - Pending development.
        '''
        # Grab the extension.
        file_extension = virtual_path.rsplit('.',1)[1]
        # Determine the name for a possibly packed version.
        # This is None if the file is not expected to be packed.
        virtual_path_pck = Unpacked_Path_to_Packed_Path(virtual_path)

        # Flag to indicate if the binary was loaded from a pck file, and
        #  needs unzipping.
        file_binary_is_zipped = False
        

        # Binary data read from a file.
        # Once a source is found, this will be filled in, so later
        #  source checks can be skipped once this is not None.
        file_binary = None
        # For debug, the path of the file sourced from, maybe a cat.
        file_source_path = None

        # Check the source folder.
        # This could do a full path check, but will reuse the parsed
        #  files found during Init.
        # Pck takes precedence over other files when X3 loads them.
        for test_virtual_path in [virtual_path_pck, virtual_path]:
            # Skip empty packed paths.
            if test_virtual_path == None:
                continue
            # Skip if not found.
            if test_virtual_path not in s.source_file_path_dict:
                continue

            # Open the file and grab the binary data.
            # If this needs to be treated as text, it will be
            #  reinterpretted elsewhere.
            file_source_path = s.source_file_path_dict[test_virtual_path]
            with open(file_source_path, 'rb') as file:
                file_binary = file.read()
                # If it was pck, clarify as zipped.
                file_binary_is_zipped = test_virtual_path == virtual_path_pck
                
            # Don't check the other suffix after a match is found.
            break


        # Check for a loose file outside the source folder, unless
        #  this is disabled in the settings.
        if file_binary == None and Settings.ignore_loose_files == False:
            sys_path = Virtual_Path_to_System_Path(virtual_path)
            sys_path_pck = Unpacked_Path_to_Packed_Path(sys_path)

            # Loop over pck and standard versions.
            for test_sys_path in [sys_path_pck, sys_path]:
                # Skip empty packed paths.
                if sys_path_pck == None:
                    continue

                # Following checks will look for a renamed file or a file with
                #  the original name.
                # TODO: consider doing a more generic renamed file check.
                file_path_to_source = None

                # If the file was not created by the customize on a previous
                #  run, and exists, use it.
                # This allows a user to overwrite a customizer file with a new
                #  version, and have it get used over any prior backup.
                if (not Log_Old.File_Is_From_Last_Run(test_sys_path)
                and os.path.exists(test_sys_path)):
                    file_path_to_source = test_sys_path
                
                # Check if there is a renamed version of the file, if the main
                #  path was not valid.
                if file_path_to_source == None:
                    renamed_sys_path = Log_Old.Get_Renamed_File_Path(test_sys_path)
                    # Source from the renamed file, if it still exists.
                    if (renamed_sys_path != None
                    and os.path.exists(renamed_sys_path)):
                        file_path_to_source = renamed_sys_path
                    
                # If no path found, go to next loop iteration.
                if file_path_to_source == None:
                    continue

                # Load from the selected file.
                file_source_path = file_path_to_source
                with open(file_path_to_source, 'rb') as file:
                    file_binary = file.read()
                    # If it was pck, clarify as zipped.
                    # (Use the test_sys_path, since the actual path may
                    #  have a backup extension.)
                    file_binary_is_zipped = test_sys_path == sys_path_pck


        # If still no binary found, check the cat/dat pairs.
        # Special check: if looking for a script, they are never
        #  in the cat/dats, so can skip checks early.
        # Note: it is possible unpacked versions of files (with a packed
        #  version) are not recognized in catalogs by the game, but this
        #  will look for them anyway.
        if (file_binary == None
        and not virtual_path.startswith('scripts/')):

            # Get the cat versions of the file path.
            cat_path = Virtual_Path_to_Cat_Path(virtual_path)
            cat_path_pck = Unpacked_Path_to_Packed_Path(cat_path)

            # Loop over the cats in priority order.
            for cat_file, cat_reader in s.catalog_file_dict.items():

                # If the reader hasn't been created, make it.
                if cat_reader == None:
                    cat_reader = Cat_Reader(cat_file)
                    s.catalog_file_dict[cat_file] = cat_reader

                # Loop over the pck and standard versions.
                # Note: this is done in the inner loop, checking each cat
                #  for a pck or non-pck before moving on to the next.
                # (It is unclear on how the game handles this, though it
                #  should be fine since the cats are expected to not
                #  mix packed and unpacked versions.)
                for test_cat_path in [cat_path_pck, cat_path]:
                    
                    # Skip empty packed paths.
                    if test_cat_path == None:
                        continue

                    # Check the cat for the file.
                    file_binary = cat_reader.Read(test_cat_path)
                    if file_binary == None:
                        continue

                    # If it returned something, then it matched, so can
                    #  stop searching.
                    file_source_path = cat_file
                    # If it was pck, clarify as zipped.
                    file_binary_is_zipped = test_cat_path == cat_path_pck
                    break

                # Stop looping over cats once a match found.
                if file_binary != None:
                    break


        # If no binary was found, error.
        if file_binary == None:
            if error_if_not_found:
                raise Common.File_Missing_Exception(
                    'Could not find a match for file {}'.format(virtual_path))
            return None

        # Decompress if needed.
        if file_binary_is_zipped:
            file_binary = s.Decompress(file_binary, virtual_path)

        # If the binary is an empty string, this is an LU dummy file,
        #  so return None.
        if not file_binary:
            return None

        # Convert the binary into a Game_File object.
        # The object constructors will handle parsing of binary data,
        #  so this just checks file extensions and picks the right class.
        # Some special lookups will be done for select files.
        if virtual_path == 'types/Globals.txt':
            game_file_class = Globals_File       
        elif file_extension == 'xml':
            game_file_class = XML_File         
        elif file_extension == 'obj':
            game_file_class = Obj_File
        elif file_extension == 'txt':
            game_file_class = T_File
        else:
            raise Exception('File type for {} not understood.'.format(virtual_path))

        # Construct the game file.
        # These will also record the path used, to help know where to place
        #  an edited file in the folder structure.
        game_file = game_file_class(
            file_binary = file_binary,
            virtual_path = virtual_path,
            file_source_path = file_source_path,
            )

        if Settings.write_file_source_paths_to_message_log:
            Write_Summary_Line(
                'Loaded file {} from {}'.format(virtual_path, file_source_path))
        
        return game_file


# Single, global copy of the reader.
# TODO: make a copy part of a File_System or similar object, instead
#  of keeping one here.
Source_Reader = Source_Reader_class()