'''
Transforms based on the universe file, sometimes editing text
files or creating director files.
'''

'''
Color sector names in the universe map and elsewhere, according to race.
This is similar to the mod (of a similar name), but will fill in the coloring
dynamically since that mod is hand crafted and outdated for XRM.

Approach:
1) Read the x3_universe.xml file, build a list of each sector by coordinates
and owner. Information on owner codes taken from: 
    https://forum.egosoft.com/viewtopic.php?t=227472&postdays=0&postorder=asc&start=0

    Coordinate form: x="0" y="0"
    Owner form: r="2"
    Owner codes:
        1 => argon
        2 => boron
        3 => split
        4 => paranid
        5 => teladi
        6 => xenon
        7 => kha'ak
        8 => pirates
        9 => goner
        12 => unclaimed (ship)
        14 => unknown (sector|beacon)
        17 => Terran (ATF)
        18 => Terran (USC)
        19 => Yaki
2) Select a color code for each owner. Codes will be implemented as prefix and suffix
tags around the sector names
    Format (copied from the colored sectors mod):
        \033{}SECTOR_NAME\033X
        Where {} is a single capital letter for the color to use.
        Known colors are:
        W - white
        R - red
        B - blue
        G - green
        Y - yellow
        M - magenta
        C - cyan
        A - grey
    Details on color formats also given at: https://forum.egosoft.com/viewtopic.php?t=129042
3) Open the language file 9961-L044.xml (maybe 7027-L044.xml too) and edit the names to 
 include the color codes. Note: L044 is English, L049 is German, etc for other languages;
 only do english.
 These files contain sector names or name references associated with each sector coordinate.
 Coordinate format is '102<y><x>', where the y,x are each given to 2 digits, and offset by +1.
    Example line:
     <t id="1020101">Kingdom End</t>
     This corresponds to sector 0,0.
 Thread https://forum.egosoft.com/viewtopic.php?p=4017000 is the source for the +1 offset,
  though it does not specify on if 'x' or 'y' goes first in naming (y is first by experience).
 Note: it appears '1020000' is specially assigned to Unknown Sector.
 Sector names can be given as references, for example:
     <t id="1020117">{7,1020000}</t>
 In this case, use the reference id for the lookup (and assume there are no chained
  references for now).

 Note: some xrm text files have parenthesis in them around generic terms, like coordinates
 or a name; apparently these are treated as comments according to:
 http://www.argonopedia.org/wiki/Text_resource_file


Edits can be done on raw text files for now, to reduce parsing overhead since these
files do not share common formatting with the other files (mostly T files) being
edited by most transforms.



How are the text files are laid out?
    -The colored sectors mod seemed to mainly put all sector names into its 9961-L044 file,
    but XRM doesn't have a similar file.
    -Sector names appear to be scattered around.
    -The default names are in 0001-L044, from 04.cat.
    -It seems like these files overwrite each other, probably going from lowest to 
    highest file name number.
    -The colored sectors mod therefore put a copy of the sector names from 0001 into its
    9961 file and colored them.
    -It is unclear on why the colored sector mod also overwrote 7027 (which mostly contains
    name indirect references), rather than just copying it into 9961 with the rest.
    -Sector names from XRM have been found in 0001, 7027, 7360 (just a few).

    Note: 9961 has been reused to copy the sector name contents of 0001, since the number 9961
     will not be used by the colored sectors mod (as this transform replaces it), and 0001 is
     otherwise a large file that includes special characters which Python's default read/write
     gives errors on (would need to play around with encodings to fix that, or else just do what
     is done here and copy out the parts of interest).
    Update: going back to editing 0001, to avoid hassles with loading 9961 properly in case there
     are any (seem to be, requiring a script or similar to load it, but may need more testing).


Note:
    Most sector names are in text block '7', but some are in text block '300007', which apparently
    gets mapped to '7' and the prefix indicates it is a associated with AP.
    So eg. sector Avarice, 1020909, has a reference to {7,20000}, while the actual text name
    for 'Avarice' is in {300007,20000} going by the ids in the code itself.
    For the most part, this shouldn't be relevant to changes here, but is noted in case it
    ever matters in the future.


Note:
    Some sectors are not recolored properly. An analysis of Mercanry Rift, renamed in XRM to
     Hell Forge, seems to indicate that MR (x=18,y=9) is not renamed directly (eg. not by
     using 1021019, which has its name in 0001), but instead by using 1024019, which would
     correspond to sector x=18,y=39 which is well off the map grid.
     (Note: 1034019 is the description for Hell Forge, verifying that 4019 is the correct
      suffix identified above.)

    Is it possible that, similar to id='300007' getting remapped to id='7', that the game
     also subtracts 30 from high sector coordinates to get the actual sector?

    However, another example of Family Zyarth (double check name; x=18,y=5; code 0619) was renamed in
     XRM to Circle of Deceit by redirecting the 1020619 name to 1023801. 
    -If there were an implicit %30 operation on the coordinates, the latter would go to 
     sector 0801 (x=0,y=7, Savage Spur), which clearly is not happening.

The open question is: how does the Hell Forge name at 1024019 get assigned to the entry
 at 1021019?
    -In the XRM version of 7027, 1021019 is directly given the Hell Forge name, and 1031019 is
     used directly for the description.
    -In the XRM-TCAP version, there is no 1021019 renaming, though entry 1024001 does
     redirect to 1021019 (which shouldn't matter for this question, and just renames whatever
     sector that is to Mercenary Rift), and this is the version with 1024019 containing Hell Forge.
    -In the XRM-TCAP patch, the behavior of XRM-TCAP is retained. This is the version nominally
     being run with.

    In theory, this should mean Mercenary Rift doesn't get renamed, since the XRM-TCAP patch
    moved its renaming and description to some other (apparently unused) code.
    However, in game the Hell Forge name is still visible.

    -Is the game still loading the XRM version for some reason, eg. some read error on the
    modified XRM-TCAP patch version (newline format maybe?).
        -This seems less likely, since file 7027 also changes Family Zyarth's name back, and
        that name restoration does show up in game.
        -Notepad indicates the XRM and XRM-TCAP versions of this file has the same encoding
        and line ending format.

    -Is the game using an older text name for some reason?
        -The fact that sector colors update immediately suggests this shouldn't be the case.
        -Using a script to print the text on page 7, entry 1021019, returns Mercenary's Rift
        correctly colored red.
        -Starting a new game still has the Hell Forge name in place.

    -Is a script renaming the system?
        -On a new start next to the XRM system Privateer Gate, the system gate started with
        no name and just a sector coordinate reference, but on a second look picked up
        the Privateer Gate name. This may indicate the name being set by script, where
        the script didn't run immediately.
        -On a general overview, no scripts or mission directory files found which do
        sector renaming, except perhaps for some special player sectors.
        -This sector, Privateer Gate, is code 1020921, and in both the XRM and XRM-TCAP
        versions of 7027 is renamed directly, not through any weird tricks.

-Open issue; unsolved.
-For now, some sector names will not be colored.
-Can maybe hand color them in the future if there are not many and a proper fix
remains unfound.

    
'''
from File_Manager import *
import os


@Check_Dependencies('x3_universe.xml','0001-L044.xml','7027-L044.xml','7360-L044.xml')
def Color_Sector_Names(
    #Specify the color to use for each race/affiliation.
    #To save some implementation time, races should be defined by their code number
    # in the universe file.
    Race_color_letters = {
            #argon
            '1': 'B',
            #boron
            '2': 'G',
            #split
            '3': 'M',
            #paranid
            '4': 'C',
            #teladi
            '5': 'Y',
            #xenon
            '6': 'R',
            #kha'ak
            '7': 'R',
            #pirates
            '8': 'R',
            #goner
            '9': 'B',
            #unknown; leave uncolored or just use grey. Code is more consistent
            # for now to just use grey.
            '14': 'A',
            #Terran (ATF)
            '17': 'W',
            #Terran (USC)
            '18': 'W',
            #Yaki
            '19': 'R',
        }
    ):
    '''
    Colors sector names in the map based on race owners declared
    in the x3_universe file. Some sectors may remain uncolored if
    their name is not set in the standard way through text files.
    Only works on the English files, L044, for now.
    Note: searching sectors by typing a name will no longer work
     except on uncolored sectors, eg. unknown sectors.

    * race_color_letters:
      - Dict matching race id string to the color code string to be used.
        Default is filled out similar to the standalone colored sectors mod.
    '''
    import re

    #Open the universe file and scan through it to find sector owners.
    #This could be done with a fuller xml parser, but since the operation is simple just
    # do a quick pattern check on each line.
    #TODO: maybe also parse some other map files, eg War_Effort which has a different
    # race ownership for sector used in the Final Fury plot that switches from
    # unknown to Argon (Unknown in x3_universe, Argon in War_Effort).
    sector_id_color_dict = {}
    #Loop over the universe lines.
    for line in Load_File('x3_universe.xml').text.splitlines():

        #Expect every system declaration line to have a 'size' field.
        if 'size=' in line:

            #Verify by the line also defining generic missions chances.
            if 'qtrade=' not in line:
                print('Skipped {}, parsing error.'.__name__)
                return

            #Find the x,y,r terms.
            field_dict = Parse_universe_line(line)

            #Determine the sector code in the language file.
            #This starts with prefix 102.
            id = '102{:02d}{:02d}'.format(
                #Add 1 to these to match up with the language file.
                #Put y first.
                int(field_dict['y']) +1 , 
                int(field_dict['x']) +1 )

            #Look up the color letter and store it.
            sector_id_color_dict[id] = Race_color_letters[field_dict['r']]


    #Now that all sector names and color codes are recorded, go through the
    # text files.
    #This will begin edits in the sector name section, identified by
    # start and end codes.
    #Note: a language file may have definitions broken up across multiple
    # Sectornames blocks with different ids.
    start_code = 'title="Boardcomp. Sectornames"'
    end_code   = '</page>'

    #Loop over the language files to edit.
    #Try to edit 0001 directly for now; don't use 9961 as intermediary.
    for text_file_name in ['0001-L044.xml','7027-L044.xml','7360-L044.xml']: #'9961-L044.xml'
        
        #Break the text into lines, for easier editing.
        file_contents = Load_File(text_file_name)
        line_list = file_contents.text.splitlines()
        start_found = False

        #Loop over the lines by index.
        for index, this_line in enumerate(line_list):

            #Skip empty lines (do a quick split to toss white space).
            if not this_line.split():
                continue
            
            #Look for the start line if not found.
            if not start_found:
                if start_code in this_line:
                    start_found = True
                #Can skip the rest of this line.
                continue

            #Look for the end code.
            if end_code in this_line:
                #Unflag the start, so that the loop will search for the
                # next sector name block (if any).
                start_found = False
                continue

            #Otherwise, this line should be of a format like:
            # <t id="1020101">Kingdom End</t>
            #or
            # <t id="1020117">{7,1020000}</t>
            #The latter case is a redirection to another line, and
            # can be ignored for coloring (the line redirected to should
            # have the color applied). Currently this appears to only be
            # used for unknown sector for the example colored sectors mod,
            # though may show up elsewhere in some text files for xrm.
            #Start by getting the quoted id.
            #Use regex search, pattern on quotes around numbers.
            match_object = re.search(r'"([0-9]*)"', this_line)
            assert match_object != None
            #The id should be the only match, which can be obtained by
            # using .group(1) (group 0 is the whole string apparently).
            id = match_object.group(1)

            #If there is no color for this sector id, skip it.
            #(This occurs for eg. Unknown Sector, which has a special code not
            # assigned to any particular real sector).
            if id not in sector_id_color_dict:
                continue

            #Look up the color letter; it should hopefully be found.
            color = sector_id_color_dict[id]

            #Now look up the right side to wrap in color formatting.
            #Use regex, pattern on the '>' and '<', numbers, letters, spaces,
            # braces, parenthesis (use \ to escape them) allowed. Also add
            # some special chars as needed, eg. ' and ,.
            match_object = re.search(r">([A-Za-z0-9\s\(\)/{}',-]*)<", this_line)
            assert match_object != None
            sector_name = match_object.group(1)

            #There may be comments or references in the sector name, but it
            # should be okay to just wrap it all in the text color blindly.

            #Do a replacement and put it back.
            line_list[index] = this_line.replace(sector_name, r'\033{}{}\033X'.format(
                color,
                sector_name
                ))

        #Put the lines back. Keep an ending newline, since some original files had that.
        file_contents.text = '\n'.join(line_list)+'\n'
                
    return


@Check_Dependencies('x3_universe.xml')
def Restore_Aldrin_rock():
    '''
    Restors the big rock in Aldrin for XRM, reverting to the vanilla
    sector layout.
    Note: only works on a new game.
    '''
    #Similar to X3_Director, do a text search and replace.
    #Since the text is long, put it at the end of this module.
    original_text, replacement_text = Get_Aldrin_rock_texts()
    
    file_contents = Load_File('x3_universe.xml')
    #Verify the original_block is present (matches succesfully).
    if not file_contents.text.count(original_text) == 1:
        print('Skipped {}, format of source not as expected from XRM.'.__name__)
        return
    file_contents.text = file_contents.text.replace(original_text, replacement_text)
        
    
@Check_Dependencies('x3_universe.xml')
def Restore_Hub_Music(
    apply_to_existing_save = False,
    _cleanup = False
    ):
    '''
    If Hub sector (13,8) music should be restored to that in AP.
    (XRM sets the track to 0.) Applies to new games, and optionally to
    an existing save.

    * apply_to_existing_save:
      - If True, makes a drop-in director script that will fire once
        and change the music for an existing save game. This is not reversable
        at this time.
    '''
    #Pick a queue name for this; also use as file name.
    queue_name = 'X3_Customizer_Restore_Hub_Music'

    #Clean out old director file if requested.
    if _cleanup:
        Make_Director_Shell(queue_name, _cleanup = True)
        return

    #Do the test replacement, as above, keying off of sector
    # 13,8, the Hub sector.
    original_text    = '<o t="1" x="13" y="8" r="14" size="10000000" m="0"'
    replacement_text = '<o t="1" x="13" y="8" r="14" size="10000000" m="8302"'

    file_contents = Load_File('x3_universe.xml')
    #Verify the original_block is present (matches succesfully).
    if not file_contents.text.count(original_text) == 1:
        print('Skipped {}, format of source not as expected from XRM.'.__name__)
        return
    file_contents.text = file_contents.text.replace(original_text, replacement_text)

    #When a save already has the wrong music, apply a patch.
    if apply_to_existing_save:
        #Lay out the body of the director command.
        #This is packed into a do_all block.
        #XRMINST.xml does this as well, and can be used as a reference maybe.
        #The director manual says only x,y needed, which is good since the hub
        # sector name is unclear.
        text = (r'<alter_sector x="13" y="8" music="8302"/>')
        #Make the file.
        Make_Director_Shell(queue_name, text)
    else:
        #TODO: delete the file made above, if it exists.
        #May need to add support for a cleanup function to be called for
        # transforms that were not otherwise used, to clean out old files.
        pass

    
@Check_Dependencies('x3_universe.xml')
def Restore_M148_Music(
    apply_to_existing_save = False,
    _cleanup = False
    ):
    '''
    If Argon Sector M148 (14,8) music should be restored to that in AP.
    (XRM changes this to the argon prime music.) Applies to new games, 
    and optionally to an existing save.
    
    * apply_to_existing_save:
      - If True, makes a drop-in director script that will fire once
        and change the music for an existing save game. This is not reversable
        at this time.
    '''
    #Pick a queue name for this; also use as file name.
    queue_name = 'X3_Customizer_Restore_M148_Music'

    #Clean out old director file if requested.
    if _cleanup:
        Make_Director_Shell(queue_name, _cleanup = True)
        return

    #Do the test replacement, as above, keying off of sector
    # 14,8, the M148 sector.
    original_text    = '<o t="1" x="14" y="8" r="1" size="22500000" m="8100"'
    replacement_text = '<o t="1" x="14" y="8" r="1" size="22500000" m="8509"'

    file_contents = Load_File('x3_universe.xml')
    #Verify the original_block is present (matches succesfully).
    if not file_contents.text.count(original_text) == 1:
        print('Skipped {}, format of source not as expected from XRM.'.__name__)
        return
    file_contents.text = file_contents.text.replace(original_text, replacement_text)

    #When a save already has the wrong music, apply a patch.
    if apply_to_existing_save:
        #Lay out the body of the director command.
        #This is packed into a do_all block.
        #XRMINST.xml does this as well, and can be used as a reference maybe.
        #The director manual says only x,y needed, which is good since the hub
        # sector name is unclear.
        text = (r'<alter_sector x="14" y="8" music="8509"/>')
        #Make the file.
        Make_Director_Shell(queue_name, text)
    else:
        #TODO: delete the file made above, if it exists.
        pass

    
def Parse_universe_line(line):
    '''
    Parse a line from the universe file.
    Returns a dict, keyed by field name; values are raw text, typically integers.
    '''
    #Convert the different fields into a dict.
    field_dict = {}

    #Line format is similar to (with some fields removed): 
    # <o t="1" x="14" y="10" r="18" size="15000000" m="0" p="-1">
    #Remove the '<o' and '>', and the quotes.
    line = line.replace('<o','').replace('>','').replace('"','')

    #Loop over the entries in the line by splitting on spaces.
    for entry in line.split():
        #Split on the '='.
        entry_split = entry.split('=')
        #The left side is the entry name, right side is value.
        field_dict[entry_split[0]] = entry_split[1]

    return field_dict


def Make_Director_Shell(queue_name, body_text = None, _cleanup = False):
    '''
    Support function to make a director shell file, setting up a queue
    with the given body text.
    Optionally, delete any old file previously generated.
    '''
    #Get the path to the file to generate.
    file_path = os.path.join('Director',queue_name + '.xml')
    #If in cleanup mode, check for the file and delete it if found.
    if _cleanup:
        if os.path.exists(file_path):
            os.remove(file_path)
        return

    #Copied shell text from a patch script that cleared invulnerable station flags.
    #This will make the queue name and text body replaceable.
    #Since the shell text naturally has {} in it, don't use format here, just
    # use replace.
    shell_text = r'''<?xml version="1.0" encoding="ISO-8859-1" ?>
<?xml-stylesheet href="director.xsl" type="text/xsl" ?>
<director name="template" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="director.xsd">
    <documentation>
    <author name="X3_Customizer" alias="..." contact="..." />
    <content reference="X3_Customizer" name="X3_Customizer generated" description="Director command injector." />
    <version number="0.0" date="today" status="testing" />
    </documentation>
    <cues>
    <cue name="INSERT_QUEUE_NAME" check="cancel">
        <condition>
        <check_value value="{player.age}" min="10s"/>
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
'''.replace('INSERT_QUEUE_NAME', queue_name).replace('INSERT_BODY', body_text)

    #Path to the director folder and write the file, with this queue name.
    #Working directory should alrady be the addon directory, so dig down 1 folder.
    with open(file_path, 'w') as file:
        file.write(shell_text)



def Get_Aldrin_rock_texts():
    #Texts taken from XRM (called original) and TC plots for AP (called replacement).
    #Replacement text includes the 'SS_SPECIAL_ASTEROIDMOON', but the entire block is included
    # since all of the rocks and factories around the Aldrin rock need position adjustments
    # as well.
    original_text = '''		<o t="2" s="0" neb="0" stars="0"/>
		<o t="3" s="7" x="177236584" y="-1088110584" z="-1012326949" color="1973775"/>
		<o t="3" s="41" x="516165787" y="1281056167" z="-122990315" color="1320995"/>
		<o f="1" t="17" s="0" x="-101029641" y="5473381" z="-36966126" atype="1" aamount="20" a="5963" b="52347" g="63413"/>
		<o f="1" t="17" s="2" x="49402092" y="13060905" z="49681848" atype="0" aamount="34" a="5294" b="64917" g="1323"/>
		<o f="1" t="17" s="1" x="47576748" y="21281229" z="35373017" atype="0" aamount="12" a="58133" b="56612" g="61706"/>
		<o f="1" t="17" s="1" x="-91500504" y="18797904" z="133178520" atype="1" aamount="40" a="8995" b="56852" g="28889"/>
		<o f="1" t="17" s="2" x="-131889930" y="-7504261" z="10960647" atype="1" aamount="32" a="10060" b="1784" g="32938"/>
		<o f="1" t="17" s="1" x="-2016732" y="-2091227" z="76471900" atype="1" aamount="26" a="62173" b="63997" g="34243"/>
		<o f="1" t="17" s="2" x="9921306" y="22723836" z="10872210" atype="0" aamount="24" a="45679" b="55363" g="28917"/>
		<o f="1" t="17" s="0" x="-24010179" y="1712048" z="-34365000" atype="0" aamount="24" a="57859" b="12260" g="64336"/>
		<o f="1" t="17" s="2" x="-144166662" y="-28228233" z="26484507" atype="1" aamount="50" a="24479" b="11813" g="65143"/>
		<o f="1" t="17" s="2" x="-18740760" y="-21016273" z="-16287762" atype="0" aamount="58" a="37123" b="53601" g="34625"/>
		<o f="1" t="17" s="1" x="363597" y="-1796680" z="43882794" atype="0" aamount="18" a="57850" b="60429" g="6512"/>
		<o f="1" t="17" s="0" x="-86316960" y="17840679" z="-4320636" atype="0" aamount="28" a="4189" b="8997" g="31805"/>
		<o f="1" t="17" s="2" x="-15759358" y="-15418522" z="-24654184" atype="0" aamount="52" a="33432" b="62129" g="4756"/>
		<o f="1" t="17" s="0" x="-65047083" y="-22859014" z="-43703580" atype="0" aamount="54" a="65500" b="55278" g="31620"/>
		<o f="1" t="17" s="0" x="-93706944" y="1773342" z="92168121" atype="0" aamount="48" a="32539" b="62056" g="683"/>
		<o f="1" t="17" s="0" x="-3240759" y="-6300813" z="-36928350" atype="0" aamount="10" a="20289" b="12417" g="33090"/>
		<o f="1" t="17" s="2" x="-65571679" y="18140595" z="122030988" atype="1" aamount="32" a="64749" b="63599" g="5468"/>
		<o f="1" t="17" s="2" x="-132565926" y="1568757" z="66323481" atype="0" aamount="24" a="44082" b="54220" g="29889"/>
		<o f="1" t="17" s="0" x="-151029222" y="5215046" z="-12313104" atype="0" aamount="28" a="64697" b="2788" g="32103"/>
		<o f="1" t="17" s="2" x="-67680684" y="-13189182" z="-46200468" atype="0" aamount="22" a="53192" b="53654" g="36535"/>
		<o f="1" t="17" s="1" x="15162150" y="-1032852" z="20584020" atype="1" aamount="4" a="29637" b="59551" g="32553"/>
		<o f="1" t="17" s="2" x="-77019925" y="-16917427" z="138862944" atype="1" aamount="30" a="3254" b="4308" g="62436"/>
		<o f="1" t="17" s="1" x="-43725858" y="13403106" z="-32788053" atype="0" aamount="26" a="62837" b="51557" g="4641"/>
		<o f="1" t="17" s="2" x="-102192537" y="-16059422" z="103581960" atype="1" aamount="48" a="65161" b="64118" g="60859"/>
		<o f="1" t="17" s="0" x="-143070126" y="5406839" z="95633415" atype="0" aamount="38" a="19512" b="51786" g="496"/>
		<o f="1" t="17" s="2" x="-163223304" y="9489514" z="39429240" atype="1" aamount="52" a="33926" b="61431" g="3595"/>
		<o f="1" t="17" s="0" x="-144739950" y="-22442803" z="77047638" atype="0" aamount="24" a="21917" b="64511" g="33010"/>
		<o f="1" t="17" s="2" x="-142302372" y="16069151" z="38888487" atype="0" aamount="6" a="28995" b="5803" g="3230"/>
		<o f="1" t="17" s="0" x="-58521168" y="-19081629" z="-28091720" atype="0" aamount="10" a="65515" b="223" g="32120"/>
		<o f="1" t="17" s="0" x="-42958437" y="1703019" z="104237412" atype="0" aamount="8" a="60364" b="8437" g="31982"/>
		<o f="1" t="17" s="2" x="15856998" y="-15364245" z="53771856" atype="0" aamount="30" a="6358" b="3091" g="31537"/>
		<o f="1" t="17" s="2" x="-115084404" y="-23856942" z="-42317544" atype="0" aamount="18" a="2933" b="9706" g="62191"/>
		<o f="1" t="17" s="2" x="-66044960" y="27762261" z="46025499" atype="1" aamount="36" a="64072" b="62655" g="63385"/>
		<o f="1" t="17" s="2" x="41763912" y="-18690231" z="57975192" atype="1" aamount="50" a="49063" b="52617" g="24756"/>
		<o f="1" t="17" s="2" x="-166761540" y="19023634" z="29996331" atype="0" aamount="32" a="52726" b="57188" g="3136"/>
		<o f="1" t="17" s="2" x="8503860" y="-16765218" z="111202494" atype="0" aamount="48" a="64893" b="63279" g="4485"/>
		<o f="1" t="17" s="2" x="-36165166" y="5502516" z="-41314992" atype="0" aamount="32" a="37177" b="55027" g="2605"/>
		<o f="1" t="17" s="2" x="-838854" y="-9584743" z="63066195" atype="0" aamount="40" a="6958" b="35" g="64591"/>
		<o f="1" t="17" s="1" x="-54029427" y="-20905335" z="-46059900" atype="1" aamount="2" a="60011" b="4947" g="25891"/>
		<o f="1" t="17" s="2" x="-58150338" y="-19514417" z="-26214720" atype="0" aamount="18" a="32507" b="64821" g="37045"/>
		<o f="1" t="17" s="0" x="-136334208" y="-9720715" z="-16142526" atype="1" aamount="52" a="46626" b="2993" g="267"/>
		<o f="1" t="17" s="0" x="-154863264" y="-2076359" z="46943587" atype="0" aamount="30" a="58179" b="8335" g="64895"/>
		<o f="1" t="17" s="1" x="-118228092" y="14621073" z="87301875" atype="1" aamount="40" a="24560" b="59142" g="27483"/>
		<o f="1" t="17" s="2" x="-124629384" y="10918091" z="-30187860" atype="0" aamount="52" a="2572" b="7126" g="6748"/>
		<o f="1" t="17" s="0" x="-5443134" y="-2514652" z="103102962" atype="0" aamount="2" a="37220" b="58816" g="33547"/>
		<o f="1" t="17" s="2" x="-84132795" y="14377935" z="-49916316" atype="1" aamount="46" a="128" b="2428" g="3456"/>
		<o f="1" t="17" s="2" x="-29847612" y="-24215986" z="129650520" atype="0" aamount="56" a="12719" b="12393" g="4477"/>
		<o f="1" t="17" s="0" x="-120912744" y="26261502" z="2316690" atype="0" aamount="16" a="30596" b="58245" g="811"/>
		<o f="1" t="17" s="0" x="-136449936" y="-4961296" z="60509964" atype="0" aamount="14" a="24626" b="59523" g="33246"/>
		<o f="1" t="17" s="2" x="-123800634" y="10948001" z="83468931" atype="1" aamount="18" a="41575" b="622" g="33397"/>
		<o f="1" t="17" s="2" x="4665528" y="-3079228" z="94344240" atype="0" aamount="38" a="30144" b="7960" g="3997"/>
		<o f="1" t="17" s="2" x="-26720796" y="382797" z="-47093016" atype="0" aamount="16" a="5222" b="10527" g="8803"/>
		<o f="1" t="17" s="2" x="-99328836" y="5872515" z="-38003916" atype="1" aamount="12" a="28561" b="11685" g="34689"/>
		<o f="1" t="17" s="2" x="-44870916" y="2113581" z="27364143" atype="0" aamount="58" a="63677" b="58477" g="63238"/>
		<o f="1" t="17" s="1" x="-56642532" y="12912987" z="73642593" atype="0" aamount="20" a="27976" b="9460" g="2862"/>
		<o f="1" t="17" s="0" x="-133192896" y="5693140" z="25649757" atype="0" aamount="34" a="34139" b="997" g="657"/>
		<o f="1" t="17" s="1" x="-100108536" y="-5985602" z="-49296306" atype="0" aamount="22" a="17421" b="62087" g="4824"/>
		<o f="1" t="17" s="2" x="-38055996" y="-17123301" z="56640912" atype="0" aamount="32" a="7906" b="12514" g="11437"/>
		<o f="1" t="17" s="2" x="39265500" y="-5492189" z="32424793" atype="0" aamount="18" a="8563" b="3051" g="1120"/>
		<o f="1" t="17" s="2" x="-14886699" y="-11479764" z="-34750116" atype="1" aamount="12" a="63991" b="60685" g="6234"/>
		<o f="1" t="17" s="0" x="-127623936" y="9386501" z="100256646" atype="0" aamount="44" a="45592" b="8584" g="33260"/>
		<o f="1" t="17" s="1" x="-15133836" y="-13236175" z="-35941194" atype="0" aamount="34" a="39167" b="7646" g="3736"/>
		<o f="1" t="17" s="2" x="20557014" y="-2055918" z="5856189" atype="0" aamount="28" a="26770" b="59956" g="31659"/>
		<o f="1" t="17" s="0" x="-50990983" y="14011102" z="129254586" atype="0" aamount="50" a="6958" b="8502" g="31957"/>
		<o f="1" t="17" s="1" x="-159315468" y="-1720863" z="9280782" atype="0" aamount="26" a="32643" b="59053" g="4419"/>
		<o f="1" t="17" s="0" x="10666428" y="22615326" z="10196514" atype="1" aamount="50" a="47536" b="12793" g="33486"/>
		<o f="1" t="17" s="2" x="-18470388" y="-994269" z="91910088" atype="1" aamount="4" a="38607" b="5588" g="31654"/>
		<o f="1" t="17" s="2" x="-69408060" y="-11866302" z="-3945420" atype="0" aamount="20" a="1589" b="6750" g="6286"/>
		<o f="1" t="17" s="2" x="-52348534" y="26411842" z="44872956" atype="1" aamount="36" a="45441" b="56914" g="29468"/>
		<o f="1" t="17" s="2" x="-16102932" y="-5192737" z="16921632" atype="0" aamount="6" a="57389" b="667" g="756"/>
		<o f="1" t="17" s="2" x="-56951274" y="-9018908" z="62664621" atype="1" aamount="40" a="64140" b="3321" g="3657"/>
		<o f="1" t="17" s="2" x="-112948314" y="6903471" z="28936674" atype="1" aamount="12" a="2463" b="4559" g="61746"/>
		<o f="1" t="17" s="2" x="-114689155" y="4371104" z="44516400" atype="1" aamount="2" a="2341" b="11907" g="6941"/>
		<o f="1" t="17" s="2" x="-108225624" y="-9872" z="69027757" atype="1" aamount="50" a="65337" b="2242" g="2788"/>
		<o f="1" t="17" s="1" x="-2666508" y="18705956" z="25117416" atype="0" aamount="26" a="57710" b="14055" g="56800"/>
		<o f="1" t="17" s="2" x="-90926100" y="-17655273" z="74753349" atype="1" aamount="14" a="27603" b="12555" g="1041"/>
		<o f="1" t="17" s="0" x="-54204768" y="-6478685" z="23556600" atype="0" aamount="40" a="419" b="9748" g="31663"/>
		<o f="1" t="17" s="2" x="-57896292" y="4507246" z="52960602" atype="0" aamount="10" a="1671" b="6580" g="63277"/>
		<o f="1" t="17" s="0" x="13534194" y="-22886723" z="102745560" atype="0" aamount="40" a="17138" b="55066" g="65409"/>
		<o f="1" t="17" s="0" x="16642296" y="-22732731" z="-18938262" atype="0" aamount="2" a="20961" b="302" g="182"/>
		<o f="1" t="17" s="2" x="-63668532" y="16245601" z="9456540" atype="0" aamount="28" a="2360" b="6627" g="6528"/>
		<o f="1" t="17" s="0" x="-27482184" y="2682431" z="96842394" atype="1" aamount="54" a="16037" b="13404" g="32415"/>
		<o f="1" t="17" s="2" x="-89210115" y="20746821" z="106157208" atype="0" aamount="40" a="27231" b="10150" g="34811"/>
		<o f="1" t="17" s="1" x="-76870327" y="-18833474" z="122119146" atype="0" aamount="28" a="22201" b="52564" g="29407"/>
		<o f="1" t="17" s="2" x="18430458" y="27633531" z="-25836258" atype="1" aamount="2" a="43087" b="62792" g="32307"/>
		<o f="1" t="17" s="0" x="17709036" y="5570570" z="18772044" atype="0" aamount="24" a="36185" b="2176" g="33428"/>
		<o f="1" t="17" s="0" x="4077816" y="-2625531" z="-1542645" atype="1" aamount="18" a="20135" b="56363" g="32998"/>
		<o f="1" t="17" s="0" x="18420204" y="-1221959" z="-573945" atype="0" aamount="44" a="47759" b="60657" g="32968"/>
		<o f="1" t="17" s="2" x="-31340442" y="11095413" z="126171372" atype="0" aamount="44" a="2336" b="64644" g="31656"/>
		<o f="1" t="17" s="2" x="-115350675" y="11823978" z="92293933" atype="0" aamount="46" a="64268" b="62283" g="60678"/>
		<o f="1" t="17" s="2" x="22423656" y="16740738" z="55584880" atype="1" aamount="10" a="54381" b="52088" g="3540"/>
		<o f="1" t="17" s="1" x="-49024804" y="-19177128" z="14963730" atype="1" aamount="28" a="56043" b="56270" g="5349"/>
		<o f="1" t="17" s="0" x="-103833744" y="-23616877" z="-23273088" atype="0" aamount="16" a="30322" b="63171" g="623"/>
		<o f="1" t="17" s="2" x="37351854" y="-13381971" z="50850372" atype="0" aamount="20" a="31838" b="2853" g="36559"/>
		<o f="1" t="17" s="0" x="-3837072" y="3838869" z="-28992018" atype="0" aamount="26" a="22805" b="61546" g="320"/>
		<o f="1" t="17" s="2" x="-162723444" y="-9710757" z="66952789" atype="0" aamount="52" a="33870" b="60883" g="4231"/>
		<o f="1" t="17" s="0" x="-114308055" y="14581976" z="15698778" atype="0" aamount="12" a="51098" b="7848" g="32732"/>
		<o f="1" t="17" s="2" x="-65964744" y="-5820171" z="-12718248" atype="0" aamount="46" a="9954" b="13755" g="2942"/>
		<o t="16" s="SS_WARE_CREDITS" x="-32596514" y="19069964" z="-29340637" n="200000"/>
		<o t="6" s="SS_FAC_LC_3" x="26051569" y="-7230254" z="51764296" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_2" x="-51685854" y="0" z="-36389802" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_5" x="27395904" y="-12815395" z="31965876" r="18" a="32768" b="0" g="0">
		</o>
		<o f="1" t="6" s="SS_FAC_LC_6" x="-37676429" y="3516017" z="-3042315" r="18" a="-7168" b="-10240" g="11264">
		</o>
		<o t="6" s="SS_FAC_LC_4" x="-81193750" y="-1135626" z="-24143813" r="18" a="22528" b="-7168" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_1" x="-37006578" y="-14802631" z="117927631" r="18" a="32768" b="0" g="11264">
		</o>
		<o f="1" t="6" s="SS_FAC_LC_5" x="-213440" y="-392506" z="-10484151" r="18" a="32768" b="0" g="0">
		</o>
		<o f="1" t="6" s="SS_FAC_LC_5" x="-110094478" y="2675238" z="-7628755" r="18" a="32768" b="0" g="0">
		</o>
		<o f="1" t="6" s="SS_FAC_LC_7" x="-153780622" y="-11294344" z="22367895" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_4" x="-138682198" y="-2826749" z="-774921" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_2" x="-62935854" y="0" z="124860198" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_5" x="-125489308" y="11250000" z="47245067" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_3" x="-25030920" y="-7401315" z="40026644" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_5" x="-26291596" y="2184604" z="75028376" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_3" x="-4465461" y="6717200" z="94059543" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_4" x="-118693750" y="-1135626" z="93981186" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_7" x="-87810197" y="0" z="53412828" r="18" a="32768" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_6" x="-118939144" y="-1875000" z="124749177" r="18" a="-9216" b="0" g="0">
		</o>
		<o t="6" s="SS_FAC_LC_1" x="-24054276" y="9868420" z="-30345394" r="18" a="32768" b="0" g="11264">
		</o>
		<o t="5" s="SS_DOCK_LC_2" x="-63575329" y="-19101216" z="91949013" r="18" a="3072" b="-4096" g="7168">
		</o>
		<o t="5" s="SS_DOCK_LC_1" x="27594573" y="2757337" z="78688322" r="18" a="32768" b="0" g="0">
		</o>
		<o t="5" s="SS_DOCK_LC_5" x="-86612829" y="1523784" z="22536513" r="18" a="9216" b="-11264" g="7168">
		</o>'''

    replacement_text = '''		<o t="2" s="0" neb="0" stars="0"/>
		<o t="3" s="7" x="177236584" y="-1088110584" z="-1012326949" color="1973775"/>
		<o t="3" s="41" x="516165787" y="1281056167" z="-122990315" color="1320995"/>
		<o f="1" t="17" s="2" x="8503860" y="-16765218" z="111202494" atype="0" aamount="48" a="64893" b="63279" g="4485"/>
		<o f="1" t="17" s="0" x="-50990983" y="14011102" z="129254586" atype="0" aamount="50" a="6958" b="8502" g="31957"/>
		<o f="1" t="17" s="2" x="-131889930" y="-7504261" z="10960647" atype="1" aamount="32" a="10060" b="1784" g="32938"/>
		<o f="1" t="17" s="2" x="13404612" y="-994269" z="99410088" atype="1" aamount="4" a="38607" b="5588" g="31654"/>
		<o f="1" t="17" s="2" x="9921306" y="22723836" z="10872210" atype="0" aamount="24" a="45679" b="55363" g="28917"/>
		<o f="1" t="17" s="0" x="-136449936" y="-4961296" z="60509964" atype="0" aamount="14" a="24626" b="59523" g="33246"/>
		<o f="1" t="17" s="2" x="-132565926" y="1568757" z="66323481" atype="0" aamount="24" a="44082" b="54220" g="29889"/>
		<o f="1" t="17" s="1" x="-91500504" y="18797904" z="133178520" atype="1" aamount="40" a="8995" b="56852" g="28889"/>
		<o f="1" t="17" s="0" x="-58521168" y="-19081629" z="-28091720" atype="0" aamount="10" a="65515" b="223" g="32120"/>
		<o f="1" t="17" s="2" x="-123800634" y="10948001" z="83468931" atype="1" aamount="18" a="41575" b="622" g="33397"/>
		<o f="1" t="17" s="2" x="4665528" y="-3079228" z="94344240" atype="0" aamount="38" a="30144" b="7960" g="3997"/>
		<o f="1" t="17" s="2" x="15856998" y="-15364245" z="53771856" atype="0" aamount="30" a="6358" b="3091" g="31537"/>
		<o f="1" t="17" s="0" x="4077816" y="-2625531" z="-1542645" atype="1" aamount="18" a="20135" b="56363" g="32998"/>
		<o f="1" t="17" s="1" x="-54029427" y="-20905335" z="-46059900" atype="1" aamount="2" a="60011" b="4947" g="25891"/>
		<o f="1" t="17" s="2" x="-162723444" y="-9710757" z="66952789" atype="0" aamount="52" a="33870" b="60883" g="4231"/>
		<o f="1" t="17" s="0" x="-71083437" y="1703019" z="124862412" atype="0" aamount="8" a="60364" b="8437" g="31982"/>
		<o f="1" t="17" s="2" x="6798726" y="-9018908" z="96414621" atype="1" aamount="40" a="64140" b="3321" g="3657"/>
		<o f="1" t="17" s="2" x="41763912" y="-18690231" z="57975192" atype="1" aamount="50" a="49063" b="52617" g="24756"/>
		<o f="1" t="17" s="1" x="-168891732" y="-2091227" z="44596900" atype="1" aamount="26" a="62173" b="63997" g="34243"/>
		<o f="1" t="17" s="0" x="-82329768" y="-6478685" z="147306600" atype="0" aamount="40" a="419" b="9748" g="31663"/>
		<o f="1" t="17" s="2" x="-14886699" y="-11479764" z="-34750116" atype="1" aamount="12" a="63991" b="60685" g="6234"/>
		<o f="1" t="17" s="2" x="-163223304" y="9489514" z="39429240" atype="1" aamount="52" a="33926" b="61431" g="3595"/>
		<o f="1" t="17" s="2" x="-142302372" y="16069151" z="38888487" atype="0" aamount="6" a="28995" b="5803" g="3230"/>
		<o f="1" t="17" s="0" x="-124114950" y="-22442803" z="80797638" atype="0" aamount="24" a="21917" b="64511" g="33010"/>
		<o f="1" t="17" s="2" x="-77019925" y="-16917427" z="138862944" atype="1" aamount="30" a="3254" b="4308" g="62436"/>
		<o f="1" t="17" s="1" x="-100108536" y="-5985602" z="-49296306" atype="0" aamount="22" a="17421" b="62087" g="4824"/>
		<o f="1" t="17" s="0" x="25017816" y="2682431" z="113717394" atype="1" aamount="54" a="16037" b="13404" g="32415"/>
		<o f="1" t="17" s="1" x="47576748" y="21281229" z="35373017" atype="0" aamount="12" a="58133" b="56612" g="61706"/>
		<o f="1" t="17" s="2" x="-14210115" y="20746821" z="-55092792" atype="0" aamount="40" a="27231" b="10150" g="34811"/>
		<o f="1" t="17" s="2" x="-93668532" y="16245601" z="-41168460" atype="0" aamount="28" a="2360" b="6627" g="6528"/>
		<o f="1" t="17" s="2" x="37351854" y="-13381971" z="50850372" atype="0" aamount="20" a="31838" b="2853" g="36559"/>
		<o f="1" t="17" s="0" x="-3837072" y="3838869" z="-28992018" atype="0" aamount="26" a="22805" b="61546" g="320"/>
		<o f="1" t="17" s="0" x="-12615759" y="-6300813" z="-36928350" atype="0" aamount="10" a="20289" b="12417" g="33090"/>
		<o f="1" t="17" s="2" x="19698900" y="-17655273" z="61628349" atype="1" aamount="14" a="27603" b="12555" g="1041"/>
		<o f="1" t="17" s="2" x="-150879384" y="10918091" z="-7687860" atype="0" aamount="52" a="2572" b="7126" g="6748"/>
		<o f="1" t="17" s="0" x="17709036" y="5570570" z="18772044" atype="0" aamount="24" a="36185" b="2176" g="33428"/>
		<o f="1" t="17" s="1" x="-118228092" y="14621073" z="87301875" atype="1" aamount="40" a="24560" b="59142" g="27483"/>
		<o f="1" t="17" s="1" x="-43725858" y="13403106" z="-32788053" atype="0" aamount="26" a="62837" b="51557" g="4641"/>
		<o f="1" t="17" s="2" x="-7839744" y="-5820171" z="-12718248" atype="0" aamount="46" a="9954" b="13755" g="2942"/>
		<o f="1" t="17" s="0" x="16642296" y="-22732731" z="-18938262" atype="0" aamount="2" a="20961" b="302" g="182"/>
		<o f="1" t="17" s="2" x="-58150338" y="-19514417" z="-26214720" atype="0" aamount="18" a="32507" b="64821" g="37045"/>
		<o f="1" t="17" s="2" x="-15759358" y="-15418522" z="-24654184" atype="0" aamount="52" a="33432" b="62129" g="4756"/>
		<o f="1" t="17" s="0" x="-101029641" y="5473381" z="-36966126" atype="1" aamount="20" a="5963" b="52347" g="63413"/>
		<o f="1" t="17" s="2" x="-152430996" y="-17123301" z="-8984088" atype="0" aamount="32" a="7906" b="12514" g="11437"/>
		<o f="1" t="17" s="2" x="-109198314" y="6903471" z="-23563326" atype="1" aamount="12" a="2463" b="4559" g="61746"/>
		<o f="1" t="17" s="2" x="-84132795" y="14377935" z="-49916316" atype="1" aamount="46" a="128" b="2428" g="3456"/>
		<o f="1" t="17" s="0" x="-151029222" y="5215046" z="-12313104" atype="0" aamount="28" a="64697" b="2788" g="32103"/>
		<o f="1" t="17" s="2" x="-42973534" y="26411842" z="131122956" atype="1" aamount="36" a="45441" b="56914" g="29468"/>
		<o f="1" t="17" s="2" x="-130725624" y="-9872" z="57777757" atype="1" aamount="50" a="65337" b="2242" g="2788"/>
		<o f="1" t="17" s="0" x="-95558055" y="14581976" z="-34926222" atype="0" aamount="12" a="51098" b="7848" g="32732"/>
		<o f="1" t="17" s="2" x="-34064155" y="4371104" z="-37983600" atype="1" aamount="2" a="2341" b="11907" g="6941"/>
		<o f="1" t="17" s="0" x="-136334208" y="-9720715" z="-16142526" atype="1" aamount="52" a="46626" b="2993" g="267"/>
		<o f="1" t="17" s="2" x="-36165166" y="5502516" z="-41314992" atype="0" aamount="32" a="37177" b="55027" g="2605"/>
		<o f="1" t="17" s="1" x="-6416508" y="18705956" z="116992416" atype="0" aamount="26" a="57710" b="14055" g="56800"/>
		<o f="1" t="17" s="1" x="-69649804" y="-19177128" z="-41286270" atype="1" aamount="28" a="56043" b="56270" g="5349"/>
		<o f="1" t="17" s="1" x="-76870327" y="-18833474" z="122119146" atype="0" aamount="28" a="22201" b="52564" g="29407"/>
		<o f="1" t="17" s="2" x="39265500" y="-5492189" z="32424793" atype="0" aamount="18" a="8563" b="3051" g="1120"/>
		<o f="1" t="17" s="2" x="-67680684" y="-13189182" z="-46200468" atype="0" aamount="22" a="53192" b="53654" g="36535"/>
		<o f="1" t="17" s="0" x="-157566960" y="17840679" z="-15570636" atype="0" aamount="28" a="4189" b="8997" g="31805"/>
		<o f="1" t="17" s="1" x="-24011403" y="-1796680" z="-29242206" atype="0" aamount="18" a="57850" b="60429" g="6512"/>
		<o f="1" t="17" s="2" x="-144166662" y="-28228233" z="26484507" atype="1" aamount="50" a="24479" b="11813" g="65143"/>
		<o f="1" t="17" s="2" x="-133158060" y="-11866302" z="-18945420" atype="0" aamount="20" a="1589" b="6750" g="6286"/>
		<o f="1" t="17" s="2" x="49402092" y="13060905" z="49681848" atype="0" aamount="34" a="5294" b="64917" g="1323"/>
		<o f="1" t="17" s="2" x="30772068" y="-5192737" z="-11203368" atype="0" aamount="6" a="57389" b="667" g="756"/>
		<o f="1" t="17" s="2" x="-115350675" y="11823978" z="92293933" atype="0" aamount="46" a="64268" b="62283" g="60678"/>
		<o f="1" t="17" s="0" x="18420204" y="-1221959" z="-573945" atype="0" aamount="44" a="47759" b="60657" g="32968"/>
		<o f="1" t="17" s="2" x="-102192537" y="-16059422" z="103581960" atype="1" aamount="48" a="65161" b="64118" g="60859"/>
		<o f="1" t="17" s="2" x="9504084" y="2113581" z="8614143" atype="0" aamount="58" a="63677" b="58477" g="63238"/>
		<o f="1" t="17" s="0" x="-133192896" y="5693140" z="25649757" atype="0" aamount="34" a="34139" b="997" g="657"/>
		<o f="1" t="17" s="0" x="-120912744" y="26261502" z="2316690" atype="0" aamount="16" a="30596" b="58245" g="811"/>
		<o f="1" t="17" s="2" x="-31340442" y="11095413" z="126171372" atype="0" aamount="44" a="2336" b="64644" g="31656"/>
		<o f="1" t="17" s="1" x="-131642532" y="12912987" z="73642593" atype="0" aamount="20" a="27976" b="9460" g="2862"/>
		<o f="1" t="17" s="1" x="-159315468" y="-1720863" z="9280782" atype="0" aamount="26" a="32643" b="59053" g="4419"/>
		<o f="1" t="17" s="0" x="-65047083" y="-22859014" z="-43703580" atype="0" aamount="54" a="65500" b="55278" g="31620"/>
		<o f="1" t="17" s="0" x="-103833744" y="-23616877" z="-23273088" atype="0" aamount="16" a="30322" b="63171" g="623"/>
		<o f="1" t="17" s="2" x="-29847612" y="-24215986" z="129650520" atype="0" aamount="56" a="12719" b="12393" g="4477"/>
		<o f="1" t="17" s="2" x="17911146" y="-9584743" z="63066195" atype="0" aamount="40" a="6958" b="35" g="64591"/>
		<o f="1" t="17" s="0" x="13534194" y="-22886723" z="102745560" atype="0" aamount="40" a="17138" b="55066" g="65409"/>
		<o f="1" t="17" s="2" x="22423656" y="16740738" z="55584880" atype="1" aamount="10" a="54381" b="52088" g="3540"/>
		<o f="1" t="17" s="0" x="-24010179" y="1712048" z="-34365000" atype="0" aamount="24" a="57859" b="12260" g="64336"/>
		<o f="1" t="17" s="2" x="-18740760" y="-21016273" z="-16287762" atype="0" aamount="58" a="37123" b="53601" g="34625"/>
		<o f="1" t="17" s="2" x="18430458" y="27633531" z="-25836258" atype="1" aamount="2" a="43087" b="62792" g="32307"/>
		<o f="1" t="17" s="0" x="-5443134" y="-2514652" z="103102962" atype="0" aamount="2" a="37220" b="58816" g="33547"/>
		<o f="1" t="17" s="0" x="-170581944" y="1773342" z="49043121" atype="0" aamount="48" a="32539" b="62056" g="683"/>
		<o f="1" t="17" s="2" x="-99328836" y="5872515" z="-38003916" atype="1" aamount="12" a="28561" b="11685" g="34689"/>
		<o f="1" t="17" s="0" x="-154863264" y="-2076359" z="46943587" atype="0" aamount="30" a="58179" b="8335" g="64895"/>
		<o f="1" t="17" s="1" x="15162150" y="-1032852" z="20584020" atype="1" aamount="4" a="29637" b="59551" g="32553"/>
		<o f="1" t="17" s="2" x="-162896292" y="4507246" z="36085602" atype="0" aamount="10" a="1671" b="6580" g="63277"/>
		<o f="1" t="17" s="0" x="10666428" y="22615326" z="10196514" atype="1" aamount="50" a="47536" b="12793" g="33486"/>
		<o f="1" t="17" s="2" x="-115084404" y="-23856942" z="-42317544" atype="0" aamount="18" a="2933" b="9706" g="62191"/>
		<o f="1" t="17" s="2" x="-65571679" y="18140595" z="122030988" atype="1" aamount="32" a="64749" b="63599" g="5468"/>
		<o f="1" t="17" s="2" x="-26720796" y="382797" z="-47093016" atype="0" aamount="16" a="5222" b="10527" g="8803"/>
		<o f="1" t="17" s="2" x="-166761540" y="19023634" z="29996331" atype="0" aamount="32" a="52726" b="57188" g="3136"/>
		<o f="1" t="17" s="0" x="-127623936" y="9386501" z="100256646" atype="0" aamount="44" a="45592" b="8584" g="33260"/>
		<o f="1" t="17" s="2" x="-2294960" y="27762261" z="-27099501" atype="1" aamount="36" a="64072" b="62655" g="63385"/>
		<o f="1" t="17" s="0" x="-143070126" y="5406839" z="95633415" atype="0" aamount="38" a="19512" b="51786" g="496"/>
		<o f="1" t="17" s="1" x="-15133836" y="-13236175" z="-35941194" atype="0" aamount="34" a="39167" b="7646" g="3736"/>
		<o f="1" t="17" s="2" x="20557014" y="-2055918" z="5856189" atype="0" aamount="28" a="26770" b="59956" g="31659"/>
		<o t="16" s="SS_WARE_CREDITS" x="-32596514" y="19069964" z="-29340637" n="20000"/>
		<o f="1" t="28" s="0" x="-150905672" y="-9195159" z="-25448768" atype="0" aamount="58" a="35018" b="3899" g="59511"/>
		<o f="1" t="28" s="0" x="-195123584" y="6973988" z="88822440" atype="0" aamount="46" a="21030" b="9666" g="59562"/>
		<o f="1" t="28" s="0" x="-8522568" y="-7475690" z="135832680" atype="1" aamount="6" a="59199" b="59078" g="6196"/>
		<o f="1" t="28" s="4" x="-101179296" y="-8812857" z="-37280624" atype="0" aamount="20" a="12760" b="9251" g="33158"/>
		<o f="1" t="28" s="4" x="23244072" y="-12537696" z="-42455704" atype="0" aamount="30" a="50468" b="60506" g="30983"/>
		<o f="1" t="28" s="0" x="-89552285" y="-2696264" z="-25190488" atype="1" aamount="22" a="19473" b="1275" g="65271"/>
		<o f="1" t="28" s="0" x="63384944" y="2144390" z="89265372" atype="0" aamount="44" a="51194" b="4572" g="64874"/>
		<o f="1" t="28" s="4" x="-90666453" y="-14388568" z="-48068936" atype="0" aamount="30" a="47959" b="6094" g="63473"/>
		<o f="1" t="28" s="0" x="1994520" y="2661611" z="-20002880" atype="0" aamount="30" a="29256" b="55802" g="60321"/>
		<o f="1" t="28" s="0" x="47155656" y="-8324387" z="38866094" atype="0" aamount="58" a="14788" b="10792" g="10255"/>
		<o f="1" t="28" s="0" x="-3772184" y="-22936080" z="-42043016" atype="0" aamount="28" a="24163" b="9299" g="56376"/>
		<o f="1" t="28" s="0" x="-188934096" y="7304944" z="-23866456" atype="0" aamount="28" a="723" b="6872" g="6246"/>
		<o f="1" t="28" s="0" x="-171573296" y="-2677382" z="71229620" atype="0" aamount="20" a="37572" b="6921" g="59389"/>
		<o f="1" t="28" s="0" x="25757872" y="11205398" z="8074772" atype="0" aamount="6" a="51159" b="53570" g="4805"/>
		<o f="1" t="28" s="0" x="-188616664" y="6914288" z="14726148" atype="0" aamount="24" a="5586" b="51589" g="8973"/>
		<o f="1" t="28" s="0" x="-66621176" y="2452797" z="-41868800" atype="1" aamount="60" a="35930" b="6064" g="26370"/>
		<o f="1" t="28" s="4" x="-151930072" y="4652976" z="-9686582" atype="0" aamount="34" a="17334" b="57033" g="37248"/>
		<o f="1" t="28" s="0" x="-213271888" y="6497812" z="43165512" atype="0" aamount="6" a="47911" b="52597" g="10186"/>
		<o f="1" t="28" s="0" x="-37077952" y="-6296377" z="-32994168" atype="1" aamount="26" a="39565" b="6363" g="60227"/>
		<o f="1" t="28" s="4" x="-3830440" y="-3346607" z="141569296" atype="1" aamount="30" a="20889" b="6196" g="3625"/>
		<o f="1" t="28" s="0" x="-100580935" y="-14141727" z="143155716" atype="1" aamount="4" a="24802" b="60080" g="62914"/>
		<o f="1" t="28" s="4" x="-166848512" y="-2705321" z="130507544" atype="0" aamount="54" a="60438" b="57701" g="59811"/>
		<o f="1" t="28" s="0" x="-4387552" y="-7590841" z="-28041144" atype="0" aamount="14" a="38233" b="62590" g="59804"/>
		<o f="1" t="28" s="0" x="-176539288" y="-12621162" z="-21490424" atype="0" aamount="34" a="46290" b="1366" g="61950"/>
		<o f="1" t="28" s="0" x="1893144" y="7257122" z="-21957096" atype="1" aamount="56" a="44222" b="65275" g="29057"/>
		<o f="1" t="28" s="0" x="-106347628" y="-12603048" z="142537607" atype="1" aamount="28" a="64118" b="9596" g="6262"/>
		<o f="1" t="28" s="4" x="-61084688" y="29933746" z="171967504" atype="1" aamount="56" a="45555" b="63273" g="185"/>
		<o f="1" t="28" s="4" x="-13572168" y="-2126539" z="-65712576" atype="1" aamount="52" a="43666" b="2644" g="1106"/>
		<o f="1" t="28" s="0" x="-127877768" y="-7887558" z="-68508552" atype="1" aamount="14" a="39401" b="59887" g="26324"/>
		<o f="1" t="28" s="0" x="-134189528" y="-8751281" z="144615104" atype="0" aamount="24" a="4932" b="8686" g="8199"/>
		<o f="1" t="28" s="4" x="-5673544" y="-2642560" z="147284168" atype="0" aamount="34" a="31892" b="7197" g="6227"/>
		<o f="1" t="28" s="4" x="-163409376" y="26634863" z="-26648576" atype="1" aamount="32" a="2389" b="4867" g="28872"/>
		<o f="1" t="28" s="4" x="2137312" y="-22795608" z="-57917816" atype="1" aamount="16" a="32576" b="60309" g="37374"/>
		<o f="1" t="28" s="4" x="29407264" y="7034145" z="45662183" atype="1" aamount="58" a="27167" b="63349" g="4670"/>
		<o f="1" t="28" s="4" x="30115112" y="-12510574" z="112795916" atype="0" aamount="34" a="52730" b="2845" g="62199"/>
		<o f="1" t="28" s="0" x="-130737788" y="1422221" z="-69280312" atype="0" aamount="34" a="18650" b="11614" g="4566"/>
		<o f="1" t="28" s="0" x="-115064228" y="-2747" z="-56939456" atype="0" aamount="20" a="17871" b="57728" g="65211"/>
		<o f="1" t="28" s="4" x="-216640064" y="-2682444" z="56203208" atype="0" aamount="16" a="31155" b="455" g="37351"/>
		<o f="1" t="28" s="4" x="64727312" y="-7786636" z="58763271" atype="0" aamount="22" a="26020" b="13005" g="7877"/>
		<o f="1" t="28" s="0" x="-108091457" y="16524573" z="135133224" atype="1" aamount="32" a="56575" b="9213" g="2099"/>
		<o f="1" t="28" s="4" x="20122144" y="-10781151" z="7906968" atype="0" aamount="22" a="56042" b="57314" g="28484"/>
		<o f="1" t="28" s="0" x="21830112" y="-7052374" z="-13846512" atype="0" aamount="14" a="56500" b="6800" g="34820"/>
		<o f="1" t="28" s="0" x="42627640" y="-11720521" z="46233982" atype="0" aamount="52" a="45039" b="59758" g="27873"/>
		<o f="1" t="28" s="0" x="-4646304" y="-1265972" z="-79818896" atype="1" aamount="56" a="35597" b="64086" g="59882"/>
		<o f="1" t="28" s="4" x="-30785596" y="-3220474" z="169666592" atype="0" aamount="48" a="42020" b="61740" g="34147"/>
		<o f="1" t="28" s="0" x="-150911464" y="-19052419" z="-57427144" atype="0" aamount="38" a="36206" b="63151" g="59796"/>
		<o f="1" t="28" s="0" x="-116231220" y="-1984355" z="-47451048" atype="0" aamount="48" a="64395" b="62211" g="38664"/>
		<o f="1" t="28" s="4" x="15216712" y="-2623806" z="961860" atype="0" aamount="60" a="14078" b="62890" g="661"/>
		<o f="1" t="28" s="0" x="-92555927" y="33286821" z="-21015180" atype="0" aamount="58" a="58044" b="6680" g="35610"/>
		<o f="1" t="28" s="0" x="-172225016" y="-12871817" z="-16969904" atype="0" aamount="6" a="15494" b="5935" g="36056"/>
		<o f="1" t="28" s="4" x="18298408" y="40930482" z="-8669776" atype="1" aamount="10" a="32894" b="8816" g="40182"/>
		<o f="1" t="28" s="4" x="64574016" y="2824903" z="64564607" atype="1" aamount="36" a="46955" b="1409" g="32072"/>
		<o f="1" t="28" s="4" x="27956968" y="-12787413" z="143458264" atype="0" aamount="44" a="12667" b="55480" g="32383"/>
		<o f="1" t="28" s="0" x="-98112836" y="-23691056" z="-21652712" atype="0" aamount="60" a="52722" b="54818" g="8030"/>
		<o f="1" t="28" s="0" x="-169925836" y="4910623" z="139088409" atype="0" aamount="52" a="19351" b="46" g="65264"/>
		<o f="1" t="28" s="0" x="62837552" y="7027841" z="88266504" atype="1" aamount="8" a="19030" b="11211" g="58436"/>
		<o f="1" t="28" s="0" x="46384840" y="-12104867" z="84527218" atype="1" aamount="14" a="32439" b="5381" g="26132"/>
		<o f="1" t="28" s="0" x="-183000232" y="6841638" z="62538288" atype="1" aamount="28" a="30335" b="51980" g="58014"/>
		<o f="1" t="28" s="0" x="28930853" y="-6275951" z="-16181350" atype="0" aamount="36" a="39139" b="63701" g="27351"/>
		<o f="1" t="28" s="0" x="-149199216" y="-7803207" z="-6058728" atype="0" aamount="22" a="65412" b="52021" g="50773"/>
		<o f="1" t="28" s="4" x="-15001508" y="-12354992" z="139665840" atype="0" aamount="40" a="54821" b="9270" g="25469"/>
		<o f="1" t="28" s="0" x="45364832" y="-2966188" z="63409940" atype="1" aamount="24" a="24797" b="65319" g="29727"/>
		<o f="1" t="28" s="0" x="-164214376" y="160578" z="2745936" atype="0" aamount="24" a="63093" b="59666" g="39563"/>
		<o f="1" t="28" s="0" x="-6476024" y="27752491" z="-78772336" atype="0" aamount="28" a="6100" b="12103" g="12629"/>
		<o f="1" t="28" s="4" x="-158908416" y="-10197403" z="96883276" atype="0" aamount="2" a="45376" b="11389" g="33987"/>
		<o f="1" t="28" s="4" x="15753288" y="12531208" z="47020451" atype="1" aamount="54" a="4504" b="363" g="62203"/>
		<o f="1" t="28" s="4" x="-186075024" y="2520528" z="-6699376" atype="1" aamount="6" a="44477" b="54290" g="104"/>
		<o f="1" t="28" s="0" x="67419184" y="-2687563" z="65225102" atype="1" aamount="40" a="63263" b="52094" g="15523"/>
		<o f="1" t="28" s="0" x="16682944" y="5584215" z="4354332" atype="1" aamount="34" a="33022" b="6136" g="58609"/>
		<o f="1" t="28" s="0" x="-210264360" y="-5984822" z="105467506" atype="1" aamount="26" a="28264" b="5344" g="59443"/>
		<o f="1" t="28" s="0" x="-108474970" y="-13381556" z="-40249504" atype="1" aamount="32" a="13788" b="61286" g="34989"/>
		<o f="1" t="28" s="0" x="-135010648" y="-20255716" z="-8588616" atype="0" aamount="48" a="50349" b="7787" g="64125"/>
		<o f="1" t="28" s="4" x="-11459908" y="-12557171" z="-26155184" atype="1" aamount="4" a="6785" b="5382" g="30399"/>
		<o f="1" t="28" s="0" x="-187141768" y="-14823661" z="22885236" atype="1" aamount="12" a="53094" b="11981" g="65439"/>
		<o f="1" t="28" s="0" x="-105286552" y="-7551876" z="-28419114" atype="0" aamount="34" a="11158" b="2030" g="4132"/>
		<o f="1" t="28" s="0" x="-201124560" y="-12650759" z="38376562" atype="1" aamount="32" a="32341" b="56907" g="59150"/>
		<o f="1" t="28" s="0" x="-117251376" y="-3515978" z="-13216032" atype="0" aamount="14" a="12240" b="53334" g="3165"/>
		<o f="1" t="28" s="0" x="15367416" y="-4464411" z="22860284" atype="1" aamount="48" a="40479" b="2959" g="28009"/>
		<o f="1" t="28" s="0" x="-7611384" y="-8087448" z="-77060288" atype="0" aamount="52" a="28331" b="63243" g="61296"/>
		<o f="1" t="28" s="0" x="15405808" y="24540383" z="-44702360" atype="0" aamount="24" a="17223" b="10671" g="5861"/>
		<o f="1" t="28" s="0" x="-177039328" y="-13662361" z="66917437" atype="0" aamount="20" a="40265" b="57521" g="57673"/>
		<o f="1" t="28" s="0" x="8055488" y="-17559287" z="-10043416" atype="0" aamount="32" a="39975" b="64996" g="60457"/>
		<o f="1" t="28" s="4" x="8113472" y="-12502195" z="11937492" atype="0" aamount="48" a="14438" b="56534" g="6213"/>
		<o f="1" t="28" s="4" x="-20918360" y="-7110567" z="-43579128" atype="0" aamount="44" a="61356" b="58197" g="26988"/>
		<o f="1" t="28" s="0" x="-147074360" y="15192447" z="-42841504" atype="0" aamount="34" a="18689" b="327" g="176"/>
		<o f="1" t="28" s="4" x="2297670" y="3872071" z="-16253412" atype="0" aamount="16" a="28938" b="56346" g="6758"/>
		<o f="1" t="28" s="0" x="-144703136" y="9190438" z="-8555904" atype="0" aamount="2" a="19920" b="10392" g="60051"/>
		<o f="1" t="28" s="0" x="-16826548" y="-15343741" z="-64181640" atype="0" aamount="60" a="48976" b="6048" g="63537"/>
		<o f="1" t="28" s="4" x="-117619648" y="-13612177" z="-20942888" atype="0" aamount="50" a="19976" b="7152" g="35537"/>
		<o f="1" t="28" s="0" x="-8902508" y="-15131225" z="-98165968" atype="1" aamount="2" a="22746" b="62652" g="63770"/>
		<o f="1" t="28" s="4" x="-17990332" y="6963268" z="-23624648" atype="0" aamount="48" a="32855" b="10149" g="8732"/>
		<o f="1" t="28" s="0" x="-4104120" y="1448793" z="-51770520" atype="0" aamount="48" a="17118" b="1246" g="1225"/>
		<o f="1" t="28" s="0" x="-216710528" y="-11509122" z="66936222" atype="1" aamount="44" a="51977" b="57404" g="60001"/>
		<o f="1" t="28" s="0" x="18819040" y="6672284" z="-2843788" atype="0" aamount="36" a="58112" b="62443" g="36767"/>
		<o f="1" t="28" s="0" x="-206442448" y="-12685262" z="50552600" atype="0" aamount="26" a="18699" b="60957" g="65138"/>
		<o f="1" t="28" s="0" x="-105630940" y="28725762" z="145105312" atype="0" aamount="8" a="15365" b="9068" g="5445"/>
		<o f="1" t="28" s="4" x="-1456968" y="-12899234" z="-76082960" atype="0" aamount="20" a="46039" b="3535" g="65002"/>
		<o f="1" t="28" s="4" x="26575808" y="-8134601" z="13953220" atype="0" aamount="4" a="21973" b="14990" g="8185"/>
		<o f="1" t="28" s="4" x="-150484840" y="-21836578" z="119561600" atype="0" aamount="56" a="47906" b="2725" g="31459"/>
		<o f="1" t="28" s="0" x="20257592" y="-12650026" z="51218771" atype="1" aamount="52" a="59232" b="7395" g="3454"/>
		<o f="1" t="28" s="0" x="-217162704" y="428841" z="50333697" atype="0" aamount="54" a="54849" b="4372" g="34081"/>
		<o f="1" t="28" s="4" x="-163140840" y="-18669609" z="93835088" atype="0" aamount="42" a="57224" b="59675" g="28448"/>
		<o f="1" t="28" s="0" x="-125001348" y="4078152" z="-62596041" atype="0" aamount="30" a="49959" b="3099" g="64275"/>
		<o f="1" t="28" s="0" x="-37533432" y="7227499" z="146854400" atype="0" aamount="28" a="54339" b="1048" g="34107"/>
		<o f="1" t="28" s="0" x="-42377234" y="-8598698" z="-30406095" atype="0" aamount="58" a="48171" b="59909" g="29541"/>
		<o f="1" t="28" s="0" x="-171477888" y="-13611724" z="-41664" atype="1" aamount="32" a="55927" b="53399" g="59453"/>
		<o f="1" t="28" s="0" x="-83129742" y="-15010215" z="-35478064" atype="1" aamount="4" a="20610" b="748" g="64375"/>
		<o f="1" t="28" s="0" x="-55405074" y="-12580849" z="-62773280" atype="1" aamount="28" a="21877" b="52857" g="64558"/>
		<o f="1" t="28" s="4" x="-44139262" y="-12210052" z="-37088056" atype="0" aamount="52" a="55425" b="8128" g="59244"/>
		<o f="1" t="28" s="0" x="-11641944" y="7695910" z="-101191488" atype="0" aamount="58" a="28203" b="2919" g="60481"/>
		<o f="1" t="28" s="4" x="9819064" y="8201937" z="-22338928" atype="0" aamount="32" a="15054" b="61238" g="34236"/>
		<o f="1" t="28" s="0" x="-100931188" y="-13433291" z="-26966664" atype="0" aamount="8" a="40202" b="64584" g="60459"/>
		<o f="1" t="28" s="0" x="6353080" y="14934892" z="-24592576" atype="0" aamount="42" a="59416" b="64079" g="4124"/>
		<o f="1" t="28" s="4" x="16562368" y="3687828" z="43376404" atype="0" aamount="16" a="27366" b="5087" g="4923"/>
		<o f="1" t="28" s="0" x="-64549845" y="29362710" z="186746488" atype="0" aamount="34" a="41416" b="63030" g="60488"/>
		<o f="1" t="28" s="4" x="-7422720" y="6624617" z="-31071112" atype="1" aamount="30" a="29104" b="60560" g="37871"/>
		<o f="1" t="28" s="0" x="44090392" y="-3230941" z="-21627040" atype="1" aamount="20" a="25543" b="4942" g="60714"/>
		<o f="1" t="28" s="4" x="18412408" y="-2649298" z="47055034" atype="0" aamount="60" a="11634" b="7500" g="65314"/>
		<o f="1" t="28" s="0" x="-100089682" y="-1783164" z="-20822528" atype="1" aamount="22" a="58489" b="64084" g="36509"/>
		<o f="1" t="28" s="0" x="-171318064" y="2218233" z="103374800" atype="0" aamount="44" a="45147" b="58260" g="59799"/>
		<o f="1" t="28" s="4" x="19965840" y="-3234676" z="-47415392" atype="0" aamount="60" a="42588" b="6485" g="2535"/>
		<o f="1" t="28" s="4" x="13676456" y="-13149363" z="-45631488" atype="0" aamount="60" a="53643" b="8076" g="59753"/>
		<o f="1" t="28" s="0" x="57500608" y="-7982879" z="104216736" atype="1" aamount="40" a="64881" b="4595" g="5440"/>
		<o f="1" t="28" s="4" x="-177422216" y="-1126788" z="64854269" atype="0" aamount="28" a="20520" b="56225" g="6919"/>
		<o f="1" t="28" s="0" x="-215657360" y="-16826168" z="38161154" atype="1" aamount="22" a="39022" b="4595" g="60254"/>
		<o f="1" t="28" s="4" x="16328488" y="-1703470" z="95966408" atype="0" aamount="44" a="43693" b="195" g="878"/>
		<o f="1" t="28" s="0" x="31276168" y="6806428" z="39388892" atype="1" aamount="28" a="19799" b="8335" g="30927"/>
		<o f="1" t="28" s="0" x="4727448" y="-8136177" z="177522648" atype="0" aamount="8" a="23516" b="1243" g="30097"/>
		<o f="1" t="28" s="0" x="-76233144" y="-23700644" z="-25106286" atype="0" aamount="36" a="34696" b="622" g="59898"/>
		<o f="1" t="28" s="0" x="13631136" y="7554789" z="-24705856" atype="0" aamount="50" a="14464" b="59773" g="1769"/>
		<o f="1" t="28" s="0" x="28701082" y="23881065" z="-4534698" atype="0" aamount="24" a="47353" b="7954" g="31193"/>
		<o f="1" t="28" s="0" x="17958152" y="-2836116" z="114840008" atype="1" aamount="16" a="59205" b="10215" g="36481"/>
		<o f="1" t="28" s="0" x="-416736" y="-1299258" z="117624088" atype="0" aamount="20" a="593" b="11376" g="41020"/>
		<o f="1" t="28" s="0" x="39888920" y="15048271" z="-7340232" atype="0" aamount="26" a="53829" b="55042" g="12849"/>
		<o f="1" t="28" s="0" x="-14731116" y="8308190" z="-55456328" atype="0" aamount="44" a="27491" b="60989" g="61686"/>
		<o f="1" t="28" s="0" x="-206739112" y="-2752206" z="7430908" atype="0" aamount="12" a="12401" b="64674" g="35944"/>
		<o f="1" t="28" s="0" x="-76464771" y="24656797" z="-44914312" atype="0" aamount="26" a="51487" b="60784" g="65405"/>
		<o f="1" t="28" s="0" x="-120559685" y="38545" z="-59066367" atype="0" aamount="38" a="45492" b="13032" g="59905"/>
		<o f="1" t="28" s="0" x="27503088" y="1716630" z="53624539" atype="0" aamount="46" a="55735" b="62285" g="2824"/>
		<o f="1" t="28" s="0" x="-149096960" y="-3075292" z="4809332" atype="0" aamount="24" a="51228" b="53493" g="37019"/>
		<o f="1" t="28" s="0" x="-202085496" y="8907287" z="77361770" atype="1" aamount="26" a="2912" b="51767" g="11128"/>
		<o f="1" t="28" s="0" x="22667168" y="1934855" z="-40128048" atype="1" aamount="24" a="53151" b="52142" g="65073"/>
		<o f="1" t="28" s="0" x="-186150112" y="1757884" z="31580344" atype="0" aamount="58" a="18090" b="53563" g="34387"/>
		<o f="1" t="28" s="0" x="18006128" y="-7429494" z="34472278" atype="1" aamount="50" a="20203" b="56936" g="32742"/>
		<o f="1" t="28" s="0" x="22328862" y="-17280851" z="-15225756" atype="0" aamount="18" a="14070" b="5135" g="3764"/>
		<o f="1" t="28" s="4" x="-65412465" y="-2343034" z="-32231680" atype="0" aamount="2" a="52893" b="4092" g="29094"/>
		<o f="1" t="28" s="0" x="1260064" y="-14296600" z="-7096416" atype="0" aamount="60" a="50867" b="58642" g="59968"/>
		<o f="1" t="28" s="4" x="-17539008" y="-16660111" z="-61431280" atype="1" aamount="28" a="18980" b="62770" g="3751"/>
		<o f="1" t="28" s="4" x="-112563592" y="6288414" z="-47993760" atype="1" aamount="4" a="56236" b="57707" g="28481"/>
		<o f="1" t="28" s="0" x="24037512" y="-12251340" z="-26859360" atype="0" aamount="40" a="57045" b="65017" g="35681"/>
		<o f="1" t="28" s="4" x="-204058168" y="-1160588" z="-9917032" atype="0" aamount="22" a="51455" b="65107" g="30324"/>
		<o f="1" t="28" s="0" x="47159504" y="2006932" z="-8756248" atype="1" aamount="20" a="6820" b="10087" g="42879"/>
		<o f="1" t="28" s="0" x="-184816624" y="-9457330" z="130093816" atype="1" aamount="42" a="39796" b="8330" g="27194"/>
		<o f="1" t="28" s="0" x="14592936" y="-6660797" z="-31020568" atype="0" aamount="20" a="64942" b="10517" g="7076"/>
		<o f="1" t="28" s="4" x="-171926800" y="-13264438" z="75789906" atype="0" aamount="36" a="12278" b="10396" g="191"/>
		<o f="1" t="28" s="4" x="-174073048" y="2037443" z="64405093" atype="0" aamount="14" a="38823" b="3982" g="36354"/>
		<o f="1" t="28" s="0" x="21369296" y="28747793" z="141396064" atype="0" aamount="8" a="18105" b="3403" g="936"/>
		<o f="1" t="28" s="0" x="-13734968" y="-7523733" z="-65383160" atype="0" aamount="40" a="36719" b="64309" g="59923"/>
		<o f="1" t="28" s="0" x="-188325544" y="-2970392" z="-16270752" atype="1" aamount="24" a="19756" b="11251" g="33338"/>
		<o t="20" s="SS_SPECIAL_ASTEROIDMOON" x="-57236841" y="-2097039" z="46134867" a="7168" b="0" g="-14336" v="0"/>
		<o t="6" s="SS_FAC_LC_1" x="-37006578" y="-14802631" z="117927631" r="18" a="32768" b="0" g="11264"/>
		<o t="6" s="SS_FAC_LC_4" x="-118693750" y="-1135626" z="93981186" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_2" x="-51685854" y="0" z="-36389802" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_6" x="-128782894" y="-1875000" z="149124177" r="18" a="-9216" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_4" x="-81193750" y="-1135626" z="-24143813" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_3" x="26051569" y="-7230254" z="51764296" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_4" x="-138682198" y="-2826749" z="-774921" r="18" a="32768" b="0" g="0"/>
		<o f="1" t="6" s="SS_FAC_LC_7" x="-153780622" y="-11294344" z="22367895" r="18" a="32768" b="0" g="0"/>
		<o f="1" t="6" s="SS_FAC_LC_5" x="-213440" y="-392506" z="-10484151" r="18" a="32768" b="0" g="0"/>
		<o f="1" t="6" s="SS_FAC_LC_5" x="-128494478" y="2675238" z="89871245" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_1" x="-24054276" y="9868420" z="-30345394" r="18" a="32768" b="0" g="11264"/>
		<o t="6" s="SS_FAC_LC_3" x="-16430920" y="-7401315" z="109564144" r="18" a="32768" b="0" g="0"/>
		<o f="1" t="6" s="SS_FAC_LC_6" x="-43301429" y="-56483983" z="-46167315" r="18" a="25600" b="-10240" g="11264"/>
		<o t="6" s="SS_FAC_LC_2" x="-62935854" y="0" z="124860198" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_5" x="-110489308" y="11250000" z="-3379933" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_5" x="8645904" y="2184604" z="91965876" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_3" x="33034539" y="6717200" z="9684543" r="18" a="32768" b="0" g="0"/>
		<o f="1" t="6" s="SS_FAC_LC_EEMPC" x="49859539" y="6317200" z="49684543" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_7" x="-137047697" y="0" z="53412828" r="18" a="32768" b="0" g="0"/>
		<o t="6" s="SS_FAC_LC_5" x="27395904" y="-12815395" z="31965876" r="18" a="32768" b="0" g="0"/>
		<o t="5" s="SS_DOCK_LC_5" x="-133100329" y="1523784" z="-31800987" r="18" a="9216" b="-11264" g="7168"/>
		<o t="5" s="SS_DOCK_LC_1" x="27594573" y="2757337" z="78688322" r="18" a="32768" b="0" g="0"/>
		<o t="5" s="SS_DOCK_LC_2" x="-149975329" y="1523784" z="75074013" r="18" a="9216" b="-11264" g="7168"/>'''

    return original_text, replacement_text