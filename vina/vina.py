"""
The vina package provides functions to do VIsual NAvigation studies

The package creates images of a 3D object using blender. The images are render
in a flyby scenario. UCAC4 star catalogue to create the background. Afterwards
hese images are used with openMVG and openMVS to reconstruct the 3D model and
reconstruct the trajectory.
"""

import starcatalogue.starcatalogue as starcatalogue
import trajectory_simulator.trajectory_simulator as trajectory_simulator