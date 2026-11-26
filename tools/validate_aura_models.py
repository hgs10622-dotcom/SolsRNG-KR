#!/usr/bin/env python3
"""Validate every generated aura GLB and write a deployment manifest."""
from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "supabase" / "aura_catalog.json"
ASSET_DIR = ROOT / "assets" / "aura"
MANIFEST = ASSET_DIR / "manifest.json"
EXPECTED_MODELS = 1000
JSON_CHUNK = 0x4E4F534A


def read_glb(path: Path) -> tuple[dict, int, str]:
    raw = path.read_bytes()
    if len(raw) < 20:
        raise ValueError("file is too small to be a GLB")
    magic, version, declared_length = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(raw):
        raise ValueError("invalid GLB v2 header or length")

    chunk_length, chunk_type = struct.unpack_from("<II", raw, 12)
    if chunk_type != JSON_CHUNK or 20 + chunk_length > len(raw):
        raise ValueError("missing or invalid GLB JSON chunk")
    document = json.loads(raw[20:20 + chunk_length].decode("utf-8"))
    meshes = document.get("meshes", [])
    if not meshes:
        raise ValueError("GLB contains no meshes")

    position_accessors = []
    for mesh in meshes:
        for primitive in mesh.get("primitives", []):
            accessor_index = primitive.get("attributes", {}).get("POSITION")
            if accessor_index is None:
                continue
            accessors = document.get("accessors", [])
            if accessor_index >= len(accessors):
                raise ValueError("mesh references a missing POSITION accessor")
            accessor = accessors[accessor_index]
            if "min" in accessor and "max" in accessor:
                position_accessors.append((accessor["min"], accessor["max"]))
    if not position_accessors:
        raise ValueError("GLB has no bounded vertex-position accessors")

    mins = [min(float(bounds[0][axis]) for bounds in position_accessors) for axis in range(3)]
    maxs = [max(float(bounds[1][axis]) for bounds in position_accessors) for axis in range(3)]
    if not all(math.isfinite(v) for v in mins + maxs):
        raise ValueError("model bounds contain non-finite values")
    if any(maxs[i] - mins[i] <= 0 for i in range(3)):
        raise ValueError("model has a zero-sized axis")

    return document, len(meshes), hashlib.sha256(raw).hexdigest()


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    ids = [item["id"] for item in catalog]
    if len(catalog) != EXPECTED_MODELS or len(set(ids)) != EXPECTED_MODELS:
        raise SystemExit(f"catalog must contain {EXPECTED_MODELS} unique aura IDs")

    entries = []
    seen_hashes: dict[str, str] = {}
    failures = []
    for index, aura in enumerate(catalog, 1):
        aura_id = aura["id"]
        path = ASSET_DIR / f"{aura_id}.glb"
        try:
            if not path.is_file():
                raise ValueError("model file is missing")
            if path.stat().st_size < 512:
                raise ValueError("model file is unexpectedly small")
            document, mesh_count, digest = read_glb(path)
            previous = seen_hashes.get(digest)
            if previous:
                raise ValueError(f"identical model bytes to {previous}")
            seen_hashes[digest] = aura_id

            accessors = document.get("accessors", [])
            bounds = [
                [min(float(a["min"][axis]) for a in accessors if a.get("type") == "VEC3" and "min" in a),
                 max(float(a["max"][axis]) for a in accessors if a.get("type") == "VEC3" and "max" in a)]
                for axis in range(3)
            ]
            entries.append({
                "id": aura_id,
                "name": aura.get("name", aura_id),
                "rarity": aura.get("rarity", ""),
                "tier": int(aura.get("tier", 0)),
                "file": f"{aura_id}.glb",
                "bytes": path.stat().st_size,
                "mesh_count": mesh_count,
                "sha256": digest,
                "position_bounds": bounds,
            })
        except Exception as exc:
            failures.append(f"{aura_id}: {exc}")
        if index % 100 == 0:
            print(f"validated {index}/{EXPECTED_MODELS}")

    if failures:
        raise SystemExit("GLB validation failed:\n" + "\n".join(failures[:30]))
    if len(entries) != EXPECTED_MODELS or len(seen_hashes) != EXPECTED_MODELS:
        raise SystemExit("not all models are present and byte-distinct")

    MANIFEST.write_text(
        json.dumps({"model_count": len(entries), "models": entries}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Validated {len(entries)} unique GLB models; wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
