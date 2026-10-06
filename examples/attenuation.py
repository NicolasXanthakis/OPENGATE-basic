from pathlib import Path

import opengate as gate
from opengate.utility import g4_units

import uproot
import numpy as np

import matplotlib.pyplot as plt


def run_sim(thickness_cm, n_photons=10_000, seed=42):
    cm = g4_units.cm
    keV = g4_units.keV

    thickness_cm = thickness_cm
    n_photons = n_photons

    sim = gate.Simulation()
    sim.number_of_threads = 1
    sim.random_seed = seed
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

    sim.run(start_new_process=True)
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

    return transmission      

if __name__ == "__main__":
    thicknesses = np.array([1, 2, 5, 10, 15, 20])
    n_photons = 10_000

    transmissions = np.array([
        run_sim(float(thickness), n_photons, seed=42 + i)
        for i, thickness in enumerate(thicknesses)
    ])

    # Binomial statistical uncertainty: one standard deviation
    errors = np.sqrt(
        transmissions * (1 - transmissions) / n_photons
    )

    # Fit T = exp(-mu*x), constrained to T(0) = 1
    # Weighted fit in logarithmic space
    weights = (transmissions / errors) ** 2
    mu = -np.sum(
        weights * thicknesses * np.log(transmissions)
    ) / np.sum(weights * thicknesses**2)

    print(f"\nFitted attenuation coefficient: {mu:.4f} cm^-1")

    x = np.linspace(0, thicknesses.max(), 200)

    fig, ax = plt.subplots()
    ax.errorbar(
        thicknesses, transmissions,
        yerr=errors, fmt="o", capsize=4,
        label="Simulation ± 1σ",
    )
    ax.plot(
        x, np.exp(-mu * x),
        label=f"Exponential fit: μ = {mu:.4f} cm⁻¹",
    )
    ax.set(
        xlabel="Water thickness (cm)",
        ylabel="Direct photon transmission",
        title="511 keV photon attenuation in water",
        ylim=(0, 1.05),
    )
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()

    output_dir = Path(__file__).resolve().parents[1] / "output"
    fig.savefig(output_dir / "attenuation.png", dpi=200)

    np.savetxt(
        output_dir / "attenuation.csv",
        np.column_stack((thicknesses, transmissions, errors)),
        delimiter=",",
        header="thickness_cm,transmission,standard_error",
        comments="",
    )

    plt.show()