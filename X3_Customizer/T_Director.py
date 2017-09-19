'''
Transforms to the director xml files.
These are generally targetted at specific lines of the original input.

'''
import copy
from File_Manager import *


@Check_Dependencies('3.08 Sector Management.xml')
def Standardize_Tunings(
    enging_tuning_crates = 4,
    rudder_tuning_crates = 4,
    engine_tunings_per_crate = 4,
    rudder_tunings_per_crate = 3
    ):
    '''
    If the number of randomized tuning creates at gamestart should be
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
    #Make sure the input is an integer.
    assert isinstance(enging_tuning_crates, int)
    assert isinstance(rudder_tuning_crates, int)
    assert isinstance(engine_tunings_per_crate, int)
    assert isinstance(rudder_tunings_per_crate, int)

    #The section of code to modify in the original file looks like:
    #(Note, since this is used as a replacement, indentation whitespace needs
    # to be exact.)
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
    #To standardize tunings to roughly the average case, maybe slightly
    # above for ease of the transform, can change the number of
    # loops from 8 to 4, chance the inner do_any to do_all so that each
    # loop creates one of each tuning type, and change the min/max
    # tunings to 4, eg. 16 engine and 16 rudder tunings.
    #Update: revisit this, since it spawns pairs of tunings in the same
    # sector instead of spreading them out more.
    #Update: running "find_sector name="ASP.Tuningsector{counter@placing4}"" after
    # having done it previously appears to cause the file to not load, so just
    # copying the inner body and looping 4 times is not enough.
    #Try copying the entire thing, giving the second copy a different
    # counter, each loop running 4 times separately.
    #TODO: optionally set the outer loop to 2 and do 2 iterations of each of the crates, 
    # one at 3 and one at 4 tunings, to get the proper average.
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
            #Do replacements of text, instead of using normal format specifier
            # due to brackets in the original text.
            .replace('ENGINE_CRATES', str(enging_tuning_crates))
            .replace('RUDDER_CRATES', str(rudder_tuning_crates))
            .replace('ENGINE_TUNES', str(engine_tunings_per_crate))
            .replace('RUDDER_TUNES', str(rudder_tunings_per_crate))
            )
              
    #Grab the sector management file.
    file_contents = Load_File('3.08 Sector Management.xml')
    #Verify the original_block is present (matches succesfully).
    assert file_contents.text.count(original_text) == 1
    file_contents.text = file_contents.text.replace(original_text, replacement_text)

    #-Removed; old line-by-line method didn't scale well.
    ##Define the modifications as a special dict of fields.
    #transform_dict = {
    #    #Start edits when seeing this line.
    #    'start_line' : '<do_all exact="8" counter="placing4">',
    #    #Indexes are line offsets from start, values are functions to be applied to the
    #    # line to obtain the replacement line, or the key of another entry which
    #    # contains the desired function (for function sharing).
    #    #Swap loop count.
    #    0  : lambda line : line.replace('8','4'),
    #    #Switch to do_all, opener and closer.
    #    3  : lambda line : line.replace('do_any','do_all'),
    #    14 : 3,
    #    #Switch to always getting 4 tunings.
    #    7  : lambda line : line.replace('2','4').replace('5','4'),
    #    12 : 7,
    #    }
    ##Apply the transform rules.
    #Apply_transform_to_lines(line_list, transform_dict)


    
@Check_Dependencies('2.119 Trade Convoy.xml')
def Convoys_made_of_race_ships():
    '''
    If convoy defense missions should use the convoy's race to select their ship type.
    The vanilla script uses randomized ship types (eg. a terran convoy flying teladi ships).
    '''        
    #Swap this particular line to use the convoy race instead of default.
    #This line should occur twice, for the trader and its escorts.
    original_text = '''<param name="Maker Race" value="default" comment="The race of the ship maker"/>'''
    replacement_text = '''<param name="Maker Race" value="{value@L2M119.Convoy Race}" comment="The race of the ship maker"/>'''
    #Grab the director file.
    file_contents = Load_File('2.119 Trade Convoy.xml')
    #Verify the original_block is present (matches succesfully).
    assert file_contents.text.count(original_text) == 2
    file_contents.text = file_contents.text.replace(original_text, replacement_text)



    
@Check_Dependencies('3.05 Gamestart Missions.xml')
def Standardize_Start_Plot_Overtunings(
    #Pick what fraction of the maximum overtunings to give.
    #Overtuning will be set to some % of the maximum, which should roughly
    # correspond with moderate reloading (since the default loadout algorithm
    # makes higher tunings exponentially less likely in some manner, requiring
    # likely many reloads).
    #Eg. a maxed hyperion would be 250 m/s, but half max would be 210, which
    # is easy to reach with light reloading.
    #Checking forums, 230+ hyperions are often reported, which would require
    # 9 overtunes out of 12, or 75%.
    #Somewhere in between these points is probably reasonable.
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

    #Sections of interest (in different locations) are,
    # for Kea:
    original_kea = '''<create_ship name="this.reward" dockobject="this.dock" typename="SS_SH_T_M3P_ENH" race="player">
                        <equipment loadout="default">
                          <ware typename="SS_WARE_TECH213" exact="18"/>
                          <ware typename="SS_WARE_TECH246" exact="9"/>
                        </equipment>'''
    #And, for Hyperion:
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
    #Rudder is SS_WARE_TECH246, engine is SS_WARE_TECH213.
    #Editing can either focus on giving max loadout and reducing the tunings,
    # or inserting lines to remove the default tuning counts and then add in
    # the full base tunings with some reduced number of overtunings.
    #Go with the second option, since there are examples online, eg.
    # https://forum.egosoft.com/viewtopic.php?t=376828
    #Note: the above example appears like it might be buggy, since it removes
    # tunings based on player.ship, not the spawned ship; replace it with a
    # fixed count maybe, eg. the max possible tunings, and rely on it to floor
    # at 0.
    #Update: setting large negative values seems to bug out the file, such that game
    # doesn't load it for whatever reason. Try to set negative value exactly matching
    # that of the ship's max normal tunings (maybe there is a check during parsing).
    #Kea: Normal max 15 engine, 15 rudder.
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
    #Hyperion, normal max 15 engine, 18 rudder.
    #Perseus, normal max 12 engine, 12 rudder.
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
            
    #Grab the sector management file.
    file_contents = Load_File('3.05 Gamestart Missions.xml')
    #Verify the original_block is present (matches succesfully).
    assert file_contents.text.count(original_kea) == 1
    assert file_contents.text.count(original_hyp) == 1
    file_contents.text = (file_contents.text
                            .replace(original_kea, replacement_kea)
                            .replace(original_hyp, replacement_hyp))
        
    #-Removed; old line-by-line method didn't scale well.
    ##Want to edit '3.05 Gamestart Missions'
    #line_list = director_file_dict['3.05 Gamestart Missions']
    ##Make separate transforms, since they occur at widely different line numbers.
    ##Kea.
    #transform_kea_dict = {
    #    'start_line' : '<create_ship name="this.reward" dockobject="this.dock" typename="SS_SH_T_M3P_ENH" race="player">',
    #    #Insert a line before by returning a string with a newline in it.
    #    #Normal max 15 engine, 15 rudder.
    #    2: lambda line: '{}{}\n{}'.format(
    #        #Copy some whitespace to make the line pretty.
    #        Get_whitespace(line),
    #        #Remove existing tunings.
    #        '<ware typename="SS_WARE_TECH213" exact="-50">',
    #        #Add normal max to the fraction of max.
    #        line.replace('18', '{}'.format(int(15 + 18 * fraction_of_max)))
    #        ),
    #    3: lambda line: '{}{}\n{}'.format(
    #        Get_whitespace(line),
    #        #Remove existing tunings.
    #        '<ware typename="SS_WARE_TECH246" exact="-50">',
    #        line.replace('9', '{}'.format(int(15 + 9 * fraction_of_max)))
    #        ),
    #    }
    ##Hyperion and advanced perseus.
    #transform_hyperion_dict = {
    #    'start_line' : '<create_ship name="this.reward" dockobject="this.dock" typename="SS_SH_P_M6_ADV" race="player">',
    #    #Hyperion, normal max 15 engine, 18 rudder.
    #    2: lambda line: '{}{}\n{}'.format(
    #        Get_whitespace(line),
    #        #Remove existing tunings.
    #        '<ware typename="SS_WARE_TECH213" exact="-50">',
    #        #Normal max is 10             
    #        line.replace('12', '{}'.format(int(15 + 12 * fraction_of_max)))
    #        ),
    #    3: lambda line: '{}{}\n{}'.format(
    #        Get_whitespace(line),
    #        #Remove existing tunings.
    #        '<ware typename="SS_WARE_TECH246" exact="-50">',
    #        #Normal max for a kea is 15.       
    #        line.replace('8', '{}'.format(int(18 + 8 * fraction_of_max)))
    #        ),
    #    #Perseus, normal max 12 engine, 12 rudder.
    #    8: lambda line: '{}{}\n{}'.format(
    #        Get_whitespace(line),
    #        #Remove existing tunings.
    #        '<ware typename="SS_WARE_TECH213" exact="-50">',
    #        #Normal max for a kea is 15.              
    #        line.replace('8', '{}'.format(int(12 + 8 * fraction_of_max)))
    #        ),
    #    9: lambda line: '{}{}\n{}'.format(
    #        Get_whitespace(line),
    #        #Remove existing tunings.
    #        '<ware typename="SS_WARE_TECH246" exact="-50">',
    #        #Normal max for a kea is 15.       
    #        line.replace('5', '{}'.format(int(12 + 5 * fraction_of_max)))
    #        ),
    #    }
    #        
    ##Apply the transform rules.
    #Apply_transform_to_lines(line_list, transform_kea_dict)
    #Apply_transform_to_lines(line_list, transform_hyperion_dict)


    return


#TODO:
#Adjust generic mission spawn chances, per category.


#-Removed; old line-by-line method didn't scale well.
#def Get_whitespace(line):
#    'Helper function to return the leading white space from a line.'
#    #Trick found at:
#    # https://stackoverflow.com/questions/2268532/grab-a-lines-whitespace-indention-with-python
#    #Basically, get the line without the whitespace, check its length, and take a 
#    # slice of the line from the start out to the difference in length between
#    # the original line and lstripped line.
#    return line[ : len(line) - len( line.lstrip() )]
#
#def Apply_transform_to_lines(line_list, transform_dict):
#    '''
#    Support function to apply a transform to a group of lines.
#    '''
#    #This will track progress in the transform by creating a copy of
#    # the dict, and popping off entries as they are satisfied, finishing
#    # when the copy is empty.
#    transform_dict_local = copy.copy(transform_dict)
#    #Go through the copy and standardize it, so that any entries which
#    # reference other entries get replaced with those entrie's values.
#    # Eg. if entry X has value Y, and Y is another key, replace the value
#    # of X with the value of Y.
#    for key, value in transform_dict_local.items():
#        if value in transform_dict_local:
#            transform_dict_local[key] = transform_dict_local[value]
#
#    #If the start line has been found.
#    start_found = False
#    #The current line offset from the start.
#    offset_from_start = 0
#
#    #Loop over lines by index, to make replacement more convenient.
#    for index in range(len(line_list)):
#        #Get this line.
#        line = line_list[index]
#        new_line = None
#
#        #If looking for the start still.
#        if not start_found:
#            if transform_dict_local['start_line'] in line:
#                #If matched, remove start_line.
#                transform_dict_local.pop('start_line')
#                start_found = True
#
#        #Do line offset checks once start is found.
#        #This should work for offset 0, eg. on the same line that find the
#        # start tag.
#        if start_found:
#            #Check if the current line is in the dict.
#            if offset_from_start in transform_dict_local:
#                #Apply the transform.
#                new_line = transform_dict_local[offset_from_start](line)
#                #Remove the transform.
#                transform_dict_local.pop(offset_from_start)
#        
#            #Advance line offset counter.
#            offset_from_start += 1
#
#        #Put the new line back.
#        if new_line:
#            line_list[index] = new_line
#
#
#        #Done when the transform dict is empty.
#        if not transform_dict_local:
#            break
#
#    #Error if stuff left in the transform dict.
#    assert not transform_dict_local
#
#    #Return nothing; the list was modified in place.
#    return