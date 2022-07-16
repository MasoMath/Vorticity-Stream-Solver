'''
Gianluca Gisolo

This script constructs a movie using an 4,5 solver.
The resolution is determined by 2^N to make use of the speed
from FFT construction of the differential equation being used. 
Saves file as mp4 using ffmpeg encoder.

Notation used in comments is outlined in README.md file.
'''
import vortStreamInteractor
import vortStreamAnimator
import vortStreamSolver
import random
import numpy as np


def randomize_initial_conditions(custom_initial, random_initial, endpt):
    '''
    Checks bool parameters custom_initial and random_initial to see if the user
    wants to create custom initial conditions or randomly generate them.
    This method uses the float endpt param to ensure the initial conditions
    lie within the boundary.
    
    Returns a list of lists, [e_1 e_2 e_3 ...] where each for each j, the
    list e_j is an initial condition for a starting vorticity. Each e_j is
    of the form [xShift yShift xStretch yStretch].
    '''
    if random_initial or custom_initial:
        print('\nHow many vorticities will we have? (Must be an int)')
        try:
            user_input = int(input())
        except ValueError:
            print('\nYour input could not be cast as an int...')
            user_input = random.randrange(10)
            print('Therefore we instead will start with ' + str(user_input)
                    + ' vorticities')
        if random_initial:         
            return [[
                    random.uniform(-endpt, endpt), random.uniform(-endpt, endpt),
                    ((-1)**random.randrange(2)) * random.uniform(0.01, endpt),
                    ((-1)**random.randrange(2)) * random.uniform(0.01, endpt)
                    ] for i in range(user_input)]
        elif custom_initial:
            initials = []
            print('\n\nPlease provide 4 floats separated by spaces (see notes below):\n'+
                    'The first two must be between endpts, the last two must be nonzero '
                    + 'and if either \nof the last two have a negative sign, that will flip'
                    + ' the orientation of the vorticity'
                    + '\ni.e. -4 2 2 3.14 \n WARNING: If any conditions are not good'
                    + ' it will be replaced with a random condition!')
            for i in range(user_input):
                print('\n\n Vorticity number ' + str(i))
                init_con = input().split()
                try:
                    init_con = [float(con) for con in init_con]
                    if ((init_con[0] > endpt or init_con[0] < -endpt) or
                        (init_con[1] > endpt or init_con[1] < -endpt)):
                        print('\nVorticities out of bound... Generating them...')
                        init_con[0] = random.uniform(-endpt, endpt)
                        init_con[1] = random.uniform(-endpt, endpt)
                    if (init_con[2] == 0) or (init_con[3] == 0):
                        print('Vorticities scaling is undefined... Redefining...')
                        init_con[2] = ((-1)**random.randrange(2)) * random.uniform(0.01, endpt)
                        init_con[3] = ((-1)**random.randrange(2)) * random.uniform(0.01, endpt)        
                except ValueError:
                    print('Your input could not be cast to a float... generating instead...')
                    init_con = [
                        random.uniform(-endpt, endpt), random.uniform(-endpt, endpt),
                        ((-1)**random.randrange(2)) * random.uniform(0.01, endpt),
                        ((-1)**random.randrange(2)) * random.uniform(0.01, endpt)
                    ]
                    print('\n\nThis is what is being added \n' + str(init_con))
                initials.append(init_con)                
            return initials
    return []

def main():
    """
    Main method. Responsible for calling and transfering information from other
    python files.
    """
    n_factor, endpt, time_length, fps, ani_file_name, cmap, custom_initial = vortStreamInteractor.script_intro()

    print('\nWould you like to randomize your initial conditions? (y/n)')
    user_input = input()
    random_initial = user_input[0].lower() == 'y'
    initial_conditions = randomize_initial_conditions(custom_initial, random_initial, endpt)

    # Constraints; n must be a multiple of 2
    n = 2**n_factor
    tspan = np.linspace(0,time_length - 1,time_length, dtype=int)

    # This solves the given system
    [omega, xDom, yDom] = vortStreamSolver.FFTsolver(
        n, tspan, initial_conditions, endpt=endpt,
        custom_initial=custom_initial, random_initial=random_initial
    )

    # This animates and saves the given system
    vortStreamAnimator.createAnimated3DPlot(
        xDom, yDom, omega, endpt=endpt, n=n, frameNum=time_length, cmap=cmap, 
        ani_file_name=ani_file_name, fps=fps
    )

if __name__ == "__main__":
    main()
