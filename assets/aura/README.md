# Original Aura GLB Assets

This directory is populated during the GitHub Pages build by `tools/generate_aura_models.py`.

The build creates one GLB per catalog entry (1,000 total), then `tools/validate_aura_models.py` validates the GLB files and writes `manifest.json`. Generated binary assets are deployment artifacts and are not committed individually to the source repository.

Each model is authored from its own catalog name, description, color palette, and rarity tier. The models are loaded by the web app on demand.
