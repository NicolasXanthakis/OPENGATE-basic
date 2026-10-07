import opengate as gate
from opengate.utility import g4_units

def run_sim():

    # Units
    cm = g4_units.cm
    keV = g4_units.keV

    # Sim settings
    sim =  gate.Simulation()
    sim.number_of_threads = 1
    sim.random_seed = 1
    sim.visu = True

    # World

    sim.world.size = [100 * cm, 100 * cm, 100 * cm]
    sim.world.material = "G4_AIR"

    # Plastic phantom: 10 cm diameter, 5 cm height (simplified Derenzo phantom)
    phantom = sim.add_volume("Tubs", "phantom")
    phantom.rmin = 0
    phantom.rmax = 5 * cm
    phantom.dz = 2.5 * cm
    phantom.material = "G4_PLEXIGLASS"
    phantom.color = [0.9, 0.3, 0.3, 0.3] #red

    # Positions of seven water-filled holes, in centimetres
    hole_positions = [
        [0, 0],
        [2, 0],
        [1, 1.73],
        [-1, 1.73],
        [-2, 0],
        [-1, -1.73],
        [1, -1.73],
    ]

    water_holes = []

    for i, (x, y) in enumerate(hole_positions):
        hole = sim.add_volume("Tubs", f"water_hole_{i}")
        hole.mother = phantom.name
        hole.rmin = 0
        hole.rmax = 0.5 * cm
        hole.dz = 2 * cm
        hole.translation = [x * cm, y * cm, 0]
        hole.material = "G4_WATER"
        hole.color = [0.2, 0.5, 1.0, 0.8]

        water_holes.append(hole)

    # Source
    n_ions_per_hole = 10

    for i, hole in enumerate(water_holes):
        source = sim.add_source("GenericSource", f"f18_source_{i}")
        source.attached_to = hole.name
        source.particle = "ion 9 18"
        source.n = n_ions_per_hole

        # Source coordinates 
        source.position.type = "cylinder"
        source.position.radius = hole.rmax
        source.position.dz = hole.dz

        # Parent nuclei are initially at rest, and decay immediately
        source.direction.type = "iso"
        source.energy.type = "mono"
        source.energy.mono = 0
        source.user_particle_life_time = 0


    # Physics
    sim.physics_manager.physics_list_name = (
        "G4EmStandardPhysics_option4"
    )
    sim.physics_manager.enable_decay = True

    # Stats
    stats = sim.add_actor("SimulationStatisticsActor", "stats")
    stats.track_types_flag = True


    # Run the simulation and print particle statistics
    sim.run()
    print(stats)

if __name__ == "__main__":
    run_sim()