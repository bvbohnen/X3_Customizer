'''
Loads and stores source files to be modified, and writes them
out when finished.
'''

from File_Fields import *
import os
from collections import OrderedDict
import inspect
import shutil

#Specify the path to the addon folder.
#Preferably full path, else relative path from location calling
# this customizer.
Path_to_addon_folder = None
#Specify the path to the source folder, relative to the addon folder.
Source_folder = None
#Name a file to write detailed output messages to.
Message_file_name = None

#Make a convenience function to set these paths.
def Set_Path(
    path_to_addon_folder,
    source_folder,
    summary_file = 'X3_Customizer_summary.txt',
    ):
    '''
    Sets the pathing to be used for file loading and writing.

    * path_to_addon_folder:
      - Path to the X3 AP addon folder, containing the source_folder.
        Output files will be written relative to here.
      - If this is not the addon folder, a warning will be printed but
        operation will continue, writing files to this folder, though
        files will need to be moved to the proper addon folder to be
        applied to the game. Some generated files may be placed in
        the directory above this folder, eg. the expected TC directory.

    * source_folder:
      - Subfolder in the addon directory containing unmodified files, 
        internally having the same folder structure as addon to be
        used when writing out transform results.
      - (eg. output to addon\types will source from input in
         addon\source_folder\types).

    * summary_file:
      - Path and name for where a summary file will be written, with
        any transform results. Defaults to 'X3_Customizer_summary.txt' 
        in the addon directory.
    '''
    global Path_to_addon_folder
    global Source_folder
    global Message_file_name
    Path_to_addon_folder = path_to_addon_folder
    Source_folder = source_folder
    Message_file_name = summary_file
    return


#Track the file object, to append to it on the fly.
Message_file = None
def Write_Summary_Line(line, no_newline = False):
    '''
    Write a line to the summary file.
    A newline is inserted automatically if no_newline == False.
    '''
    global Message_file
    #Open the file if needed.
    if Message_file == None:
        Message_file = open(Message_file_name, 'w')
    Message_file.write(line + '\n' if not no_newline else '')
    

#To simplify code a bit, predefine the paths for all expected
# file names. This avoids having to specify path at every transform,
# using an annoying os.path.join call. This is also more dynamic
# to user folder structures than pre-specifying all paths.
#Key by file name; value is the path relative to the source folder.
File_path_dict = {}

#Make a set of all transform file names that may be used by transforms,
# used in filtering the source files tracked.
#This gets filled in by decorators, which should all get processed before
# the first call to Init (through a call to Load_File) occurs and uses
# this set.
Transform_required_file_names = set()

#Record a set of all transforms.
#This is filled in by the decorator at startup.
Transform_list = []

#Record a set of transforms that were called.
#Transforms not on this list at the end of a run may need to do
# cleanup of older files generated on prior runs.
#This is filled in by the decorator.
Transforms_names_run = set()


#On the first call to Load_File from any transform, do some extra
# setup.
First_call = True
def Init():
    'Initialize the file manager.'
    #Safety check for First_call already being cleared, return early.
    global First_call
    if not First_call:
        return
    First_call = False

    #The file paths should be defined at this point. Error if not.
    if Path_to_addon_folder == None:
        raise Exception('Path to the AP/addon folder not specified.')
    if Source_folder == None:
        raise Exception('Folder with the source files not specified.')

    #Verify the AP path looks correct.
    if not os.path.exists(Path_to_addon_folder):
        raise Exception('Path to the AP/addon folder appears invalid.')
    if not os.path.exists(os.path.join(Path_to_addon_folder, Source_folder)):
        raise Exception('Path to the source folder appears invalid.')

    #Check for 01.cat, and that the path ends in 'addon'.
    #Print a warning but continue if anything looks wrong; the user may
    # wish to have this tool generate files to a separate directory first.
    if any((not Path_to_addon_folder.endswith('addon'),
            not os.path.exists(os.path.join(Path_to_addon_folder, '01.cat')))
           ):
        print('Warning: Path to the AP/addon folder appears wrong.\n'
              'Generated files may need manual moving to the correct folder.')
        

    #Dynamically find all files in the source folder.
    #These will all be copied at final writeout, even if not modified, eg.
    # if a transform was formerly run on a file but then commented out,
    # need to overwrite the previous results with a non-transformed version
    # of the file.
    #Use os.walk to go through the source folder and all subfolders.
    #Note: dir_path is the relative dir from the source folder, including
    # the source folder. This could be removed by doing a nested walk
    # from each folder in the source_folder, though this wouldn't work if
    # the user just wanted to give a basic list of files to transform and
    # manually handle moving around outputs.
    # Edits to the path can remove the first folder, though are clumsy
    # to implement.
    # The working directory could be moved to the source directory
    # temporarily for this, though starting walk using '.' will have
    # that as the start of the path still (which might be fine).
    os.chdir(os.path.join(Path_to_addon_folder, Source_folder))
    for dir_path, folder_names, file_names in os.walk('.'):
        #Loop over the file names.
        for file_name in file_names:

            #If this file_name matches any transform, note its path.
            if file_name in Transform_required_file_names:

                #Error if the file already seen.
                if file_name in File_path_dict:
                    #Just print a message and continue.
                    print('Error: file {} seen on multiple paths; defaulting to path {}'
                          .format(file_name, File_path_dict[file_name]))
                else:
                    File_path_dict[file_name] = dir_path
                    

    #Set the working directory to the AP directory.
    #This makes it easier for transforms to generate any misc files.
    os.chdir(Path_to_addon_folder)

    return


#Dict to hold file contents, as well as specify their full path.
#Keyed by file name with path.
#This gets filled in by transforms as they load the files.
#T files will generally be loaded into lists of dictionaries keyed by field
# name or index, with each list entry being a separate line.
#XML files will generally be loaded as a XML_File object holding
# the encoding and raw text.
File_dict = {}

class XML_File():
    '''
    Simple XML file contents holder with encoding and text.
    Members:
        text     : Raw text for this file.
        encoding : String indicating the encoding type of the xml.
    '''
    def __init__(s):
        s.text = None
        s.encoding = None
    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        #For xml, this will be the full XML_File object so that its
        # text field can be edited.
        return s

class T_File():
    '''
    T file contents holder, as a life of OrderedDict objects.
    Each OrderedDict represents a separate line.
    Class exists mainly to clarify naming for now, and for any
    future attribute expansion.
    Members:
        line_dict_list  : List of OrderedDict objects, each holding the labelled 
                          contents of a line.
                          This includes all lines, with headers.
        data_dict_list  : As above, but only holding lines that have data, skipping 
                          headers. This is used for transform editing.
    '''
    def __init__(s):
        s.line_dict_list = []
        s.data_dict_list = []
    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        #For T files, this is the list of line dicts with data, which can
        # be edited directly.
        return s.data_dict_list
    

class File_Missing_Exception(Exception):
    '''Exception raised when Load_File doesn't find the file.'''
    pass


#Decorator function for transforms to check if their required
# files are found, and have nice handling when not found.
#The args will be the file names.
#This is implemented as a two-stage decorator, the outer one handling
# the file check, the inner one returning the function.
#Eg. decorators have one implicit input argument, the following object,
# such that "@dec func" is like "dec(func)".
#To support input args, a two-stage decorator is used, such that
# "@dec(args) func" becomes "dec(args)(func)", where the decorator
# will return a nested decorator after handling args, and the nested
# decorator will accept the function as its arg.
#To get the wrapped function's name and documentation preserved,
# use the 'wraps' decorator from functools.
#Update: this will also support a keyword 'category' argument, which
# will be the documentation transform category override to use when
# the automated category is unwanted.
from functools import wraps
def Check_Dependencies(*file_names, category = None):
    #Record the required file names to a set for use elsewhere.
    Transform_required_file_names.update(file_names)

    #Make the inner decorator function, capturing the wrapped function.
    def inner_decorator(func):

        #Attach the required file_names to the wrapped function,
        # since they are only available on function definition at the
        # moment, and will be checked at run time.
        func._file_names = file_names
        #Attach the override category to the function.
        #TODO: maybe fill in the default category here, but for now
        # it is done in Make_Documentation.
        func._category = category

        #Record the transform function.
        Transform_list.append(func)

        #Set up the actual function that users will call, capturing
        # any args/kwargs.
        @wraps(func)
        def wrapper(*args, **kwargs):

            #Note this transform as being seen.
            Transforms_names_run.add(func.__name__)
            
            #On the first call, do some extra setup.
            if First_call:
                Init()

            #Loop over the required files.
            for file_name in func._file_names:
                #Do a test load; if succesful, the file was found.
                try:
                    Load_File(file_name)
                except File_Missing_Exception:
                    print('Skipped {}, required file {} not found.'.format(
                        func.__name__,
                        file_name
                        ))
                    #Return nothing and skip the call.
                    return
            #Return the normal function call results.
            return func(*args, **kwargs)

        #Return the callable function.
        return wrapper

    #Return the decorator to handle the function.
    return inner_decorator


def Get_Source_File_Path(file_name):
    '''
    Returns the path to the given source file_name, from the addon directory.
    Path will be relative to the AP/addon/source directory.
    If a path isn't known, returns None.
    '''
    if file_name in File_path_dict:
        #Look up the path from the source folder, and add it to the
        # path to the source folder.
        return os.path.join(Source_folder, File_path_dict[file_name], file_name)
    return None


def Get_Output_File_Path(file_name):
    '''
    Returns the path to the given output file_name, from the addon directory.
    Path will be relative to the AP/addon directory.
    '''
    if file_name in File_path_dict:
        #Look up the path from the source folder, and add it to the
        # path to the AP/addon folder, eg. the working directory.
        file_path = os.path.join(File_path_dict[file_name], file_name)
        #Quick safety check: error if matches the source file path.
        source_file_path = Get_Source_File_Path(file_name)
        assert file_path != source_file_path
        return file_path


def Load_Folder(folder_name):
    '''
    Returns a list of file contents for files in the given folder.
    Eg. if folder_name is 'maps', returns the contents of all files
    in the 'maps' folder.
    '''
    return_list = []
    #Since files are pre-specified for now, some may not be present.
    #For now, error if expected file(s) not found.
    for file_name in File_path_dict[folder_name]:
        #Try to load the file.
        return_list.append(Load_File(file_name))


def Load_File(file_name, return_t_file = False, error_if_not_found = True):
    '''
    Returns the contents of the given file, either raw text for XML
    or a dictionary for T files.
    If the file has not been loaded yet, reads from the expected
    source file.
    If the file is not found and error_if_not_found == True, 
    raises an exception, else returns None.
    If return_t_file == True, returns the T_File object instead of just
    the trimmed dict of data lines.
    '''

    #If the file is not loaded, handle loading.
    if file_name not in File_dict:

        #Lookup the file path.
        file_path = Get_Source_File_Path(file_name)

        #Error if the file isn't found, or return None.
        if file_path == None or not os.path.exists(file_path):
            if error_if_not_found:
                raise File_Missing_Exception()
            return None

        #If this is an xml file, do a raw load to a XML_File object.
        if file_path.endswith('xml'):

            #Load the misc xml files.
            this_xml_file = XML_File()

            #Get the encoding to use, since xml files are sensitive to this.
            this_xml_file.encoding = Find_encoding(file_path)
            with open(file_path, 'r', encoding = this_xml_file.encoding) as file:
                #Read in the raw text and store it.
                this_xml_file.text = file.read()

            File_dict[file_name] = this_xml_file

            #-Removed; use text instead of xml.
            ##Parse the xml.
            #xml_tree = xml.etree.ElementTree.parse(file_path)
            #subdict[file_name] = xml_tree


        #If this is a T file, parse its fields.
        elif file_path.endswith('txt'):

            #Field ordering could be done with named tuples, but in practice it is 
            # probably easiest to just use ordered dicts.
            #Indices without names will be keyed by the index integer.
                    
            #Open this file, vanilla version, and read into a list of lists.
            with open(file_path, 'r') as file:
                #This gets a list of lines, where each line is a list of strings.
                #Read in the data lines into a list of lists.
                #Sublists are a series of text strings.
                #Since lines end in semicolons, the last entry will generally be a simple new line.
                #Comment lines (//) are ignored.
                data_list_list = []
                for line in file.readlines():
                    if not line.startswith('//'):
                        data_list_list.append(line.split(';'))

            #Prepare a T_File object to fill in.
            this_t_file = T_File()
            #Lookup the fields for this file name.
            field_dict = T_file_name_field_dict_dict[file_name]

            #Loop over the lines.
            for data_list in data_list_list:

                #Create an ordered dict for this line.
                this_dict = OrderedDict()

                #Note: the line may be a tc format or ap format, in the
                # case of the jobs file.
                #If the fields_dict specifies a line count for an AP
                # format, and that format is seen here, it will provide
                # some special insertion points for new AP fields.
                #The default field_dict is for the tc format in this
                # case, with no extra lines.
                if 'lines_ap' in field_dict:
                    if len(data_list) == field_dict['lines_ap']:
                        #Switch to the ap field dict.
                        #This will only swap once; afterward there is no
                        # 'lines_ap' field in field_dict, and these checks
                        # are skipped.
                        field_dict = T_file_name_field_dict_dict[field_dict['ap_name']]
                        
                #Step through the fields, with an index counter.
                for index, field_string in enumerate(data_list):

                    #If this index has a field name, use it, otherwise use the index for a key.
                    this_key = index
                    if index in field_dict:
                        this_key = field_dict[index]
                    #Also check negative indices.
                    negative_index = index - len(data_list)
                    if negative_index in field_dict:
                        this_key = field_dict[negative_index]

                    #Record in the ordered dict.
                    #Values will not be converted to ints, since some might need to stay strings.
                    #Int conversion should happen upon use elsewhere.
                    this_dict[this_key] = field_string
                                
                #Add this line dict to the list that tracks all lines.
                this_t_file.line_dict_list.append(this_dict)
                #Conditionally add this line dict to the data tracking list, skipping
                # if the line is too short.
                if len(this_dict) >= field_dict['min_data_entries']:
                    this_t_file.data_dict_list.append(this_dict)

                #Store the contents in the File_dict.
                File_dict[file_name] = this_t_file

        else:
            raise Exception('File type for {} not understood.'.format(file_name))
                
    #Return the file contents.
    if not return_t_file:
        return File_dict[file_name].Read_Data()
    else:
        return File_dict[file_name]

            
def Find_encoding(file_path):
    '''
    Tries to determine the encoding to use for reading or writing an xml file.
    Returns a string name of the encoding.
    '''

    #Codec is found on the first line. Examples:
    # <?xml version="1.0" encoding="ISO-8859-1" ?>
    # <?xml version="1.0" encoding="UTF-8" ?>
    #Getting the encoding right is important for special character handling, and
    # also ensuring other programs that load any written file based on the
    # xml declared encoding will be using the right one (eg. utf-8 wasn't used
    # to write an xml file declared as iso-8859 or similar).

    #Start by test opening the file, always treating as utf-8 (since this
    # seems to be the most reliable).
    with open(file_path, 'r', encoding = 'utf-8') as file:

        #Get the first line by using split lines in a loop, and break early.
        for line in file.readlines():
            assert 'encoding' in line

            #Just do some quick splits to get to the code string.
            #Split on 'encoding'
            subline = line.partition('encoding')[2]

            #This should now have '="ISO-8859-1"...'.
            #Remove the '='.
            subline = subline.replace('=','')

            #Split on all quotes.
            #This will create a an empty string for text before
            # the first quote.
            split_line = subline.split('"')

            #There should be at least 3 entries,
            # [empty string, encoding string, other stuff].
            assert len(split_line) >= 3

            #The second entry should be the encoding.
            encoding = split_line[1]
            #Send it back.
            return encoding


def Cleanup():
    '''
    Handles cleanup of old transform files, generally aimed at transforms
    which were not run and which have a cleanup attribute.
    '''
    #Loop over the transforms.
    for transform in Transform_list:
        #Skip if this was run, since it should handle its own cleanup
        # as needed based on input args.
        if transform.__name__ in Transforms_names_run:
            continue

        #Look up the arg names first (ignore the *args, **kwargs names).
        argspec = inspect.getargspec(transform)
        #Check if this transform has a cleanup method.
        if '_cleanup' in argspec.args:
            #Run the transform in cleanup mode.
            transform(_cleanup = True)

                
def Write_Files():
    '''
    Write output files for all source file content edited by transforms.
    Outputs will overwrite any existing files.
    '''    
    #Loop over the files that were loaded.
    for file_name, file_object in File_dict.items():

        #Look up the output path.
        file_path = Get_Output_File_Path(file_name)

        #Handle T files.
        if isinstance(file_object, T_File):
            #Open the file to write to.
            with open(file_path, 'w') as file:
                #Loop over the lines.
                for line_dict in file_object.line_dict_list:

                    #Convert the line fields to a list.
                    field_list = line_dict.values()
                    #Join with semicolons.
                    this_line = ';'.join(field_list)

                    #Write to the file.
                    #The last entry of each sublist is alrady a new line, so no new line
                    # needed here.
                    file.write(this_line)

            #For some reason, TwareT has a pck version created sometimes,
            # which ends up overriding the custom version.
            #If a pck file exists, rename it.
            pck_file_path = file_path.replace('.txt','.pck')
            if os.path.exists(pck_file_path):
                #Just stick a suffix on it, so it isn't completely gone.
                os.rename(pck_file_path, pck_file_path + '.x3c.bak')


        elif isinstance(file_object, XML_File):
            #Open with the right encoding.
            with open(file_path, 'w', encoding = file_object.encoding) as file:   
                #Just write as raw text.  
                file.write(file_object.text)

            #-Removed; use text instead of xml.
            #Let the xml plugin pick the encoding to write out in.
            #xml_tree.write(file_path)


    #Loop over the files that were not loaded. These may need to be included
    # in case a prior run transformed them, then the transform was removed
    # such that they weren't loaded but need to overwrite old changes.
    #These will do direct copies.
    for file_name in File_path_dict:
        #Skip the loaded files.
        if file_name in File_dict:
            continue

        #Look up the source  path.
        source_file_path = Get_Source_File_Path(file_name)
        #Look up the output path.
        dest_file_path = Get_Output_File_Path(file_name)
        
        #Do the copy.
        shutil.copy(source_file_path, dest_file_path)

    return