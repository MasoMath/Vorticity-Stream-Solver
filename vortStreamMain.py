'''
Gianluca Gisolo

This script constructs a movie using an 4,5 solver.
The resolution is determined by 2^N to make use of the speed
from FFT construction of the differential equation being used. 
Saves file as mp4 using ffmpeg encoder
'''
import vortStreamInteractor
import vortStreamAnimator
import vortStreamSolver
import random
import numpy as np

DEFAULT = { 
    'N_FACTOR' : 4,
    'ENDPT' : 10,
    'TIME_LENGTH' : 100,
    'FPS' : 20,
    'ANI_FILE_NAME' : 'surface_plot_ani',
    'CMAP' : 'viridis'
}

# random.seed(23)

def randomize_initial_conditions(custom_initial, random_initial, endpt):
    if random_initial or custom_initial:
        print('\nHow many vorticiities will we have? (Must be an int)')
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
    n_factor, endpt, time_length, fps, ani_file_name, cmap, custom_initial = vortStreamInteractor.script_intro()

    print('\nWould you like to randomize your initial conditions? (y/n)')
    user_input = input()
    random_initial = user_input[0].lower() == 'y'
    initial_conditions = randomize_initial_conditions(custom_initial, random_initial, endpt)

    # Constraints; n must be a multiple of 2
    n = 2**n_factor
    tspan = np.linspace(0,time_length - 1,time_length, dtype=int)

    [omega, xDom, yDom] = vortStreamSolver.FFTsolver(
        n, tspan, initial_conditions, endpt=endpt,
        custom_initial=custom_initial, random_initial=random_initial
    )

    vortStreamAnimator.createAnimated3DPlot(
        xDom, yDom, omega, endpt=endpt, n=n, frameNum=time_length, cmap=cmap, 
        ani_file_name=ani_file_name, fps=fps
    )

if __name__ == "__main__":
    main()
