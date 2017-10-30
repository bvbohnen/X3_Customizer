'''
Generate documentation for the customizer.
This will parse the docstrings at the top of X3_Customizer and
for each transform, and write them to a plain text file.

This can generally be called directly as an entry function.


Quick markdown notes, for the readme which will be dispayed on
github, and the main documentation just because:

 -Newlines don't particularly matter. Can break up lines for a text
 file, and they will get joined back together.

 -This is bad for a list of transforms, since they get lumped together,
 so aim to put markdown characters on them to listify them.

 -Adding asterisks at the start of lines will turn them into a list,
 as long as there is a space between the asterisk and the text.

 -Indentation by 4 spaces or 1 tab creates code blocks; try to avoid 
 this level of indent unless code blocking is intentional.

 -Indentation is built into some docstrings, though the only one that
 should matter for the markdown version is x3_customizer. That one needs
 to be carefully adjusted to avoid 4-space chains, including across
 newlines.

 -Triple -,*,_ will place a horizontal thick line. Can be used between
 sections. Avoid dashes, though, since they make whatever is above them
 into a header, unless that is desired.

'''

import X3_Customizer
import Change_Log
import Transforms
import File_Manager
import sys, os
from collections import OrderedDict

def Make(args):

    #TODO:
    #Make a variation on the simple doc which has some formatting for
    # the egosoft forum, including code blocks and removing newlines
    # when the next line starts with a lowercase character.

    #Make a list of lines or text blocks to print out.
    doc_lines = []

    #Also include a simple version, which will truncate
    # the transform descriptions, aimed at providing a summary which
    # is suitable for posting.
    #Git appears to expect a README.md file; this can be used to
    # generate that, although one directory up.
    doc_short_lines = []

    #Set the indent type. A single spaces for now.
    #Avoid indenting by 4 unless wanting a code block, for the simple
    # file that gets markdowned.
    indent = ' '

    def Make_Horizontal_Line(include_in_simple = True):
        'Adds a horizontal line, with extra newline before and after.'
        this_line = '\n***\n'
        doc_lines.append(this_line)
        if include_in_simple:
            doc_short_lines.append(this_line)

    def Add_Line(line, indent_level = 0, include_in_simple = True):
        'Add a single line to the files, including any newlines.'
        #Prefix with a number of indents.
        this_line = indent * indent_level + line
        doc_lines.append(this_line)
        if include_in_simple:
            doc_short_lines.append(this_line)

    def Add_Lines(text_block, indent_level = 0, 
                  include_in_simple = True,
                  only_header_in_simple = False,
                  merge_lines = False):
        '''
        Record a set of lines from text_block, with indent, splitting on
        newlines. May not include all starting or ending newlines, depending
        on behavior of splitlines(). Starting newlines are explicitly
        ignored.
        If include_in_simple == True, the simple file will not have any
        lines added.
        If only_header_in_simple == True, the simple file will not have
        any lines added past the first empty line following a text line,
        eg. only the first group of text lines are included.
        If merge_lines == True, this will attempt to merge lines together
        that appear to be part of the same paragraph.
        '''
        #Merge before further processing.
        if merge_lines:
            text_block = Merge_Lines(text_block)

        #Flag for when an empty line is found.
        #This will not count any pruned starting empty lines, eg. when
        # triple quotes are used they tend to put an initial empty line.
        empty_line_found = False
        non_empty_line_found = False

        #Loop over the lines.
        for line in text_block.splitlines():

            #Note if this line has contents.
            if not non_empty_line_found and line.strip():
                non_empty_line_found = True
            #Skip until a non empty line found.
            if not non_empty_line_found:
                continue

            #Note if this is an empty line.
            if not empty_line_found and not line.strip():
                empty_line_found = True

            #Prefix with a number of indents.
            this_line = indent * indent_level + line
            #Add to the main document.
            doc_lines.append(this_line)
            if include_in_simple:
                #Add to the short document only if including everything or
                # an empty line not hit yet.
                if not (only_header_in_simple and empty_line_found):
                    doc_short_lines.append(this_line)


    def Record_Func(function, 
                    indent_level = 0, 
                    end_with_empty_line = True,
                    include_in_simple = False):
        '''
        Adds lines for a function name with docstring and requirements.
        If include_in_simple == True, the simple file is skipped entirely.
        Otherwise, the simple file will get a truncated name with the initial
        part of the docstring, and no requirement list.
        '''

        #Get the name as-is.
        #Put an asterix in front for markdown.
        Add_Line('* ' + function.__name__, indent_level, 
                  include_in_simple = include_in_simple)

        #If there are required files, print them.
        if hasattr(function, '_file_names'):
            #For markdown, don't want this attached to the file name,
            # but also don't want it causing an extra list indent on
            # the docstring. An extra newline and a healthy indent
            # seems to work.
            Add_Line('', include_in_simple = False)
            Add_Lines('{}Requires: {}'
                        .format(
                             indent * (indent_level + 1),
                             #Join the required file names with commas.
                             ', '.join(function._file_names)),
                         indent_level +1,
                         include_in_simple = False
                         )

        #Stick another newline, then the function docstring, maybe
        # truncated for the simple file.
        Add_Line('', include_in_simple = include_in_simple)
        Add_Lines(function.__doc__, indent_level +1, 
                  include_in_simple = include_in_simple,
                  only_header_in_simple = True,
                  #Get rid of excess newlines.
                  merge_lines = True
                  )

        if end_with_empty_line:
            Add_Line('')


    #Grab the main docstring.
    #TODO: figure out how to split off the example tree.
    Add_Lines(X3_Customizer.__doc__, merge_lines = True)
    
    #Add a note for the simple documentation to point to the full one.
    doc_short_lines.append('\nFull documentation found in Documentation.md.')

    #Grab any setup methods.
    #Skip this for the simple summary.
    Make_Horizontal_Line(include_in_simple = False)
    Add_Line('Setup methods:', include_in_simple = False)
    Add_Line('', include_in_simple = False)
    #For now, just the Set_Path method.
    Record_Func(File_Manager.Set_Path, indent_level = 2,
                include_in_simple = False)
    

    #Grab the various transform functions.
    #This can grab every item in Transforms that has been decorated with
    # Check_Dependencies.
    #Pack these into an ordereddict, keyed by a tuple of 
    # (home module name, function name), to enable different 
    # sorting options.
    transform_modules_dict = OrderedDict()
    for item_name in dir(Transforms):
        item = getattr(Transforms, item_name)

        #Check for the _file_names attribute, attached by the decorator.
        if hasattr(item, '_file_names'):
            #Record the transform.
            transform_modules_dict[(item.__module__,item.__name__)] = item
            

    #-Removed, old raw alphabetical style.
    ##Put a header for the transform list.
    #Make_Horizontal_Line()
    #Add_Line('Transform List:')
    #Add_Line('')
    #
    ##Go with alphabetical on transform name, item[0][1], eg. the
    ## key's second field.
    #for (module_name, transform_name), transform in sorted(transform_modules_dict.items(),
    #                                     key = lambda x: x[0][1]):
    #    #These will be in the simple file, though truncated.
    #    Record_Func(transform, indent_level = 1, include_in_simple = True)
            
    #Could alphabetize these or maybe categorize by the T module they
    # come from.  Straight categorization by python module isn't very
    # friendly to breaking up modules for code organization, though.
    #Solutions could be to explicitly categorize here, to explicitly
    # categorize in the transforms during setup, or to categorize by
    # the files being edited.
    #The edited files get messy in some cases, eg. when modifying
    # language files, so is probably not the best idea.
    #Categorizing at the transforms is difficult to edit if changing
    # around categories for any reason.
    #Go with explicit module categorization here, mainly joining up 
    # modules with similar names. This can match the first word after
    # the 'T_'.
    #In cases where the automatic category is unwanted, transforms may
    # specify an override category. This is in the transform._category
    # field.

    #Set up a dict keyed by category.
    category_name_transforms_dict_dict = OrderedDict()
    #Loop over the modules.
    for (module_name, transform_name), transform in transform_modules_dict.items():

        #Get a truncated module_name, the first word
        # after the underscore.
        category = module_name.split('_')[1]
        #Drop the ending 's' if there was one (which was mostly present to
        # mimic the X3 source file names, eg. 'tships'.
        if category[-1] == 's':
            category = category[0:-1]
        #If the transform has an override category, use it.
        if transform._category != None:
            category = transform._category

        #Create the category if needed.
        if not category in category_name_transforms_dict_dict:
            category_name_transforms_dict_dict[category] = OrderedDict()
        #Add to the category by name.
        category_name_transforms_dict_dict[category][transform_name] = transform

    #Can now print out by category.
    for category, transform_dict in sorted(category_name_transforms_dict_dict.items()):
    
        #Put a header for the category transform list.
        Make_Horizontal_Line()
        Add_Line('{} Transforms:'.format(category))
        Add_Line('')

        #Loop over the transforms in the category.
        for transform_name, transform in sorted(transform_dict.items()):
            #Add the text.
            Record_Func(transform, indent_level = 1, include_in_simple = True)



    #Print out the example module as well.
    #The example will accompany the simple version, since it is a good way
    # to express what the customizer is doing.
    Make_Horizontal_Line()
    Add_Line('Example input file, User_Transforms_Example.py:')
    #Need a newline before the code, otherwise the code block
    # isn't made right away (the file header gets lumped with the above).
    Add_Line('')
    with open('User_Transforms_Example.py', 'r') as file:
        #Put in 4 indents to make a code block.
        Add_Lines(file.read(), indent_level = 4)


    #Print out the change log.
    Make_Horizontal_Line()
    Add_Lines(Change_Log.__doc__, merge_lines = True)

    #Print out the license.
    #The simple version will skip this.
    #This probably isn't needed if there is a license file floating around
    # in the repository; remove for now.
    #Make_Horizontal_Line(include_in_simple = False)
    #with open(os.path.join('..','License.txt'), 'r') as file:
    #    Add_Lines(file.read(), include_in_simple = False)




    #Write out the full doc.
    #Put these 1 directory up to separate from the code.
    with open(os.path.join('..','Documentation.md'), 'w') as file:
        file.write('\n'.join(doc_lines))

    #Write out the simpler readme.
    with open(os.path.join('..','README.md'), 'w') as file:
        file.write('\n'.join(doc_short_lines))


def Merge_Lines(text_block):
    '''
    To get a better text file from the python docstrings, with proper
     full lines and wordwrap, do a pass over the text block and
     do some line joins.
    General idea is that two lines can merge if:
    -Both have normal text characters (eg. not '---').
    -Not in a code block (4+ space indent series of lines outside of
     a list).
    -Second line does not start a sublist (starts with -,*,etc.).
    Note: markdown merge rules are more complicated, but this should be
    sufficient for the expected text formats.
    This should not be called on code blocks.
    This will also look for and remove <code></code> tags, a temporary
    way to specify in docstrings sections not to be line merged.
    '''
    #List of lines to merge with previous.
    merge_line_list = []
    #Note if the prior line had text.
    prior_line_had_text = False
    #Note if a code block appears active.
    code_block_active = False
    #Convert the input to a list.
    line_list = [x for x in text_block.splitlines()]

    for line_number, line in enumerate(line_list):
        #Get rid of indent spacing.
        strip_line = line.strip()
        merge = True

        #If this is a <code> tag, start a code block, and remove
        # the tag.
        if strip_line == '<code>':
            code_block_active = True
            merge = False
            line_list[line_number] = ''
            strip_line = ''
            
        elif strip_line == '</code>':
            code_block_active = False
            merge = False
            line_list[line_number] = ''
            strip_line = ''

        #When a code block is active, don't merge.
        elif code_block_active:
            merge = False

        #Skip the first line; nothing prior to merge with.
        elif line_number == 0:
            merge = False
        
        #If the line is empty, leave empty.
        elif not strip_line:
            merge = False

        #If the line starts with a sublist character, don't merge.
        elif strip_line[0] in ['*','-']:
            merge = False

        #If the prior line didn't have text, don't merge.
        elif not prior_line_had_text:
            merge = False


        #If merging, record the line.
        if merge:
            merge_line_list.append(line_number)

        #Update the prior line status.
        prior_line_had_text = len(strip_line) > 0


    #Second pass will do the merges.
    #This will aim to remove indentation, and replace with a single space.
    #This will delete lines as going, requiring the merge_line numbers to be
    # adjusted by the lines removed prior. This can be captured with an
    # enumerate effectively.
    for lines_removed, merge_line in enumerate(merge_line_list):

        #Adjust the merge_line based on the current line list.
        this_merge_line = merge_line - lines_removed

        #Get the lines.
        prior_line = line_list[this_merge_line-1]
        this_line = line_list[this_merge_line]

        #Remove spacing at the end of the first, beginning of the second.
        prior_line = prior_line.rstrip()
        this_line = this_line.lstrip()

        #Join and put back.
        line_list[this_merge_line-1] = prior_line + ' ' + this_line

        #Delete the unused line.
        line_list.pop(this_merge_line)
        
    #Return as a raw text block.
    return '\n'.join(line_list)


if __name__ == '__main__':
    Make(sys.argv)
    