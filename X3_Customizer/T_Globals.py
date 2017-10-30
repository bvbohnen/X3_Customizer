'''
Transforms to globals.
'''
from File_Manager import *
import Flags


#Transporter distance adjustment.
#TODO, SG_MAX_DISTANCE_BEAMING

#Docking computer distance adjustment.
#TODO, SG_MAX_VERTEXDIST_DOCKCOMPUTER

        
@Check_Dependencies('TMissiles.txt', 'Globals.txt', category = 'Missile')
def Set_Missile_Swarm_Count(
        swarm_count = 5
    ):
    '''
    Set the number of submissiles fired by swarm missiles.
    Submissile damage is adjusted accordingly to maintain overall damage.

    * swarm_count:
      - Int, the number of missiles per swarm.
    '''
    for this_dict in Load_File('Globals.txt'):
        if this_dict['name'] == 'SG_MISSILE_SWARM_COUNT':

            #Record swarm missile count.
            old_swarm_count = int(this_dict['value'])
            #Calculate the damage factor.
            damage_factor = old_swarm_count / swarm_count

            #Loop over the missiles.
            for missile_dict in Load_File('TMissiles.txt'):

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
        
        

@Check_Dependencies('Globals.txt', category = 'Missile')
def Adjust_Missile_Hulls(
    scaling_factor = 1
    ):
    '''
    Adjust the hull value for all missiles by the scaling factor.
    Does not affect boarding pod hulls.

    * scaling_factor:
      - Multiplier on missile hull values.
    '''
    for this_dict in Load_File('Globals.txt'):
        #Look for any of the missile hull fields.
        #Could match on 'MAXHULL_' and skip the swarm adjustment and
        # boarding pods, or otherwise just print out all fields
        # individually. Go with individual for now, in case of adding
        # per-missile hull adjustments in the future.
        if this_dict['name'] in [
            'MAXHULL_MISSILE'
            'MAXHULL_MISSILE_LIGHT'
            'MAXHULL_MISSILE_MEDIUM'
            'MAXHULL_MISSILE_HEAVY'
            'MAXHULL_MISSILE_BOMBER'
            'MAXHULL_TORPEDO'
            'MAXHULL_MISSILE_AF'
            'MAXHULL_MISSILE_KHAAK'
            ]:
            new_value = int(this_dict['value']) * scaling_factor
            this_dict['value'] = str(int(new_value))


@Check_Dependencies('Globals.txt')
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
            
        
@Check_Dependencies('Globals.txt')
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
            
            
@Check_Dependencies('Globals.txt')
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
                
            
@Check_Dependencies('Globals.txt')
def Adjust_Strafe(
        #Try out halving these, to make strafe less tempting, and less jumpy when in
        # a spacesuit.
        small_ship_factor = 1,
        big_ship_factor   = 1
    ):
    '''
    Strafe adjustment factor.
    Note: this does not appear to have any effect during brief testing.
    
    * small_ship_factor:
      - Multiplier on small ship strafe.
    * big_ship_factor:
      - Multiplier on big ship strafe.
    '''
    #Appears to use an integer value which may be in the standard
    # 2 meters / ms metric.
    #Original for fighters is ~50k, or maybe 25 m/s.
    Adjust_Global('SG_MAXSTRAFEFACTOR_SMALLSHIP', small_ship_factor)
    Adjust_Global('SG_MAXSTRAFEFACTOR_BIGSHIP', big_ship_factor)
                

#Generic transforms taking specific global named flags.
@Check_Dependencies('Globals.txt')
def Set_Global(field_name, value):
    '''
    Set a global flag to the given value.
    Generic transform works on any named global field.

    * field_name:
      - String, name of the field in Globals.txt
    * value:
      - Int, the value to set.
    '''
    for this_dict in Load_File('Globals.txt'):
        if this_dict['name'] == field_name:
            #Note: all globals are integers.
            this_dict['value'] = str(int(value))
            break

    
@Check_Dependencies('Globals.txt')
def Adjust_Global(field_name, scaling_factor):
    '''
    Adjust a global flag by the given multiplier.
    Generic transform works on any named global field.

    * field_name:
      - String, name of the field in Globals.txt
    * scaling_factor:
      - Multiplier to apply to the existing value.
    '''
    #Can return early if just multiplying by 1.
    if multiplier == 1:
        return
    for this_dict in Load_File('Globals.txt'):
        if this_dict['name'] == field_name:
            new_value = int(this_dict['value']) * scaling_factor
            #Note: all globals are integers.
            this_dict['value'] = str(int(new_value))
            break