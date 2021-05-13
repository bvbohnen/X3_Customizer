'''
Modifications to ship tuning crates.
'''
from ... import File_Manager

@File_Manager.Transform_Wrapper('director/3.08 Sector Management.xml', 
                                LU = False, TC = False, FL = False)
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

    return

    
@File_Manager.Transform_Wrapper('director/3.05 Gamestart Missions.xml', 
                                LU = False, FL = False)
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

