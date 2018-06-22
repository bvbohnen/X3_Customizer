'''
Transforms messing with game sounds.
This will mostly focus on just replacing or swapping entries
in the s folder.
'''
from .. import File_Manager

@File_Manager.Transform_Wrapper()
def Remove_Sound(sound_id):
    '''
    Removes a sound by writing an empty file in its place, based
    on the sound's id.

    * sound_id
     - Int, the id of the sound file to be overwritten.
    '''
    # Files are placed one folder up, and then in the s subfolder.
    virtual_path = 's/{}.wav'.format(sound_id)
    # Create an empty file.
    File_Manager.Add_File(File_Manager.Misc_File(
        virtual_path = virtual_path,
        text = ''))

    return

 
@File_Manager.Transform_Wrapper()
def Remove_Combat_Beep():
    '''
    Removes the beep that plays when entering combat.
    '''
    Remove_Sound(923)
