'''
Any misc support functions can be placed here.
Initially, this just has one function used by some other transform categories.
'''
from collections import defaultdict
import xml.etree.ElementTree as ET
from xml.dom import minidom

from ... import File_Manager
from ...Common import Flags


def XML_Find_All_Matches(base_node, match_node):
    '''
    Searches an xml node's contents to find a match to a given reference
    node. Will match node type, all attributes, and all children
    recursively. Returns a list of matching child nodes of base_node,
    possibly empty with no matches.
    '''
    # Start with a pre-filtering that does not check ref_node children,
    #  only type and attributes.
    # Use xpath './/' to search all children recursively of the parent.
    xpath = './/{}'.format(match_node.tag)

    # Add all of the ref_node attributes.
    for name, value in match_node.items():
        xpath += '[@{}="{}"]'.format(name, value)

    # Can add simple child node type checks without getting too messy.
    # This just checks that the matched node has a child node of the
    #  appropriate type name; it doesn't filter out having extra
    #  children or similar.
    # ET is unintuitive about this, but to work through children this
    #  needs to to an unqualified iteration (which intuitively would
    #  should give attribute names, to match up with .items(), but
    #  whatever).
    for child in match_node:
        xpath += '[{}]'.format(child.tag)

    # Get the initial matches.
    found_nodes = base_node.findall(xpath)

    # Filter out those without the right number of children.
    found_nodes = [x for x in found_nodes 
                   if len(x) == len(match_node)]

    # Now work through children checks.
    # This can potentially be simplified by stripping off fluff text (eg.
    #  tail and such), converting nodes to text strings, and comparing those
    #  text strings. That would handle all recursive aspects in one step,
    #  and shouldn't have to much overhead if the pre-filter did a good
    #  job trimming down the problem space. Use a support function for this.
    match_text = XML_To_Unformatted_String(match_node)
    found_nodes = [x for x in found_nodes 
                   if XML_To_Unformatted_String(x) == match_text]

    return found_nodes


def XML_Find_Match(base_node, match_node):
    '''
    Searches an xml node's contents to find a match to a given reference
    node. Will match node type, all attributes, and all children
    recursively. Returns the corresponding child of base_node if found,
    else returns None. Error if there are 0 or multiple matches.
    '''
    found_nodes = XML_Find_All_Matches(base_node, match_node)
    
    # Error if there isn't a single match.
    found_count = len(found_nodes)
    if found_count == 0:
        raise Exception('XML_Find_Match failed to find a match')
    elif found_count > 1:
        raise Exception('XML_Find_Match found {} matches'.format(found_count))

    # Return a single node.
    return found_nodes[0]


def XML_To_Unformatted_String(node):
    '''
    Convert an xml node (with attributes, children, etc.) to a string,
    omitting whitespace from the 'text' and 'tail' fields. Attributes
    are sorted. 
    '''
    # Possible approaches:
    # 1) Deepcopy the node, edit all text/tail members to
    #    strip() them, and use the normal xml tostring method.
    # 2) Manually stride through text/attributes/tail constructing a
    #    string, then recursively append strings from each child to
    #    it.
    # The former is easier, but clumsy for nodes with a lot of content
    #  in them.  Try out (2).

    # Strip the text and tail here. If None, make an empty string.
    text = node.text.strip() if node.text else ''
    tail = node.tail.strip() if node.tail else ''

    # This will always use "<tag >" for the node definition, with "</tag>" to
    #  then close the node (eg. no "<tag />"), for simpler logic.
    text = '<{}{}{}{}{}>{}{}{}{}</{}>'.format(
        # Opener.
        node.tag,

        # Text field, with preceeding space if present.
        ' ' if text else '',
        text,

        # Collect attributes together, with preceeding space if present.
        ' ' if node.items() else '',
        ' '.join(['{}="{}"'.format(key, value) 
                  for key, value in sorted(node.items())]),
        
        # Tail. Don't need space on this, since after the >.
        tail,
        
        # Extra final newline if there are children.
        '\n' if node else '',
        # Append all children.
        # Note: newline separators are unnecessary, but may make debug
        #  viewing easier.
        '\n'.join([XML_To_Unformatted_String(child) for child in node]),
        # Extra final newline if there are children.
        '\n' if node else '',
        
        # Closer.
        node.tag,
        )
    #print(text)
    return text


def XML_Replace_Node(parent_node, old_node, new_node):
    '''
    Replace a child node of the parent.
    '''
    index = list(parent_node).index(old_node)
    parent.remove(old_node)
    parent_node.insert(index, new_node)
    return

def XML_Insert_After(parent_node, old_node, new_node):
    '''
    Insert a new node after an old child node under the parent.
    '''
    index = list(parent_node).index(old_node)
    parent_node.insert(index + 1, new_node)
    return


def Make_Director_Shell(cue_name, body_text = None, file_name = None):
    '''
    Support function to make a director shell file, setting up a queue
    with the given body text.
    The file name will reuse the cue_name if file_name not given.
    Optionally, delete any old file previously generated instead of
    creating one.
    '''
    #  Set the default file name.
    if not file_name:
        file_name = cue_name + '.xml'
    assert '.xml' in file_name


    # Copied shell text from a patch script that cleared invulnerable station flags.
    # This will make the queue name and text body replaceable.
    # Since the shell text naturally has {} in it, don't use format here, just
    #  use replace.
    # Update: the 'check' term in the cue definition indicates what to do when
    #  the first condition check fails; in the invuln-station-fix, it is set to
    #  cancel, indicating that when it checks on a new game (player age check
    #  fails) it will cancel and not run the cue.
    #  To ensure these cues do run on new games, do not use a check value, or
    #  set it to none, which should put the cue on a constant recheck.
    shell_text = r'''<?xml version="1.0" encoding="ISO-8859-1" ?>
<?xml-stylesheet href="director.xsl" type="text/xsl" ?>
<director name="template" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="director.xsd">
    <documentation>
    <author name="X3_Customizer" alias="..." contact="..." />
    <content reference="X3_Customizer" name="X3_Customizer generated" description="Director command injector." />
    <version number="0.0" date="today" status="testing" />
    </documentation>
    <cues>
    <cue name="INSERT_CUE_NAME">
        <condition>
        <check_value value="{player.age}" min="1s"/>
        </condition>
        <timing>
        <time exact="1s"/>
        </timing>
        <action>
        <do_all>
            INSERT_BODY
        </do_all>
        </action>
    </cue>
    </cues>
</director>
'''.replace('INSERT_CUE_NAME', cue_name).replace('INSERT_BODY', body_text)

    # TODO: maybe clean up formatting here for indents, which will also
    #  allow for cleaning up the text block indents above.

    # Record a file object to be written later.
    File_Manager.Add_File(File_Manager.Misc_File(
        virtual_path = 'director/' + file_name, 
        text = shell_text))

    return



def Generate_Director_Text_To_Update_Shipyards(
        new_wares_list,
        indent_str = '    ',
        indent_level = 0,
        removal_mode = False,
        return_xml = False):
    '''
    Create director script text which will select all shipyards, and
     add to them new ships or factories if they have the matching
     template object already sold.
    The list of new_wares_list should be annotated with template_name, the
     name of the existing product to look for when deciding which
     shipyards to add wares to, and should have a 'name' dict field
     with their own name, as well as a 'race' index field.
    If return_xml == True, this will return an xml do_all node, else
     will return a string version.
    If removal_mode == True, this will remove the wares from shipyards
     instead of adding them.
    Optionally, provide an extra indent_level to add to returned text.
    The returned text will be wrapped in a do_all block.
    '''

    # This will eventually be xml, so do it using a list of xml nodes
    #  to be placed inside of a do_all block.
    # This should be a lot more elegant than raw text strings.
    do_all_root = ET.Element('do_all',{})

    '''
    Can do this in two general ways:

    1) Find all stations, loop on them, check their products and add
     new entries.
    2) Pick template object and find all stations that produce it,
     and add the new entry to those.

    Option (1) may be faster if the find_station command is slow,
     since it only need to run once. Option (2) is likely simpler,
     however, since it can potentially avoid checking if a template
     ware is on the station product list.

    Can try either, but go with (2) initially since it seems slightly
     simpler.

    Update: 
     Option (2) seems to be slow, requiring close to 2 minutes to
     complete when adding 811 factories to XRM.
     Also, option (2) wants to match all stations; documentation is
     somewhat unclear, saying that the 'multiple' option doesn't work
     with a resource match, which may imply it also doesn't work
     with a product match.
    Go with option (1).
     Update: option (1) is comparatively super fast.
    '''

    # To speed up the script, try to add all new objects together
    #  which share the same template object, and also categorize
    #  by race.
    # Note: in removal mode, there are no template objects to worry
    #  about; just put the ware itself in the template for that case,
    #  to get reuse of the match code.
    # Make a race : template_name : new_wares_sublist dict.
    race_template_wares_list_dict_dict = defaultdict(
                                        lambda : defaultdict(list))

    for ware_dict in new_wares_list:
        # Get the race as a string, using director race names.
        race_type = Flags.Director_race_code_name_dict[int(ware_dict['race'])]
        race_template_wares_list_dict_dict[
            race_type][
                # Use the template name, or ware name if removing it.
                ware_dict.template_name if removal_mode == False else ware_dict['name']
                ].append(ware_dict)


    # For removal mode, much of this code will be the same until getting
    #  into the do_if node when a template name is matched.

    # Loop over the races.
    for race, template_wares_list_dict in race_template_wares_list_dict_dict.items():

        # For fun, toss up a help message to say what is happening.
        # -Removed; the game basically freezes while this runs, so the
        #  display doesn't show up until after it completes. Can still
        #  put a final message.
        # help_node = ET.Element('show_help',{
        #     'text' : 'Updating {} shipyards with new wares.'.format(race),
        #     # Try out 5 seconds or so.
        #     'duration' : '5000'})
        # do_all_root.append(help_node)

        # Gather a list of all shipyards for this race.
        # Example:
        #  <find_station group="Shipyards" multiple="1">
        #      <sector x="0" y="0"/>
        #      <jumps max="100"/>
        #  </find_station>
        # Note: groups appear to be sticky, as in multiple commands with
        #  the same group will append to it, so after each shipyard group
        #  is handled the group should be cleared out.
        # Note: when looking for terrans, also match with atf, which can
        #  be done using the special 'terrangroup' flag.
        station_node = ET.Element('find_station',{
            'group' : 'Shipyards',
            'multiple' : '1',
            'class' : 'shipyard',
            'race' : race if race not in ['terran','atf'] else 'terrangroup',
            })
        station_node.extend( [
            ET.Element('sector',{'x' : '0','y' : '0'}),
            ET.Element('jumps',{'max' : '100'}),
            # -Removed; ware check doesn't appear to work with multi match.
            # This is leftover from trying style (2).
            # ET.Element('ware',{'typename' : template_name,
            #                    # Require at least 1 unit; otherwise this
            #                    # seemed to be matching everything.
            #                    'min'      : '1'}),
            ])

        # Set up a loop over the stations.
        # Example:
        #  <do_all exact="{group.object.count@Shipyards}" counter="count">
        loop_node = ET.Element('do_all',{
            # Give the number of shipyards to count through.
            'exact' : '{group.object.count@Shipyards}',
            # Name the counter.
            'counter' : 'count'})

        #  Indent here to indicate inside the loop above.
        if 1:
            # This string will be used to reference a given shipyard,
            #  by indexing into the Shipyards group based on the current
            #  counter value.
            shipyard = '{group.object.{counter@count}@Shipyards}'

            # Loop over all of the templates to be checked.
            for template_name, new_wares_list in template_wares_list_dict.items():

                # Check if this shipyard has this ware as a product.
                # Thankfully, there appears to be a convenient command
                #  for this, getting a boolean.
                # Put this in a do_if node.
                if_node = ET.Element('do_if',{
                    'value' : '{{object.products.{}.exists@{}}}'.format(
                        template_name,
                        shipyard
                        ),
                    'exact' : '1'})
                # Add this to the loop.
                loop_node.append(if_node)

                # Indent for the do_if block.
                if 1:
                    # Loop over the new wares.
                    for new_ware in new_wares_list:

                        # In removal mode, it should be okay to remove the
                        #  product blindly.
                        if removal_mode:
                            # Only need to give a typename here; amount 
                            #  doesn't matter since it does a full removal.
                            remove_node = ET.Element('remove_products',{'object' : shipyard})
                            remove_node.append(ET.Element('ware',{
                                'typename' : new_ware['name']}))
                            # Stick in the outer do_if.
                            if_node.append(remove_node)

                        else:
                            # Aim is to add just 1 unit of product, and to not add
                            #  any more if the station already has at least 1 unit.
                            # This will require another do_if, conditioned on the
                            #  product count.
                            # Check if the ware doesn't exist.
                            inner_if_node = ET.Element('do_if',{
                                'value' : '{{object.products.{}.exists@{}}}'.format(
                                    new_ware['name'],
                                    shipyard
                                    ),
                                'exact' : '0'})
                            # Stick in the outer do_if.
                            if_node.append(inner_if_node)

                            # Indent again.
                            if 1:
                                # Add the product to the current shipyard.
                                insert_node = ET.Element('add_products',{'object' : shipyard})
                                insert_node.append(ET.Element('ware',{
                                    'typename' : new_ware['name'],
                                    #  Give 1 unit, else shows up in game with 0.
                                    'exact' : '1'}))
                                # Stick inside the do_if.
                                inner_if_node.append(insert_node)
                    
        # Clear out the shipyard group.
        clear_node = ET.Element('remove_group',{'group' : 'Shipyards'})
            
        # Stick these in the outer do_all.
        do_all_root.append(station_node)
        do_all_root.append(loop_node)
        do_all_root.append(clear_node)

        
    # Make a final status message.
    do_all_root.append( ET.Element('show_help',{
        'text' : 'Completed shipyard ware update.',
        # Try out a few seconds.
        # This seems to have the processing time counted against
        #  it, so should be longer than that.
        # In testing, takes a few seconds to process.
        'duration' : '6000'}))


    # Send back the xml node if requested.
    if return_xml:
        return do_all_root

    # Otherwise convert to text.
    else:
        # Give it some nice formatting.
        xml_text = ET.tostring(do_all_root)
        minidom_root = minidom.parseString(xml_text)
        xml_text = minidom_root.toprettyxml(indent = indent_str)

        # Post-process it to get rid of the xml declaration node, and add
        #  extra indents.
        xml_lines = xml_text.splitlines()
        assert 'version' in xml_lines[0]
        xml_lines = xml_lines[1:]
        for index in range(len(xml_lines)):
            xml_lines[index] = indent_str * indent_level + xml_lines[index]
        xml_text = '\n'.join(xml_lines)
        return xml_text