from pathlib import Path

import opengate as gate
from opengate.utility import g4_units

import uproot
import numpy as np


def run_sim():
    cm = g4_units.cm
    keV = g4_units.keV

    thickness_cm = 10
    n_photons = 10_000

    sim = gate.Simulation()
    sim.number_of_threads = 1
    sim.random_seed = 42
    sim.visu = False

    # Save outputs in the project's output folder
    output_dir = Path(__file__).resolve().parents[1] / "output"
    output_dir.mkdir(exist_ok=True)
    sim.output_dir = output_dir

    # Vacuum isolates interactions in the water
    sim.world.size = [100 * cm] * 3
    sim.world.material = "G4_Galactic"

    # Water slab
    water = sim.add_volume("Box", "water")
    water.size = [10 * cm, 10 * cm, thickness_cm * cm]
    water.material = "G4_WATER"
    water.color = [0.2, 0.5, 1.0, 0.4]

    # Parallel circular photon beam
    source = sim.add_source("GenericSource", "photons")
    source.particle = "gamma"
    source.n = n_photons
    source.position.type = "disc"
    source.position.radius = 2 * cm
    source.position.translation = [
        0, 0, -(thickness_cm / 2 + 5) * cm
    ]
    source.direction.type = "momentum"
    source.direction.momentum = [0, 0, 1]
    source.energy.type = "mono"
    source.energy.mono = 511 * keV

    sim.physics_manager.physics_list_name = (
        "G4EmStandardPhysics_option4"
    )

    # Scoring plane behind the water
    plane = sim.add_volume("Box", "scoring_plane")
    plane.size = [10 * cm, 10 * cm, 0.01 * cm]
    plane.translation = [
        0, 0, (thickness_cm / 2 + 1) * cm
    ]
    plane.material = "G4_Galactic"

    # Record particles entering the plane
    phsp = sim.add_actor("PhaseSpaceActor", "transmission")
    phsp.attached_to = plane.name
    phsp.steps_to_store = "entering"
    phsp.attributes = [
        "ParticleName",
        "PreKineticEnergy",
        "PreDirection",
        "EventID",
        "TrackID",
        "ParentID",
    ]
    phsp.output_filename = f"transmission_{thickness_cm}cm.root"

    stats = sim.add_actor("SimulationStatisticsActor", "stats")
    stats.track_types_flag = True

    sim.run()
    print(stats)
    print(f"Water thickness: {thickness_cm} cm")
    print(f"Source photons: {n_photons}")
    print(f"Results folder: {output_dir}")

    root_path = output_dir / f"transmission_{thickness_cm}cm.root"

    with uproot.open(root_path) as file:
        print("Trees:", file.keys())
        tree = file["transmission"]
        print("Columns:", tree.keys())
        print("Recorded entries:", tree.num_entries)

        data = tree.arrays(library="np")

        # Select primary photons retaining their initial energy and direction
        direct = (
            (data["ParentID"] == 0)
            & np.isclose(
                data["PreKineticEnergy"], 511 * keV,
                rtol=0, atol=1e-6 * keV
            )
            & (np.abs(data["PreDirection_X"]) < 1e-8)
            & (np.abs(data["PreDirection_Y"]) < 1e-8)
            & (np.abs(data["PreDirection_Z"] - 1) < 1e-8)
        )

        # Count each source event once
        n_direct = len(np.unique(data["EventID"][direct]))
        transmission = n_direct / n_photons

        print(f"Direct photons: {n_direct}")
        print(f"Transmission: {transmission:.2%}")        

if __name__ == "__main__":
    run_sim()