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
    * path_to_output_folder
      - String, the path to where files should be written.
      - If None, defaults to the path_to_x3_folder, so that files can
        be immediately recognized by the game.
      - Primary for use when testing generated outputs without risk
        of overwriting game files.
    * path_to_source_folder
      - String, the path to the source folder, either a full path or relative
        to the calling location.
      - Constructed from path_to_addon_folder and source_folder.
      - None if no source folder specified.
    * path_to_log_folder
      - String, the path to the folder to place any output logs in, or
        to read prior output logs from.
    * message_file_name
      - String, name a file to write detailed output messages to.
    * log_file_name
      - String, name a file to write json log output to.
    * disable_cleanup_and_writeback
      - Bool, if True then cleanup from a prior run as well as any final
        writes will be skipped.
    * write_file_source_paths_to_message_log
      - Bool, if True then the path for any source files read will be
        printed in the message log.
    * skip_all_transforms
      - Bool, if True all transforms will be skipped.
      - For use during cleaning mode.
    * ignore_loose_files
      - Bool, if True then any files loose in the game folders (outside
        the user source folder or a cat/dat pair) will be ignored, as
        if they were produced by the customizer on a prior run.
    * use_scipy_for_scaling_equations
      - Bool, if True then scipy will be used to optimize scaling
        equations, for smoother curves between the boundaries.
      - If False or scipy is not found, then a simple linear scaling
        will be used instead.
    * show_scaling_plots
      - Bool, if True and matplotlib and numpy are available, any
        generated scaling equations will be plotted (and their
        x and y vectors printed for reference).
    * developer
      - Bool, if True then enable some behavior meant just for development,
        such as leaving exceptions uncaught or letting file patchers do
        the best job they can when hitting problems.
    * verbose
      - Bool, if True some extra status messages may be printed.
    '''
    def __init__(s):
        s.path_to_addon_folder = None
        s.path_to_x3_folder = None
        s.path_to_output_folder = None
        s.path_to_source_folder = None
        s.path_to_log_folder = None
        s.message_file_name = None
        s.log_file_name = None
        # Temp entry for relative source folder.
        s._relative_source_folder = None
        s.disable_cleanup_and_writeback = False
        s.write_file_source_paths_to_message_log = False
        s.skip_all_transforms = False
        s.ignore_loose_files = False
        s.use_scipy_for_scaling_equations = True
        s.show_scaling_plots = False
        s.developer = False
        s.verbose = True
        

    def Set_Addon_Folder(s, path):
        '''
        Sets the addon folder and x3 folder paths, from the addon folder
        initial path. Updates the path_to_source_folder if needed.
        '''
        if path == None:
            return
        s.path_to_addon_folder = os.path.abspath(path)
        # Go up one level to get the base x3 folder (with some trimming
        #  to clean it up).
        s.path_to_x3_folder = os.path.abspath(os.path.join(path, '..'))
        # Update the full source path.
        s.Update_Source_Folder_Path()


    def Set_X3_Folder(s, path):
        '''
        Sets the addon folder and x3 folder paths, from the X3 folder
        initial path. Updates the path_to_source_folder if needed.
        '''
        if path == None:
            return
        s.path_to_x3_folder = os.path.abspath(path)
        # Go down one level for the addon folder.
        s.path_to_addon_folder = os.path.abspath(os.path.join(path, 'addon'))
        # Update the full source path.
        s.Update_Source_Folder_Path()


    def Set_Output_Folder(s, path):
        '''
        Sets the folder to output generated game files to, as if it
        were the X3 base folder.
        '''
        if path == None:
            return
        if os.path.isabs(path):
            s.path_to_output_folder = path
        else:
            s.path_to_output_folder = os.path.abspath(
                os.path.join(s.path_to_addon_folder, path))


    def Set_Source_Folder(s, path):
        '''
        Sets the source folder path relative to the addon folder, and
        updates its absolute path if the addon folder is known and the
        given path is not absolute.
        '''
        if path == None:
            return
        # Absolute paths do a direct write.
        if os.path.isabs(path):
            s.path_to_source_folder = path
        else:
            # Relative paths get stored, and may be updated to a full
            #  path right away if the addon folder is known.
            s._relative_source_folder = path
            # Update the full source path.
            s.Update_Source_Folder_Path()


    def Update_Source_Folder_Path(s):
        '''
        Update the full source path if addon and source folders specified
        and source is relative.
        '''
        if s.path_to_addon_folder != None and s._relative_source_folder != None:
            s.path_to_source_folder = os.path.abspath(
                os.path.join(s.path_to_addon_folder, s._relative_source_folder))

            
    def Set_Log_Folder(s, path):
        '''
        Sets the log folder path, relative to the addon folder if not absolute.
        '''
        if os.path.isabs(path):
            s.path_to_log_folder = path
        else:
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
        # Basic checks to make sure necessary paths were specified.
        if not s.path_to_addon_folder:
            raise Exception('Path to the AP/addon folder not specified.')
        if not s.path_to_log_folder:
            raise Exception('Path to the log folder not specified.')
        #if not s.path_to_source_folder:
        #    raise Exception('Folder with the source files not specified.')

        # Verify the AP path looks correct.
        # The X3 path should automatically be correct if the AP folder
        #  is correct.
        if not os.path.exists(s.path_to_addon_folder):
            raise Exception('Path to the AP/addon folder appears invalid.')

        # Check for 01.cat, and that the path ends in 'addon'.
        # Print a warning but continue if anything looks wrong; the user may
        #  wish to have this tool generate files to a separate directory first.
        if any((not s.path_to_addon_folder.endswith('addon'),
                not os.path.exists(os.path.join(s.path_to_addon_folder, '01.cat')))
               ):
            print('Warning: Path to the AP\\addon folder appears wrong.\n'
                  'Generated files may need manual moving to the correct folder.\n'
                  'Automated source file extraction will fail.')
            
        #-Removed; source folder is now optional.
        #if not os.path.exists(s.path_to_source_folder):
        #    # Create an empty source folder to capture any extracted files.
        #    os.makedirs(s.path_to_source_folder)
        #    # -Removed error for now; assume intentional.
        #    #raise Exception('Path to the source folder appears invalid.')
        #    print('Warning: Source folder {} not found and has been created'.format(
        #        s.path_to_source_folder))

        # Create the log folder if it does not exist.
        if not os.path.exists(s.path_to_log_folder):
            os.makedirs(s.path_to_log_folder)

        # Set the output folder to match the x3 folder, if one
        #  was not given.
        if s.path_to_output_folder == None:
            s.path_to_output_folder = s.path_to_x3_folder


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


    def Get_Output_Folder(s, extra_path = None):
        '''
        Returns the path to the output folder, optionally with some
        extra relative path applied.
        '''
        if extra_path != None:
            return os.path.join(s.path_to_output_folder, extra_path)
        return s.path_to_output_folder


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

