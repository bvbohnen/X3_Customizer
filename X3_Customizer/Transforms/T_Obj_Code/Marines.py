from ... import File_Manager
from ... import Common
Settings = Common.Settings
from .Obj_Shared import *
from ...File_Manager import Transform_Was_Run_Before

'''
Notes on mixing Set_Max_Marines and Max_Marines_Video_Id_Overwrite:
    For most ships, these two transforms do not have a conflict. The
    larger of the ship default or the video id will be used as the
    marine count.

    However, the sirokos runs into trouble, since both transforms
    are editing the same code section.

    Set_Max_Marines alone:
        Sirokos changes are made to the obj code.

    Max_Marines_Video_Id_Overwrite alone:
        A default (30) must be set for the sirokos in its video id since
        its special obj code will be removed.

    Set_Max_Marines then Max_Marines_Video_Id_Overwrite:
        The Set_Max_Marines doesn't know about the following transform,
        so to be safe, it can edit the sirokos obj code and also
        edit the sirokos video id with the requested value (if one
        was given; if no sirokos value requested, leave the video id
        unchanged in case the user already filled it in manually).

        Max_Marines_Video_Id_Overwrite will check the video id
        on the sirokos, and fill in the default 30 only if the current
        value is 0 (unchanged).  This will also need to wildcard the
        obj byte with the sirokos marine count, in case it was
        changed.

    Max_Marines_Video_Id_Overwrite then Set_Max_Marines
        Set_Max_Marines will need to check if Max_Marines_Video_Id_Overwrite
        has been called already (looking at a recorded transform list),
        and skip the sirokos obj edit if so. It will still change
        the sirokos video id (if given a non-default value).

    With the above approach, these two transforms should mesh together
    in an intuitive way for the user.
'''

@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False, TC = False)
def Set_Max_Marines(
        tm_count = 8,
        tp_count = 40,
        m6_count = 8,
        capital_count = 20,
        # Set no default on sirokos, since its code may need special
        #  handling. Want to distinguish between this being requested
        #  as 30, vs being unspecified.
        sirokos_count = None,
    ):
    '''
    Sets the maximum number of marines that each ship type can carry.
    These are byte values, signed, so max is 127.
    Note: in some cases, a larger ship type may use the marine count of
    a smaller ship if it is greater.
    
    * tm_count
      - Int, marines carried by TMs.
    * tp_count
      - Int, marines carried by TPs.
    * m6_count
      - Int, marines carried by M6s.
      - Overridden by tm_count if it is larger.
    * capital_count
      - Int, marines carried by capital ships: M1, M2, M7, TL.
      - Overridden by tm_count if it is larger.
    * sirokos_count
      - Int, marines carried by the Sirokos, or whichever ship is located
        at entry 263 in Tships (when starting count at 1).
      - Overridden by capital_count if it is larger.
      - Note: XRM does not use this slot in Tships.
    '''
    # Make input args ints, limit to 1 to max_count.
    max_count = 127
    tm_count = max(1, min(int(tm_count), max_count))
    tp_count = max(1, min(int(tp_count), max_count))
    m6_count = max(1, min(int(m6_count), max_count))
    capital_count = max(1, min(int(capital_count), max_count))

    # Convert to hex strings, 1 byte each.
    tm_count      = Int_To_Hex_String(tm_count, 1)
    tp_count      = Int_To_Hex_String(tp_count, 1)
    m6_count      = Int_To_Hex_String(m6_count, 1)
    capital_count = Int_To_Hex_String(capital_count, 1)

    '''
    These are generally just going to be integer value edits of
    the GetMaxMarines functions (base and overloads).
    Entries generally are doubled, one const is used in a comparison,
    second copy is used on one comparison path, so 2 patches per
    marine count changed.
    Sirokos is a special case, with an ship subtype id comparison and
    early return of 30.
    For now, all locations are edited, but arg defaults should leave
    things unchanged.

    Note on overrides:
        The GetMaxMarines often call the GetMaxMarines of a parent class,
        and use that returned value if greater than the custom value.
        The chains appear to be:
            SHIP (with sirokos check) - SHIP_BIG - Obj_2019
                                                 - SHIP_M6
                                      - SHIP_TP
        This mechanism allows the lower level sirokos check to override
        that for other capital ships as long as the sirokos has a higher
        value.

    Note on LU:
        This removes most of the overloads and just has the base function
        look up the ware volume of the ship, and hence the marine count
        is set through tships instead.
        TODO: add support for this alternate style of marine changes.
    '''

    # Lay out the replacement region, capturing both values (otherwise
    #  ambiguity problems crop up).
    patch_fields = [
        # TM. Inherits from SHIP_BIG.
        # Around offset 0x000CFA1C.
        ['05'  '08'    '5D''34''........''0D''0001''32''........'
         '05'  '08'    '14''0002''24''83''24''01''83''6E''0006''01', 
         '..'+tm_count+'..''..''........''..''....''..''........'
         '..'+tm_count],
        
        # Capitals, inherit from Obj_2019.
        # Around offset 0x000D58EE.
        ['05'  '14'         '5D''34''........''0D''0001''32''........'
         '05'  '14'         '14''0002''24''83''24''01''83''6E''0007''0D', 
         '..'+capital_count+'..''..''........''..''....''..''........'
         '..'+capital_count],
        
        # M6. Uses SHIP_M6.
        # Around offset 0x000D68DB.
        ['05'  '08'    '5D''34''........''0D''0001''32''........'
         '05'  '08'    '14''0002''24''83''24''01''83''6E''0007''05', 
         '..'+m6_count+'..''..''........''..''....''..''........'
         '..'+m6_count],
        
        # TP. Uses SHIP_TP.
        # Around offset 0x000D9537.
        ['05'  '28'    '5D''34''........''0D''0001''32''........'
         '05'  '28'    '14''0002''24''83''24''01''83''6E''0007''0D', 
         '..'+tp_count+'..''..''........''..''....''..''........'
         '..'+tp_count],

        ]
    
    # Construct the patches.
    patch_list = []
    for ref_code, replacement in patch_fields:
        patch_list.append( Obj_Patch(
            #offsets = [offset],
            ref_code = ref_code,
            new_code = replacement,
        ))
   
    # Handle the sirokos code specially.
    if sirokos_count != None:
        # If Max_Marines_Video_Id_Overwrite has no been run, do an
        #  obj edit.
        if not Transform_Was_Run_Before('Max_Marines_Video_Id_Overwrite'):
            sirokos_hex_count = max(1, min(int(sirokos_count), max_count))
            sirokos_hex_count = Int_To_Hex_String(sirokos_count, 1)

            # Sirokos. Special case of SHIP.
            # Only one value to patch.
            # Around offset 0x000A876E.
            ref_code = '05'  '1E'  '83''01''83''01''83''6E''0005''0F''0062' 
            replacement = '..'+sirokos_hex_count
            patch_list.append( Obj_Patch(
                #offsets = [offset],
                ref_code = ref_code,
                new_code = replacement,
            ))

        # Whether Max_Marines_Video_Id_Overwrite was run or not, also
        #  change the sirokos video_id field.
        # Note: if the sirokos was moved, to be consistent, this will
        #  only edit the 263rd entry in tships.
        tships_list = File_Manager.Load_File('types/TShips.txt')
        sirokos_entry = tships_list[262]
        # Side note: this will allow for going over the 127 obj byte limit.
        sirokos_entry['video_id'] = str(sirokos_count)
        # Note: the video_id update happens even if a patch fails.

    # Apply the patches.
    Apply_Obj_Patch_Group(patch_list)

    return


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False, TC = False)
def Max_Marines_Video_Id_Overwrite(
    ):
    '''
    Remove the sirokos overwrite and put in its place a check for ships video ID
    Which if larger than the default value will overwrite
    '''
	
    # Construct the patches.
    patch = Obj_Patch(
            ref_code = '0F000E' '060106' '5B' '34000A8771' '05..' '83' '01' '83',
            new_code = NOP*5 + '0F000E' '0507' '03' '82000148E9' '83',
            )
   

    # Apply the patches.
    Apply_Obj_Patch(patch)

    # Since the patch will scrap the sirokos special case handling,
    #  fill in a default for the corresponding video_id.
    # Only do this if the existing entry is 0, to avoid overwriting
    #  an already customized value.
    tships_list = File_Manager.Load_File('types/TShips.txt')
    sirokos_entry = tships_list[262]
    if int(sirokos_entry['video_id']) == 0:
        sirokos_entry['video_id'] = str(30)

    return


# TODO: a transform for use with Max_Marines_Video_Id_Overwrite to
#  set the marine count on specific ships.


@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False, TC = False)
def Make_Terran_Stations_Make_Terran_Marines(
    ):
    '''
    Allow Terran stations (eg. orbital patrol bases) to generate
    Terran marines instead of random commonwealth marines.
    Additional modding may be needed to add marines as products of some
    Terran stations (not included here) before an effect is seen.
    '''
    '''
    Refactors STATION.CreateAddMarine first by making the failures for the
    Pirate check and then the general race mask check use the same block
    for selecting a random race.
    
    Then use the newly freed bytes for changing the race mask from a small int
    to a large int. This allows the mask to include all possible races.
    
    Next we just flip the bit in the mask for terran to true and we have are end \
    result of terran stations creating terran marines.
    '''

    patch = Obj_Patch(
            ref_code = '01' '0F000F' '8500000D71' '0D0001' '0508' '5B' '34000950F0' '053E' '02'
	    	       '8400007450' '140002' '24' '320009510E' '01' '0F000F' '8500004C66' '053E' 
	               '53' '64' '340009510E' '053E' '02' '8400007450' '140002' '24' '01',
            new_code = '01' '0F000F' '8500000D71' '0D0001' '0508' '5A' '3400095102' '0C0C' '0C'
	               '0C0C0C0C0C' '0C0C0C' '0C' '0C0C' '01' '0F000F' '8500004C66' '070004003E' 
	               '53' '64' '340009510E' '053E' '02' '8400007450' '140002' '24' '01',
            )
    Apply_Obj_Patch(patch)

    return

@File_Manager.Transform_Wrapper('L/x3story.obj', LU = False, TC = False)
def Set_Marine_Training_Cost_And_Time_Divisors(
	cost_divisor = 5,
        time_divisor = 5,
    ):
    '''
    The higher the divisor the cheaper/faster training will be
    The lower the divisor the more expensive/slower training will be
    '''

    # Each skill has a max value of 100, so any value over 100 will always result in 0
    max_count = 100

    cost_divisor = max(1, min(int(cost_divisor), max_count))
    time_divisor = max(1, min(int(time_divisor), max_count))

    # Convert to hex strings, 1 byte each.
    cost_divisor = Int_To_Hex_String(cost_divisor, 1)
    time_divisor = Int_To_Hex_String(time_divisor, 1)

    patch_fields = [
	['32' '000D3C7F' '0D' '0002' '05' '..'         '51' '02' '46' '0D' '0004' '06' '1388',
	 '32' '000D3C7F' '0D' '0002' '05'+cost_divisor+'51' '02' '46' '0D' '0004' '06' '1388'],
        ['32' '000D3D3F' '0D' '0002' '05' '..'         '51' '02' '46' '0D' '0004' '06' '012C',
	 '32' '000D3D3F' '0D' '0002' '05'+time_divisor+'51' '02' '46' '0D' '0004' '06' '012C'],
        ]

    patch_list = []
    for ref_code, replacement in patch_fields:
        patch_list.append( Obj_Patch(
            #offsets = [offset],
            ref_code = ref_code,
            new_code = replacement,
        ))
	
    # Apply the patches.
    Apply_Obj_Patch_Group(patch_list)

    return
