'''
Transforms to jobs.
'''
'''
Spawn reductions can be made either by:
1) Reduced job count:
    -Ensures the universe will not grow too have too many ships,
    which can particularly happen over a long game as hostile groups get clustered
    into sectors where they don't die (eg. random pirate spawns might end up stuck
    in pirate sectors eventually).
2) Reduced spawn rate:
    -Introduce more satisfaction in ships being killed off, knowing it will 
    take them some time to reappear instead of just a few minutes.
    -Want to focus adjustment to the fast respawn timers (eg minutes), not
    the slow ones (eg. hours).
    -A flat multiplier on respawn time wouldn't work well, since really short
    timers would still be pretty short.
    -A flat adder might work okay, eg. +20 minutes, so that ships with short
    timers get a bit jump, ships with long timers have a smaller relative
    jump.
    -Many ships have default timers of 30 or 60 minutes, it is mostly raider
    groups with short respawns.
    -Update: some of the big ships are used in raiding groups, which gets to
    be a bit much if they respawn every hour.
    -Can add a multiplier before the adder to try to help both situations,
    and hopefully not depopulate traders too much (though those in safe
    sectors should be fine).

A mixture of both approaches would likely be best.
Adjustments can be made based on some name checks, so that eg. Pirate jobs
might be reduced more than Transporter jobs.
'''
from File_Manager import *


@Check_Dependencies('Jobs.txt')
def Adjust_Job_Count(
    #Adjustment factors to apply, based on various race or name matches.
    #The first match will be used.
    #Key will try to match an owner field in the jobs file (use lowercase affiliation
    # name, no ' in khaak), or failing that will try to do a job name match (partial
    # match supported).
    #The generic * match will match anything remaining.
    job_count_factors = [('*', 1)]
    ):
    '''
    Adjusts job counts using a multiplier. These will always have a minimum of 1.

    * job_count_factors:
      - List of tuples pairing an identifier key with the adjustment value to apply.
        The first match will be used.
      - Key will try to match a boolean field in the jobs file (see File_Fields
        for field names), or failing that will try to do a job name match (partial
        match supported) based on the name in the jobs file.
      - '*' will match all jobs not otherwise matched.
    '''
    #Loop over the jobs.
    for this_dict in Load_File('Jobs.txt'):
        #Skip dummy entries, determined by abscence of a script for now.
        #Xrm has many of these dummies seemingly to act as spacing or placeholders.
        if not this_dict['script']:
            continue

        #Check for key in the dict, going in order.
        factor = Find_entry_match(this_dict, job_count_factors)

        #Adjust both max jobs and max jobs per sector.
        for entry in ['max_jobs', 'max_jobs_in_sector']:
            value = int(this_dict[entry])
            value = round(value * factor)
            #Floor of 1.
            value = max(1, value)
            #Put back.
            this_dict[entry] = str(value)

                
            
@Check_Dependencies('Jobs.txt')
def Adjust_Job_Respawn_Time(
    time_adder_list = [('*', 1)],
    time_multiplier_list = [('*', 1)]
    ):
    '''
    Adjusts job respawn times, using an adder and multiplier on the 
    existing respawn time.

    * time_adder_list, time_multiplier_list:
      - Lists of tuples pairing an identifier key with the adjustment value to apply.
        The first match will be used.
      - Key will try to match a boolean field in the jobs file, 
        (eg. 'owner_argon' or 'classification_trader', see File_Fields
        for field names), or failing that will try to do a job name match (partial
        match supported) based on the name in the jobs file.
      - '*' will match all jobs not otherwise matched.
    '''
    #Loop over the jobs.
    for this_dict in Load_File('Jobs.txt'):
        if not this_dict['script']:
            continue

        #Check for key in the dict, going in order.
        #Multiplier is on the base timer, before the adder is added.
        multiplier = Find_entry_match(this_dict, time_multiplier_list)
        minutes_to_add = Find_entry_match(this_dict, time_adder_list)

        #Apply adjustment, converting minutes to seconds.
        value = int(this_dict['respawn_time'])
        value = round(value * multiplier + minutes_to_add * 60)
        this_dict['respawn_time'] = str(value)

    return




@Check_Dependencies('Jobs.txt')
def Set_Job_Spawn_Locations(
    jobs_types = [],
    sector_flags_to_set = None,
    creation_flags_to_set = None,
    docked_chance = None,
    ):
    '''
    Sets the spawn location of ships created for jobs, eg. at a shipyard, at
    a gate, docked at a station, etc.
    
    * jobs_types:
      - List of keys for the jobs to modify.
      - Key will try to match a boolean field in the jobs file, 
        (eg. 'owner_argon' or 'classification_trader', see File_Fields
        for field names), or failing that will try to do a job name match (partial
        match supported) based on the name in the jobs file.
      - '*' will match all jobs not otherwise matched.
    * sector_flags_to_set:
      - List of sector selection flag names to be set. Unselected flags will
        be cleared. Supported names are:
        - 'select_owners_sector'
        - 'select_not_enemy_sector'
        - 'select_core_sector'
        - 'select_border_sector'
        - 'select_shipyard_sector'
        - 'select_owner_station_sector'
    * creation_flags_to_set:
      - List of creation flag names to be set. Unselected flags will
        be cleared. Supported names are:
        - 'create_in_shipyard'
        - 'create_in_gate'
        - 'create_inside_sector'
        - 'create_outside_sector'
    * docked_chance:
      - Int, 0 to 100, the percentage chance the ship is docked when spawned.
    '''
    #Loop over the jobs.
    for this_dict in Load_File('Jobs.txt'):
        if not this_dict['script']:
            continue

        #Skip if this is not matched to jobs_types.
        if not Check_for_match(this_dict, jobs_types):
            continue

        if sector_flags_to_set:
            #Do a loop over all expected flags.
            for flag in [
                    'select_owners_sector',
                    'select_not_enemy_sector',
                    'select_core_sector',
                    'select_border_sector',
                    'select_shipyard_sector',
                    'select_owner_station_sector']:

                #Set or clear the flag based on input arg.
                #Ignore old settings, to make autoclearing them more
                # convenient, since new flags are likely meant to
                # be complete replacements.
                if flag in sector_flags_to_set:
                    new_value = '1'
                else:
                    new_value = '0'
                this_dict[flag] = new_value
                
        if creation_flags_to_set:
            #This will work basically the same as above.
            for flag in [
                    'create_in_shipyard',
                    'create_in_gate',
                    'create_inside_sector',
                    'create_outside_sector']:
                if flag in creation_flags_to_set:
                    new_value = '1'
                else:
                    new_value = '0'
                this_dict[flag] = new_value


        if docked_chance != None:
            #Do some bounds checking.
            assert isinstance(docked_chance, int)
            assert 0 <= docked_chance <= 100
            this_dict['docked_chance'] = str(docked_chance)

    return


def Find_entry_match(job_dict, entry_list):
    '''
    Support function tries to find which entry in the entry_list matches
    to a given job_dict, matching flags first, then job name, returning
    the first entry in entry_list that matches.
    '''
    #This will attempt to match a flag in the job_dict first,
    # then a partial name match, then a wildcard if one given.
    #Loop over list entries, in order.
    for key, entry in entry_list:
        #Check for direct key match; assume value is boolean.
        if key in job_dict and job_dict[key] == '1':
            return entry
        
    #Loop again.
    for key, entry in entry_list:

        #Check for job name match; partial match supported, the key
        # just needs to be present in the job name. 
        if key in job_dict['name']:
            return entry
        
    #Loop again.
    for key, entry in entry_list:
        #Wildcard match.
        if key == '*':
            return entry

    #Probably shouldn't be here, but return None.
    return None


def Check_for_match(job_dict, key_list):
    '''
    Checks if any key in key_list matches a given job_dict.
    Tries flag matches, partial name matches, wildcard match.
    Returns true on match, else False.
    '''
    #Unlike above, this can do all checks in one loop, because it
    # doesn't matter which match happens.
    #Loop over the keys.
    for key in key_list:
        #Check for direct key match; assume value is boolean.
        if key in job_dict and job_dict[key] == '1':
            return True
        #Check for job name match; partial match supported, the key
        # just needs to be present in the job name. 
        if key in job_dict['name']:
            return True
        #Wildcard match.
        if key == '*':
            return True
    return False