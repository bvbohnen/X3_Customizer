'''
Classes to represent game files.
'''
import os
from Common.Settings import Settings
from collections import OrderedDict
from . import File_Fields

class Game_File:
    '''
    Base class to represent a source file.
    This may be read from the source folder or a cat/dat pair.
    In either case, this will capture some properties of the file
    for organization purposes.

    Attributes:
    * name
      - String, name of the file, without pathing, and uncompressed.
      - This is the same as used in transform requirements and loads.
    * virtual_path
      - String, the path to the file in the game's virtual file system.
      - Matches the relative path from the source folder for files
        found there, else the path found in the cat file entry.

    Parameters:
    * source_path_name
      - String, absolute path to the file on the hard disk, likely in
        the source folder (or maybe scripts folder or elsewhere).
      - Should be with a non-pck extension, even if the file was packed.
      - Skip this if cat_path_name or virtual_path_name given instead.
      - An actual source does not need to exist, if only an intended
        output path is desired.
    * cat_path_name
      - String, path and name of the file in the cat entry.
      - Should be with a non-pck extension, even if the file was packed.
      - Path should be formatted with forward slashes as separators,
        as used in the cat files, which will differ from normal
        windows paths.
      - If the path starts with 'addon', that will be ignored automatically
        when constructing the virtual_path, similar to the X3_Editor2 VFS.
      - Skip this if source_path_name or virtual_path_name given instead.
    * virtual_path_name
      - String, path and name for the game's virtual file system.
      - Skip this if source_path_name or cat_path_name given instead.
    * dat_bytes
      - Int, number of bytes in the dat file for this entry.
      - Skip if not sourced from the dat file.
      - Unused.
    * dat_offset
      - Int, number of bytes offset into the dat file where this file
        contents begin.
      - Skip if not sourced from the dat file.
      - Unused.
    '''
    def __init__(
            s,
            source_path_name = None,
            cat_path_name = None,
            virtual_path_name = None,
            #dat_bytes = None,
            #dat_offset = None,
        ):
        #s.dat_bytes = dat_bytes
        #s.dat_offset = dat_offset

        # Parse out the name and virtual_path.
        if source_path_name != None:
            # Pull off the last term for the name.
            remaining_path, s.name = os.path.split(source_path_name)
            # Get the relative path from the source folder, to correct
            #  for absolute paths.
            s.virtual_path = os.path.relpath(remaining_path, 
                                             Settings.Get_Source_Folder())

        elif cat_path_name != None:
            # Separate on forward slashes, pull out the last term for
            #  the name, and rejoin the rest with os.path.
            path_split = cat_path_name.split('/')
            s.name = path_split[-1]
            path_folders = cat_path_name.split('/')[0:-1]

            # Drop a starting 'addon' folder, to normalize to the
            #  source folder setup (which doesn't distinguish 'addon').
            # ('addon' should always be followed by something, so don't
            #  worry about that being the only item in the list.)
            if path_folders[0] == 'addon':
                path_folders = path_folders[1:]
            s.virtual_path = os.path.join(*path_folders)

        elif virtual_path_name != None:
            # Pick out the name, but otherwise nothing special should
            #  be needed here.
            s.virtual_path, s.name = os.path.split(virtual_path_name)

        else:
            raise Exception()

        return


    def Get_Output_Path(s):
        '''
        Returns the full path to be used when writing out this file
         after any modifications, including file name, uncompressed.
        This may be placed in an 'addon' folder or a base game folder,
         depending on the file's virtual_path.
        '''
        # Note the starting folder.
        path_start_folder = s.virtual_path.split(os.path.sep)[0]
        # Record the selected 'addon' or base x3 path here.
        base_path = None
        
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
            # On a match, record the addon folder.
            if path_start_folder.lower() == test_folder:
                base_path = Settings.Get_Addon_Folder()
                break

        # Default to the base x3 folder.
        if base_path == None:
            base_path = Settings.Get_X3_Folder()

        # Add this file's virtual path and name to the base path and return.
        return os.path.join(base_path, s.virtual_path, s.name)

        
        
class XML_File(Game_File):
    '''
    Simple XML file contents holder with encoding and text.

    Attributes:
    * text
      - Raw text for this file.
    * encoding
      - String indicating the encoding type of the xml.
    '''
    def __init__(s, file_binary, **kwargs):
        super().__init__(**kwargs)
        
        # Get the encoding to use, since xml files are sensitive to this.
        s.encoding = s.Find_Encoding(file_binary)
        # Translate to text with this encoding.
        # Note: when using 'open()' to read a file, python will convert
        #  line endings to \n even if they were \r\n. Python strings also
        #  use a bare \n, so doing string searches on file contents
        #  requires the file be normalized to \n. When using bytes.decode,
        #  it does not do newline conversion, so that is done explicitly
        #  here.
        s.text = file_binary.decode(s.encoding).replace('\r\n','\n')

        # -Removed; use text instead of xml.
        ## Parse the xml.
        #xml_tree = xml.etree.ElementTree.parse(file_path)
        #subdict[file_name] = xml_tree

            
    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        # For xml, this will be the full XML_File object so that its
        #  text field can be edited.
        return s    


    @staticmethod
    def Find_Encoding(file_binary):
        '''
        Tries to determine the encoding to use for reading or writing an
        xml file.
        Returns a string name of the encoding.
        '''
        # Codec is found on the first line. Examples:
        #  <?xml version="1.0" encoding="ISO-8859-1" ?>
        #  <?xml version="1.0" encoding="UTF-8" ?>
        # Getting the encoding right is important for special character
        #  handling, and also ensuring other programs that load any written
        #  file based on the xml declared encoding will be using the right one
        #  (eg. utf-8 wasn't used to write an xml file declared as iso-8859
        #   or similar).

        # Convert binary to text; always treating as utf-8 (since this
        #  seems to be the most reliable, and is generally the default).
        file_text = file_binary.decode('utf-8').replace('\r\n','\n')

        # Get the first line by using split lines in a loop, and break early.
        for line in file_text.splitlines():
            # If there is no encoding specified on the first line, as with
            #  script files, just assume utf-8.
            if not 'encoding' in line:
                return 'utf-8'

            # Just do some quick splits to get to the code string.
            # Split on 'encoding'
            subline = line.partition('encoding')[2]

            # This should now have '="ISO-8859-1"...'.
            # Remove the '='.
            subline = subline.replace('=','')

            # Split on all quotes.
            # This will create a an empty string for text before
            #  the first quote.
            split_line = subline.split('"')

            # There should be at least 3 entries,
            #  [empty string, encoding string, other stuff].
            assert len(split_line) >= 3

            # The second entry should be the encoding.
            encoding = split_line[1]
            # Send it back.
            return encoding
            
        return None


    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''        
        # Open with the right encoding.
        with open(file_path, 'w', encoding = s.encoding) as file:   
            # Just write as raw text.  
            file.write(s.text)

        #-Removed; use text instead of xml.
        # Let the xml plugin pick the encoding to write out in.
        #xml_tree.write(file_path)


class T_File(Game_File):
    '''
    T file contents holder, as a list of OrderedDict objects.
    Represents files found in the 'types' folder.
    Each OrderedDict represents a separate line.
    Class exists mainly to clarify naming for now, and for any
    future attribute expansion.

    Attributes:
    * text
      - Raw text for this file.
    * line_dict_list
      - List of OrderedDict objects, each holding the labelled 
        contents of a line.
      - This includes all lines, with headers.
    * data_dict_list
      - As above, but only holding lines that have data, skipping 
        headers. This is used for transform editing.
    '''
    def __init__(s, file_binary, **kwargs):
        super().__init__(**kwargs)
        s.text = None
        s.line_dict_list = []
        s.data_dict_list = []
                
        # Field ordering could be done with named tuples, but in practice
        #  it is  probably easiest to just use ordered dicts.
        # Indices without names will be keyed by the index integer.

        # Get the file text. Treat as default utf-8.
        # Store a copy of raw text, in case it is ever wanted anywhere.
        # General expectation is that this isn't used, except maybe
        #  in making patches from pre-modified files.
        s.text = file_binary.decode().replace('\r\n','\n')


        # This gets a list of lines, where each line is a list of strings.
        # Read in the data lines into a list of lists.
        # Sublists are a series of text strings.
        # Since lines end in semicolons, the last entry will generally 
        #  be a simple new line.
        data_list_list = []
        # Keep line endings when splitting (True arg to splitlines).
        for line in s.text.splitlines(True):
            # Comment lines (//) are ignored.
            if line.startswith('//'):
                continue
            # Split the entries.
            data_list_list.append(line.split(';'))
            

        # Lookup the fields for this file name.
        field_dict = File_Fields.T_file_name_field_dict_dict[s.name]

        # Loop over the lines, aiming to annotate the entries with field
        #  names.
        for data_list in data_list_list:

            # Create an ordered dict for this line to hold the fields.
            this_dict = OrderedDict()

            # Note: the line may be a TC format or AP format, in the
            #  case of the jobs file.
            # If the fields_dict specifies a line count for an AP
            #  format, and that format is seen here, it will provide
            #  some special insertion points for new AP fields.
            # The default field_dict is for the TC format in this
            #  case, with no extra lines.
            # (This is inside the loop, so it gets triggered on the first
            #  data line which has a length matching an AP file).
            if ('lines_ap' in field_dict
            and len(data_list) == field_dict['lines_ap']):
                # Switch to the ap field dict.
                # This will only swap once; afterward there is no
                #  'lines_ap' field in field_dict, and these checks
                #  are skipped.
                field_dict = File_Fields.T_file_name_field_dict_dict[
                    field_dict['ap_name']]
                        

            # Step through the fields, with an index counter.
            for index, field_string in enumerate(data_list):

                # If this index has a field name, use it, otherwise use 
                #  the index for a key.
                this_key = index
                # Only do the named key check when the line is considered
                #  a data line; don't do this for headers/comments.
                if len(data_list) >= field_dict['min_data_entries']:
                    if index in field_dict:
                        this_key = field_dict[index]
                    # Also check negative indices.
                    negative_index = index - len(data_list)
                    if negative_index in field_dict:
                        this_key = field_dict[negative_index]
                        # Error if both matched; something went wrong in that
                        #  case.
                        assert index not in field_dict

                # Record in the ordered dict.
                # Values will not be converted to ints, since some might 
                #  need to stay strings.
                # Int conversion should happen upon use elsewhere.
                this_dict[this_key] = field_string
                                

            # Add this line dict to the list that tracks all lines.
            s.line_dict_list.append(this_dict)
            # Conditionally add this line dict to the data tracking list,
            #  skipping if the line is too short.
            if len(this_dict) >= field_dict['min_data_entries']:
                s.data_dict_list.append(this_dict)


    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        # For T files, this is the list of line dicts with data, which can
        #  be edited directly.
        return s.data_dict_list
    

    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''
        # Open the file to write to.
        with open(file_path, 'w') as file:
            # Loop over the lines.
            for line_dict in s.line_dict_list:

                # Convert the line fields to a list.
                field_list = line_dict.values()
                # Join with semicolons.
                this_line = ';'.join(field_list)

                # Write to the file.
                # The last entry of each sublist is alrady a new line, so
                #  no new line needed here.
                file.write(this_line)


class Obj_File(Game_File):
    '''
    Obj file contents holder.
    These are binary files holding KC assembly level code.
    '''
    def __init__(s, file_binary, **kwargs):
        super().__init__(**kwargs)
        s.binary = file_binary

    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        # For obj, this will be the full Obj_File object so that its
        #  binary field can be edited.
        return s
    

    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''
        # Do a binary write.
        with open(file_path, 'wb') as file:
            file.write(s.binary)


class Misc_File(Game_File):
    '''
    Generic container for misc file types transforms may generate.
    This will only support file writing.

    Attributes:
    * text
      - String, raw text for the file. Optional if binary is present.
    * binary
      - Bytes object, binary for this file. Optional if text is present.
    '''
    def __init__(s, text = None, binary = None, **kwargs):
        super().__init__(**kwargs)
        s.text = text
        s.binary = binary
        

    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''
        if s.text != None:
            # Do a text write.
            with open(file_path, 'w') as file:
                file.write(s.text)
        elif s.binary != None:
            # Do a binary write.
            with open(file_path, 'wb') as file:
                file.write(s.binary)
