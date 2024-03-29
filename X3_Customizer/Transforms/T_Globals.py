'''
Transforms to globals.

TODO: fully update this code to make use of the newer Globals_File class.
'''
from collections import OrderedDict

from .. import File_Manager
from ..Common import Flags

# Transporter distance adjustment.
#TODO, SG_MAX_DISTANCE_BEAMING

# Docking computer distance adjustment.
#TODO, SG_MAX_VERTEXDIST_DOCKCOMPUTER

# Tracked object adjustment (eg. UI brackets).
# TODO, SG_TRACKER_NUM_ items.

# TODO: new FL globals.
# https://www.egosoft.com:8444/confluence/display/X3WIKI/6D+-+Mod+Files+Changes

        
@File_Manager.Transform_Wrapper('types/TMissiles.txt', 'types/Globals.txt', category = 'Missile')
def Set_Missile_Swarm_Count(
        swarm_count = 5
    ):
    '''
    Set the number of submissiles fired by swarm missiles.
    Submissile damage is adjusted accordingly to maintain overall damage.

    * swarm_count:
      - Int, the number of missiles per swarm.
    '''
    for this_dict in File_Manager.Load_File('types/Globals.txt'):
        if this_dict['name'] == 'SG_MISSILE_SWARM_COUNT':

            #Record swarm missile count.
            old_swarm_count = int(this_dict['value'])
            #Calculate the damage factor.
            damage_factor = old_swarm_count / swarm_count

            #Loop over the missiles.
            for missile_dict in File_Manager.Load_File('types/TMissiles.txt'):

                #Skip if this is not a multishot missile.
                flags_dict = Flags.Unpack_Tmissiles_Flags(missile_dict)
                if not flags_dict['fragmentation']:
                    continue
                #Adjust the damage.
                damage = int(missile_dict['damage']) * damage_factor
                #Round to nearest 100 if over 1000 or so.
                if damage > 1000:
                    damage = round(damage/100)*100
                missile_dict['damage'] = str(int(damage))

            #Set the new count.
            this_dict['value'] = str(swarm_count)
            break

        #Comments in the original globals suggest setting the missile
        # wiggle, eg. position ranodmization, to 65k / swarm count.
        if this_dict['name'] == 'SG_MISSILE_SWARM_WIGGLE_FACTOR':
            this_dict['value'] = str(int(64*1024 / swarm_count))

        #Change the hull factor, which reduces swarm missile hull
        # values, based on the count. Vanilla has this at 12% assuming
        # 8 missile swarms.
        if this_dict['name'] == 'MAXHULL_MISSILE_SWARMPCT':
            hull_percent = 100 / swarm_count
            #Bound it to 1-100, to be safe.
            hull_percent = min(100, hull_percent)
            hull_percent = max(1, hull_percent)
            this_dict['value'] = str(int(hull_percent))
        
        

@File_Manager.Transform_Wrapper('types/Globals.txt', category = 'Missile')
def Adjust_Missile_Hulls(
    scaling_factor = 1
    ):
    '''
    Adjust the hull value for all missiles by the scaling factor.
    Does not affect boarding pod hulls.

    * scaling_factor:
      - Multiplier on missile hull values.
    '''
    #Look for any of the missile hull fields.
    #Could match on 'MAXHULL_' and skip the swarm adjustment and
    # boarding pods, or otherwise just print out all fields
    # individually. Go with individual for now, in case of adding
    # per-missile hull adjustments in the future.
    #Note: these are in the globals for xrm, but not the vanilla
    # game globals, so they should be added to the globals file
    # first with defaults if needed.
    # See https://forum.egosoft.com/viewtopic.php?t=316886&start=68
    # for the default values.
    # TODO: do these actually need SG_ prefixed to them?
    #  XRM doesn't have the prefix, nor does the above link for the
    #  final values, but that could be a misinterpretation on xrm's
    #  part, and maybe the non-sg_ version is a source code term and
    #  the sg_ version is needed for the globals.txt.
    # TODO: switch this to using the new global defaults table and the
    #  access methods in the globals_file class.
    default_damage_dict = {
        'MAXHULL_MISSILE'        : 5,
        'MAXHULL_MISSILE_AF'     : 5,
        'MAXHULL_MISSILE_DMBF'   : 5,
        'MAXHULL_MISSILE_LIGHT'  : 50,
        'MAXHULL_MISSILE_MEDIUM' : 90,
        'MAXHULL_MISSILE_KHAAK'  : 200,
        'MAXHULL_MISSILE_HEAVY'  : 2000,
        'MAXHULL_MISSILE_BOMBER' : 2700,
        'MAXHULL_TORPEDO'        : 4000,
        }

    # Pass 1: determine which maxhull entries are not present.
    names_to_add = [x for x in default_damage_dict]
    for this_dict in File_Manager.Load_File('types/Globals.txt'):
        if this_dict['name'] in default_damage_dict:
            names_to_add.remove(this_dict['name'])

    # Pass 2: add the entries with defaults.
    # Start by making the new lines, as ordered dicts.
    lines_to_add = []
    for name in names_to_add:
        this_line = OrderedDict()
        this_line['name'] = name
        this_line['value'] = str(default_damage_dict[name])
        this_line[2] = '\n'
        lines_to_add.append(this_line)
        
    # Add the entries to the t file.
    File_Manager.Load_File('types/Globals.txt', return_game_file = True).Add_Entries(
        lines_to_add)
    
    # Pass 3: apply the transform normally, on the defaults or
    # whatever was in the file already.
    for this_dict in File_Manager.Load_File('types/Globals.txt'):
        if this_dict['name'] in default_damage_dict:
            new_value = int(this_dict['value']) * scaling_factor
            this_dict['value'] = str(int(new_value))


@File_Manager.Transform_Wrapper('types/Globals.txt')
def Set_Communication_Distance(
        distance_in_km = 75
    ):
    '''
    Set max distance for opening communications with factories and ships.

    * distance_in_km
      - Int, max communication distance.
    '''
    #Give range in meters.
    Set_Global('SG_MAX_DISTANCE_COMM', distance_in_km * 1000)
            
        
@File_Manager.Transform_Wrapper('types/Globals.txt')
def Set_Complex_Connection_Distance(
        distance_in_km = 100
    ):
    '''
    Set max range between factories in a complex.
    With complex cleaner and tubeless complexes, this can practically be anything, 
     particularly useful when connecting up distant asteroids.

    * distance_in_km
      - Int, max connection distance.
    '''
    #Give range in meters.
    Set_Global('SG_MAX_DISTANCE_BUILDCOMPLEX', distance_in_km * 1000)
            
            
@File_Manager.Transform_Wrapper('types/Globals.txt')
def Set_Dock_Storage_Capacity(
        player_factor = 3,
        npc_factor = 1,
        hub_factor = 6
    ):
    '''
    Change the capacity of storage docks: equipment docks, trading posts, etc.

    * player_factor:
      - Int, multiplier for player docks. Vanilla default is 3.
    * npc_factor:
      - Int, multiplier for npc docks. Vanilla default is 1.
    * hub_factor:
      - Int, multiplier for the Hub. Vanilla default is 6.
    '''
    Set_Global('SG_DOCK_STORAGE_FACTOR', player_factor)
    Set_Global('SG_NPC_DOCK_STORAGE_FACTOR', npc_factor)
    Set_Global('SG_HUB_STORAGE_FACTOR', hub_factor)
    Set_Global('SG_NPC_HUB_STORAGE_FACTOR', hub_factor)
                
            
@File_Manager.Transform_Wrapper('types/Globals.txt')
def Adjust_Strafe(
        # Try out halving these, to make strafe less tempting, and less jumpy
        # when in a spacesuit.
        small_ship_factor = 1,
        big_ship_factor   = 1
    ):
    '''
    Strafe adjustment factor.  Experimental.
    Note: this does not appear to have any effect during brief testing.
    
    * small_ship_factor:
      - Multiplier on small ship strafe.
    * big_ship_factor:
      - Multiplier on big ship strafe.
    '''
    # Appears to use an integer value which may be in the standard
    #  2 meters / ms metric.
    # Original for fighters is ~50k, or maybe 25 m/s.
    Adjust_Global('SG_MAXSTRAFEFACTOR_SMALLSHIP', small_ship_factor)
    Adjust_Global('SG_MAXSTRAFEFACTOR_BIGSHIP', big_ship_factor)
                

#Generic transforms taking specific global named flags.
@File_Manager.Transform_Wrapper('types/Globals.txt')
def Set_Global(field_name, value):
    '''
    Set a global flag to the given value.
    Generic transform works on any named global field.

    * field_name:
      - String, name of the field in Globals.txt
    * value:
      - Int, the value to set.
    '''
    for this_dict in File_Manager.Load_File('types/Globals.txt'):
        if this_dict['name'] == field_name:
            #Note: all globals are integers.
            this_dict['value'] = str(int(value))
            break

    
@File_Manager.Transform_Wrapper('types/Globals.txt')
def Adjust_Global(field_name, scaling_factor):
    '''
    Adjust a global flag by the given scaling_factor.
    Generic transform works on any named global field.

    * field_name:
      - String, name of the field in Globals.txt
    * scaling_factor:
      - Multiplier to apply to the existing value.
    '''
    # Can return early if just multiplying by 1.
    if scaling_factor == 1:
        return
    for this_dict in File_Manager.Load_File('types/Globals.txt'):
        if this_dict['name'] == field_name:
            new_value = int(this_dict['value']) * scaling_factor
            # Note: all globals are integers.
            this_dict['value'] = str(int(new_value))
            break
