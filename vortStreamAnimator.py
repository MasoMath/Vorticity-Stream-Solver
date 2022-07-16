'''
Gianluca Gisolo

3D animator for Vorticity-Stream fxn solutions
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# function for creating visuals
def createAnimated3DPlot(xDom, yDom, zValues, endpt, n,
                            ani_file_name='vort_stream_solution',
                            fps=20, frameNum=20, cmap='viridis'
                            ):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # Setting bounds, view angle, and removing labels
    ax.axes.set_xlim3d(-endpt, endpt)
    ax.axes.set_ylim3d(-endpt, endpt)
    ax.axes.set_zlim3d(-3, 3)
    ax.axes.set_zticklabels([])
    plt.xticks(color='w')
    plt.yticks(color='w')

    # creates initial state and allocates plot into memory
    plot = [ax.plot_surface(xDom, yDom, np.reshape(zValues[0], (n,n)),
                            color='0.75', rstride=1, cstride=1
                            )]

    # Creates animation
    ani = FuncAnimation(fig, _updateAnimation, frameNum, 
                        fargs=(xDom, yDom, zValues, n, plot, ax, cmap),
                        interval=1000/fps)
    ani.save('./animations/' + ani_file_name +'.mp4',writer='ffmpeg',fps=fps)

# update animation function
def _updateAnimation(frame_number, xDom, yDom, zValues, n, plot, ax, cmap):
    plot[0].remove()
    plot[0] = ax.plot_surface(xDom, yDom, np.reshape(zValues[frame_number], (n,n)), 
                                cmap=cmap)