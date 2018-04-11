'''
Code for generation scaling equations, used by various transforms.

TODO: maybe remove dependency on scipy.optimize to make this more
accessible with just base python packages.
For now, scipy will only be imported when the scaling equation is
built, so transforms that don't use it will not need scipy.
'''

import math

'''
Fit function thoughts, made from the perspective of adjusting bullet speeds:

Simple formula: x*(y/(x+y))
 x = original damage
 y = tuning parameter
 For y=2000:
  x=2000 -> 1000 (slows down the sped up light weapons nicely)
  x=500  ->  400 (slows lower rate weapons less, though still a bit much)

Stronger formula: x*(y/(x+y))^z
 Since the (y/(x+y)) is effectively a scaling factor on the original damage, adding
 a power term 'z' should make that factor stronger the further it is below 1.
 For y=5000, z = 2
  x=2000 -> 1020
  x=500  ->  413 (not much better, would like to keep it 450+)
 Note that z < 0 also allows the equation to do have increasing returns by flipping
  the reduction factor over. Eg. 1/2 factor becomes (1/2)^-1 = 2

Can add an overall scaling term to correct the low end values back up:
 x*w*(y/(x+y))^z
 Where w,y,z are tuning parameters.
 The 'w' term can bring the 500 point back in line, and hopefully not effect lower
 points too much (there shouldn't be much below 300).

This was run through optimization, to get:
 w = 1.21
 y = 1.05e7
 z = 4.67e3
To keep some of the xrm speed, without also speeding up slow weapons too much, this
 can also aim for scaling x=2000 -> 1300 or so. This gives:
 w = 1.21
 y = 1.05e7
 z = 4.67e3
These parameters can be calculated dynamically before a transform uses them.


Question: can this same formula be used to increase small values while not increasing
large values, eg. with buffs to small weapons?
-The scaling term (y/(x+y)) can go from <1 to >1 with a negative power applied to it,
translating diminishing returns to increasing returns.
-Diminishing returns had y>>x : as x->0, scaling factor rises to 1.
-If y<<x, then as x->inf, scaling factor rises to 1.
Answer: in theory yes, it should work, with a small y and negative z.
-In practice, this found to have trouble getting a good fit, not nearly as 
 powerful as the diminishing returns style.
-Can only really solve for 1 data point well.
-The optimizer appears to try to 0 out the z term, leaving just a linear w term.
-This makes sense: as x increases, the scaling term will always diverge from 1,
 which is not what is wanted.

Can the function be flipped around in a way that will stabalize it for this case:
-Want small x to give a scaler far from 1, large x to converge on 1.
-Try: x*w*(x/(x+y))^z
-When x>>y, scaling goes to 1.
-When x~y, scaling goes to 1/2.

Result: the new equation (called 'reversed' below) works well for this case.


The above equations have a little bit of a problem with overshoot:
 If asked to scale the range 1 to 10 (to eg. 1 to 20), an outlier at 15
 might be excessively impacted (eg. yielding 100 instead of an expected 30).
This is a natural problem with these equations, that they are only smooth
in the range they are calibrated for.

To mitigate this overshoot problem, the calibrated equation will be packed
with a wrapper function that will check the input range, and will return
the calibrated scaling point nearest to the input if the input falls outside
the calibration range.
 Eg. if an equation is calibrated for 1 to 10, then seeing a 15 will cause
 the wrapped equation to return the scaling for 10, its nearest calibration
 point.


A problem exists with overflow in the fitting function when large values
are present.  To help stabalize against this, input terms will be scaled
to be close to 1, and the scaling term will be attached to the returned
scaling function to be automatically applied during evaluation.

'''
class Scaling_Function():
    '''
    Scaling function wrapper class.
    Records the base equation, coefficients, and valid range.
    May be called like a normal function, providing the input to scale.
    '''
    def __init__(s, scaling_func, coefs, x_vec, x_scaling, y_scaling):
        # Record the input scaling factors for x and y.
        # These are determined during function selection and fitting,
        #  and get applied during evaluation.
        s.x_scaling = x_scaling
        s.y_scaling = y_scaling
        # Record the central scaling python function, and the
        #  coefs determined for it.
        s.scaling_func = scaling_func
        s.coefs = coefs
        # Record the x input range.
        s.x_min = min(x_vec)
        s.x_max = max(x_vec)
        # Record the min/max y points as well, taken from the
        #  scaling function selected.
        s.y_min = s.scaling_func(s.x_min, *s.coefs)
        s.y_max = s.scaling_func(s.x_max, *s.coefs)
        # Record the min/max y/x ratios.
        s.yx_ratio_min = s.y_min / s.x_min
        s.yx_ratio_max = s.y_max / s.x_max
        return

    # Provide the call wrapper.
    def __call__(s, x):
        # Apply the x_scaling to the input.
        x = x * s.x_scaling
        # Check for x out of the calibration bounds, and use
        #  the nearest bound's y/x ratio if so.
        if x > s.x_max:
            # Don't want to return the actual y_max, since the out of
            #  range x should still be getting proportionally scaled.
            #  Eg. if x = 2*x_max, and y_max = x_max, then want y = 2*x.
            # Multiply x by the max y/x ratio.
            y_scaled = x * s.yx_ratio_max
        elif x < s.x_min:
            y_scaled = x * s.yx_ratio_min
        else:
            # Run the scaling func on it.
            y_scaled = s.scaling_func(x, *s.coefs)
        # Unscale and return.
        # (Could probably flip the y_scaling and just do a mult, but speed
        #  doesn't matter.)
        y = y_scaled / s.y_scaling
        return y

# Fit function
def Fit_equation(x, a,b,c):
    # Do some bounds checking.
    # a,b should never be negative.
    if a<0 or b<0:
        # Return a silly number to discourage the optimizer.
        return float('inf')
    # Use the version stable at low x.
    return x *a *((b / (x+b))**c)

def Fit_equation_reversed(x, a,b,c):
    if a<0 or b<0:
        return float('inf')
    # Use the version stable at high x.
    return x *a *((x / (x+b))**c)


def Get_Scaling_Fit(x_vec, y_vec, **kwargs):
    '''
    Returns a function-like Scaling_Function class object.
    If (y < x) in general, a diminishing formula is used, otherwise
     and increasing formula is used.
    If the largest changes occur near the low x, smallest
     changes at high x, a reversed scaling formula is used.
    '''

    # Rescale the inputs to place them close to 1.
    # This can be done later, before fitting, but is easiest if
    #  done early always.
    x_vec, x_scaling = Rescale_Vec(x_vec)
    y_vec, y_scaling = Rescale_Vec(y_vec)

    # Do a test on the inputs to figure out if this is in diminishing or 
    #  increasing returns mode.
    diminishing_mode = True
    # Check all data points summed up, and compare.
    if sum(y_vec) > sum(x_vec):
        # If y>x, not diminishing.
        diminishing_mode = False


    # Pick the fit equation to use. Select this automatically based
    #  on the input values (eg. is the bigger change on the small side or
    #  the large side).
    # Get the smallest x indices.
    x_min_index = x_vec.index( min(x_vec))
    x_max_index = x_vec.index( max(x_vec))
    # Get the ratio of x/y at the small and large points.
    x_min_to_y = x_vec[x_min_index] / y_vec[x_min_index]
    x_max_to_y = x_vec[x_max_index] / y_vec[x_max_index]

    # Default to standard equation.
    reverse = False
    # When in diminishing mode, if the max x/y is smaller than the
    #  min x/y, then use the reverse formula.
    if diminishing_mode and x_max_to_y < x_min_to_y:
        reverse = True
    # When in increasing mode, if the max x/y is larger than the
    #  min x/y, then reverse.
    if not diminishing_mode and x_max_to_y > x_min_to_y:
        reverse = True
    
    # Pick the equation to use.
    fit_equation_to_use = Fit_equation
    if reverse:
        fit_equation_to_use = Fit_equation_reversed
        

    # Curve fit entry function (gets the full x vector, returns y vector).
    def curve_fit_entry_func(x_vec, *coefs):
        y = []
        for x in x_vec:
            y.append(fit_equation_to_use(x, *coefs))
        return y


    def minimize_entry_func(coefs, x_vec, y_vec):
        # Get a vectors of values using these coefs.
        y_new = [fit_equation_to_use(x,*coefs) for x in x_vec]
                
        # Aim to minimize the ratio differences in y.
        # -Removed in favor of SAD; also, this had a spurious divide
        #  by 0 warning (maybe for missile damage scaling).
        ##Get ratio in both directions, take the max of either.
        ##Eg. 1/2 and 2/1 will both evaluate to 2.
        # diffs = [max(y0/y1, y1/y0) for y0, y1 in zip(y_new, y_vec)]
        ##Could optionally increase the weight on large diffs, eg. by
        ## squaring.
        # diffs = [d**2 for d in diffs]
        # error = sum(diffs)

        # Can also try sum of least squares style.
        sad = sum([(y0 - y1) **2 for y0, y1 in zip(y_new, y_vec)])

        # return error
        return sad


    # Find initial coefs.
    '''
    These can set w and z to 1, y to whatever satisfies the first data pair.
    Eg. y = x*b/(x+b), solve for b.
     yx + yb = xb
     yx = b(x-y)
     yx/(x-y) = b

    Sanity check: if y = 0.5, x = 1, then b = 1 to divide properly. Checks out in both eqs.

    What if y==x at this point?  Would get divide by 0.
    -Try all points until one does not divide by 0.
    -If such a point not found, all data is equal, and can set b0 to some very high number,
     higher than anything in the x vector (50x should do).

    What is y>x, such that b is negative?
    -Leads to a math domain error when optimizing, in practice, since the power term is
     operating on a negative, eg (-1)^c.
    -If y = 1, x = 0.5, then b = -1.
    -The expected fix for this is to have the overall power term be negative, eg. -1, so that
     the equation to solve is y = x*(x+b)/b.
     yb = xx + xb
     yb - xb = xx
     b = xx / (y-x)
     Sanity check: if y = 1, x = 0.5, then b = 0.5.

    Can look at the vector data to determine which mode is expected, and set the coefs
    accordingly.
    '''
    
    # Find b0 and z0 based on mode.
    if diminishing_mode:
        z0 = 1
        # Start b0 at something higher than anything in x, in case
        #  all data points are the same.
        b0 = 50 * max(x_vec)
        # Calc b for the first mismatched data points.
        for x,y in zip(x_vec, y_vec):
            if x != y:
                b0 = y * x / (x - y)
                break
        # Set the bounds for the coefs.
        # Force a,b to be positive, but allow z to go negative.
        coef_bounds = [(0,None),(0,None),(-5,5)]
    else:
        z0 = -1
        # Start b0 at something lower than anything in x.
        b0 = min(x_vec) / 50
        # Calc b for the first mismatched data points.
        for x,y in zip(x_vec, y_vec):
            if x != y:
                b0 = x * x / (y - x)
                break
        # Set the bounds for the coefs.
        coef_bounds = [(0,None),(0,None),(-5,5)]
    coefs_0 = [1,b0,z0]

    # Do curve fit.
    import scipy.optimize as optimize
    # -Removed, couldn't handle increasing returns cases, probably because of
    #  lack of staying in bounds (keeps making b negative).
    # coefs, _ = optimize.curve_fit(curve_fit_entry_func, x_vec, y_vec, coefs_0)

    # Use minimize instead.
    # This aims to minimize a single value returned by the target function.
    optimize_result = optimize.minimize(
        # Objective function; should return a scaler value to minimize.
        # Eg. calculate speeds, take difference from the original speeds, return
        #  some estimate of error (eg. max difference).
        fun = minimize_entry_func,
        # Starting guess
        x0 = coefs_0,
        # Pass as args the x and y data.
        args = (x_vec, y_vec),
        # Use default solver for now.
        # Set the bounds.
        bounds = coef_bounds
        )
    coefs = optimize_result.x

    # Make the scaling function object.
    this_func = Scaling_Function( 
        fit_equation_to_use, coefs, x_vec, x_scaling, y_scaling)

    # Calculate the data points for debug check.
    final_y_vec = [this_func(x) for x in x_vec]

    if 0:
        # For debug, view the curve to see if it looks as expected.
        Plot_Fit(this_func)

    return this_func


def Rescale_Vec(vec):
    'Scale a vector so that its values are centered around 1.'
    # This can be based off of the average value in the input.
    # return vec, 1 #Test return.
    avg = sum(vec)/len(vec)
    scaling = 1/avg
    new_vec = [x*scaling for x in vec]
    return new_vec, scaling


def Plot_Fit(fit_equation):
    'Make a plot of this fit.'
    import matplotlib.pyplot
    import numpy
    # Plot over the full range, plus an extra 10% on each side to see
    #  if the limiter is working.
    # Treat the x inputs as original values to be scaled (eg. take the
    #  internal x_min/x_max and unscale them first).
    x_spaced = numpy.linspace(fit_equation.x_min * 0.9 / fit_equation.x_scaling, 
                              fit_equation.x_max * 1.1 / fit_equation.x_scaling, 
                              50)
    y_spaced = [fit_equation(x) for x in x_spaced]
    plot = matplotlib.pyplot.plot(x_spaced, y_spaced)
    matplotlib.pyplot.show()
    return