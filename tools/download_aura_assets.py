#!/usr/bin/env python3
"""Download pinned CC0 crystal GLBs used as optional outer-aura geometry."""
from pathlib import Path
from urllib.request import Request, urlopen

OUT = Path("assets/aura/external")
OUT.mkdir(parents=True, exist_ok=True)

ASSETS = {
    "violet-crystal-cluster.glb": "https://tevy.dev/models/violet-crystal-cluster/v1/lod0.glb",
    "cyan-crystal-shard.glb": "https://tevy.dev/models/cyan-crystal-shard/v1/lod0.glb",
}

for filename, url in ASSETS.items():
    target = OUT / filename
    request = Request(url, headers={"User-Agent": "AETHER-RNG-asset-builder/1.0"})
    with urlopen(request, timeout=45) as response:
        data = response.read()
    if len(data) < 32 or data[:4] != b"glTF":
        raise SystemExit(f"Invalid GLB received for {filename} ({len(data)} bytes)")
    target.write_bytes(data)
    print(f"Downloaded {filename}: {len(data):,} bytes")

(OUT / "ASSET-LICENSES.txt").write_text(
    "Outer aura crystal accents\n"
    "Violet Crystal Cluster — CC0 1.0 Universal\n"
    "Source: https://tevy.dev/models/violet-crystal-cluster\n"
    "Cyan Crystal Shard — CC0 1.0 Universal\n"
    "Source: https://tevy.dev/models/cyan-crystal-shard\n"
    "Both source assets are redistributed under CC0 1.0.\n",
    encoding="utf-8",
)
