'''
These transforms fix known bugs in the egosoft MD scripts.

Note: transforms planned; not yet implemented.
'''
import xml.etree.ElementTree as ET
from .Support import XML_Find_Match, XML_Find_All_Matches, Make_Director_Shell
from . import Support # TODO: move xml functions to another module.
from ... import File_Manager

'''
TODO:

New Home (tc plots for ap)
    - The final gate connection is not completed; only affects the base
    version of this mod; rereleases tend to fix the bug.
    - Low priority, since fixes exist and this is just a mod.

'''

# TODO: convenience transform that runs all fixes, likely including these
#  and some in other modules.

    
@File_Manager.Transform_Wrapper('director/2.024 Player Corp.xml')
def Fix_Corporation_Troubles_Balance_Rollover():
    '''
    In the Corporation Troubles plot, prevents the bank balance from
    reaching >2 billion and rolling over due to the 32-bit signed
    integer limit.
    '''
    '''
    Notes:
    
    Related thread with the complaint:
    https://forum.egosoft.com/viewtopic.php?f=2&t=401564

    Corperate bank balance accumulates every 60 minutes from
    income/outgoing, and can eventually reach 2 billion and overflow.

    A simple fix would be a limit check at the accumulation point, preventing
    any change once reaching a safe cap (with some slack for adjustments
    from random missions, though those mostly subtract and appear to only
    add up to ~10 million or so when selling fake assets).

    '''
    # Value to limit the balance to.
    # Go for something easy and obvious, with headroom.
    # 2 billion is probably safe (100+ million headroom), but there is a
    #  'loan' step that can add 200 million to the balance (maybe done once
    #  at start, unclear), so just limit to 1 billion for now.
    max_balance = 1000000000
    
    # Lay out the format of the original node, for matching.
    match_node = ET.fromstring(
        '''
        <do_all>
          <set_value name="L2M024.CorpBankBalance" exact="{value@L2M024.CorpIncome}" operation="add"/>
          <set_value name="L2M024.CorpBankBalance" exact="{value@L2M024.CorpOutgoing}" operation="subtract"/>
          <set_value name="L2M024.AccountTime" exact="{player.age}+3600"/>
          <reset_cue cue="L2M024 Income Update"/>
        </do_all>
        ''')

    # Grab the director file.
    file_contents = File_Manager.Load_File('director/2.024 Player Corp.xml')
    tree = file_contents.Get_XML_Tree()
    
    ## Find the insertion point.
    ## It is a bit clumsy to try to pick this directly out of the xml tree
    ##  structure, so instead look for the housing cue node:
    ##  <cue name="L2M024 Income Update" ...>
    ## Searching syntax is a little weird. In short:
    ##  '.': root node.
    ##  '//': recursive search of all children.
    ##  'cue': look for 'cue' nodes.
    ##  []: attributes values to match.
    #found_nodes = tree.findall(".//cue[@name='L2M024 Income Update']")
    ## Should have a single match.
    #assert len(found_nodes) == 1

    # Find the original node using the support match function.
    orig_node = XML_Find_Match(tree, match_node)

    # Make the new node to be inserted, a do_if.
    # This will write the text and parse it; could also manually make
    #  the elements. TODO: try both ways and see what is cleaner and
    #  more manageable.
    insert_node = ET.fromstring(''.join([
        # Check for over limit.
        '<do_if value="{value@L2M024.CorpBankBalance}"'+' min="{}">'.format(max_balance),
        # Set to limit.
        '  <set_value name="L2M024.CorpBankBalance"'+' exact="{}"/>'.format(max_balance),
        '</do_if>',
        ]))

    orig_node.append(insert_node)

    # Push the changed xml tree to the file tracker.
    # Reformat to get proper indents on new nodes.
    file_contents.Update_From_XML_Node(tree, reformat = True)

    return


    
@File_Manager.Transform_Wrapper('director/2.004 Terran Plot Scene 4.xml')
def Fix_Terran_Plot_Aimless_TPs():
    '''
    In the Terran Conflict plot when allied TPs move to capture an Elephant,
    fix replacement TPs to move toward the Elephant instead of wandering
    aimlessly.
    '''
    '''
    Notes:
    
    Related thread with the complaint:
    https://forum.egosoft.com/viewtopic.php?f=93&t=397816
    
    Problem is around <cue name="L2M004 Protect Boarding Crews">.
    The initial set of TPs get the command:
      <command command="follow" commandobject="L2M004.SplitTL"/>
    The replacement TPs have all the same settings, except the command:
      <command command="moveposition" commandobject="L2M004.SplitTL"/>

    Supposing "moveposition" doesn't properly accept an object instead
    of a coordinate, this would explain the described problems of TPs flying
    off to the south of the map.

    These script commands can be found in the obj code around L00195A3E.
    Here, the behavior of "moveposition" is more clear:
        - "commandobject" is only used to set the sector if "sector" not given.
        - "position" is likely required for proper behavior, as it is
        interpretted by a call to CUE.ReadPosition(position, sector).
        - Thought: the above could be a bug in the KC, and the intended call
        was CUE.ReadPosition(position, object). If true, changing that might
        catch other similar script bugs naturally, but don't worry about
        that for now (it would need more looking into).

    The fix is simple: replacement TPs get the correct "follow" command.
    '''
    match_node = ET.fromstring(
        '<command command="moveposition" commandobject="L2M004.SplitTL"/>')

    # Grab the director file.
    file_contents = File_Manager.Load_File('director/2.004 Terran Plot Scene 4.xml')
    tree = file_contents.Get_XML_Tree()
    
    # Find the original node using the support match function.
    orig_node = XML_Find_Match(tree, match_node)

    # Edit it.
    orig_node.set('command','follow')

    # Push the changed xml tree to the file tracker.
    # Reformat to get proper indents on new nodes.
    file_contents.Update_From_XML_Node(tree, reformat = True)

    return



@File_Manager.Transform_Wrapper('director/0.83 Dual Convoy.xml', 
                                'director/2.183 Dual Convoy.xml')
def Fix_Dual_Convoy_Invincible_Stations():
    '''
    Fixes Dual Convoy generic missions to no longer leave stations
    permenently invincible, and to no longer risk clearing invincibility
    from plot stations, as well as fixes a minor bug in the parameter list.

    Stations used by these missions will no longer be set invincible,
    and a mission is cancelled if an end point station is destroyed.

    Does not affect any invinciblity flags already set in an existing save.
    Consider also using Fix_Reset_Invincible_Stations to clear leftover
    flags in an existing save.
    '''

    '''
    Notes:
        
    Related thread with the complaint:
    https://forum.egosoft.com/viewtopic.php?f=2&t=400240

    Problem 1:
        This node exists in the setup part of the mission, prior to creating
        a mission briefing.
        <set_group_invincible group="L2M183.StationGroup" invincible="1"/>

        The "L2M183 End" cue has a matching command to clear the flag, but
        this can only ever be reached after the active part of the mission
        is started by the player accepting it.

        Without acceptance, the mission will either time out, or get removed
        due to the player traversing several gates.
        It looks like a third situation is when a start/end station gets
        destroyed somehow after being set invincible; that case can also
        be fixed for extra safety.

    Problem 2:
        In addition to leaving stations invuln, this script may also end
        up clearing the invuln flag on plot critical stations, if it
        selects one as a start/end point, potentially breaking those plots
        in a way they don't expect.

    Problem 3 (minor; noticed along the way):
        In "0.83 Dual Convoy" the parameter lists have "StartStation1" twice
        instead of "StartStation2".
        It is unclear on what effects this bug might have; maybe none since
        the start stations are not used in the script anywhere, but it might
        be good form to fix this.


    Two possible fix approaches:
    1)  Aim to preserve the invincibility on mission stations.
        - Add a set_group_invincible node to each place the mission can get
        cancelled, clearing invincibility.
        - Also, to protect plot stations, change the station selection code
        to cancel this generic mission early (before invuln gets set) if
        any of the selected stations are already set to invuln.
        - Note: this is imperfect, as a selected station may also get used
        for a plot after this generic mission is activated, leading to
        accidental clearing of its plot-set invuln flag.

    2)  Remove invincibility entirely.
        - Remove the invuln setting and clearing commands.
        - Stations already invuln in an existing save can be addressed by
          some other method that would be needed anyway to clean out
          stale flags.
        - Ensure the mission will exit nicely if a station gets destroyed.

    Go with option (2), since (1) still leaves bugs in place.

    How to clean up missions when stations are destroyed?
        - Existing conditions for ending the mission aren't really set up to
        capture station destruction.
        - So, set up a new cue just for this case, triggering if either end
        station gets destroyed (start stations can be ignored).
        - Action logic can borrow from the other cues to trigger cleanup,
        set a return code, etc.

    Test results:
        Quick test destroying an end point station did cancel out the
        mission, albeit with a message saying the convoy was destroyed.

        Any further robustness tests are pending.
    '''
    # Get the input files of interest.
    # For lack of a better name prefix, these are 'low' and 'high' for
    #  the level of their logic.
    low_file_contents = File_Manager.Load_File('director/0.83 Dual Convoy.xml')
    low_tree = low_file_contents.Get_XML_Tree()
    high_file_contents = File_Manager.Load_File('director/2.183 Dual Convoy.xml')
    high_tree = high_file_contents.Get_XML_Tree()

    
    # Simple parameter name fix.
    match_node = ET.fromstring(
        '<param name="StartStation1" type="objectname" compulsory="1"'
        ' description="Start Station 2 for the mission"/>')    
    found_nodes = XML_Find_All_Matches(low_tree, match_node)
    # There should be two matches.
    assert len(found_nodes) == 2
    # Adjust the name.
    for node in found_nodes:
        node.set('name','StartStation2') 


    # Add the new abort-like cue.
    # Create a new node to insert after the abort.
    # Progress will be set to 2, failure, so that the higher level will
    #  cancel the objective.  (The abort progress code, 99, doesn't have
    #  any higher level handler.)
    # To be safe, also borrow some cue cancelling commands from the
    #  'convoy destroyed' cue.
    insert_node = ET.fromstring(
        '''
        <cue name="L0M83 Station Destroyed">
          <condition>
            <check_value value="{object.exists@{param@Cue}.{param@ID} L0M83EndStation1}*{object.exists@{param@Cue}.{param@ID} L0M83EndStation2}" exact="0"/>
          </condition>
          <action>
            <do_all>
              <set_value name="{param@Cue}.{param@ID} L0M83 Progress" exact="2"/>
              <set_value name="L0M83.CleanUp" exact="1"/>
              <cancel_cue cue="L0M83 Convoy 1 Finished"/>
              <cancel_cue cue="L0M83 Convoy 2 Finished"/>
              <cancel_cue cue="L0M83 Start Enemies"/>
            </do_all>
          </action>
        </cue>
        '''
        )

    # Make sure the new queue name is not already present, in case this
    #  transform was already run before.
    assert low_tree.find('.//cue[@name="L0M83 Station Destroyed"]') == None

    # Insert after the abort.
    # Find the original abort node.
    abort_node = low_tree.find('.//cue[@name="L0M83 Aborted"]')
    # Find its parent as well.
    parent_node = low_tree.find('.//cue[@name="L0M83 Aborted"]/..')    
    # Find the index of the node in the child list of its parent.
    #abort_index = list(parent_node).index(abort_node)
    #parent_node.insert(abort_index + 1, insert_node)
    Support.XML_Insert_After(parent_node, abort_node, insert_node)
    
    # Match children to parents.
    child_parent_dict = {child : parent
                        for parent in high_tree.iter()
                        for child in parent}

    # Remove the invincibility settings from the top level script.
    # Loop over the set_group_invincible nodes.
    for node in high_tree.findall('.//set_group_invincible'):
        # Remove from the parent.
        child_parent_dict[node].remove(node)

    
    # Update the xml in both files.
    # By doing this at the end, any errors above will prevent any partial
    #  changes from being completed.
    low_file_contents.Update_From_XML_Node(low_tree, reformat = True)
    high_file_contents.Update_From_XML_Node(high_tree, reformat = True)

    return



@File_Manager.Transform_Wrapper()
def Fix_Reset_Invincible_Stations(cue_index = 0):
    '''
    Resets the invinciblity flag on stations in an existing save.
    Works by re-triggering the matching script contained in an AP patch,
    which will preserve invincibilty for AP plot related stations.
    Warnings: invincibility flags from other sources (eg. TC plots for AP)
    may be lost.
    Pending test and verification.

    * cue_index
      - Int, index for the director cue which will retrigger the reset
        call. Increment this if wanting to run the reset script again for
        an existing save, as each cue name will fire only once.
      - Default is 0.
    '''
    reset_file_base_name = 'X3_Customizer_Reset_Invincible_Stations'
    Make_Director_Shell(
        cue_name = reset_file_base_name + '_' + str(cue_index), 
        body_text = '<reset_cue cue="Reset_Invincible_Stations"/>',
        file_name = reset_file_base_name +'.xml')

    '''
    TODO: patch the existing script to be more robust for stations
    it might miss. Eg., at a glance, it doesn't include "L2M023.A2 CKPS"
    for Shady Business.
    '''
    return



@File_Manager.Transform_Wrapper('director/2.023 Shady Business.xml')
def _Fix_Shady_Business_Captured_Ship_Despawn():
    '''
    In the Shady Business plot, at the end, various spawned ship groups
    will be destroyed without considering if the player captured any
    of them. This adds in player ownership checks before destruction
    is allowed.
    In development.
    '''
    '''
    Notes:
    
    Related thread with the complaint:
    https://forum.egosoft.com/viewtopic.php?f=2&t=401504
    
    Problem:
        Problem code is in cue "L2M023.Cleanup", which destroys several
        groups of ships without any checks on ownership.

        In addition to the complained about case, the destruction commands
        occur many other places in the script.

    Fix:
        For each single-ship destruction ("destroy_object") node, can
        bury it underneath a do_if that checks ownership first.

        For the group destruction ("destroy_group") nodes, a more complex
        replacement is needed which will loop over the group on a per-ship
        basis, check ownership and destroy.

        To capture all cases, the script will need to be searched and have
        these checks placed at every instance of these commands.

    TODO:
        Should this edit be made to all scripts blindly?  Or is player
        ship destruction wanted in some cases?

        Could the obj code be edited in some way to achieve this effect
        more naturally?

    '''
    # Put the script name here, in possible prep for making this transform
    #  work on any script.
    script_name = 'director/2.023 Shady Business.xml'

    # Grab the director file.
    file_contents = File_Manager.Load_File(script_name)
    tree = file_contents.Get_XML_Tree()
        
    # Find all destroy_object nodes.
    destroy_object_nodes = tree.findall('.//destroy_object')

    # Find all destroy_group nodes.
    destroy_group_nodes = tree.findall('.//destroy_group')

    # TODO: edit the nodes.

    # Push the changed xml tree to the file tracker.
    # Reformat to get proper indents on new nodes.
    file_contents.Update_From_XML_Node(tree, reformat = True)

    return
