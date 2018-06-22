'''
Transforms to globals.
'''
from collections import OrderedDict

from .. import File_Manager
from ..Common import Flags

#Transporter distance adjustment.
#TODO, SG_MAX_DISTANCE_BEAMING

#Docking computer distance adjustment.
#TODO, SG_MAX_VERTEXDIST_DOCKCOMPUTER

        
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
    # TODO: switch this to using the new global defaults table.
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
        #Try out halving these, to make strafe less tempting, and less jumpy when in
        # a spacesuit.
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
    #Appears to use an integer value which may be in the standard
    # 2 meters / ms metric.
    #Original for fighters is ~50k, or maybe 25 m/s.
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
    for this_dict in File_Manager.Load_File('types/Globals.txt'):
        if this_dict['name'] == field_name:
            new_value = int(this_dict['value']) * scaling_factor
            #Note: all globals are integers.
            this_dict['value'] = str(int(new_value))
            break



# Table capturing all known global names and their defaults.
# Names taken from the x3:ap executable version 3.3.
# Defaults taken from vanilla AP globals.txt, or from misc
# online searches, or from guesses.
# Default is None when completely unknown.
# Note: distance units are generally in 1/500 meters.
# Where interesting comments are in the globals.txt, they are quited here.
Global_Defaults = {

    # Unclear. 85 m/s.  Could this be a strafe replacement or similar?
    'SG_AVRSPEED'                           : 42500,
    
    # Values related to ship steering.
    'SG_CURSORSTEERING_DAMPING'             : 30,
    # "max cursor firing angle, must be < 90"
    'SG_CURSORSTEERING_MAXFIREANGLE'        : 30,

    # Unknown. Could increasing this affect draw ranges, or when
    # a detailed model swaps in for the low-poly distant models?
    'SG_DETAILVISIBLE_MINDIST'              : 0,

    # Appearance related factors, presumably.
    'SG_HUEMODIFIER_MAX_ARGON'              : 30,
    'SG_HUEMODIFIER_MAX_BORON'              : 0,
    'SG_HUEMODIFIER_MAX_GONER'              : 0,
    'SG_HUEMODIFIER_MAX_KHAAK'              : 0,
    'SG_HUEMODIFIER_MAX_PARANID'            : 20,
    'SG_HUEMODIFIER_MAX_PIRATE'             : 0,
    'SG_HUEMODIFIER_MAX_RACE1'              : 359,
    'SG_HUEMODIFIER_MAX_RACE2'              : 359,
    'SG_HUEMODIFIER_MAX_SPLIT'              : 0,
    'SG_HUEMODIFIER_MAX_TELADI'             : 20,
    'SG_HUEMODIFIER_MAX_TERRAN'             : 0,
    'SG_HUEMODIFIER_MAX_XENON'              : 20,
    'SG_HUEMODIFIER_MAX_YAKI'               : 0,
    'SG_HUEMODIFIER_MIN_ARGON'              : 340,
    'SG_HUEMODIFIER_MIN_BORON'              : 0,
    'SG_HUEMODIFIER_MIN_GONER'              : 0,
    'SG_HUEMODIFIER_MIN_KHAAK'              : 0,
    'SG_HUEMODIFIER_MIN_PARANID'            : 340,
    'SG_HUEMODIFIER_MIN_PIRATE'             : 0,
    'SG_HUEMODIFIER_MIN_RACE1'              : 0,
    'SG_HUEMODIFIER_MIN_RACE2'              : 0,
    'SG_HUEMODIFIER_MIN_SPLIT'              : 0,
    'SG_HUEMODIFIER_MIN_TELADI'             : 340,
    'SG_HUEMODIFIER_MIN_TERRAN'             : 0,
    'SG_HUEMODIFIER_MIN_XENON'              : 340,
    'SG_HUEMODIFIER_MIN_YAKI'               : 0,
    'SG_HUE_ZEROPOS_ARGON'                  : -26,
    'SG_HUE_ZEROPOS_BORON'                  : 0,
    'SG_HUE_ZEROPOS_GONER'                  : 0,
    'SG_HUE_ZEROPOS_KHAAK'                  : 0,
    'SG_HUE_ZEROPOS_PARANID'                : 0,
    'SG_HUE_ZEROPOS_PIRATE'                 : 0,
    'SG_HUE_ZEROPOS_RACE1'                  : 0,
    'SG_HUE_ZEROPOS_RACE2'                  : 0,
    'SG_HUE_ZEROPOS_SPLIT'                  : 0,
    'SG_HUE_ZEROPOS_TELADI'                 : 130,
    'SG_HUE_ZEROPOS_TERRAN'                 : 0,
    'SG_HUE_ZEROPOS_XENON'                  : 0,
    'SG_HUE_ZEROPOS_YAKI'                   : 0,
    'SG_SATMODIFIER_DEFAULT_ARGON'          : 65536,
    'SG_SATMODIFIER_DEFAULT_BORON'          : 65536,
    'SG_SATMODIFIER_DEFAULT_GONER'          : 65536,
    'SG_SATMODIFIER_DEFAULT_KHAAK'          : 65536,
    'SG_SATMODIFIER_DEFAULT_PARANID'        : 65536,
    'SG_SATMODIFIER_DEFAULT_PIRATE'         : 65536,
    'SG_SATMODIFIER_DEFAULT_RACE1'          : 65536,
    'SG_SATMODIFIER_DEFAULT_RACE2'          : 65536,
    'SG_SATMODIFIER_DEFAULT_SPLIT'          : 65536,
    'SG_SATMODIFIER_DEFAULT_TELADI'         : 65536,
    'SG_SATMODIFIER_DEFAULT_TERRAN'         : 65536,
    'SG_SATMODIFIER_DEFAULT_XENON'          : 65536,
    'SG_SATMODIFIER_DEFAULT_YAKI'           : 65536,
    'SG_SATMODIFIER_SPECIAL_ARGON'          : 65536,
    'SG_SATMODIFIER_SPECIAL_BORON'          : 65536,
    'SG_SATMODIFIER_SPECIAL_GONER'          : 65536,
    'SG_SATMODIFIER_SPECIAL_KHAAK'          : 65536,
    'SG_SATMODIFIER_SPECIAL_PARANID'        : 65536,
    'SG_SATMODIFIER_SPECIAL_PIRATE'         : 65536,
    'SG_SATMODIFIER_SPECIAL_RACE1'          : 65536,
    'SG_SATMODIFIER_SPECIAL_RACE2'          : 65536,
    'SG_SATMODIFIER_SPECIAL_SPLIT'          : 65536,
    'SG_SATMODIFIER_SPECIAL_TELADI'         : 65536,
    'SG_SATMODIFIER_SPECIAL_TERRAN'         : 65536,
    'SG_SATMODIFIER_SPECIAL_XENON'          : 65536,
    'SG_SATMODIFIER_SPECIAL_YAKI'           : 65536,

    # May be related to how much a ship drifts on turns.
    'SG_MAXGLIDESPEED'                      : 100,

    # Various hull values.
    # May need to look these up in game for defaults.
    'SG_MAXHULL_ASTEROID'                   : None,
    'SG_MAXHULL_BOARDINGPOD'                : None,
    'SG_MAXHULL_CELESTIAL'                  : None,
    'SG_MAXHULL_CONTAINER'                  : None,
    'SG_MAXHULL_DEBRIS'                     : None,
    'SG_MAXHULL_DOCK'                       : None,
    'SG_MAXHULL_FAC_BIO'                    : None,
    'SG_MAXHULL_FAC_COMPLEX'                : None,
    'SG_MAXHULL_FAC_DEFAULT'                : None,
    'SG_MAXHULL_FAC_FOOD'                   : None,
    'SG_MAXHULL_FAC_MINE'                   : None,
    'SG_MAXHULL_FAC_POWER'                  : None,
    'SG_MAXHULL_FAC_SHIP'                   : None,
    'SG_MAXHULL_FAC_STORAGE'                : None,
    'SG_MAXHULL_FAC_TECH'                   : None,
    'SG_MAXHULL_SPECIAL'                    : None,
    'SG_MAXHULL_WARPGATE'                   : None,
    'SG_MAXHULL_WRECK'                      : None,

    # Missile hull values from here:
    # https://forum.egosoft.com/viewtopic.php?t=316886&start=68
    'SG_MAXHULL_MISSILE'                    : 5,
    'SG_MAXHULL_MISSILE_AF'                 : 5,
    'SG_MAXHULL_MISSILE_BOMBER'             : 2700,
    'SG_MAXHULL_MISSILE_DMBF'               : 5,
    'SG_MAXHULL_MISSILE_HEAVY'              : 2000,
    'SG_MAXHULL_MISSILE_KHAAK'              : 200,
    'SG_MAXHULL_MISSILE_LIGHT'              : 50,
    'SG_MAXHULL_MISSILE_MEDIUM'             : 90,
    # This one could not be found anywhere on google.
    # At a guess, may be the same as base missile, at 5.
    'SG_MAXHULL_MISSILE_SWARMPCT'           : 5, # Guess
    'SG_MAXHULL_TORPEDO'                    : 4000,
    # Swarm missile related fields.
    'SG_MISSILE_SWARM_COUNT'                : 8,
    # "time for a full rotation in ms, 0 stops rotation"
    'SG_MISSILE_SWARM_ROT_TIME'             : 15000,
    # "random position variance, 65536/missilecount is a good base"
    'SG_MISSILE_SWARM_WIGGLE_FACTOR'        : 8192,
    

    # Strafe factors may be unused. TODO: test.
    # About 52 and 98 m/s respectively.
    'SG_MAXSTRAFEFACTOR_BIGSHIP'            : 26214,
    'SG_MAXSTRAFEFACTOR_SMALLSHIP'          : 49152,

    # These units are in meters.
    'SG_MAX_DISTANCE_BEAMING'               : 5000,
    'SG_MAX_DISTANCE_BUILDCOMPLEX'          : 20000,
    'SG_MAX_DISTANCE_COMM'                  : 25000,
    # This distance is to nearest vertex of the dock target.
    'SG_MAX_VERTEXDIST_DOCKCOMPUTER'        : 4000,

    # Field of view limits.
    'SG_MIN_FOV'                            : 70,
    'SG_MAX_FOV'                            : 100,

    # Related to generic missions.
    'SG_MISSION_QUOTA_BUILD'                : 4,
    'SG_MISSION_QUOTA_FIGHT'                : 4,
    'SG_MISSION_QUOTA_THINK'                : 4,
    'SG_MISSION_QUOTA_TRADE'                : 4,

    # Unknown. Tuning values for something.
    # At a guess: mobile mining yield per pickup and energy to
    # break down rocks.
    'SG_MM_BULLET_ENERGY'                   : 10000,
    'SG_MM_DESTRUCTION_RANGE'               : 100000,
    'SG_MM_EMPTY_DIVISOR'                   : 1,
    'SG_MM_EMPTY_MULTIPLIER'                : 1,
    'SG_MM_EMPTY_PERCENTAGE'                : 30,
    'SG_MM_FIXED_MINIMUM'                   : 1,
    # "0:fixed, 1-4:formulae"
    'SG_MM_METHOD'                          : 1,
    'SG_MM_RANDOM_MINIMUM'                  : 2,
    'SG_MM_RANDOM_RANGE'                    : 0,
    'SG_MM_RELVALUE_BASE'                   : 100,
    # "0:none, 1:random, 2:fixed"
    'SG_MM_RELVALUE_TYPE'                   : 1,
    'SG_MM_YIELD_DIVISOR'                   : 30,
    'SG_MM_YIELD_MULTIPLIER'                : 1,
    # "0:none, 1:random, 2:fixed"
    'SG_MM_YIELD_TYPE'                      : 1,
    # "0:none, 1:normal"
    'SG_MM_YIELD_ZERO'                      : 0,
    
    # Storage space multipliers for docks/hub.
    'SG_DOCK_STORAGE_FACTOR'                : 3,
    'SG_HUB_STORAGE_FACTOR'                 : 6,
    'SG_NPC_DOCK_STORAGE_FACTOR'            : 1,
    'SG_NPC_HUB_STORAGE_FACTOR'             : 6,
    # Unknown. Maybe these increase storage based on wares
    # being large or high price, to get around the low limit
    # on high end goods like PPCs and such.
    'SG_DOCK_STORAGE_PRICE_FACTOR'          : None,
    'SG_DOCK_STORAGE_VOL_FACTOR'            : None,
    # Hub gate realignment settings.
    'SG_GATE_REALIGNMENT_ENERGY'            : 10000,
    # Time to complete a relink.
    'SG_GATE_REALIGNMENT_LINK'              : 300,
    # Cooldown between relinks.
    'SG_GATE_REALIGNMENT_WAIT'              : 7200,

    # Unknown. Suggests alternate OOS combat mechanics, maybe
    # a 0 gives TC/Reunion style mechanics instead of the
    # updated AP ones.
    'SG_OOS_FIGHT_MODE'                     : 1,
    
    # Ranges of various scanners.
    'SG_SCANNER_RANGE_FREIGHTSCANNER'       : 2000000,
    'SG_SCANNER_RANGE_ORBITALLASER'         : 1250000,
    'SG_SCANNER_RANGE_SATELLITE'            : 11000000,
    'SG_SCANNER_RANGE_SATELLITE2'           : 17500000,
    'SG_SCANNER_RANGE_SHIP'                 : 5000000,
    'SG_SCANNER_RANGE_SHIP_UPGRADE2'        : 10000000,
    'SG_SCANNER_RANGE_SHIP_UPGRADE3'        : 15000000,
    # Nebula were in x2; this could be leftover from then.
    'SG_SCANNER_RANGE_SO_NEBULA'            : 750000,
    'SG_SCANNER_RANGE_STATION'              : 5000000,

    # Unknown.
    'SG_STRICT_EQUIP_LIMIT'                 : None,
    
    # Possibly the number of blue brackets put around various
    # object types.
    'SG_TRACKER_NUM_ASTEROIDS'              : 3,
    'SG_TRACKER_NUM_BEACON'                 : 2,
    'SG_TRACKER_NUM_CIVILIAN'               : 2,
    'SG_TRACKER_NUM_CONTAINER'              : 2,
    'SG_TRACKER_NUM_ENEMYSHIP'              : 8,
    'SG_TRACKER_NUM_GATES'                  : 16,
    'SG_TRACKER_NUM_HUGEENEMYSHIP'          : 8,
    'SG_TRACKER_NUM_HUGEPLSHIP'             : 10,
    'SG_TRACKER_NUM_HUGESHIP'               : 10,
    'SG_TRACKER_NUM_INMISSILE'              : 2,
    'SG_TRACKER_NUM_MINES'                  : 4,
    'SG_TRACKER_NUM_OTHER'                  : 3,
    'SG_TRACKER_NUM_PLSHIP'                 : 16,
    'SG_TRACKER_NUM_SHIP'                   : 10,
    'SG_TRACKER_NUM_STATION'                : 8,

    # Tractor beam values.
    # In meters.
    'SG_TRACTOR_BREAK_DIST'                 : 1332,
    'SG_TRACTOR_SPEED_LIMIT'                : 80,
    # "fixed point spring constant"
    'SG_TRACTOR_SPRING_CONST'               : 4369,
    'SG_TRACTOR_SPRING_DIST'                : 777,
    
    # AP war values.
    'SG_WAR_SCORE_HULL_DIVISOR'             : 2000,
    'SG_WAR_SCORE_MD_MULTIPLIER'            : 1,
    'SG_WAR_SCORE_PLAYER_MULTIPLIER'        : 20,
    'SG_WAR_SCORE_RELVAL_DIVISOR'           : 1000,
    }