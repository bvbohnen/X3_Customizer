'''
Transforms to the director xml files.
These are generally targetted at specific lines of the original input.

'''
import copy
from collections import defaultdict
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .. import File_Manager
from ..Common import Flags

@File_Manager.Transform_Wrapper('director/3.01 Generic Missions.xml')
def Adjust_Generic_Missions(
    adjustment_dict = {},
    cap_at_100 = False
    ):
    '''
    Adjust the spawn chance of various generic mission types, relative
    to each other. Note: decreasing chance on unwanted missions seems
    to work better than increasing chance on wanted missions.

    * adjustment_dict:
      - Dict keyed by mission identifiers or preset categories, holding
        the chance multiplier.
      - Keys may be cue names, eg. 'L2M104A', or categories, eg. 'Fight'.
        Specific cue names will override categories.
      - Categories and cue names for the vanilla AP are as follows, where
        the term after the category is the base mission chance shared by
        all missions in that category, as used in the game files.
      - Trade (TXXX)
        - L2M104A : Deliver Wares to Station in need
        - L2M104B : Deliver Illegal Wares to Pirate Station
        - L2M104C : Deliver Illegal Wares to Trading Station
        - L2M116  : Transport Cargo
        - L2M130  : Passenger Transport
        - L2M150a : Buy Used Ship
      - Fight (XFXX)
        - L2M101  : Assassination
        - L2M108  : Xenon Invasion
        - L2M119  : Escort Convoy
        - L2M127  : Destroy Convoy
        - L2M134  : Generic Patrol
        - L2M135  : Defend Object
        - L2M183  : Dual Convoy
      - Build (XXBX)
        - L2M122  : Build Station    
      - Think (XXXT)
        - L2M103  : Transport Passenger
        - L2M105  : Return Ship
        - L2M113  : Follow Ship
        - L2M129  : Deliver Matching Ship
        - L2M133  : Freight Scan
        - L2M145  : Scan Asteroids
        - L2M180  : Repair Station
        - L2M181  : Multiple Transport
        - L2M182  : Tour Of A Lifetime
        - L2M136  : Notoriety Hack
        - L2M144  : Buy Asteroid Survey
        - L2M147  : Buy Sector Data
        - L2M161  : Buy Blueprints
        - DPL2M186: Sell Blueprints
    * cap_at_100:
      - Bool, if True then mission chance adjustment will cap at 100, the
        typical highest in vanilla AP. Default False.
    '''
    import xml.etree.ElementTree
    # Translate the base chance codes to category names.
    code_category_dict = {
        'TXXX': 'Trade',
        'XFXX': 'Fight',
        'XXBX': 'Build',
        'XXXT': 'Think',
        }

    # The general format of the line being edited looks like:
    # <set_value name="this.L2M104A" exact="1" chance="{player.sector.quota.TXXX}*20"/>
    # Could consider using proper xml parsing for this, but for now just
    #  do it a brute force way.

    # Get the base file content.
    file_contents = File_Manager.Load_File('director/3.01 Generic Missions.xml')
    # Make a copy of text for editing.
    new_file_text = copy.copy(file_contents.Get_Text())

    # Loop over the lines.
    for line in file_contents.Get_Text().splitlines():
        # Skip lines without 'chance' in them.
        if 'chance="{' not in line:
            continue
        # Skip lines that are commented.
        if line.strip().startswith('<!--'):
            continue
        # Verify this line looks as expected.
        assert 'set_value' in line
        assert 'player.sector.quota.' in line


        # Parse the line xml.
        element = xml.etree.ElementTree.fromstring(line)
        # print(element.items())
        
        # Pick apart the components.
        # Cue name has the form 'this.L2M104A', so remove the 'this.'.
        cue_name = element.get('name').replace('this.','')

        # Category and chance has the form '{player.sector.quota.TXXX}*20'
        chance_text = element.get('chance')

        # Pull out the original multiplier, in the 0-100 range.
        multiplier_str = chance_text.split('*')[1]

        # Pull out the category.
        category_code = chance_text.split('}')[0].replace('{player.sector.quota.','')
        category = code_category_dict[category_code]
        

        # Determine the adjustment factor to use.
        adjustment = None
        if cue_name in adjustment_dict:
            adjustment = adjustment_dict[cue_name]
        # Check the category next.
        elif category in adjustment_dict:
            adjustment = adjustment_dict[category]

        # If there is no adjustment to apply, continue.
        if adjustment == None:
            continue

        # Adjust the multiplier, round, and floor to 0.
        new_multiplier = round(int(multiplier_str) * adjustment)
        new_multiplier = max(0, new_multiplier)
        # Optionally cap at 100.
        if cap_at_100:
            new_multiplier = min(100, new_multiplier)
        # Actual max is unknown, though comments suggest base chances are
        #  up to 700, which then get multiplied to 70k, suggesting a
        #  32-bit value is used for the chance in the game interpreter.

        # Edit the chance field with the new multiplier.
        new_chance_text = chance_text.replace(multiplier_str, str(new_multiplier))
        # Put it back.
        element.set('chance', new_chance_text)
        # print(element.items())

            
        # Need to set this to unicode, otherwise it returns a byte
        #  string and not a normal string.
        # Also, note that this will return the node attributes in
        #  sorted order; there is no clean way to preserve the 
        #  original order. This is a little uglier than intended,
        #  but shouldn't really matter.
        new_line = xml.etree.ElementTree.tostring(element, encoding="unicode")

        # Replace the original with the new line.
        # Ignore leading white space in the original, so it gets preserved.
        new_file_text = new_file_text.replace(line.strip(), new_line)

    # Update the file text with the changes.
    file_contents.Update_From_Text(new_file_text)

    
# Convenience version of the above to turn off all missions.
@File_Manager.Transform_Wrapper('director/3.01 Generic Missions.xml')
def Disable_Generic_Missions():
    '''
    Disable generic missions from spawning. Existing generic missions
    will be left untouched.
    '''
    Adjust_Generic_Missions({
        'Trade': 0,
        'Fight': 0,
        'Build': 0,
        'Think': 0,
        })


@File_Manager.Transform_Wrapper('director/3.08 Sector Management.xml', 
                                LU = False, TC = False)
def Standardize_Tunings(
    enging_tuning_crates = 4,
    rudder_tuning_crates = 4,
    engine_tunings_per_crate = 4,
    rudder_tunings_per_crate = 3
    ):
    '''
    Set the number of randomized tuning creates at gamestart to be
     de-randomized into a standard number of tunings.
    Note: vanilla has 2-5 average tunings per crate, 8 crates total.
    Default args here reach this average, biasing toward engine tunings.

    * enging_tuning_crates:
      - Int, the number of engine tuning crates to spawn. Default 4.
    * rudder_tuning_crates:
      - Int, the number of rudder tuning crates to spawn. Default 4.
    * engine_tunings_per_crate:
      - Int, the number of tunings in each engine crate. Default 4.
    * rudder_tunings_per_crate:
      - Int, the number of tunings in each rudder crate. Default 3.

    '''
    # Make sure the input is an integer.
    assert isinstance(enging_tuning_crates, int)
    assert isinstance(rudder_tuning_crates, int)
    assert isinstance(engine_tunings_per_crate, int)
    assert isinstance(rudder_tunings_per_crate, int)

    # The section of code to modify in the original file looks like:
    # (Note, since this is used as a replacement, indentation whitespace needs
    #  to be exact.)
    original_text = '''<do_all exact="8" counter="placing4">
                <find_sector name="ASP.Tuningsector{counter@placing4}" sector="{player.sector}" min="1" race="pirate"/>
                <do_if value="{sector.exists@ASP.Tuningsector{counter@placing4}}" exact="1">
                  <do_any>
                    <create_crate invincible="1" secret="1">
                      <position x="0" y="0" z="0" min="({sector.size.km@ASP.Tuningsector{counter@placing4}}+({sector.size.km@ASP.Tuningsector{counter@placing4}}/20))km" max="({sector.size.km@ASP.Tuningsector{counter@placing4}}+({sector.size.km@ASP.Tuningsector{counter@placing4}}/3))km"/>
                      <sector sector="ASP.Tuningsector{counter@placing4}"/>
                      <ware typename="SS_WARE_TECH213" min="2" max="5"/>
                    </create_crate>
                    <create_crate invincible="1" secret="1">
                      <position x="0" y="0" z="0" min="({sector.size.km@ASP.Tuningsector{counter@placing4}}+({sector.size.km@ASP.Tuningsector{counter@placing4}}/20))km" max="({sector.size.km@ASP.Tuningsector{counter@placing4}}+({sector.size.km@ASP.Tuningsector{counter@placing4}}/3))km"/>
                      <sector sector="ASP.Tuningsector{counter@placing4}"/>
                      <ware typename="SS_WARE_TECH246" min="2" max="5"/>
                    </create_crate>
                  </do_any>
                </do_if>
              </do_all>'''
    # To standardize tunings to roughly the average case, maybe slightly
    #  above for ease of the transform, can change the number of
    #  loops from 8 to 4, chance the inner do_any to do_all so that each
    #  loop creates one of each tuning type, and change the min/max
    #  tunings to 4, eg. 16 engine and 16 rudder tunings.
    # Update: revisit this, since it spawns pairs of tunings in the same
    #  sector instead of spreading them out more.
    # Update: running "find_sector name="ASP.Tuningsector{counter@placing4}"" after
    #  having done it previously appears to cause the file to not load, so just
    #  copying the inner body and looping 4 times is not enough.
    # Try copying the entire thing, giving the second copy a different
    #  counter, each loop running 4 times separately.
    # TODO: optionally set the outer loop to 2 and do 2 iterations of each of the crates, 
    #  one at 3 and one at 4 tunings, to get the proper average.
    replacement_text = ('''<do_all exact="ENGINE_CRATES" counter="placing4">
                <find_sector name="ASP.Tuningsector{counter@placing4}" sector="{player.sector}" min="1" race="pirate"/>
                <do_if value="{sector.exists@ASP.Tuningsector{counter@placing4}}" exact="1">
                  <do_any>
                    <create_crate invincible="1" secret="1">
                      <position x="0" y="0" z="0" min="({sector.size.km@ASP.Tuningsector{counter@placing4}}+({sector.size.km@ASP.Tuningsector{counter@placing4}}/20))km" max="({sector.size.km@ASP.Tuningsector{counter@placing4}}+({sector.size.km@ASP.Tuningsector{counter@placing4}}/3))km"/>
                      <sector sector="ASP.Tuningsector{counter@placing4}"/>
                      <ware typename="SS_WARE_TECH213" min="ENGINE_TUNES" max="ENGINE_TUNES"/>
                    </create_crate>
                  </do_any>
                </do_if>
              </do_all>
              <do_all exact="RUDDER_CRATES" counter="placing4b">
                <find_sector name="ASP.Tuningsector{counter@placing4b}" sector="{player.sector}" min="1" race="pirate"/>
                <do_if value="{sector.exists@ASP.Tuningsector{counter@placing4b}}" exact="1">
                  <do_any>
                    <create_crate invincible="1" secret="1">
                      <position x="0" y="0" z="0" min="({sector.size.km@ASP.Tuningsector{counter@placing4b}}+({sector.size.km@ASP.Tuningsector{counter@placing4b}}/20))km" max="({sector.size.km@ASP.Tuningsector{counter@placing4b}}+({sector.size.km@ASP.Tuningsector{counter@placing4b}}/3))km"/>
                      <sector sector="ASP.Tuningsector{counter@placing4b}"/>
                      <ware typename="SS_WARE_TECH246" min="RUDDER_TUNES" max="RUDDER_TUNES"/>
                    </create_crate>
                  </do_any>
                </do_if>
              </do_all>'''
            # Do replacements of text, instead of using normal format specifier
            #  due to brackets in the original text.
            .replace('ENGINE_CRATES', str(enging_tuning_crates))
            .replace('RUDDER_CRATES', str(rudder_tuning_crates))
            .replace('ENGINE_TUNES', str(engine_tunings_per_crate))
            .replace('RUDDER_TUNES', str(rudder_tunings_per_crate))
            )
              
    # Grab the sector management file.
    file_contents = File_Manager.Load_File('director/3.08 Sector Management.xml')
    # Verify the original_block is present (matches successfully).
    assert file_contents.Get_Text().count(original_text) == 1
    file_contents.Update_From_Text(
        file_contents.Get_Text().replace(original_text, replacement_text))

    # -Removed; old line-by-line method didn't scale well.
    ##Define the modifications as a special dict of fields.
    # transform_dict = {
    #     #Start edits when seeing this line.
    #     'start_line' : '<do_all exact="8" counter="placing4">',
    #     #Indexes are line offsets from start, values are functions to be applied to the
    #     # line to obtain the replacement line, or the key of another entry which
    #     # contains the desired function (for function sharing).
    #     #Swap loop count.
    #     0  : lambda line : line.replace('8','4'),
    #     #Switch to do_all, opener and closer.
    #     3  : lambda line : line.replace('do_any','do_all'),
    #     14 : 3,
    #     #Switch to always getting 4 tunings.
    #     7  : lambda line : line.replace('2','4').replace('5','4'),
    #     12 : 7,
    #     }
    ##Apply the transform rules.
    # Apply_transform_to_lines(line_list, transform_dict)


    
@File_Manager.Transform_Wrapper('director/2.119 Trade Convoy.xml')
def Convoys_made_of_race_ships():
    '''
    If convoy defense missions should use the convoy's race to select their ship type.
    The vanilla script uses randomized ship types (eg. a terran convoy flying teladi ships).
    '''        
    # Swap this particular line to use the convoy race instead of default.
    # This line should occur twice, for the trader and its escorts.
    original_text = '''<param name="Maker Race" value="default" comment="The race of the ship maker"/>'''
    replacement_text = '''<param name="Maker Race" value="{value@L2M119.Convoy Race}" comment="The race of the ship maker"/>'''
    # Grab the director file.
    file_contents = File_Manager.Load_File('director/2.119 Trade Convoy.xml')
    # Verify the original_block is present (matches successfully).
    assert file_contents.Get_Text().count(original_text) == 2
    file_contents.Update_From_Text(
        file_contents.Get_Text().replace(original_text, replacement_text))



    
@File_Manager.Transform_Wrapper('director/3.05 Gamestart Missions.xml', LU = False)
def Standardize_Start_Plot_Overtunings(
    # Pick what fraction of the maximum overtunings to give.
    # Overtuning will be set to some % of the maximum, which should roughly
    #  correspond with moderate reloading (since the default loadout algorithm
    #  makes higher tunings exponentially less likely in some manner, requiring
    #  likely many reloads).
    # Eg. a maxed hyperion would be 250 m/s, but half max would be 210, which
    #  is easy to reach with light reloading.
    # Checking forums, 230+ hyperions are often reported, which would require
    #  9 overtunes out of 12, or 75%.
    # Somewhere in between these points is probably reasonable.
    fraction_of_max = 0.70
    ):
    '''
    Set the starting plots with overtuned ships to have their tunings
     standardized instead of being random.

    * fraction_of_max:
      - Float, typically between 0 and 1, the fraction of the max overtuning
        to use. A value of 0 will remove overtunings, and 1 will give max 
        overtuning that is available in vanilla.
        Default of 0.7 is set to mimic moderate game reloading results.
    '''

    # Sections of interest (in different locations) are,
    #  for Kea:
    original_kea = '''<create_ship name="this.reward" dockobject="this.dock" typename="SS_SH_T_M3P_ENH" race="player">
                        <equipment loadout="default">
                          <ware typename="SS_WARE_TECH213" exact="18"/>
                          <ware typename="SS_WARE_TECH246" exact="9"/>
                        </equipment>'''
    # And, for Hyperion:
    original_hyp = '''<create_ship name="this.reward" dockobject="this.dock" typename="SS_SH_P_M6_ADV" race="player">
                              <equipment loadout="default">
                                <ware typename="SS_WARE_TECH213" exact="12"/>
                                <ware typename="SS_WARE_TECH246" exact="8"/>
                              </equipment>
                            </create_ship>
                            <create_ship name="this.reward2" dockobject="this.dock" typename="SS_SH_P_M3_ADV" race="player">
                              <equipment loadout="default">
                                <ware typename="SS_WARE_TECH213" exact="8"/>
                                <ware typename="SS_WARE_TECH246" exact="5"/>
                              </equipment>
                            </create_ship>'''
    # Rudder is SS_WARE_TECH246, engine is SS_WARE_TECH213.
    # Editing can either focus on giving max loadout and reducing the tunings,
    #  or inserting lines to remove the default tuning counts and then add in
    #  the full base tunings with some reduced number of overtunings.
    # Go with the second option, since there are examples online, eg.
    #  https://forum.egosoft.com/viewtopic.php?t=376828
    # Note: the above example appears like it might be buggy, since it removes
    #  tunings based on player.ship, not the spawned ship; replace it with a
    #  fixed count maybe, eg. the max possible tunings, and rely on it to floor
    #  at 0.
    # Update: setting large negative values seems to bug out the file, such that game
    #  doesn't load it for whatever reason. Try to set negative value exactly matching
    #  that of the ship's max normal tunings (maybe there is a check during parsing).
    # Kea: Normal max 15 engine, 15 rudder.
    replacement_kea = '''<create_ship name="this.reward" dockobject="this.dock" typename="SS_SH_T_M3P_ENH" race="player">
                        <equipment loadout="default">
                          <ware typename="SS_WARE_TECH213" exact="-15"/>
                          <ware typename="SS_WARE_TECH246" exact="-15"/>
                          <ware typename="SS_WARE_TECH213" exact="{}"/>
                          <ware typename="SS_WARE_TECH246" exact="{}"/>
                        </equipment>'''.format(
                            round(15 + 18 * fraction_of_max),
                            round(15 + 9 * fraction_of_max)
                            )
    # Hyperion, normal max 15 engine, 18 rudder.
    # Perseus, normal max 12 engine, 12 rudder.
    replacement_hyp = '''<create_ship name="this.reward" dockobject="this.dock" typename="SS_SH_P_M6_ADV" race="player">
                              <equipment loadout="default">
                                <ware typename="SS_WARE_TECH213" exact="-15"/>
                                <ware typename="SS_WARE_TECH246" exact="-18"/>
                                <ware typename="SS_WARE_TECH213" exact="{}"/>
                                <ware typename="SS_WARE_TECH246" exact="{}"/>
                              </equipment>
                            </create_ship>
                            <create_ship name="this.reward2" dockobject="this.dock" typename="SS_SH_P_M3_ADV" race="player">
                              <equipment loadout="default">
                                <ware typename="SS_WARE_TECH213" exact="-12"/>
                                <ware typename="SS_WARE_TECH246" exact="-12"/>
                                <ware typename="SS_WARE_TECH213" exact="{}"/>
                                <ware typename="SS_WARE_TECH246" exact="{}"/>
                              </equipment>
                            </create_ship>'''.format(
                            round(15 + 12 * fraction_of_max),
                            round(18 + 8 * fraction_of_max),
                            round(12 + 8 * fraction_of_max),
                            round(12 + 5 * fraction_of_max),
                            )
            
    # Grab the sector management file.
    file_contents = File_Manager.Load_File('director/3.05 Gamestart Missions.xml')
    # Verify the original_block is present (matches successfully).
    assert file_contents.Get_Text().count(original_kea) == 1
    assert file_contents.Get_Text().count(original_hyp) == 1
    file_contents.Update_From_Text = (
        file_contents.Get_Text()
            .replace(original_kea, replacement_kea)
            .replace(original_hyp, replacement_hyp))
        
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

    # Record a file object to be written later.
    File_Manager.Add_File(File_Manager.Misc_File(
        virtual_path = 'director/' + file_name, 
        text = shell_text))


        
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

    #  This will eventually be xml, so do it using a list of xml nodes
    #  to be placed inside of a do_all block.
    #  This should be a lot more elegant than raw text strings.
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

    #  To speed up the script, try to add all new objects together
    #   which share the same template object, and also categorize
    #   by race.
    #  Note: in removal mode, there are no template objects to worry
    #   about; just put the ware itself in the template for that case,
    #   to get reuse of the match code.
    #  Make a race : template_name : new_wares_sublist dict.
    race_template_wares_list_dict_dict = defaultdict(
                                        lambda : defaultdict(list))

    for ware_dict in new_wares_list:
        #  Get the race as a string, using director race names.
        race_type = Flags.Director_race_code_name_dict[int(ware_dict['race'])]
        race_template_wares_list_dict_dict[
            race_type][
                #  Use the template name, or ware name if removing it.
                ware_dict.template_name if removal_mode == False else ware_dict['name']
                ].append(ware_dict)


    #  For removal mode, much of this code will be the same until getting
    #   into the do_if node when a template name is matched.

    #  Loop over the races.
    for race, template_wares_list_dict in race_template_wares_list_dict_dict.items():

        #  For fun, toss up a help message to say what is happening.
        #  -Removed; the game basically freezes while this runs, so the
        #  display doesn't show up until after it completes. Can still
        #  put a final message.
        # help_node = ET.Element('show_help',{
        #     'text' : 'Updating {} shipyards with new wares.'.format(race),
        #     # Try out 5 seconds or so.
        #     'duration' : '5000'})
        # do_all_root.append(help_node)

        #  Gather a list of all shipyards for this race.
        #  Example:
        #  <find_station group="Shipyards" multiple="1">
        #      <sector x="0" y="0"/>
        #      <jumps max="100"/>
        #  </find_station>
        #  Note: groups appear to be sticky, as in multiple commands with
        #  the same group will append to it, so after each shipyard group
        #  is handled the group should be cleared out.
        #  Note: when looking for terrans, also match with atf, which can
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
            #  -Removed; ware check doesn't appear to work with multi match.
            #  This is leftover from trying style (2).
            # ET.Element('ware',{'typename' : template_name,
            #                    # Require at least 1 unit; otherwise this
            #                    # seemed to be matching everything.
            #                    'min'      : '1'}),
            ])

        #  Set up a loop over the stations.
        #  Example:
        #  <do_all exact="{group.object.count@Shipyards}" counter="count">
        loop_node = ET.Element('do_all',{
            #  Give the number of shipyards to count through.
            'exact' : '{group.object.count@Shipyards}',
            #  Name the counter.
            'counter' : 'count'})

        #  Indent here to indicate inside the loop above.
        if 1:
            #  This string will be used to reference a given shipyard,
            #  by indexing into the Shipyards group based on the current
            #  counter value.
            shipyard = '{group.object.{counter@count}@Shipyards}'

            #  Loop over all of the templates to be checked.
            for template_name, new_wares_list in template_wares_list_dict.items():

                #  Check if this shipyard has this ware as a product.
                #  Thankfully, there appears to be a convenient command
                #  for this, getting a boolean.
                #  Put this in a do_if node.
                if_node = ET.Element('do_if',{
                    'value' : '{{object.products.{}.exists@{}}}'.format(
                        template_name,
                        shipyard
                        ),
                    'exact' : '1'})
                #  Add this to the loop.
                loop_node.append(if_node)

                #  Indent for the do_if block.
                if 1:
                    #  Loop over the new wares.
                    for new_ware in new_wares_list:

                        #  In removal mode, it should be okay to remove the
                        #  product blindly.
                        if removal_mode:
                            #  Only need to give a typename here; amount 
                            #  doesn't matter since it does a full removal.
                            remove_node = ET.Element('remove_products',{'object' : shipyard})
                            remove_node.append(ET.Element('ware',{
                                'typename' : new_ware['name']}))
                            #  Stick in the outer do_if.
                            if_node.append(remove_node)

                        else:
                            #  Aim is to add just 1 unit of product, and to not add
                            #   any more if the station already has at least 1 unit.
                            #  This will require another do_if, conditioned on the
                            #   product count.
                            #  Check if the ware doesn't exist.
                            inner_if_node = ET.Element('do_if',{
                                'value' : '{{object.products.{}.exists@{}}}'.format(
                                    new_ware['name'],
                                    shipyard
                                    ),
                                'exact' : '0'})
                            #  Stick in the outer do_if.
                            if_node.append(inner_if_node)

                            #  Indent again.
                            if 1:
                                #  Add the product to the current shipyard.
                                insert_node = ET.Element('add_products',{'object' : shipyard})
                                insert_node.append(ET.Element('ware',{
                                    'typename' : new_ware['name'],
                                    #  Give 1 unit, else shows up in game with 0.
                                    'exact' : '1'}))
                                #  Stick inside the do_if.
                                inner_if_node.append(insert_node)
                    
        #  Clear out the shipyard group.
        clear_node = ET.Element('remove_group',{'group' : 'Shipyards'})
            
        #  Stick these in the outer do_all.
        do_all_root.append(station_node)
        do_all_root.append(loop_node)
        do_all_root.append(clear_node)

        
    #  Make a final status message.
    do_all_root.append( ET.Element('show_help',{
        'text' : 'Completed shipyard ware update.',
        #  Try out a few seconds.
        #  This seems to have the processing time counted against
        #  it, so should be longer than that.
        #  In testing, takes a few seconds to process.
        'duration' : '6000'}))


    #  Send back the xml node if requested.
    if return_xml:
        return do_all_root

    #  Otherwise convert to text.
    else:
        #  Give it some nice formatting.
        xml_text = ET.tostring(do_all_root)
        minidom_root = minidom.parseString(xml_text)
        xml_text = minidom_root.toprettyxml(indent = indent_str)

        #  Post-process it to get rid of the xml declaration node, and add
        #  an extra indents.
        xml_lines = xml_text.splitlines()
        assert 'version' in xml_lines[0]
        xml_lines = xml_lines[1:]
        for index in range(len(xml_lines)):
            xml_lines[index] = indent_str * indent_level + xml_lines[index]
        xml_text = '\n'.join(xml_lines)
        return xml_text