'''
Support for packing files to a cat/dat pair.
See Cat_Reader for details on catalog files.

TODO: compression.
Extensions to use:
 xml,txt -> pck
 bob -> pbb
 bod -> pbd
All appear to use gzip, according to some google searching.

'''
from ..Common.Settings import Settings
import os
from pathlib import Path
from .File_Paths import *
from . import File_Types
import gzip


class Cat_Writer:
    '''
    Support class for collecting modified files into a single catalog.
    Initial functionality will not gzip the files.

    Attributes:
    * cat_path
      - Path, the full path to the cat file.
    * dat_path
      - Path, the full path to corresponding dat file.
      - Set automatically to match the cat_path index.
    * game_files
      - List of Game_File objects to be written.
    '''
    def __init__(self, cat_path):
        # Ensure this is a Path.
        self.cat_path = Path(cat_path)
        self.dat_path = self.cat_path.with_suffix('.dat')
        self.game_files = []

        return


    def Add_File(self, game_file):
        '''
        Add a Game_File to be recorded into the catalog.
        '''
        assert isinstance(game_file, File_Types.Game_File)
        self.game_files.append(game_file)


    def Write(self):
        '''
        Write the contents to a cat/dat file pair.
        Any existing files will be overwritten.
        '''
        # Cat contents will be kept as a list of strings.
        # Dat contents will be running binary.
        # First pass gets raw (maybe zipped) binary; second pass will encode.
        cat_lines = []
        dat_binary = bytearray()

        # The first cat line is the name of the dat file, no path.
        cat_lines.append(self.dat_path.name)

        # Collect info from the files.
        # Note: this may generate nothing if no game files were added,
        #  eg. when making dummy catalogs.
        for game_file in self.game_files:

            # Get the binary data; any text should be utf-8.
            this_binary = game_file.Get_Binary()

            # Get the cat path for the file.
            cat_path = Virtual_Path_to_Cat_Path(game_file.virtual_path)

            # Get any possible compressed version of this path.
            # This is None if packing not supported.
            cat_path_pck = Unpacked_Path_to_Packed_Path(cat_path)

            # If packing, gzip the binary.
            if cat_path_pck:
                this_binary = gzip.compress(this_binary)
                # Use the pck name in the catalog.
                cat_path = cat_path_pck
                
            # Append to the existing dat binary.
            dat_binary += this_binary

            # Add the virtual path and the byte size of the file to the cat.
            cat_lines.append(cat_path +' '+ str(len(this_binary)))

        # The cat needs to end in a newline.
        cat_lines.append('')

        # Convert the cat to utf-8 binary.
        cat_str = '\n'.join(cat_lines)
        cat_binary = bytes(cat_str, encoding = 'utf-8')

        # Do the Xor encoding passes.
        cat_binary = self.Encode_Cat(cat_binary)
        dat_binary = self.Encode_Dat(dat_binary)

        # Write the data out.
        with open(self.cat_path, 'wb') as file:
            file.write(cat_binary)
        with open(self.dat_path, 'wb') as file:
            file.write(dat_binary)

        return


    @staticmethod
    def Encode_Cat(binary):
        '''
        Encode the cat binary using a running Xor.
        '''
        xor_value = 0xDB
        encoded_bytes = bytearray()
        for byte in binary:
            # Apply the xor and store it.
            encoded_bytes.append(byte ^ xor_value)
            # Advance the xor_value, keeping to the byte range.
            xor_value = (xor_value + 1) % 256
        return encoded_bytes
    

    @staticmethod
    def Encode_Dat(binary):
        '''
        Encode the dat binary using an Xor.
        '''
        encoded_bytes = bytearray()
        encoded_bytes = bytearray(x ^ 0x33 for x in binary)
        return encoded_bytes

    #-Older, x2? style encoding used in loose pck files.
    #@staticmethod
    #def Encode_Dat(binary):
    #    '''
    #    Encode the dat binary using an Xor.
    #    '''
    #    # This will add 1 byte at the start, which gets xor'd with all
    #    #  following bytes along with 0xC8.
    #    # Try 0 for the first byte for now; maybe look into this more if
    #    #  the game expects something else.
    #    encoded_bytes = bytearray()
    #    encoded_bytes.append(0)
    #    magic = encoded_bytes[0] ^ 0xC8
    #    encoded_bytes = bytearray(x ^ magic for x in binary)
    #    return encoded_bytes

        
