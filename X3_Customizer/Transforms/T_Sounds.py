'''
Transforms messing with game sounds.
This will mostly focus on just replacing or swapping entries
in the s folder.
'''
from File_Manager import *
import copy
import os


@Check_Dependencies()
def Remove_Sound(
        sound_id, 
        cleanup = False
        ):
    '''
    Removes a sound by writing an empty file in its place, based
    on the sound's id. If a non-empty file is already present in
    the 's' folder, it will be backed up.

    * sound_id
     - Int, the id of the sound file to be overwritten.
    * cleanup
     - Bool, if True then any empty overwrite file will be removed,
       restoring a sound previously overwritten.
    '''
    # Files are placed one folder up, and then in the s subfolder.
    base_folder = os.path.join('..', 's')
    file_name = '{}.wav'.format(sound_id)
    backup_file_name = '{}.wav.x3c.bak'.format(sound_id)
    file_path = os.path.join(base_folder, file_name)
    backup_file_path = os.path.join(base_folder, backup_file_name)
    
    #When being called for cleanup, run the Cleanup function and return.
    if cleanup:
        if os.path.exists(file_path):
            # Check if a file exists of size 0.
            if os.path.getsize(file_path) < 10:
                os.remove(file_path)
        # Check if there is a backup file in place, and any
        # empty file was removed.
        if not os.path.exists(file_path) and os.path.exists(backup_file_path):
            # Rename it.
            os.rename(backup_file_path, file_path)
        return
        
    #Make the target folder if needed.
    if not os.path.exists(base_folder):
        os.mkdir(base_folder)

    # If a file is already present, check its size.
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10:
        # Some file with stuff in it is here, so back it up.
        os.rename(file_path, backup_file_path)

    # Now, if no file is present, make an empty one, otherwise the
    # file should already be an empty one from a prior run.
    #if not os.path.exists(file_path):
    #    with open(file_path, 'w') as file:
    #        pass
    # Switch to making a better tracked file object.
    File_Manager.Add_File(
        file_name,
        Misc_File(
            virtual_path_name = os.path.relpath(file_path, Settings.Get_X3_Folder()),
            text = ''))

    return

 
@Check_Dependencies()
def Remove_Combat_Beep(
        #Special flag to clean out old files.
        _cleanup = False
    ):
    '''
    Removes the beep that plays when entering combat.
    '''
    Remove_Sound(923, _cleanup)
