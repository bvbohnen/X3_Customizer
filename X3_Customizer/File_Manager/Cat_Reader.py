'''
Support for unpacking files from cat/dat pairs.

The general idea on how to read the catalog files is taken from:
https://forum.egosoft.com/viewtopic.php?t=361709

Cat files appears to have been encoded by Xoring each byte with
a running value which increments on each byte, starting at 0xDB (maybe
stands for database?).

Once this layer is decoded, the format appears to be:
line 0: <cat_file_name>
line n: <file_path_and_name byte_count>

The corresponding dat file contains the contents indicated by the catalog
file, in order. The start position of the data is based on the sum of
prior file sizes.
Some data files are in a gzipped format (eg. .pck files), but that aspect
is not captured by the cat/dat setup.

Note: the data has an extra layer of encoding by xoring with 0x33.

'''
from ..Common.Settings import Settings
import os
from .File_Paths import *

#class Dat_File_Entry:
#    '''
#    Class to represent an entry in the dat file, the contents of
#    one packed file. This is mainly for organization currently,
#    and may be expanded with a copy of the file contents in the future.
#
#    Attributes:
#    * size
#      - Int, the size in bytes for the entry.
#    * start_offset
#      - Int, the offset into the dat file where this entry begins.
#    * end_offset
#      - Int, the offset into the dat file where this entry ends, inclusive.
#      - Determines automatically from size and start_offset.
#    '''
#    def __init__(s, size, start_offset):
#        s.size = size
#        s.start_offset = start_offset
#        s.end_offset = start_offset + size - 1

class Cat_Reader:
    '''
    Parsed catalog file contents.

    Attributes:
    * cat_path
      - String, the full path to the cat file.
    * dat_path
      - String, the full path to corresponding dat file, as specified in
        the cat file.
      - This is expected to be in the same directory as the cat file.
    * file_size_dict
      - Dict, keyed by file cat path with name, containing the integer
        number of bytes of file data in the dat file.
      - Essentially, a direct unpacked version of the cat contents.
      - File paths use forward slashes as separators, and start in the
        base X3 directory (above 'addon').
    * file_offset_dict
      - Dict, keyed by file cat path with name, containing the integer
        offset into the dat file where the contents begin.
      - This is summed from prior entries in the file_size_dict.
    '''
    def __init__(s, cat_path = None):
        s.cat_path = cat_path
        s.file_size_dict = {}
        s.file_offset_dict = {}
                
        # Read the cat binary data. Error if not found.
        if not os.path.exists(s.cat_path):
            raise Exception('Error: failed to find cat file at {}'.format(path))
        with open(s.cat_path, 'rb') as file:
            binary = file.read()
            
        # Convert back to a long string, and split the lines.
        # Also, pick off the first line for the dat file name.
        dat_name, *decoded_lines = s.Decode_Cat(binary).splitlines()
        # Set the dat path, sharing the cat folder.
        folder, _ = os.path.split(s.cat_path)
        s.dat_path = os.path.join(folder, dat_name)
        # Verify the dat_path has the .dat extension, as expected.
        assert s.dat_path.endswith('.dat')

        # Note: addon/04.cat was observed to point to 'foo.dat', which
        #  implies the game will just look for a dat file named the same
        #  as the cat instead of what is stated inside the cat.
        # Just do a direct overwrite for now.
        # TODO: maybe toss a warning, but probably nobody cares.
        s.dat_path = s.cat_path.replace('.cat','.dat')

        # Loop over the lines.
        # Also track a running offset for packed file start locations.
        start_offset = 0
        for line in decoded_lines:

            # Get the packed file's name and size.
            # Note: the file name may include spaces, and the name is
            #  separated from the size by a space, so this will need
            #  to only split on the last space.
            cat_path, size_str = line.rsplit(' ', 1)
            size_bytes = int(size_str)

            # Record its size and start offset.
            s.file_size_dict[cat_path] = size_bytes
            s.file_offset_dict[cat_path] = start_offset

            # Advance the offset for the next packed file.
            start_offset += size_bytes
            
        return


    @staticmethod
    def Decode_Cat(binary):
        '''
        Decode the cat binary into text.
        Returns a raw text string.
        '''
        # Remove the encoding and convert to characters, using a simple
        #  loop to make the logic easy to read.
        xor_value = 0xDB
        decoded_bytes = []
        for byte in binary:
            # Apply the xor and convert to a character.
            char = chr(byte ^ xor_value)
            # Store it.
            decoded_bytes.append(char)
            # Advance the xor_value, keeping to the byte range.
            xor_value = (xor_value + 1) % 256
        return ''.join(decoded_bytes)

        
    def Read(s, cat_path, error_if_not_found = False):
        '''
        Read an entry in the corresponding dat file, based on the
        provided file name (including internal path).

        * cat_path
          - String, path of the file to look up in cat format, which
            includes the 'addon' as needed.
          - If packed files are wanted, this should end in .pck.
        * error_if_not_found
          - Bool, if True and the name is not recorded in this cat, then
            an exception will be thrown, otherwise returns None.
        '''
        # Check for the file being missing.
        if cat_path not in s.file_size_dict:
            if error_if_not_found:
                raise Exception('File {} not found in cat {}'.format(
                    virtual_path, s.cat_name
                    ))
            return None

        # For now, open the dat file on every call and close it
        #  afterwards.  Could also consider leaving this open
        #  across calls, if many reads are expected, for a speedup.
        with open(s.dat_path, 'rb') as file:
            # Move to the file start location.
            file.seek(s.file_offset_dict[cat_path])
            # Grab the byte range.
            data = file.read(s.file_size_dict[cat_path])

        # The data was encoded by xoring with 0x33, so apply this operation
        #  to every byte to decode.
        # Note: this method seems somewhat slow to run.
        # Use bytearray for this, since it can be useful elsewhere for
        #  mutability (mainly obj code).
        data = bytearray(x ^ 0x33 for x in data)

        # Numpy might be faster, but want to avoid non-standard packages.
        # Alternative: bytes objects are immutable like strings, so the
        #  constructor above might be running into issues making excessive
        #  copies; a bytearray might work better.
        #data = bytearray(data)
        #for index, byte in enumerate(data):
        #    data[index] = byte ^ 0x33
        # Result: this only seems maybe 10-20% faster, if that; it might
        #  be fine when not using a debugger.
        # Keep the simple code version for now; complexity is not worth
        #  such a small gain.

        return data

