import opengate as gate
from opengate.utility import g4_units
import itk
import numpy as np


def run_sim():
    cm = g4_units.cm
    keV = g4_units.keV

    sim = gate.Simulation()
    sim.number_of_threads = 1
    sim.random_seed = 1
    sim.visu = True

    # Particle track colors: 
    # Green: gamma 
    # Red: e-
    # Blue: e+

    # World: 1m3 cube
    sim.world.size = [100 * cm] * 3
    sim.world.material = "G4_AIR"

    # Water: 10 cm3 cube
    water = sim.add_volume("Box", "water")
    water.size = [10 * cm] * 3
    water.material = "G4_WATER"
    water.color = [0.2, 0.5, 1.0, 0.4]

    # Fire n photons towards the water along +Z
    source = sim.add_source("GenericSource", "photons")
    source.particle = "gamma"
    n_photons = 1000
    source.n = n_photons # gets converted to array internally
    source.position.type = "disc"
    source.position.radius = 2 * cm
    source.position.translation = [0, 0, -10 * cm]
    source.direction.type = "momentum"
    source.direction.momentum = [0, 0, 1]
    source.energy.type = "mono"
    source.energy.mono = 511 * keV

    # Physics
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

    stats = sim.add_actor("SimulationStatisticsActor", "stats")
    stats.track_types_flag = True

    E_dep = sim.add_actor("DoseActor", "water_edep")
    E_dep.attached_to = water.name
    E_dep.size = [1, 1, 1] # nr of voxels along X,Y and Z
    E_dep.spacing = [10 * cm, 10 * cm, 10 * cm] # physical size of each voxels
    E_dep.edep.write_to_disk = False 

    sim.run()
    print(stats)

    image = E_dep.edep.get_data()
    total_keV = np.sum(itk.array_from_image(image)) / keV

    print(f"Total deposited energy: {total_keV:.2f} keV")
    print(f"Mean per source photon: {total_keV / n_photons:.2f} keV")


if __name__ == "__main__":
    run_sim()