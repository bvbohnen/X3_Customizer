'''
Container for exception messages.
'''

class File_Missing_Exception(Exception):
    '''
    Exception raised when Load_File doesn't find the file,
    or the file is empty.
    '''

class Obj_Patch_Exception(Exception):
    '''
    Exception raised when an obj binary patch fails to find a
    matching reference pattern.
    '''
    
class Text_Patch_Exception(Exception):
    '''
    Exception raised when an text patch (often xml) fails to find a
    matching reference line.
    '''