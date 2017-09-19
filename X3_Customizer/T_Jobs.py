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
      - Key will try to match an boolean field in the jobs file (see File_Fields
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
        factor = Find_match(this_dict, job_count_factors)

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
      - Key will try to match an boolean field in the jobs file (see File_Fields
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
        multiplier = Find_match(this_dict, time_multiplier_list)
        minutes_to_add = Find_match(this_dict, time_adder_list)

        #Apply adjustment, converting minutes to seconds.
        value = int(this_dict['respawn_time'])
        value = round(value * multiplier + minutes_to_add * 60)
        this_dict['respawn_time'] = str(value)

    return



def Find_match(job_dict, entry_list):
    '''
    Support function tries to find which entry in the entry_list matches
    to a given job_dict, matching flags first, then job name, returning
    the first entry in entry_dict that matches.
    '''
    #Loop over list entries, in order.
    for key, entry in entry_list:

        #Check for direct key match; assume value is boolean.
        if key in job_dict and job_dict[key] == '1':
            return entry

        #Check for job name match; partial match supported, the key
        # just needs to be present in the job name. 
        if key in job_dict['name']:
            return entry

        #Wildcard match.
        if key == '*':
            return entry
    #Probably shouldn't be here, but return None.
    return None
