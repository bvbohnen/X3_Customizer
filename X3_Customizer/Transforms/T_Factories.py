'''
Transforms to factories.
'''
from collections import defaultdict
import copy

from .. import File_Manager
from .T_Director import *
from ..Common import Flags

# Global tracker for factory field adjustments based on size.
# Initialized on first call, reused on later calls to avoid any
# prior added factories changing the analysis.
# Outer key is production size (1,2,5,10), inner key is a field name,
# value is a scaling float.
size_field_ratios_dict_dict = None

# Global list of factories added in prior runs.
# This is used when the transform is called multiple times, to ensure
# all factories are accounted for in the director script (which gets
# written directly).
prior_new_factories = []


@File_Manager.Transform_Wrapper('types/TFactories.txt', 'maps/WareTemplate.xml')
def Add_More_Factory_Sizes(
        factory_types = [
            # Skip mines to avoid affecting mineral output of asteroids.
            'SG_FAC_BIO',
            'SG_FAC_FOOD',
            'SG_FAC_POWER',
            'SG_FAC_TECH'
            ],
        sizes = [
            's','m','l','xl'
            ],
        race_types = [
            'Argon', 
            'Boron', 
            'Split', 
            'Paranid', 
            'Teladi', 
            #'Xenon', 
            #'Khaak', 
            'Pirates', 
            #'Goner', 
            #'ATF', 
            'Terran', 
            'Yaki',
            ],
        cue_index = 0,
        linear_cost_scaling = False,
        print_count = False,
        warn_on_waretemplate_bugs = False,
        ):
    '''
    Adds factories of alternate sizes, from basic to XL.
    Price and volume of new sizes is based on the scaling common to
    existing factories.
    Factories will be added to existing shipyards the first time a game is
    loaded after running this transform; this may take several seconds to 
    complete, during which time the game will be unresponsive.
    Warning: it is unsafe to remove factories once they have been added to
    an existing save.

    * factory_types:
      - List of factory type names to add new sizes for.
        Defaults are ['SG_FAC_BIO','SG_FAC_FOOD','SG_FAC_POWER','SG_FAC_TECH'].
        The other potentially useful type is 'SG_FAC_MINE'.
    * sizes:
      - List of sizes to add, if not already present, given as strings.
        Defaults are ['s','m','l','xl'].
    * race_types:
      - List of race names whose factories will have sizes added. By default,
        the following are included: [Argon, Boron, Split, Paranid, Teladi, 
        Pirates, Terran, Yaki].
    * cue_index:
      - Int, index for the director cue which will update shipyards with
        added variants. Increment this when changing the variants
        in an existing save, as the update script will otherwise not fire
        again for an already used cue_index. Default is 0.
    * linear_cost_scaling:
      - Bool, if True then scaling of factory cost will be linear
        with production rate, otherwise it will scale in the same manner as
        argon solar power plants. Default False. Note: volume always scales
        like solar power plants, to avoid excessively large volumes.
    * print_count:
      - If True, the number of new factories is printed to the summary file.
    * warn_on_waretemplate_bugs:
      - If True, potential bugs in WareTemplate for nonexistent factories
        are printed to the summary file. This will not affect this transform,
        and is only intended to indicate potential problems in source files.
    '''
    global prior_new_factories
    
    # To add the factories to shipyards in game, a script has been set
    # up for running from the game script editor.
    #-Removed; no clear way to get race of station types using the script
    # language. Switched to using a director script instead.
    #_Include_Script_To_Update_Factory_Sizes()

    # Convert the input sizes to production rate integers.
    size_string_int_dict = {
        's'  : 1,
        'm'  : 2,
        'l'  : 5,
        'xl' : 10,
        }
    sizes = [size_string_int_dict[x] for x in sizes]

    # Gather a more organized list of factories.
    # Key by race, then factory type, then name_id, then production rate/size.
    # Note that factories of the same name_id and race should be matched up
    # as variant sizes of the same factory (eg. all bofu or something like that).
    race_type_name_size_factory_dict = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                dict)))
    for factory_dict in File_Manager.Load_File('types/TFactories.txt'):

        # Do not skip on race here; need to catch any stations
        # needed to determine scaling values.
        race_type = Flags.Race_code_name_dict[int(factory_dict['race'])]

        # Size is an integer in [1,2,5,10].
        size = int(factory_dict['factory_size'])
        # Mods may add rates outside this range; skip if that happens.
        if size not in [1,2,5,10]:
            continue

        race_type_name_size_factory_dict[
            # Race is an integer here.
            race_type][
                # Subtype is a string.
                factory_dict['subtype']][
                    # Name_id is an integer id.
                    int(factory_dict['name_id'])][
                        size] = factory_dict
        

    #Build a list of all factory names.
    #This is used later to ensure generated names have no conflicts
    # with existing names.
    factory_names_list = []
    for factory_dict in File_Manager.Load_File('types/TFactories.txt'):
        factory_names_list.append(factory_dict['name'])

    

    fields_to_modify = [
        # Only two fields actually change, in practice.
        # Hull/shielding appears to not be part of tfactories, and may
        # be hard set elsewhere.
        'volume',
        #Only relative value for npc is used; player is unused.
        'relative_value_npc',
        ]
    
    global size_field_ratios_dict_dict
    if size_field_ratios_dict_dict == None:
        size_field_ratios_dict_dict = defaultdict(dict)
        
        # To keep things simple, this will just grab solar power plants for
        # Argon M/L/XL to establish base multipliers, and will set S to M 
        # to follow the M to L scaling with a 2/2.5 adjustment.
        for factory_dict in File_Manager.Load_File('types/TFactories.txt'):
            if factory_dict['name'] == 'SS_FAC_A_POWER':
                m_fact = factory_dict
            if factory_dict['name'] == 'SS_FAC_A_POWER_1':
                l_fact = factory_dict
            if factory_dict['name'] == 'SS_FAC_A_POWER_2':
                xl_fact = factory_dict

        for field in fields_to_modify:
            # Fix medium at 1x.
            size_field_ratios_dict_dict[2][field] = 1
            # Set large.
            size_field_ratios_dict_dict[5][field] = (int(l_fact[field]) 
                                                       / int(m_fact[field]))
            # Set xl.
            size_field_ratios_dict_dict[10][field] = (int(xl_fact[field]) 
                                                       / int(m_fact[field]))
            # Set small.
            # If large were 2.5x medium (production rate 5 vs 2), then this
            #  linear scaling would mean small should be 0.5x medium.
            # There is normally some discount going to large, though, eg.
            #  with large = 2.3x medium. In such a case, there should be
            #  a markup on small, which there won't be if taking a simple
            #  1/5 of the large scaling.
            # In theory, if large were 1x medium, then small should be
            #  1x medium, so any formula used should satisfy that behavior.
            # This math is simpler if using the l to xl ratio, which is
            #  a 2x increase in production, similar to s to m.
            size_field_ratios_dict_dict[1][field] = (int(l_fact[field]) 
                                                       / int(xl_fact[field]))


    # Determine which factories will be added, along with which existing
    # factory will act as the template (reusing model and other fields).
    # Aim is to reuse the closest existing model, based on production amount,
    # eg. a new 1x will reuse the 2x model, a new 10x will use the 5x model,
    # etc.
    # Keep a dict of new factories to add.
    new_factories_list = []

    # Loop over each layer of the organized factory dicts.
    # Start with the races.
    for race_type, type_name_size_factory_dict in race_type_name_size_factory_dict.items():
        # Check for valid race.
        if race_type not in race_types:
            continue

        # Loop over the factory types.
        for fact_type, name_size_factory_dict in type_name_size_factory_dict.items():
            # Skip if not using this factory type.
            if fact_type not in factory_types:
                continue

            # Loop over the factory name_ids.
            # Note: factories can share names across races; this will be for
            # just one race.
            for fact_name_id, size_factory_dict in name_size_factory_dict.items():
                
                # Now, instead of loop further into existing factories, want to loop
                # over the desired factory sizes.
                for wanted_size in sizes:

                    # If this size already exists, skip.
                    if wanted_size in size_factory_dict:
                        continue

                    # Need to pick which existing factory will act as the template.
                    # Get the size offsets of existing factories from that wanted.
                    existing_sizes = list(size_factory_dict.keys())
                    size_offsets = [abs(x - wanted_size) for x in existing_sizes]
                    # Take the minimum, using its index to pick the template.
                    template_index = size_offsets.index(min(size_offsets))
                    template_size = existing_sizes[template_index]
                    template_factory_dict = size_factory_dict[template_size]

                    # Create a copy of the template.
                    new_factory_dict = copy.copy(template_factory_dict)

                    # Set the new size.
                    new_factory_dict['factory_size'] = str(wanted_size)

                    # Set a new name.
                    # This will just suffix with the size, and an x3c tag to help
                    # uniquify the name. Keep in caps to be consistent with names
                    # generally being capitalized.
                    new_name = new_factory_dict['name'] + '_X3C_{}'.format(wanted_size)
                    if new_name in factory_names_list:
                        raise Exception('Factory name {} already taken.'.format(new_name))
                    new_factory_dict['name'] = new_name

                    # Adjust the fields.
                    for field in fields_to_modify:
                        # Calculate the ratio needed.
                        # If linear scaling, it is just the production ratio,
                        # else use the calculated values.
                        if linear_cost_scaling and field == 'relative_value_npc':
                            ratio = wanted_size / template_size
                        else:
                            ratio = (
                                size_field_ratios_dict_dict[wanted_size][field] 
                              / size_field_ratios_dict_dict[template_size][field] )
                        # Adjust the value.
                        value = int(new_factory_dict[field])
                        new_factory_dict[field] = str(int(value * ratio))

                    # Record the factory.
                    new_factories_list.append(new_factory_dict)

                    # Annotate the new factory with the name of its template, for
                    # use later.
                    new_factory_dict.template_name = template_factory_dict['name']


    # Now the ware templates need to be added for these factories.
    # This will require xml editing of waretemplates.
    # Aim is to find the node for the template factory, and copy it over
    # with the new factory name.
    waretemplate_xml = File_Manager.Load_File('maps/WareTemplate.xml')
    # Parse the xml.  TODO: update to use element tree instead of node.
    element_root = waretemplate_xml.Get_XML_Tree().getroot()

    # Set up a dict matching factory name with its xml node.
    factory_name_node_dict = {}

    # Root is <universe>, child is the node for split fire, then its
    # children are the various factories (plus a couple for sector
    # setup, that can probably be ignored).
    # Loop over the split fire children.
    for element in element_root[0]:

        # Skip if not t=6, a factory object.
        if element.get('t') != '6':
            continue
        # The 's' term should hold the factory name.
        factory_name = element.get('s')

        # Verify this is a proper name.
        # Note: if bugs are present, a station in the waretemplates may
        # not have been present in tfactories, eg. this problem observed
        # in xrm with pirate distruptor factory.
        # In this case, can either quietly ignore or toss a warning, but
        # ignoring is probably fine.
        if factory_name not in factory_names_list:
            if warn_on_waretemplate_bugs:
                File_Manager.Write_Summary_Line(
                    'Warning: factory {} in WareTemplate not present in '
                    'TFactories'.format(factory_name))
            continue

        # Record this in the dict.
        factory_name_node_dict[factory_name] = element


    # Now build a list of new nodes for the new factories.
    new_xml_nodes = []
    # Loop over a copy of the factory list, do the list can be pruned
    # if select factories are skipped.
    for factory_dict in list(new_factories_list):

        # Find the template's node.
        # Note: some factories in TFactories may be unused or placeholders,
        # without any matching WareTemplate entry; in these cases, skip
        # the factories entirely.
        if factory_dict.template_name not in factory_name_node_dict:
            new_factories_list.remove(factory_dict)
            continue
        template_node = factory_name_node_dict[factory_dict.template_name]

        # Make a copy of the node.
        # This appears to require a deep copy; the attributes hold the
        # name to edit, and they may not even be a dict, so blind copying
        # is safest.
        new_node = copy.deepcopy(template_node)
        # Update the name.
        new_node.set('s', factory_dict['name'])
        new_xml_nodes.append(new_node)

    # Add the new factory nodes to the bottom of the xml split fire entry.
    element_root[0].extend(new_xml_nodes)
    # Update the file tracker.
    waretemplate_xml.Update_From_XML_Node(element_root)


    # Getting the game to update with the new waretemplates is somewhat 
    # awkward. It appears that the engine cannot set default wares directly; it
    # will only set default wares when a new factory is seen in a
    # universe file with predefined wares.
    # The waretemplates file appears to define a bunch of factories in split
    # fire, which are seen when any universe file loading happens, but not
    # actually created since only the main universe file is run (eg. the
    # engine looks at all files, but runs the selected one, so waretemple
    # gets seen and sets defaults without creating anything).
    # See https://forum.egosoft.com/viewtopic.php?t=282593&f=94&view=next
    # The trick here is to either update waretemplate.xml or put the new
    # defaults in a separate xml file, then use a dummy xml which has
    # only header nodes but creates nothing, and load that dummy using
    # a director script (fire once, or maybe fire on a timer?).

    # Take the xml tree and clean it out below split fire.
    # This needs to be done with a loop, apparently.
    child_nodes = [x for x in element_root[0]]
    for child_node in child_nodes:
        element_root[0].remove(child_node)


    # Name to use for the template file.
    dummy_template_name = 'WareTemplate_x3c_dummy'
    # Make the file.
    File_Manager.Add_File(File_Manager.Misc_File(
        virtual_path = 'maps/{}.xml'.format(dummy_template_name),
        # Translate to unicode, else a byte string is returned.
        text = ET.tostring(element_root, encoding = 'unicode')))
        

    # Prepare a director script to load the map file.
    # TODO: maybe clean out the cue_index-1 version of this, so a
    # save doesn't have extra cues tagged to it. This is probably not
    # a real problem, though, since factories should change rarely.
    text = r'<load_map file="{}"/> '.format(dummy_template_name)

    # In the same script, update the shipyards in the game.
    text += '\n' + Generate_Director_Text_To_Update_Shipyards(
        # Ensure any factories added on prior transforms are
        # included in the generated text still, instead of getting
        # lost.
        new_factories_list + prior_new_factories,
        # Add an extra 3 indents.
        indent_level = 3
        )

    # Stick the cue_index on the end of the cue name, to help ensure the
    # cue will be unique and will fire (eg. wasn't fire previously in a
    # given save).
    #Make the file.
    director_loader_base_name = 'X3_Customizer_Update_Factories'
    Make_Director_Shell(director_loader_base_name + '_' + str(cue_index), text,
                        file_name = director_loader_base_name +'.xml')
    
    # Add all of the new factories to tfactories.
    File_Manager.Load_File('types/TFactories.txt', return_game_file = True).Add_Entries(
        new_factories_list)
    
    # Add these factories to the prior new factories, to be seen
    # by any later transforms.
    prior_new_factories += new_factories_list

    #Note how many factories were added.
    if print_count:
        File_Manager.Write_Summary_Line('Number of new factories added: {}'.format(len(new_factories_list)))
        
    return

