"""Batch-run the Sentinel-1 preprocessing graph on every GRD .zip in a folder, then mosaic.

Scenes: Sentinel-1 EW/IW GRD, HH polarisation, March 2020 and March 2024, over the
Barents Sea south of Svalbard, downloaded from ASF Vertex (search.asf.alaska.edu).
Requires ESA SNAP (gpt on the PATH) and GDAL for the mosaic.

Usage:
    python scripts/snap/run_snap_batch.py data/raw/s1_march2024 outputs/s1_march2024

The monthly mosaic merges scenes acquired on different dates, so its seams are
temporal, not radiometric (thesis §4.1).
"""
import subprocess
import sys
from pathlib import Path

GRAPH = Path(__file__).with_name("s1_grd_preprocessing.xml")


def main(src_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for scene in sorted(src_dir.glob("S1*_GRD*.zip")):
        target = out_dir / f"{scene.stem}_sigma0_db.tif"
        if not target.exists():
            print(f"processing {scene.name}")
            subprocess.run(["gpt", str(GRAPH), f"-Pinput={scene}", f"-Poutput={target}"], check=True)
        outputs.append(str(target))
    if not outputs:
        sys.exit(f"no Sentinel-1 GRD zip found in {src_dir}")
    mosaic = out_dir / f"{out_dir.name}_mosaic.vrt"
    subprocess.run(["gdalbuildvrt", str(mosaic), *outputs], check=True)
    print(f"{len(outputs)} scenes -> {mosaic}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
