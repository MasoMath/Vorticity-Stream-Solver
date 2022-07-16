'''
Gianluca Gisolo

This file contains the methods needed to construct the initial conditions,
construct the needed differential matricies, and handles the solving of the
given (non-stiff) Vorticity PDE assuming periodic boundary conditions using
a Stream function and a RK45 solver.
'''
import numpy as np
from scipy.integrate import solve_ivp
import scipy.fft as fft
from scipy import sparse

def FFTsolver(n, tspan, initial_conditions, endpt=10, custom_initial=False, random_initial=False):
    """
    Parameters
    -------------
    n : int
        The power of which 2 will be raise to. i.e. 2^n. This determines the
        number of points used in the domain as it will be (2^n)^2
    tspan : NDArray
        The points in time the solver will solve for
    initial_conditions : list (of lists of floats)
        A list containing all the information that will be used to construct
        the initial conditions
    endpt : int, optional
        Determines the boundary of our domain. By default our domain will be a
        square from (-10,-10) to (10,10)
    custom_initial : bool, optional
        Determines if there are custom initial conditions to use instead of the
        default conditions
    random_initial : bool, optional
        Determines if there were any initial conditions that were randomly
        generated.
    
    Returns
    -------
    The solution to the periodic BVP and the domains as [z, x, y].
    z : NDArray
        This will be a len(tspan) x 2^(n+1) array of solutions where each row
        is a different time  
    x : NDArray
        This will be a 2^n x 2^n array of all x domain values
    y : NDArray
        This will be a 2^n x 2^n array of all y domain values
    """

    # declare constants / tolerances
    nu = 0.001
    tol = 1e-6
    
    # domain setup
    xDom = np.linspace(-endpt, endpt, n+1)
    delta = xDom[1]-xDom[0]
    xDom = xDom[0:n]
    [xDom, yDom] = np.meshgrid(xDom,xDom)
    
    # Initial condition setup
    if custom_initial or random_initial:
        omegaInitial = _constructInitialCon(xDom, yDom, initial_conditions)
    else:
        f = lambda x, y: _eFunc(x,y,[-2,-2,1,1]) + _eFunc(x,y,[2,2,1,1]) - _eFunc(x,y,[-2,2,1,1]) - _eFunc(x,y,[2,-2,1,1])
        omegaInitial = f(xDom, yDom)
    omegaInitial = np.reshape(omegaInitial,(n**2,))
    
    # Finite difference matrix setup
    [xPartial, yPartial, Lap] = periodicDiff(n, delta)
    Lap[0, 0] = -0.5 * Lap[0, 0]
    
    # Setting up kx and ky constants
    # i.e. goes through -n/2 to n/2-1 in steps of 1,
    # but it's shifted so that kx[0] = 0 and kx[n/2] = -n/2
    kx = (np.pi / endpt) * np.roll(np.linspace( -0.5 * n, n * 0.5 - 1, n, dtype=int),
                                                int(0.5 * n))
    kx[0] = tol
    ky = kx
    [kx, ky] = np.meshgrid(kx, ky)
    
    # tolerance contrants for ivp solver
    options = {"rtol": tol, "atol": tol}
    
    # Solving vorticity-stream fxn using fft
    sol = solve_ivp(vortStreamFFT, [tspan[0], tspan[-1]], omegaInitial, t_eval=tspan,
                    args=(nu, xPartial, yPartial, Lap, n, kx, ky),
                    rtol=tol, atol=tol)
    return [sol.y.transpose(), xDom, yDom]

def periodicDiff(n, delta):
    """
    Calculates x and y partials for X and Y differentials in [psi, omega],
    as well as calculates the Laplacian operator Lap.
    """
    # Calculates x and y partials for X and Y differentials in [psi, omega]
    # Calculates Laplacian operator as Lap
    # Assumes periodic BC
    n2 = n**2
    A_D = -4 * sparse.eye(n2, dtype=int)
    Y = sparse.diags([1, -1, 1, -1],[1-n,-1, 1,n-1],shape=[n,n],dtype=int)
    Y = [Y for i in range(n)]
    Y = sparse.block_diag(Y, dtype=int)
    X = sparse.diags([1, -1, 1, -1], [n-n2, -n, n, n2-n],shape=[n2, n2], dtype=int)
    Lap = A_D + abs(X) + abs(Y)
    
    X = X * 0.5 / delta
    Y = Y * 0.5 / delta
    Lap = Lap / (delta**2)
    return [X, Y, Lap]

# Vorticity-Stream fxn using fft
# returns dOmega i.e. the change in omega
def vortStreamFFT(t, omega, nu, xPartial, yPartial, Lap, n, kx, ky):
    """
    This is Vorticity-Stream function using fft to calculate what psi will be
    Returns dOmega (i.e. what the change in omega is)
    """
    
    # reshaping and fft2
    omegaHat = np.reshape(omega,(n,n))
    omegaHat = fft.fft2(omegaHat)
    
    # ifft2 and reshaping
    phiHat = - omegaHat / ( np.square(kx) + np.square(ky) )
    phi = fft.ifft2(phiHat)
    phi = np.reshape(phi, (n**2,)).real

    # Calculates [psi, omega]
    block1 = (xPartial @ phi) * (yPartial @ omega)
    block2 = (yPartial @ phi) * (xPartial @ omega)
    phiOmega = block1 - block2

    return (nu * (Lap @ omega)) - phiOmega
    
# function for easily making vorticities for initial condition
def _eFunc(x, y, para):
    
    xShift = para[0]
    yShift = para[1]
    xScale = para[2]
    yScale = para[3]
    
    return np.exp( (- ( (x - xShift)**2 ) / xScale) - ( ( (y - yShift)**2 ) / yScale) )

# Constructs initial conditions using given list of vorticities
def _constructInitialCon(x, y, initial_conditions):
    f = np.zeros(x.shape)
    for con in initial_conditions:
        neg = 0 # this is to track the orientation of the vorticity
        if con[2] < 0:
            con[2] = abs(con[2])
            neg += 1
        if con[3] < 0:
            con[3] = abs(con[3])
            neg += 1
        if neg > 0:
            f -= _eFunc(x, y, con)
        else:
            f += _eFunc(x, y, con)
    return f