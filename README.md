# OpenGATE Basic Examples

Small radiation physics simulations using OpenGATE 10 and Geant4.

## Installation

Requires Python 3.12. Tested on Windows with Python 3.12.7.

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Photons in water

`examples/photon_water.py`: a parallel beam of 511 keV photons
with a 2 cm radius enters a 10 × 10 × 10 cm water cube.

Reports particle statistics and deposited energy.
Set `sim.visu = True` to view geometry and tracks.

Run from the project root:
python examples/photon_water.py

## Photon attenuation

`examples/attenuation.py` simulates 511 keV photons passing
through water slabs of different thicknesses.

Plots direct transmission with statistical error bars and
fits an exponential curve. Example fit: μ ≈ 0.0966 cm⁻¹.

Run: python examples/attenuation.py

Plots, CSV data and ROOT files are saved in output/.

## Nuclear decay of radioisotopes inside a phantom

`examples/f18_water.py` simulates fluorine-18 uniformly distributed
inside a cylindrical plastic phantom.

Models radioactive decay to oxygen-18, positron transport and
annihilation, followed by transport of the resulting gamma photons.

$$
{}^{18}_{9}\mathrm{F} \rightarrow {}^{18}_{8}\mathrm{O} + e^{+} + \nu_e
$$

Run: python examples/f18_water.py


