"""Trajectory simulation and object rendering module."""

import copy
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
import matplotlib.pyplot as plt
import OpenEXR
import orekit
OREKIT_VM = orekit.initVM()  # pylint: disable=no-member
file_dir = Path(__file__).parent.resolve()
root_dir = (file_dir / ".." / "..").resolve()
orekit_data = root_dir / "data" / "orekit-data.zip"
from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir(str(orekit_data))
from org.orekit.time import AbsoluteDate, TimeScalesFactory  # pylint: disable=import-error
from org.hipparchus.geometry.euclidean.threed import Vector3D  # pylint: disable=import-error
from org.orekit.frames import FramesFactory  # pylint: disable=import-error
from org.orekit.utils import Constants, PVCoordinates  # pylint: disable=import-error
import skimage.filters
import skimage.transform
import simplejson as json
from mpl_toolkits.mplot3d import Axes3D

import simulation.render as render
import simulation.sc as sc
import simulation.sssb as sssb
import simulation.starcat as starcat
import utils

class Environment():
    """Simulation environment."""

    def __init__(self, name, duration):

        self.name = name
        self.res_path = utils.resolve_create_dir(root_dir / "data" / "results" / name)
        self.logger = utils.create_logger("simulation", self.res_path)

        self.ts = TimeScalesFactory.getTDB()
        self.encounter_date = AbsoluteDate(2017, 8, 19, 0, 0, 0.000, self.ts)
        self.duration = duration
        self.start_date = self.encounter_date.shiftedBy(-self.duration / 2.)
        self.end_date = self.encounter_date.shiftedBy(self.duration / 2.)

        self.ref_frame = FramesFactory.getICRF()
        self.mu_sun = Constants.IAU_2015_NOMINAL_SUN_GM

        self.frame_settings = dict()
        self.frame_settings["first"] = 0
        self.frame_settings["last"] = 2000
        self.frame_settings["step_size"] = 1

        self.logger.info("First frame: %d last frame: %d Step size: %d",
                    self.frame_settings['first'], self.frame_settings['last'],
                    self.frame_settings['step_size'])

        self.minimum_distance = 1E5
        self.with_terminator = True
        self.with_sunnyside = False
        self.timesampler_mode = 1
        self.slowmotion_factor = 10

        self.render_settings = dict()
        self.render_settings["exposure"] = 1.554
        self.render_settings["samples"] = 48
        self.render_settings["device"] = "Auto"
        self.render_settings["tile"] = 512
        self.render_settings["x_res"] = 2464
        self.render_settings["y_res"] = 2048
        self.render_settings["scene_names"] = ["MainScene",
                                               "BackgroundStars",
                                               "AsteroidOnly",
                                               "AsteroidConstDistance",
                                               "LightingReference"]

        self.camera_settings = dict()
        self.camera_settings["color_depth"] = "32"
        self.camera_settings["lens"] = 230
        self.camera_settings["sensor"] = 3.45E-3 * \
            self.render_settings["x_res"]

        self.logger.info("Rendering settings: Exposure: %d; Samples: %d",
                    self.render_settings['exposure'], self.render_settings['samples'])

        # Setup SSSB
        self.sssb = sssb.Sssb("Didymos", self.mu_sun, AbsoluteDate(
            2017, 8, 19, 0, 0, 0.000, self.ts))


        # Setup SC
        state = self.calc_sc_encounter_state()
        self.spacecraft = sc.Spacecraft(
            "CI", self.mu_sun, state, self.encounter_date)


    def simulate(self):
        """Do simulation."""
        self.logger.info("Starting simulation")

        self.sssb.setup_timesampler(
            self.start_date, self.end_date, self.frame_settings["last"],
            self.timesampler_mode, self.slowmotion_factor)
        self.spacecraft.setup_timesampler(
            self.start_date, self.end_date, self.frame_settings["last"],
            self.timesampler_mode, self.slowmotion_factor)

        self.logger.info("Propagating SSSB")
        self.sssb.propagator.propagate(self.start_date, self.end_date)

        self.logger.info("Propagating Spacecraft")
        self.spacecraft.propagator.propagate(self.start_date, self.end_date)

        self.logger.info("Simulation completed")

        self.save_results()

    def render(self):
        """Render simulation scenario."""
        self.logger.info("Rendering simulation")

        render_dir = utils.resolve_create_dir(self.res_path / "rendering")

        renderer = render.BlenderController(render_dir, self.render_settings["scene_names"])
        renderer.set_renderer()

        self.logger.info("Rendering completed")

    def save_results(self):
        """Save simulation results to a file."""
        self.logger.info("Saving propagation results")

        with open(str(self.res_path / "PositionHistory.txt"), "w+") as file:
            for (date, sc_pos, sssb_pos) in zip(self.spacecraft.date_history,
                                                self.spacecraft.pos_history,
                                                self.sssb.pos_history):

                sc_pos = np.asarray(sc_pos.toArray())
                sssb_pos = np.asarray(sssb_pos.toArray())

                file.write(str(date) + "\t" + str(sssb_pos) + "\t"
                           + str(sc_pos) + "\n")

        self.logger.info("Propagation results saved")

    def calc_sc_encounter_state(self):
        """Calculate the sc state during encounter relative to SSSB."""
        pos, vel = self.sssb.get_state(self.encounter_date)

        sc_pos = self.calc_sc_encounter_pos(pos)

        sc_vel = vel.scalarMultiply((vel.getNorm() - 10000.) / vel.getNorm())

        self.logger.info("Spacecraft relative velocity: %s", sc_vel)
        self.logger.info("Spacecraft distance from sun: %s",
                         sc_pos.getNorm()/Constants.IAU_2012_ASTRONOMICAL_UNIT)

        return PVCoordinates(sc_pos, sc_vel)

    def calc_sc_encounter_pos(self, pos):
        """Calculate the sc position during encounter relative to SSSB."""
        sssb_direction = pos.normalize()

        if not self.with_terminator:
            if not self.with_sunnyside:
                self.minimum_distance *= -1

            sssb_direction = sssb_direction.scalarMultiply(
                self.minimum_distance)
            sc_pos = pos.subtract(sssb_direction)

        else:
            shift = sssb_direction.scalarMultiply(-0.15)
            shift = shift.add(Vector3D(0., 0., 1.))
            shift = shift.normalize()
            shift = shift.scalarMultiply(self.minimum_distance)
            sc_pos = pos.add(shift)
        return sc_pos


if __name__ == "__main__":
    env = Environment("Didymos", 2 * 60.)
    env.simulate()
