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
from Common.Settings import Settings
import os

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
      - Dict, keyed by file path and name, containing the integer
        number of bytes of file data in the dat file.
      - Essentially, a direct unpacked version of the cat contents.
      - File paths use forward slashes as separators, and start in the
        base X3 directory (above 'addon').
    * file_offset_dict
      - Dict, keyed by file path and name, containing the integer
        offset into the dat file where the contents begin.
      - This is summed from prior entries in the file_size_dict.
    * file_name_to_path_dict
      - Dict, keyed by file name (without path), holding the path and name
        for the file as represented in the other dicts.
      - If a multiple files share a name, this will hold the last one
        seen.
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
            packed_file_name, size_str = line.rsplit(' ', 1)
            size_bytes = int(size_str)

            # Record its size and start offset.
            s.file_size_dict[packed_file_name] = size_bytes
            s.file_offset_dict[packed_file_name] = start_offset

            # Advance the offset for the next packed file.
            start_offset += size_bytes


        # Isolate file names from their paths, to aid in lookups.
        s.file_name_to_path_dict = {}
        for file_path_name in s.file_size_dict:
            # Grab the last part, after the last /.
            name = file_path_name.rsplit('/',1)[-1]
            s.file_name_to_path_dict[name] = file_path_name

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


    def Get_Path(s, file_name):
        '''
        Returns the internal cat path for a given file_name.
        If the name is not found, returns None.
        The provided name may already have the path specified, in
         which case this will return the input if the file is found.
        '''
        # If the input doesn't match a full path+name, try to find a matching
        #  base name.
        if (file_name not in s.file_size_dict 
        and file_name in s.file_name_to_path_dict):
            # Grab that full path.
            file_name = s.file_name_to_path_dict[file_name]
            
        # Check if the file is in this cat.
        # Returns None if not, or maybe toss an exception.
        if file_name not in s.file_size_dict:
            return None
        # Return the name, now with path.
        return file_name

    
    def Read(s, file_name, error_if_not_found = False):
        '''
        Read an entry in the corresponding dat file, based on the
        provided file name (including internal path).

        * file_name
          - String, name of the file with path, as recorded in the cat.
          - Alternatively, may be the pathless name, in which case any
            matching file may be returned.
        * error_if_not_found
          - Bool, if True and the name is not recorded in this cat, then
            an exception will be thrown, otherwise returns None.
        '''
        # Convert to a full path, if needed, or None if not found.
        file_path_name = s.Get_Path(file_name)

        if file_path_name == None:
            if error_if_not_found:
                raise Exception('File {} not found in cat {}'.format(
                    file_name, s.cat_name
                    ))
            return None

        # For now, open the dat file on every call and close it
        #  afterwards.  Could also consider leaving this open
        #  across calls, if many reads are expected, for a speedup.
        with open(s.dat_path, 'rb') as file:
            # Move to the file start location.
            file.seek(s.file_offset_dict[file_path_name])
            # Grab the byte range.
            data = file.read(s.file_size_dict[file_path_name])

        # The data was encoded by xoring with 0x33, so apply this operation
        #  to every byte to decode.
        # Note: this method seems somewhat slow to run.
        data = bytes(x ^ 0x33 for x in data)

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

