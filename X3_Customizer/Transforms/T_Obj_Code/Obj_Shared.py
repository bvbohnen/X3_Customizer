'''
General support for obj patching.
'''
import inspect
# This function will convert hex strings to bytes objects.
from binascii import unhexlify as hex2bin
from binascii import hexlify as bin2hex
import re
import copy

from ... import Common
from ... import File_Manager

# Some random, short assembly codes.
# TODO: maybe flesh these all out, with functions for ones that take
#  a followup const.
# TODO: update manual assembly to use these (requires re-verification
#  of updated patches).
PUSH_0         = '01'
PUSH_1         = '02'
PUSH_2         = '03'
PUSHB          = '05' # 1 byte int push
PUSHW          = '06' # 2 byte int push
PUSHD          = '07' # 4 byte int push
NOP            = '0C'
PUSH           = '0D'
POP            = '24'
JUMP           = '32'
JUMP_IF_NOT_0  = '33'
JUMP_IF_0      = '34'
begin_critical = '6F'
end_critical   = '70'
RETURN         = '83'

# Call codes.
CALLASM        = '82'
# For 85/87, use the address in the disassembler .str output file
#  for the method name.
# For 86/88, use the base address of the method code entry.
# target->method(num_args, *args)
CALL85         = '85'
# target->class.method(num_args, *args)
CALL86         = '86'
# this->method(num_args, *args)
CALL87         = '87'
# this->class.method(num_args, *args)
CALL88         = '88'


class Obj_Patch:
    '''
    Patch to apply to the .obj file.

    Attributes:
    * file
      - String, name of the obj file being edited.
    * ref_code
      - String, the code starting at the offset which is being replaced.
      - Used for verification and for offset searching.
      - Use '.' for any wildcard match.
      - Will be converted to a regex pattern, though the string should
        not be formatted as a regex pattern.
    * new_code
      - Byte string, the replacement code.
      - Length of this doesn't need to match ref_code.
      - Replacements will be on a 1:1 basis with existing bytes, starting
        at a matched offset and continuing until the end of the new_code.
      - Overall obj code will remain the same length.
      - Also supports byte deletions and insertions, to aid in moving
        code sections.  A '-' removes 1 byte, a '+' inserts one byte
        with a default 0 value.  Replacements continue after deletions
        points, and overwrite insertion points, eg. '++0607' will insert
        two bytes of values '0607'. The number of '-' and '+' must
        always match.
    * expected_matches
      - Int, number of places in code a match should be found.
      - Normally 1, but may be more in some cases of repeated code that
        should all be patched the same way.
    '''
    def __init__(s, file, ref_code, new_code, expected_matches = 1):
        s.file = file
        s.ref_code = ref_code
        s.new_code = new_code
        s.expected_matches = expected_matches


def _String_To_Bytes(string, add_escapes = False):
    '''
    Converts the given string into bytes.
    Strings should either be hex representations (2 characters at a time)
    or wildcards given as '.' (also in pairs, where .. matches a single
    wildcard byte). Byte values that match special regex control
    chars will be escaped.

    * add_escapes
      - Bool, if True then re.escape will be called on the non-wildcard
        entries.
      - This should be applied if the bytes will be used as a regex pattern.
    '''
    # To make striding more convenient, double all + and - so that they take
    #  up 2 chars each.
    string = string.replace('-','--').replace('+','++')

    # Make sure the input is even length, since hex conversions
    #  require 2 chars at a time (to make up a full byte).
    assert len(string) % 2 == 0

    new_bytes = b''

    # Loop over the pairs, using even indices.
    for even_index in range(0, len(string), 2):
        char_pair = string[even_index : even_index + 2]
        
        # Special chars will be handled directly.
        if char_pair == '..':
            # Encode as a single '.' so this matches one byte.
            new_bytes += str.encode('.')
        # Everything else should be strings representing hex values.
        else:
            this_byte = hex2bin(char_pair)
            # Note: for low values, this tends to produce a special
            #  string in the form '\x##', but for values that can map
            #  to normal characters, it uses that character instead.
            # However, that character could also be a special regex
            #  character, and hence direct mapping is not safe.
            # As a workaround, aim to always put an escape character
            #  prior to the encoded byte; however, this requires that
            #  the escape be a byte also (a normal python escape will
            #  escape the / in /x## and blows up). Hopefully regex
            #  will unpack the byte escape and work fine.
            # Use re.escape for this, since trying to do it manually
            #  is way too much effort (get 'bad escape' style errors
            #  easily).
            # Note: re.escape does something weird with \x00, converting
            #  it to \\000, but this appears to be okay in practice.
            if add_escapes:
                this_byte = re.escape(this_byte)
            new_bytes += this_byte

    return new_bytes


def Int_To_Hex_String(value, byte_count):
    '''
    Converts an int into a hex string, with the given byte_count
    for encoding. Always uses big endian.
    Eg. Int_To_Hex_String(62, 2) -> '003e'
    '''
    # Convert this into a byte string, hex, then back to string.
    # Always big endian.
    # Kinda messy: need to encode the int to bytes, then go from the
    #  byte string to a hex string, then decode that back to unicode.
    return bin2hex(value.to_bytes(byte_count, byteorder = 'big')).decode()
    

def Get_Matches(patch):
    '''
    Find locations in the obj code where a patch can be applied.
    Returns a list of re match objects.

    This will search for the ref_code, using regex, and applies
    the patch where a match is found.
    Error if the number of matches is not what the patch expects, or if
    the match location doesn't match the reference code.
    '''
    file_contents = File_Manager.Load_File(patch.file)

    # Get a match pattern from the ref_code, using a bytes pattern.
    # This needs to convert the given ref_code into a suitable
    #  regex pattern that will match bytes.
    ref_bytes = _String_To_Bytes(patch.ref_code, add_escapes = True)
    pattern = re.compile(
        ref_bytes,
        # Need to set . to match newline, just in case a newline character
        #  is in the wildcard region (which came up for hired TLs).
        flags = re.DOTALL)

    # Get all match points.
    # Need to use finditer for this, as it is the only one that will
    #  return multiple matches.
    # Note: does not capture overlapped matches; this is not expected
    #  to be a problem.
    matches = [x for x in re.finditer(
        pattern, 
        file_contents.binary
        )]
    
    # Look up the calling transform's name for any debug printout.
    try:
        caller_name = inspect.stack()[1][3]
    except:
        caller_name = '?'

    # Do the error check if a non-expected number of matches found.
    if len(matches) != patch.expected_matches:
        # Can raise a hard or soft error depending on mode.
        # Message will be customized based on error type.
        if Common.Settings.developer:
            print('Error: Obj patch reference code found {} matches,'
                 ' expected {}, in {}.'.format(
                     len(matches),
                     patch.expected_matches,
                     caller_name,
                     ))
            print('Pattern in use:')
            print(pattern)
        else:
            raise Common.Obj_Patch_Exception()
        return
    

    # Loop over the matches to check each of them.
    for match in matches:

        # Grab the offset of the match.
        offset = match.start()
        #print(hex(offset))

        # Get the wildcard char, as an int (since the loop below unpacks
        #  the byte string into ints automatically, and also pulls ints
        #  from the original binary).
        wildcard = str.encode('.')[0]

        # Quick verification of the ref_code, to ensure re was used correctly.
        # This will not add escapes, since they confuse the values.
        for index, ref_byte in enumerate(_String_To_Bytes(patch.ref_code)):

            # Don't check wildcards.
            if ref_byte == wildcard:
                continue

            # Check mismatch.
            # This exists as a redundant verification added during
            #  code development to make sure the regex match location was
            #  correct.
            original_byte = file_contents.binary[offset + index]
            if ref_byte != original_byte:
                if Common.Settings.developer:
                    print('Error: Obj patch regex verification mismatch')
                    return
                else:
                    raise Common.Obj_Patch_Exception()

    return matches


def Apply_Obj_Patch(patch):
    'Applies a single patch. Redirects to Apply_Obj_Patch_Group.'
    Apply_Obj_Patch_Group([patch])


def Apply_Obj_Patch_Group(patch_list):
    '''
    Applies a group of patches as a single unit.
    If any patch runs into an error, no patch in the group will be applied.
    '''
    # Start with a search for matches.
    # These calls may raise an exception on error, or could return None
    #  in dev mode.
    matches_list = []
    for patch in patch_list:
        matches_list.append(Get_Matches(patch))

    # Return early on a None was returned.
    if None in matches_list:

        # Get the indices of the patches that had errors or no errors.
        correct_patches = []
        failed_patches  = []
        for index, matches in enumerate(matches_list):
            if matches == None:
                failed_patches.append(index)
            else:
                correct_patches.append(index)

        # Print them.
        if Common.Settings.developer:
            print('Correct patches : {}.'.format(
                     correct_patches ))
            print('Failed patches  : {}.'.format(
                     failed_patches ))
        return

    # It should now be safe to apply all patches in the group.    
    for patch, matches in zip(patch_list, matches_list):
        file_contents = File_Manager.Load_File(patch.file)

        # Loop over the matches to apply each of them.
        for match in matches:

            # Grab the offset of the match.
            offset = match.start()

            # Verify there are a matched number of insertions and
            #  deletions in the new_code.
            if patch.new_code.count('+') != patch.new_code.count('-'):
                raise Exception('Error: Obj patch changes code size.')
                        
            #-Removed; old style before insert/delete characters were
            #  added in. Was this unsafe on the wildcards anyway, which
            #  could take the same value as normal bytes? May have just
            #  gotten lucky that this case didn't come up.
            ## Get the wildcard char, as an int (since the loop below unpacks
            ##  the byte string into ints automatically, and also pulls ints
            ##  from the original binary).
            #wildcard = str.encode('.')[0]
            ## Apply the patch, leaving wildcard entries unchanged.
            ## This will edit in place on the bytearray.
            #new_bytes = _String_To_Bytes(patch.new_code)
            #for index, new_byte in enumerate(new_bytes):
            #    if new_byte == wildcard:
            #        continue
            #    file_contents.binary[offset + index] = new_byte

            # Stride through the new code.
            # For convenience, this will work on char pairs (for byte
            #  conversion when needed), and so a pre-pass will duplicate
            #  all control characters (+-) accordingly. '.' is not
            #  duplicated since it is already doubled in the original
            #  string.
            new_code = patch.new_code
            for control_char in ['+','-']:
                new_code = new_code.replace(control_char, control_char*2)

            # Note the code length before starting, for error check later.
            start_length = len(file_contents.binary)

            # Loop over the pairs, using even indices.
            for even_index in range(0, len(new_code), 2):
                char_pair = new_code[even_index : even_index + 2]
                
                # If this is a wildcard, advance the offset with no change.
                if char_pair == '..':
                    offset += 1

                # If this is a deletion, remove the byte from the 
                #  file_contents and do not advance the offset (which will
                #  then be pointing at the post-deletion byte automatically).
                elif char_pair == '--':
                    file_contents.binary.pop(offset)
                    
                # If this is an addition, insert a 0.
                elif char_pair == '++':
                    file_contents.binary.insert(offset, 0)

                else:
                    # This is a replacement byte.
                    # Convert it, insert, and inc the offset.
                    # Note: bytearray requires an int version of this value,
                    #  and hex2bin returns a byte string version.
                    #  Indexing into a bytearray of byte strings
                    #  returns an int, not a string.
                    new_byte = hex2bin(char_pair)[0]
                    file_contents.binary[offset] = new_byte
                    offset += 1

            # Error check.
            assert len(file_contents.binary) == start_length
    return
