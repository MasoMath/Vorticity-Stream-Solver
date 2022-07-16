'''
Gianluca Gisolo

Interacts with the user and initalizations all the parameters for the solver.
Assumes the user is not trying to really break the solver by putting any
information that could cause the program to fail. What is determined as
'really break' is completely arbitrary.
'''

ALL_CMAPS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
    'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
    'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper',
    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
    'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
    'twilight', 'twilight_shifted', 'hsv',
    'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
    'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
    'tab20c',
    'flag', 'prism', 'ocean', 'gist_earth', 'terrain',
    'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
    'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
    'turbo', 'nipy_spectral', 'gist_ncar'
]

DEFAULT = { 
    'N_FACTOR' : 4,
    'ENDPT' : 10,
    'TIME_LENGTH' : 100,
    'FPS' : 20,
    'ANI_FILE_NAME' : 'surface_plot_ani',
    'CMAP' : 'viridis'
}

def script_intro():
    """
    Method which introduces the program and returns all parameters needed
    for the solver.

    Returns an int n_factor which will determine the resolution of the domain
    i.e. the domain will be a (2^n)^2 (x,y) square.
    Returns a float endpt which will determine the boundary of our domain.
    Returns an int time_length that is how many frames the animation will have.
    Returns an int fps which is how many frames will be played per second.
    Returns a string ani_file_name which is the name of the file.
    Returns a string cmap which is which color map the animation will use.
    Returns a bool custom_initial which determines if the user is using custom
    parameters.
    """
    print('\nWelcome to Gianluca\'s Vorticity-Stream function visulizer \n'
            + 'Would you like to customize anything? (y/n)')
    user_input = input()
    custom_initial = user_input[0].lower() == 'y'
    if custom_initial:
        print('\nThere are 6 conditions that can be changed. They are:')
        for param in DEFAULT:
            print(param)
    else:
        print('\nYou\'ve either said no, or more specifically, didn\'t say yes\n'
        + 'Running DEFAULT congfiuration...')
        for key in DEFAULT:
            print(key + ' : ' + str(DEFAULT[key]))
    n_factor = define_param_n_factor(custom_initial)
    endpt = define_param_endpt(custom_initial)
    time_length = define_param_time_length(custom_initial)
    fps = define_param_fps(custom_initial, time_length)
    ani_file_name = define_param_ani_file_name(custom_initial)
    cmap = define_param_cmap(custom_initial)
    return n_factor, endpt, time_length, fps, ani_file_name, cmap, custom_initial

# Define the factor of n that 2 will be raise to
def define_param_n_factor(custom_initial):
    if custom_initial:
        print('\nDefine the factor of the resolution (3-8; int): \n' +
            '(Note that whatever n you provide, the resolution will be 2^n)')
        try:
            user_input = int(input())
            if (user_input < 2) or (user_input > 8):
                print('The provided factor is too large or too small.')
                return define_param_n_factor(custom_initial)
            else:
                return user_input
        except ValueError:
            print('This cannot be cast to an int')
            return define_param_n_factor(custom_initial)
    else:
        return DEFAULT['N_FACTOR']

# Define the end points
def define_param_endpt(custom_initial):
    if custom_initial:
        print('\nDefine the end points of the domain (float): \n' +
            '(This should in most cases always remain as 10)')
        try:
            return float(input())
        except ValueError:
            print('This cannot be cast to a float')
            return define_param_n_factor(custom_initial)
    else:
        return DEFAULT['ENDPT']

# Define the number of frames
def define_param_time_length(custom_initial):
    if custom_initial:
        print('\nDetermine how many frames will be produced (int): \n' +
            '(Note that anything more than 400-600 might be too big)')
        try:
            user_input = int(input())
            if (user_input < 2) or (user_input > 800):
                print('The provided factor is too large or too small.')
                return define_param_n_factor(custom_initial)
            else:
                return user_input
        except ValueError:
            print('This cannot be cast to an int')
            return define_param_n_factor(custom_initial)
    else:
        return DEFAULT['TIME_LENGTH']

# Define the fps
def define_param_fps(custom_initial, time_length):
    if custom_initial:
        print('\nDetermine the fps of the animation (int): \n' +
            '(20 is a decent framerate)')
        try:
            user_input = int(input())
            if (user_input < 2) or (user_input > time_length):
                print('The provided factor is too large or too small.')
                return define_param_n_factor(custom_initial)
            else:
                return user_input
        except ValueError:
            print('This cannot be cast to an int')
            return define_param_n_factor(custom_initial)
    else:
        return DEFAULT['FPS']

# Define the animation file name
def define_param_ani_file_name(custom_initial):
    if custom_initial:
        print('\nWhat will you call this animation?')
        return input()
    else:
        return DEFAULT['ANI_FILE_NAME']

# Define the color map
def define_param_cmap(custom_initial):
    if custom_initial:
        print('\nWould you like to see what color maps you can choose? (y/n)')
        user_input = input()
        if user_input[0].lower() == 'y':
            print_cmaps()
        print('\nWhich color map would you like to use?')
        user_input = input()
        if ALL_CMAPS.count(user_input) == 0:
            print('That is not a valid color map. Please select from: \n'
                    + str(ALL_CMAPS))
            return define_param_cmap(custom_initial)
        return user_input
    else:
        return DEFAULT['CMAP']

# Prints out all color maps that are defined
def print_cmaps():
    print('\nThe following are all available cmaps:\n\n')
    iii = 1
    for color in ALL_CMAPS:
        print(color + ', ', end='')
        if iii % 8 == 0:
            print()
        iii += 1
