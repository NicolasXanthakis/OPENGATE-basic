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