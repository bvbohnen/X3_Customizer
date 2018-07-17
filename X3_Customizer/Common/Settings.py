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
    Paths tend to be filled in by a call to Set_Paths; some other
    flags are initialized from command line arguments.
    This can be modified by user scripts directly, if needed,
    eg. "Settings.target_base_tc = True" to enable TC mode.

    Attributes:
    * path_to_addon_folder
      - String, the path to the addon folder.
      - Converted to a full path if a relative path was given.
      - When target_base_tc is True, this will point to the base x3 folder
        instead.
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
        x and y vectors printed for reference). Close the plot window
        manually to continue transform processing.
    * developer
      - Bool, if True then enable some behavior meant just for development,
        such as leaving exceptions uncaught or letting file patchers do
        the best job they can when hitting problems.
    * verbose
      - Bool, if True some extra status messages may be printed.
    * allow_path_error
      - Bool, if True then if the x3 path looks wrong, the customizer
        will still attempt to run.
    * target_base_tc
      - Bool, if True then the target X3 version will be Terran Conflict
        instead of Albion Prelude.
      - Experimental; will generally replace the AP addon folder with
        the base X3 folder to minimize code changes.
    * output_to_catalog
      - Bool, if True then the modified files will be written to a single
        cat/dat pair, incrementally numbered above existing catalogs.
      - Scripts will be kept as loose files.
    '''
    '''
    -Removed attributes, for now.

    * t_folder_file_number
      - String, 4-digit number to give to any generated xml file holding
        override text in the addon/t folder.
      - This should be set to avoid numbers in use by other mods, and
        higher than those mods that might be overridden.
      - See https://forum.egosoft.com/viewtopic.php?t=216690 for values
        to be avoided.
      - Default is 9997.
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
        #s.t_folder_file_number = '9997'
        s.allow_path_error = False
        s.target_base_tc = False
        s.output_to_catalog = True
        

    #def Get_Page_Text_File_Path(s):
    #    '''
    #    Returns the path to use for the custom page text file, to
    #    be placed in the addon/t folder.
    #    Path will be cat style, eg. '/t/9997-L044.xml'.
    #    '''
    #    return 't/' + s.t_folder_file_number + '-L044.xml'


    def Set_Addon_Folder(s, path):
        '''
        Sets the addon folder and x3 folder paths, from the addon folder
        initial path. Updates the path_to_source_folder if needed.
        Error if target_base_tc is True.
        '''
        if path == None:
            return
        # Error check after the None path; don't error when no path was
        #  given.
        if s.target_base_tc:
            raise Exception(
                'Path to x3 AP addon folder is not supported for base TC.')
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
        # In TC mode, this will say in the X3 folder; all file handling
        #  that was relative to addon will instead just use the base
        #  folder.
        if not s.target_base_tc:
            s.path_to_addon_folder = os.path.abspath(
                os.path.join(path, 'addon'))
        else:
            s.path_to_addon_folder = s.path_to_x3_folder

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
        if (s.path_to_addon_folder != None 
        and s._relative_source_folder != None):
            s.path_to_source_folder = os.path.abspath(
                os.path.join(s.path_to_addon_folder, 
                             s._relative_source_folder))

            
    def Set_Log_Folder(s, path):
        '''
        Sets the log folder path, relative to the addon folder if not absolute.
        '''
        # Skip the cases where the addon folder isn't known, and let
        #  the verifier catch errors.
        if s.path_to_addon_folder == None:
            return
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

        # Messages will differ between AP and TC targets, so split some
        #  of the checks here.
        if not s.target_base_tc:

            # Verify the AP path looks correct.
            # The X3 path should automatically be correct if the AP folder
            #  is correct.
            if not os.path.exists(s.path_to_addon_folder):
                raise Exception(
                    'Path to the AP/addon folder appears to not exist.'
                    +'\n (x3 base path: {})'.format(s.path_to_x3_folder)
                    +'\n (x3 addon path: {})'.format(s.path_to_addon_folder)
                    )

            # Check for 01.cat, and that the path ends in 'addon'.
            # Print a warning but continue if anything looks wrong; the user
            #  may wish to have this tool generate files to a separate
            #  directory first.
            if any((not s.path_to_addon_folder.endswith('addon'),
                    not os.path.exists(os.path.join(
                        s.path_to_addon_folder, '01.cat')))
                   ):
                if s.allow_path_error:
                    print(  
                        'Warning: Path to the AP/addon folder appears wrong.\n'
                        'Generated files may need manual moving to the correct folder.\n'
                        'Automated source file extraction may fail.'
                        +'\n (x3 base path: {})'.format(s.path_to_x3_folder)
                        +'\n (x3 addon path: {})'.format(s.path_to_addon_folder)
                        )
                else:
                    # Hard error.
                    # Users might mistakenly set the x3 base folder as the addon
                    #  folder, or similar issues, so this helps catch those
                    #  in a cleaner way.
                    raise Exception(
                        'Path does not appear correct for the AP/addon folder.'
                        +'\n (x3 base path: {})'.format(s.path_to_x3_folder)
                        +'\n (x3 addon path: {})'.format(s.path_to_addon_folder)
                        )

        else:
            
            # Verify the X3 path looks correct.
            if not os.path.exists(s.path_to_x3_folder):
                raise Exception(
                    'Path to the X3 folder appears to not exist.'
                    +'\n (x3 base path: {})'.format(s.path_to_x3_folder)
                    )            

            # Check for 01.cat.
            # Print a warning but continue if anything looks wrong; the user
            #  may wish to have this tool generate files to a separate
            #  directory first.
            if not os.path.exists(
                    os.path.join(s.path_to_addon_folder, '01.cat') ):

                if s.allow_path_error:
                    print(  
                        'Warning: Path to the X3 folder appears wrong.\n'
                        'Generated files may need manual moving to the correct folder.\n'
                        'Automated source file extraction may fail.'
                        +'\n (x3 base path: {})'.format(s.path_to_x3_folder)
                        )
                else:
                    # Hard error.
                    raise Exception(
                        'Path does not appear correct for the X3 folder.'
                        +'\n (x3 base path: {})'.format(s.path_to_x3_folder)
                        )


        #-Removed; source folder is now optional.
        #if not os.path.exists(s.path_to_source_folder):
        #    # Create an empty source folder to capture any extracted files.
        #    os.makedirs(s.path_to_source_folder)
        #    # -Removed error for now; assume intentional.
        #    #raise Exception('Path to the source folder appears invalid.')
        #    print('Warning: Source folder {} not found and has been created'.format(
        #        s.path_to_source_folder))

        # Error if no log folder was selected.
        if s.path_to_log_folder == None:
            raise Exception('Log folder path not filled in.')

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


# This is the main access function input scripts are expected to use.
# This docstring will be included in documentation.
def Set_Path(
        # Force args to be kwargs, since that is safer if args are
        #  added/removed in the future.
        *,
        path_to_x3_folder = None,
        path_to_addon_folder = None,
        path_to_output_folder = None,
        path_to_source_folder = None,
        # Backwards compatable version of source_folder.
        source_folder = None,
        path_to_log_folder = 'x3_customizer_logs',
        summary_file = 'X3_Customizer_summary.txt',
        log_file = 'X3_Customizer_log.json',
        enable_TC_mode = False,
    ):
    '''
    Sets the paths to be used for file loading and writing.

    * path_to_x3_folder
      - Path to the X3 base folder, where the executable is located.
      - Can be skipped if path_to_addon_folder provided.
    * path_to_addon_folder
      - Path to the X3 AP addon folder.
      - Can be skipped if path_to_x3_folder provided.
    * path_to_output_folder
      - Optional, path to a folder to place output files in.
      - Defaults to match path_to_x3_folder, so that outputs are
        directly readable by the game.
    * path_to_source_folder
      - Optional, alternate folder which contains source files to be modified.
      - Maybe be given as a relative path to the "addon" directory,
        or as an absolute path.
      - Files located here should have the same directory structure
        as standard games files, eg. 'source_folder/types/Jobs.txt'.
    * path_to_log_folder
      - Path to the folder to place any output logs in, or
        to read prior output logs from.
      - Maybe be given as a relative path to the "addon" directory,
        or as an absolute path.
      - Defaults to 'x3_customizer_logs'.
      - This should not be changed between runs, since recognition of
        results from a prior customizer run depends on reading the
        prior run's log file.
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
    * enable_TC_mode
      - Bool, if True then the target X3 version will be Terran Conflict
        instead of Albion Prelude.
      - All files which would have been placed in the addon folder will
        now be placed in the base x3 folder.
      - Note: not all transforms have been tested for TC compatability.
    '''
    # Record the TC mode flag.
    # TODO: maybe rename target_base_tc to be consistent.
    # Do this before other calls, so that automated 'addon' path
    #  handling gets changed.
    Settings.target_base_tc = enable_TC_mode

    # Hide these behind None checks, to be extra safe; the Settings 
    #  verification should catch problems.
    # TODO: maybe trim Nones from here if checked in the Settings methods.
    if path_to_x3_folder != None:
        Settings.Set_X3_Folder(path_to_x3_folder)
    if path_to_addon_folder != None:
        Settings.Set_Addon_Folder(path_to_addon_folder)
    # Two ways to set source_folder for now.
    # TODO: maybe trim the old one out.
    if source_folder != None:
        Settings.Set_Source_Folder(source_folder)
    if path_to_source_folder != None:
        Settings.Set_Source_Folder(path_to_source_folder)
    if path_to_output_folder != None:
        Settings.Set_Output_Folder(path_to_output_folder)
    if path_to_log_folder != None:
        Settings.Set_Log_Folder(path_to_log_folder)
    if summary_file != None:
        Settings.Set_Message_File(summary_file)
    if log_file != None:
        Settings.Set_Log_File(log_file)

    # Note: verification is done at the first transform, not here,
    #  so that any settings overwrites can be done after (or without)
    #  the Set_Path call.

    return
