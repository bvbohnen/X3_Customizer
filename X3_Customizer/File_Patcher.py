'''
Code for generating and applying unified diff patches to
files being modified.
Goal is to be able to make relatively clean edits to the existing
x3 scripts and other source files without having to copy the
contents.
Initial version is not expected to support multiple patches to
the same file through this method.

This will operate on files in the patches folder.
This folder should generally have three versions of any given file:
    file_name
    file_name.patch
    [source file from the x3 directory]

    The bare file is the modified version, eg. out of Exscriptor, kept
    without a suffix for easier editing (eg. retain a .xml suffix).

    The .patch version contains the unified diff, and is the component
    to generally upload to the repository and distribute.

    The source file will generally be read from the x3 directory,
    after setting up the path using Set_Path() as with normal transforms.

To make a patch from a modified file, call Generate_Patch(file_name).
To rebuild a modified file from a patch, call Generate_Original(file_name).
These should be called using the flow for normal transforms, after
setting up paths appropriately for finding the source files.


Problem:
    Exscriptor/XStudio write their xml output in a different format than that
    used in the x3 source files, eg. with different indentation, and also do
    not include the sourceplaintext section, plus there is a possibility
    that element attributes will be given in a different order (when it
    is arbitrary), and the text gets a bit jumbled between nodes.
    Because of this, the diffs tend to include the full file contents, and
    are duplicated with the original and modified encodings.

    Possible solutions:
        1) Switch to using xml parsing and a diff generator, which should
        handle the indentation and attribute order inconsistencies.
            -Requires other external libraries.
            -Does not handle sourceplaintext discrepency automatically.
        2) Edit the source file when reading it in to adjust it closer
        to the exscriptor version, removing the sourceplaintext section
        and increasing indents.
            -Messy to implement, and fragile to unexpected format changes.
        3) Load both xml files using elementtree, then convert them back
        to text, then take the diff.
            -Patch application will need to follow a similar procedure.
            -Should result in matched indentation and attribute ordering.
            -Still needs removal of sourceplaintext, but this is easy
            since it is just an xml element to delete.

    Go with option (3), which should work out the best overall, albeit
    slightly slowing down patch application since the source files need
    to be xml parsed whenever a patch is applied (eg. every time the
    manager is run).

    Update: solution doesn't really deal with the text jumbling, where
    the x3 version may have some characters in a var node, and the
    other tools move those chars to a text node.
    Also, the x3 version often uses encoded characters to avoid spaces
    and some other special chars, where the tools just put in spaces/etc
    directly, further troubling the diff.


    New solution:
    For these script edits, try to do them in game and save there.
    While awkward, this should get the file format to sync up properly.
    Initial testing looks great (except the in game editor usage part).
    Middle ground: edit externally using X-Studio, make a version of the
    file without the ! (need to edit title and internals, eg. with a
    replace-all in notepad++), open in game, insert/delete a line,
    resave, put the ! back.

    Update:
    When editing scripts from mods, they may not be saved from the
    game, or could be from a much older version.
    In such cases, normalizing the file format somewhat may provide
    some relief.
    This will be done on a per-file basis.


For applying the diff as a patch, can  use third party code.
    This is mit licensed, but designed to work on files, not raw text.
    https://github.com/techtonik/python-patch
    Another, seemingly much simpler option would be this, but it lacks a license.
    https://gist.github.com/noporpoise/16e731849eb1231e86d78f9dfeca3abc
    This code has an mit license and works on text, but when tried out
    it had some bugs (was not applying all patch changes, eg. skipping
    the signature removal).
    https://github.com/danielmoniz/merge_in_memory
Ultimately, a very simple patch application function will be written,
since it can be debugged easily that way.

'''
from File_Manager import *
import os
import difflib
import xml.etree.ElementTree
from xml.dom import minidom
import re
This_dir = os.path.normpath(os.path.dirname(__file__))


def Make_Patch(file_name, verify = False, reformat_xml = False):
    '''
    Generates a patch for the given file in the patches folder.
    The patch will be the same name suffixed with .patch.
    If verify == True, a call to Apply_Patch will be made, and
    the resulting text compared to the original modified file
    to verify a match.
    The file_name should match the original source file that
    was modified, and which can be found using a standard
    call to Load_File after the source folder has been setup.
    If reformat_xml == True, this will parse xml files, strip out
    whitespace, and reconvert them to strings, to somewhat
    standardize formatting between inputs.
    '''
    print('Making patch for {}'.format(file_name))

    # Error if the modified file not found.
    modified_path = os.path.join(This_dir, 'patches', file_name)
    if not os.path.exists(modified_path):
        print('Error: file {} not found in /patches'.format(file_name))
        return

    # Get the modified text.
    with open(modified_path, 'r') as file:
        modified_file_text = file.read()

    # Search out the source file.
    try:
        source_file_text = Load_File(file_name, return_text = True)
    except File_Missing_Exception:
        print('Error: source for file {} not found'.format(file_name))
        return

    # Do some extra handling of xml to standardize format.
    if file_name.endswith('.xml'):

        # Look up the encoding on the source file, to be safe.
        # This is generally expected to be whatever was used as default
        # for scripts, which don't specify encoding; eg. utf-8.
        encoding = Load_File(file_name, return_t_file = True).encoding

        # Optionally try to reformat.
        # This will probably not end up being used, since attempts to
        # match up formatting didn't pan out due to too many integrated
        # differences.
        if reformat_xml:
            source_file_text = Standardize_XML_Format(source_file_text, encoding)
            modified_file_text = Standardize_XML_Format(modified_file_text, encoding)
        
    else:
        # Use some default encoding.
        encoding = None


    # From these, can get the diff.
    # This requires lists of strings as input, and works line-by-line,
    # doing full line replacements. The lines in the lists should
    # end in newlines to work properly.
    source_file_lines = list(source_file_text.splitlines(keepends=True))
    modified_file_lines = list(modified_file_text.splitlines(keepends=True))
    unified_diff = difflib.unified_diff(
        source_file_lines,
        modified_file_lines,
        # 'n' is the number of context lines to include around the
        # block sections changed. In general, want this to be 0 to
        # avoid including excess input lines, though with these it
        # may be possible to patch a file that doesn't match the
        # exact original source (eg. with changed line numbers).
        n = 0)

    # Write this out as-is to act as a patch.
    patch_path = modified_path + '.patch'
    with open(patch_path, 'w') as file:
        file.writelines(unified_diff)

    if verify:
        # Apply the patch, get the modified file back.
        patched_file_text = Apply_Patch(file_name, reformat_xml)
        # Compare the patched file to the original modified file.
        if patched_file_text != modified_file_text:
            print('Error: patch did not reproduce the original modified input.'
                  'Writing result to {}.patched for viewing.'.format(file_name))
            with open(os.path.join(This_dir, 'patches', file_name+'.patched'), 'w') as file:
                file.write(patched_file_text)

    return


def Apply_Patch(file_name, reformat_xml = False):
    '''
    Reads and applies a patch to the original text, producing the
    modified text, and updates the File_Manager object accordingly.
    Returns the modified text.
    '''
    # Error if the patch file not found.
    patch_path = os.path.join(This_dir, 'patches', file_name + '.patch')
    if not os.path.exists(patch_path):
        print('Error: patch for file {} not found in /patches'.format(file_name))
        return
    
    # Get the patch text.
    with open(patch_path, 'r') as file:
        patch_file_text = file.read()

    # Search out the source file.
    try:
        source_t_file = Load_File(file_name, return_t_file = True)
        source_file_text = source_t_file.text
    except File_Missing_Exception:
        print('Error: source for file {} not found'.format(file_name))
        return
    
    # Do some extra handling of xml to standardize format.
    if file_name.endswith('.xml'):
        # Look up the encoding on the source file, to be safe.
        # This is generally expected to be whatever was used as default
        # for scripts, which don't specify encoding; eg. utf-8.
        encoding = Load_File(file_name, return_t_file = True).encoding
        # Optionally try to reformat.
        if reformat_xml:
            source_file_text = Standardize_XML_Format(source_file_text, encoding)


    # To apply the patch manually, can traverse the changed blocks,
    # get their source file start line, blindly apply deletions and
    # insertions (- and + lines in the patch), and should end up
    # with everything correct.

    # Operate on a list of source lines, for easy deletion and insertion.
    # Split manually on newline, to ensure any final last empty line is
    # kept (so any verification match doesn't get a false error).
    modified_file_lines = list(source_file_text.split('\n'))

    # Keep track of insertions and deletions, to correct source line indices 
    # from the patch based on prior changes.
    line_offset = 0

    # Track if an error occurs.
    error = False

    # Loop over the patch lines.
    for patch_line in patch_file_text.splitlines():

        # Skip the file name definitions, prefixed by --- and +++, which
        # should be empty anyway since not specified earlier.
        if patch_line.startswith('---') or patch_line.startswith('+++'):
            continue

        # A line with @@ has this format:
        # @@ -source_line_start,source_line_count +dest_line_start,dest_line_count @@
        # or
        # @@ -source_line_start +dest_line_start @@
        # The latter appears when only 1 line is changed.
        # Only the source_line_start is really needed, since line counts
        # are implicit in how many - and + lines are present below the tag
        # if the patch file is well formed.
        elif patch_line.startswith('@@'):
            # Isolate it by splitting on the - and , or ' ' surrounding it.
            post_dash    = patch_line.split('-')[1]
            source_terms = post_dash.split(' ')[0]
            if ',' in source_terms:
                line_number  = int(source_terms.split(',')[0])
                source_count = int(source_terms.split(',')[1])
            else:
                line_number  = int(source_terms)
                # Default is 1 line changed.
                source_count = 1

            # Note: patch line numbers start from 1, but the list is 0 indexed,
            # so decrement by 1 to get the proper index.
            line_number -= 1
            # In the special case of a line not being deleted, and only
            # insertions happening, those insertions should be placed after
            # the line. To handle this nicely, check this case and bump
            # the line number when found.
            if source_count == 0:
                line_number += 1
            # Apply the line offset based on prior changes.
            line_number += line_offset
            continue

        # Delete a line if needed.
        elif patch_line.startswith('-'):
            # Pop off the line, and verify it matches the reference
            # in the patch.
            line_text = modified_file_lines.pop(line_number)
            ref_text = patch_line.replace('-','',1)
            if line_text != ref_text:
                error = True
                print('Error: patch line removal mismatch')
            # After the pop, line_number points to the next line (which
            # moved down an index), so leaving it unchanged should
            # support another pop following this.
            # Decrease the overall offset for future patch blocks.
            line_offset -= 1

        elif patch_line.startswith('+'):
            # Isolate the patch text and insert it.
            ref_text = patch_line.replace('+','',1)
            modified_file_lines.insert(line_number, ref_text)
            # The line number should now advance, so that another insertion
            # goes to the next line.
            line_number += 1
            # Increase the overall offset for future patch blocks.
            line_offset += 1
    
        # Any other lines in the patch are likely just context, and
        # can be safely ignored.


    # Rejoin the list into a text block, adding back the newlines.
    modified_file_text = '\n'.join(modified_file_lines)

    if error:
        print('Skipping {} due to patch error'.format(file_name))
    else:
        # Update the T file object directly.
        source_t_file.text = modified_file_text

    # Also return a copy of the new text if desired.
    return modified_file_text


def Standardize_XML_Format(xml_text, encoding):
    '''
    Standardize the newlines, indentation, and attribute ordering
    for an xml text block.
    '''    
    element_root = xml.etree.ElementTree.fromstring(xml_text)

    # Note: excess indentation can arise from the text or tail of each element,
    # eg. when it is a newline followed by spaces that prefix the next
    # element when printed, or a newline in a text field preceeding a
    # subelement.
    for element in element_root.iter():
        # If nothing is left after splitting on the whitespace, can
        # replace with an empty string.
        if element.tail:
            if not ''.join(re.split('\s+', element.tail)):
                element.tail = ''
        if element.text:
            if not ''.join(re.split('\s+', element.text)):
                element.text = ''
    modified_xml_text = xml.etree.ElementTree.tostring(element_root, 
                                                        encoding = "unicode")

    # Get rid of exscriptor "linenr" attributes from elements, which aren't
    # present in source scripts.
    for element in element_root.iter():
        element.attrib.pop('linenr', None)
                    
    # For source scripts, remove the sourceplaintext element that is not
    # present in exscriptor scripts.
    source_plain_text = element_root.find('sourceplaintext')
    if source_plain_text != None:
        element_root.remove(source_plain_text)

    # Getting standard format of lines/indents appears to require
    #  the minidom package instead.
    # Examples online just feed the elementtree text output into
    #  this and remake the text.
    # Note: elementtree output is a byte string, but minidom output
    #  appears to be a normal python string.
    modified_xml_text = xml.etree.ElementTree.tostring(element_root)
    minidom_version = minidom.parseString(modified_xml_text)
    # Make sure the final string is encoded the same way as the input,
    # else oddities can arise with eg. how spaces are given.
    modified_xml_text = minidom_version.toprettyxml(indent="\t")

    return modified_xml_text