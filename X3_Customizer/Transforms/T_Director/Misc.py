'''
Transforms to the director xml files.
These are generally targetted at specific lines of the original input.

TODO: update code to make better use of xml nodes, as convenient.

TODO: any special fixes for other mods, eg. New Home gate fix for
TC plots in AP.
'''
import copy
from ... import File_Manager

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
      - Categories and cue names for vanilla AP are as follows, where
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
    return

    
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
    return

    
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
    return


    

        