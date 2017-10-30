'''
Toying around with finding a nice curve fit for estimate laser shot speed.
This will use numpy curve_fit, which can accept multiple input vars.

Overall conclusion:
 The desired accuracy of fit was not found (wanted within 15%, got 40%).
 This has been abandoned in favor of a more top-down approach, similar to that
 done on tmissiles.
'''

import numpy as np
import scipy.optimize as optimize
import collections
import math
import pickle

from File_Manager import *
import Flags
import T_Weapons


Lasers_to_ignore_list = [
    #Skip mining/tractor lasers
    'SS_LASER_MINING',
    'SS_LASER_TUG',
    #Skip dummies
    'SS_LASER_DUMMY1',
    'SS_LASER_DUMMY2',
    #Skip aldrin weapons, which are just weaker versions of terran weapons.
    'SS_LASER_EMP_1',
    'SS_LASER_MAM_1',
    'SS_LASER_TERRANANTIFIGHTER_1',
    ]

#Entry point.
def Run():
    tbullets_dict_list = Load_File('TBullets.txt')
    tlasers_dict_list = Load_File('TLasers.txt')

    #Collect the information of interest.
    #It looks like numpy will need each variable as its own list, with all lists
    # being packed together later
    #Can collect all such lists into a dict for easy tracking.
    data_lists_dict = {
        #Set initial empty lists.
        'name'          : [], #Name of the laser, for convenience.
        'shield_dps'    : [],
        'hull_dps'      : [],
        'lifetime'      : [],
        'speed'         : [],
        'range'         : [],
        'energy_per_s'  : [],
        'price'         : [],
        'ignore_shields': [], #1 or 0.
        'use_ammo'      : [], #1 or 0.
        }

    
    #Step through each laser.
    for laser_dict in tlasers_dict_list:

        #Grab the fire delay, in milliseconds.
        this_fire_delay = int(laser_dict['fire_delay'])

        #Determine fire rate, per second.
        fire_rate = Flags.Game_Ticks_Per_Minute / this_fire_delay / 60
            
        #Determine laser pricetag.
        laser_price = int(laser_dict['production_value_npc']) * T_Weapons.Laser_price_scaling_factor

        #Only operate on the first bullet created, ignore later ones.
        bullet_index = int(laser_dict['bullet'])
        bullet_dict = tbullets_dict_list[bullet_index]
            
        #Get speed in 500-meters per s, with lifetime in ms.
        speed    = int(bullet_dict['speed'])
        lifetime = int(bullet_dict['lifetime'])
        #Avoid overwriting built in range function...
        this_range = speed * lifetime

        #Look up some fields.
        flags_dict        = Flags.Unpack_Tbullets_Flags(bullet_dict)     
        hull_damage       = int(bullet_dict['hull_damage'])
        shield_damage     = int(bullet_dict['shield_damage'])
        energy_used       = int(bullet_dict['energy_used'])

        #Calculate per second metrics.
        hull_dps   = hull_damage   * fire_rate
        shield_dps = shield_damage * fire_rate
        energy_per_s = energy_used * fire_rate

        #Skip if this is a beam weapon (instant shot speed) or zigzag (also beam).
        if flags_dict['beam'] or flags_dict['zigzag']:
            continue
        #Skip if this is an areal weapon (dps and speed are too inter releated).
        if flags_dict['areal']:
            continue
        #Skip if this is an ignored laser.
        if laser_dict['name'] in Lasers_to_ignore_list:
            continue


        #Collect the data to be used.
        data_lists_dict['name']           += [laser_dict['name']]
        data_lists_dict['shield_dps']     += [shield_dps]
        data_lists_dict['hull_dps']       += [hull_dps]
        data_lists_dict['lifetime']       += [lifetime]
        data_lists_dict['speed']          += [speed]
        data_lists_dict['range']          += [this_range]
        data_lists_dict['energy_per_s']   += [energy_per_s]
        data_lists_dict['price']          += [laser_price]
        data_lists_dict['ignore_shields'] += [1 if flags_dict['ignore_shields'] else 0]
        data_lists_dict['use_ammo']       += [1 if flags_dict['use_ammo'] else 0]
        

    #Get the input vars to collect together for the curve fit.
    #These will be fed to the estimation function.
    input_var_names = [
        'shield_dps',
        'hull_dps',
        #Can try using lifetime (decoupled from speed) or range (coupled, but the
        # more important metric).
        #Range does poorly in brief sampling.
        'lifetime',
        #'range',
        'energy_per_s',
        'price',
        'ignore_shields',
        'use_ammo',
        ]
    #Set up as a named tuple, that should work okay with numpy while still
    # being easy to work with in the optimization functions.
    global Data_tuple
    Data_tuple = collections.namedtuple('data_tuple', input_var_names)

    #Make into an array of vectors, each vector being a field (eg. 'price').
    data_array = [data_lists_dict[var_name] for var_name in input_var_names]
    #Might need to form this into an np array.
    data_array = np.array(data_array)
    
    #Grab the function to use.
    opt_function, coef_bounds = Get_Optimization_Function()
    
    #Set initial coef guess to 1 or nearest bound.
    #Chain max/min to do this in 1 line; bounds[0] is the low side, bounds[1] is the high side.
    coef_guess = []
    for bounds_tuple in coef_bounds:
        guess = 1
        #Don't check bound if it is None.
        if bounds_tuple[0] != None:
            max(guess, bounds_tuple[0])
        if bounds_tuple[1] != None:
            min(guess, bounds_tuple[1])
        coef_guess.append(guess)
    

    #-Removed, coef count determined by how many bounds.
    ##Figure out how many coefficients are needed.
    ##Can hard code this, but to be fancy can also do some probing code.
    #coefs_list = []
    #while 1:
    #    #Add a coefficient.
    #    coefs_list.append(1)
    #    #Create a dumy input vector of the right length.
    #    dummy_inputs = [1 for i in range(len(input_var_names))]
    #    #Try calling the opt function
    #    try:
    #        opt_function(dummy_inputs, coefs_list)
    #        #If here, succesful, so done filling out the initial coefs.
    #        break
    #    except:
    #        #Need more coefficients.
    #        #Go for another loop.
    #        pass
    #    #Stop if went unreasonably far.
    #    if len(coefs_list) > 20:
    #        sys.exit(' ')


    #-Removed, curve fit did poorly.
    ##The curve_fit target function.
    ##Note: this will receive the full data array, and should return a result
    ## vector.  Can make use of np.apply_along_axis() to do this cleanly.
    ##curve_fit gives the coefficients as separate input args, so use a *args style
    ## format to collect them back together.
    #def curve_fit_entry_func(x, *c):
    #    y = np.apply_along_axis( opt_function, axis=0, arr = x, c = c)
    #    return y
    ##coefs, _ = optimize.curve_fit(curve_fit_entry_func, data_array, data_lists_dict['speed'], coefs_list)
    #
    #coefs = list(coefs)
    ##Now need to get an idea of how well it worked.
    ##Use *coefs to break them apart, since array_func expects them separate.
    #speed_estimates = array_func(data_array, *coefs)
    #
    ##Can either look for relative differences or absolute differences to the
    ## correct speeds.  Relative is probably better, since eg. 10 mps error on
    ## an m5 doesn't matter as much as an m2.
    #relative_diffs = speed_estimates / np.array(data_lists_dict['speed'])
    #max_diff = max(relative_diffs)


    #Switch to using minimize, since curve_fit has no way to set bounds and ran into
    # various overflow/value/etc. errors.
    #This appears to take the coefs first, then extra arguments (eg data_array).
    def minimize_entry_func(coefs, data_array):
        #Get a vectors of speeds using these coefs.
        y = np.apply_along_axis( opt_function, axis=0, arr = data_array, c = coefs)

        #If any speeds are negative, return inf.
        if min(y) <= 0:
            return float('inf')
        
        #Can either look for relative differences or absolute differences to the
        # correct speeds.  Relative is probably better, since eg. 10 mps error on
        # an m5 doesn't matter as much as an m2.
        #Want to treat a difference of 1/2 and 2x as the same error, so take the
        # max of either ratio.
        relative_diffs_high = y / np.array(data_lists_dict['speed'])
        relative_diffs_low  = np.array(data_lists_dict['speed']) / y
        relative_diffs = np.maximum(relative_diffs_high, relative_diffs_low)

        #Can put all relative diffs together, or focus on just the max difference.
        #Max would work best if the fit can be good, otherwise a metric of all 
        # errors might be better to allow for an outlier if it makes everything
        # else more accurate.
        #Aim for max difference for now.
        max_diff = max(relative_diffs)

        return max_diff

    #-Removed, replaced with basinhopping
    ##This aims to minimize a single value returned by the target function.
    #optimize_result = optimize.minimize(
    #    #Objective function; should return a scaler value to minimize.
    #    #Eg. calculate speeds, take difference from the original speeds, return
    #    # some estimate of error (eg. max difference).
    #    fun = minimize_entry_func,
    #    #Starting guess
    #    x0 = coef_guess,
    #    #Pass the data as a bonus arg
    #    args = data_array,
    #    #Use default solver for now.
    #    #Set the bounds.
    #    bounds = coef_bounds
    #    )

    #Switch from minimize to basinhopping, the latter being aimed at finding
    # the global minima better.
    #This requires bounds be implemented as a callable function, returning False
    # when out of bounds.
    def bounds_test_func(**kwargs):
        #Arg 'x_new' should be the new coefficients. Check them.
        for new_coef, bounds_tuple in zip(kwargs['x_new'], coef_bounds):
            #Don't check bound if it is None.
            if bounds_tuple[0] != None and new_coef < bounds_tuple[0]:
                return False
            if bounds_tuple[1] != None and new_coef > bounds_tuple[1]:
                return False
        return True

    optimize_result = optimize.basinhopping(
        #Objective function; should return a scaler value to minimize.
        #Eg. calculate speeds, take difference from the original speeds, return
        # some estimate of error (eg. max difference).
        func = minimize_entry_func,
        #Optionally set number of iterations, default 100.
        #100 takes a while, so try 20ish for quicker runs, though 100 often found
        # to have better results.
        niter = 100,
        #Starting guess
        x0 = coef_guess,
        #Specify the args to the internally called minimize function,
        # using its style of format. Could maybe add bounds here as well.
        minimizer_kwargs = {
            'args' : data_array,
            'bounds' : coef_bounds,
            },
        accept_test = bounds_test_func
        )
    #Coefs are in the result.x field.
    coefs = optimize_result.x


    #Go through all lasers and print the changes.
    #Give name, old and new speed,
    # and the scaling factor.
    #Loop over indices in a sampled vector from data_lists_dict.
    for i in range(len( data_lists_dict['speed'] )):
        #Collect the data vector expected by the optimizer.
        #Note: messy code is a byproduct of the effort gone to to make everything
        # into nice vectors for the optimizer. Perhaps a better approach could have
        # been used to keep nice data structures for longer, translating closer
        # to the optimize call.
        #This will go through data_lists_dict, each named vector of interest,
        # grab the current indexed value, and pack them into a new vector.
        data_vector = [data_lists_dict[var_name][i] for var_name in input_var_names]

        #Also pull out a couple special fields.
        speed = data_lists_dict['speed'][i]
        name  = data_lists_dict['name'][i]

        #Calc the fitting function speed.
        new_speed = opt_function(data_vector, coefs)
        #Calculate difference ratio, worst case high or low.
        max_diff = max(speed / new_speed, new_speed / speed)
        print('{} : {} -> {}, x{}'.format(
            name,
            #Convert back to m/s
            speed / 500,
            new_speed / 500,
            #Give only two sig digits for the scaling factor.
            round(max_diff, 2)
            ))


    #print(coefs)
    #Look up the final max difference.
    max_diff = minimize_entry_func(coefs, data_array)
    print(max_diff)


    #Keep the best coefs across runs.
    #Set the write_new_coefs flag to True to force writing, else it will be
    # determined dynamically.
    write_new_coefs = True
    if not write_new_coefs:
        #Load old coefs if available.
        try:
            with open(Flags.Laser_Speed_Coefs_File_Name,'rb') as file:
                coefs_dict = pickle.load(file)
            #Check max_diff to see if the new one is better.
            if max_diff < coefs_dict['max_diff']:
                #New one better, record it.
                write_new_coefs = True
            else:
                print('Keeping old coefficients with max_diff = {}'.format(coefs_dict['max_diff']))
        except Exception as err:
            #File probably not found. Write one.
            write_new_coefs = True

    if write_new_coefs:
        print('Writing new coefficients')
        #Save out the coefs.
        with open(Flags.Laser_Speed_Coefs_File_Name,'wb') as file:
            pickle.dump({
                #Record the function name, in case it was from another
                # opt func.
                'function': opt_function.__name__,
                'max_diff': max_diff,
                'coefs': coefs
                }, file)

    return


#################################################################################
#Various optimization functions.
#Placed here to put them after the common code, while also keeping them in scope
# for the debugger breakpoints.

#Shared named tuple.
#Use this to name the fields in a given laser's data vector.
Data_tuple = None

#Function which picks the current optimization func.
#Written like this so it can reference funcs declared later in the file.
def Get_Optimization_Function():
    'Returns a function object to optimize for, along with a list of coef bounds.'
    func_number = 1.1

    if func_number == 0:
        return func0, func0_coef_bounds()
    elif func_number == 1:
        return func1, func1_coef_bounds()
    elif func_number == 1.1:
        return func1p1, func1_coef_bounds()


#Linear sum function
def func0(x, c):
    y = 0
    for i in range(len(x)):
        y += c[i] * x[i]
    return y
#diff 5.8

def func0_coef_bounds():
    '''
    Returns a list of tuples, the lower/upper bounds for each coefficient.
    '''
    #7 coefs, no bounds.
    return [
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        ]


#Power function, similar to what was used in excel.
#This is causing lots of trouble with the coefficients going all over the place,
# the optimizer not converging, overflow errors, etc.
#There is no obvious way to fix this.
def func1(x, c):
    xn = Data_tuple(*x)

    #This gets out of range errors when the optimizer tries wackier coefficients,
    # so catch those with a try/except.
    try:
        #Set an overall power scaling.
        y = ( math.pow(
            #Base value to be scaled.
            c[0]
            #c[1] is between 0 and 1, weighting shield vs hull.
            #Treat ignore_shields as a shield dps adder, with a coef[2].
            #c[3] scales damage terms as power.
            / math.pow(c[1] * (xn.shield_dps + xn.ignore_shields * c[2])
                    +(1-c[1]) * xn.hull_dps, c[3])

            #Put a log term on the pricing, to exaggerate the benefit of cheap lasers.
            #c[4] scales price.
            #* math.pow( math.log(xn.price, 10), c[4])
            #Version without the log.
            * math.pow( xn.price, c[4])

            #Treat ammo usage as an alternative to energy use, scale with c[5].
            #c[6] scales energy.
            * math.pow(xn.energy_per_s + xn.use_ammo * c[5], c[6])

            #c[7] scales lifetime or range.
            / math.pow(xn.lifetime, c[7])
            #Range does poorly here.
            #/ math.pow(xn.range, c[7])

            #Scale the entire thing with an overall power term, c[8].
            , c[8])
            )

    #Catch overflow errors, and value errors (eg. log of negative numbers)
    except (OverflowError, ValueError) as err:
        #Unsure what the best default state it; maybe return inf?
        y = float('inf')
    return y

#diff 2.99 with 100 iterations, though once got 2.33, so some variance but
# probably can't get to 1ish.
#diff 5.6 with 20 iterations, so iters really matters.
#1.39 with 100 iters after removing log(price); leave it off.
#13+ with 100 iters after removing the overall power term; put it back.
#4.4 when swapping lifetime to range; go back to lifetime.

def func1_coef_bounds():
    '''
    Returns a list of tuples, the lower/upper bounds for each coefficient.
    '''
    #9 coefs.
    return [
        #Base scaler; generally leave large.
        (0,None),
        #Shield/hull weighting
        (0,1),
        #Value of ignoring shields.
        (0,None),
        #Damage power
        (0,5),
        #Price power
        (0,5),
        #Ammo to energy equivelence factor, may be large
        (0,None),
        #Energy power
        (0,5),
        #Lifetime power
        (0,5),
        #Overall power
        (0,5),
        ]

#Split off from func1 for more playing.
#At this point, func1 was getting the best results (1.39), so preserving it.
#Maybe try tossing in some log terms to dampen the effects of large values.
def func1p1(x, c):
    xn = Data_tuple(*x)

    try:
        #Set an overall power scaling.
        y = ( math.pow(
            #Base value to be scaled.
            c[0]

            #c[1] is between 0 and 1, weighting shield vs hull.
            #Treat ignore_shields as a shield dps adder, with a coef[2].
            #c[3] scales damage terms as power.
            / math.pow(c[1] * (xn.shield_dps + xn.ignore_shields * c[2])
                    +(1-c[1]) * xn.hull_dps, c[3])
            
            #c[4] scales price.
            * math.pow( xn.price, c[4])

            #Treat ammo usage as an alternative to energy use, scale with c[5].
            #c[6] scales energy.
            * math.pow( xn.energy_per_s + xn.use_ammo * c[5], c[6])

            #c[7] scales lifetime or range.
            / math.pow(xn.lifetime, c[7])
            #Range does poorly here.
            #/ math.pow(xn.range, c[7])

            #Scale the entire thing with an overall power term, c[8].
            , c[8])
            )

    #Catch overflow errors, and value errors (eg. log of negative numbers)
    except (OverflowError, ValueError) as err:
        #Unsure what the best default state it; maybe return inf?
        y = float('inf')
    return y
#2.11 with log(price), 100 iters, confirming earlier results with that.
#1.39 with log(lifetime), so no change there.
#1.43 with log(energy_per_s)
#inf with log(shield dps) and log(hull dps), not sure why that messes up so badly.
#1.47 with log around (energy and use_ammo)