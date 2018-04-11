'''
Container for general customize settings.
Import as:
    from Settings import Settings

TODO: expand with any new options, eg. default verbosity and such.
'''
import os

class Settings_class:
    '''
    Container for general settings, including system paths.
    Primarily used for organization convenience.

    Attributes:
    * path_to_addon_folder
      - String, the path to the addon folder.
      - Converted to a full path if a relative path was given.
    * path_to_x3_folder
      - String, the path to the main x3 folder, one level above the addon
        folder.
      - Constructed from path_to_addon_folder.
    * path_to_source_folder
      - String, the path to the source folder, either a full path or relative
        to the calling location.
      - Constructed from path_to_addon_folder and source_folder.
    * path_to_log_folder
      - String, the path to the folder to place any output logs in, or
        to read prior output logs from.
    * message_file_name
      - String, name a file to write detailed output messages to.
    * log_file_name
      - String, name a file to write json log output to.
    '''
    def __init__(s):
        s.path_to_addon_folder = None
        s.path_to_x3_folder = None
        s.path_to_source_folder = None
        s.path_to_log_folder = None
        s.message_file_name = None
        s.log_file_name = None
        # Temp entry for relative source folder.
        s._source_folder = None


    def Set_Addon_Folder(s, path):
        '''
        Sets the addon folder and x3 folder paths, from the addon folder
        initial path. Updates the path_to_source_folder if needed.
        '''
        s.path_to_addon_folder = os.path.abspath(path)
        # Go up one level to get the base x3 folder (with some trimming
        #  to clean it up).
        s.path_to_x3_folder = os.path.abspath(os.path.join(path, '..'))
        # Update the full source path.
        s.Update_Source_Folder_Path()


    def Set_Source_Folder(s, path):
        '''
        Sets the source folder path relative to the addon folder, and
        updates its absolute path if the addon folder is known.
        '''
        s._source_folder = path
        # Update the full source path.
        s.Update_Source_Folder_Path()


    def Update_Source_Folder_Path(s):
        '''
        Update the full source path if addon and source folders specified.
        '''
        if s.path_to_addon_folder != None and s._source_folder != None:
            s.path_to_source_folder = os.path.abspath(
                os.path.join(s.path_to_addon_folder, s._source_folder))

            
    def Set_Log_Folder(s, path):
        '''
        Sets the log folder path relative to the addon folder.
        '''
        s.path_to_log_folder = os.path.abspath(
                os.path.join(s.path_to_addon_folder, path))

    def Set_Message_File(s, file_name):
        '''
        Sets the file name to use for any transform messages.
        '''
        s.message_file_name = file_name

    def Set_Log_File(s, file_name):
        '''
        Sets the file name to use for the json log.
        '''
        s.log_file_name = file_name


    def Verify_Setup(s):
        '''
        Checks the current paths for errors (not existing, etc.).
        Some situations may just throw warnings.
        Creates the source folder if it does not exist.
        '''
        # Basic checks to make sure paths were specified.
        if not s.path_to_addon_folder:
            raise Exception('Path to the AP/addon folder not specified.')
        if not s.path_to_source_folder:
            raise Exception('Folder with the source files not specified.')

        # Verify the AP path looks correct.
        # The X3 path should automatically be correct if the AP folder
        #  is correct.
        if not os.path.exists(s.path_to_addon_folder):
            raise Exception('Path to the AP/addon folder appears invalid.')
        if not os.path.exists(s.path_to_source_folder):
            # Create an empty source folder to capture any extracted files.
            os.mkdir(s.path_to_source_folder)
            # -Removed error for now; assume intentional.
            #raise Exception('Path to the source folder appears invalid.')
            print('Warning: Source folder {} not found and has been created'.format(
                s.path_to_source_folder))

        # Check for 01.cat, and that the path ends in 'addon'.
        # Print a warning but continue if anything looks wrong; the user may
        #  wish to have this tool generate files to a separate directory first.
        if any((not s.path_to_addon_folder.endswith('addon'),
                not os.path.exists(os.path.join(s.path_to_addon_folder, '01.cat')))
               ):
            print('Warning: Path to the AP\\addon folder appears wrong.\n'
                  'Generated files may need manual moving to the correct folder.\n'
                  'Automated source file extraction will fail.')

        # Create the log folder if it does not exist.
        if not os.path.exists(s.path_to_log_folder):
            os.mkdir(s.path_to_log_folder)


    def Get_Addon_Folder(s, extra_path = None):
        '''
        Returns the path to the addon folder, optionally with some
        extra relative path applied.
        '''
        if extra_path != None:
            return os.path.join(s.path_to_addon_folder, extra_path)
        return s.path_to_addon_folder

    def Get_X3_Folder(s, extra_path = None):
        '''
        Returns the path to the X3 base folder, optionally with some
        extra relative path applied.
        '''
        if extra_path != None:
            return os.path.join(s.path_to_x3_folder, extra_path)
        return s.path_to_x3_folder

    def Get_Source_Folder(s, extra_path = None):
        '''
        Returns the path to the Source folder, optionally with some
        extra relative path applied.
        '''
        if extra_path != None:
            return os.path.join(s.path_to_source_folder, extra_path)
        return s.path_to_source_folder


    def Get_Message_File_Path(s):
        '''
        Returns the path to the message file, including file name.
        '''
        return os.path.join(s.path_to_log_folder, s.message_file_name)


    def Get_Log_File_Path(s):
        '''
        Returns the path to the log file, including file name.
        '''
        return os.path.join(s.path_to_log_folder, s.log_file_name)


# General settings object, to be referenced by any place so interested.
Settings = Settings_class()

