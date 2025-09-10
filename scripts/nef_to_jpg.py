"""
NEF to JPG Converter

Behavior:
- When run as a bundled EXE dropped into any folder, it scans that folder (and subfolders)
  for .NEF files, creates a "results" directory, and writes converted JPGs there while
  preserving the relative subfolder structure. Originals are never deleted or modified.
- When run as a script via Python, it scans the current working directory.

Dependencies:
- rawpy (LibRaw bindings) for decoding NEF
- Pillow (PIL) for saving JPEG

Notes:
- If double-clicking the EXE, a prompt at the end will keep the console open.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Iterable


def is_frozen() -> bool:
	return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
	# For packaged EXE, use the EXE location; for script, use the working directory
	if is_frozen():
		return Path(sys.executable).resolve().parent
	return Path.cwd()


def iter_nef_files(root: Path) -> Iterable[Path]:
	for dirpath, dirnames, filenames in os.walk(root):
		# Skip the results folder itself if it already exists
		if Path(dirpath) == (root / "results"):
			continue
		for name in filenames:
			if name.lower().endswith(".nef"):
				yield Path(dirpath) / name


def unique_path(path: Path) -> Path:
	if not path.exists():
		return path
	base = path.with_suffix("")
	suffix = path.suffix
	i = 1
	while True:
		cand = base.with_name(f"{base.name}_{i}").with_suffix(suffix)
		if not cand.exists():
			return cand
		i += 1


def convert_nef_to_jpg(in_path: Path, out_path: Path, quality: int = 90) -> None:
	import rawpy  # type: ignore
	from PIL import Image  # type: ignore

	with rawpy.imread(str(in_path)) as raw:
		rgb = raw.postprocess(
			use_auto_wb=True,
			no_auto_bright=True,  # avoid auto brightening that can blow highlights
			output_bps=8,
			gamma=(2.222, 4.5),
		)
	img = Image.fromarray(rgb)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path = unique_path(out_path)
	img.save(out_path, format="JPEG", quality=quality, optimize=True, subsampling=0)


def main() -> int:
	base_dir = get_base_dir()
	results_dir = base_dir / "results"
	results_dir.mkdir(exist_ok=True)

	print(f"Scanning for NEF files under: {base_dir}")
	nef_files = list(iter_nef_files(base_dir))
	if not nef_files:
		print("No NEF images found. Nothing to do.")
		if is_frozen():
			input("Press Enter to close...")
		return 0

	total = len(nef_files)
	print(f"Found {total} NEF file(s). Converting to: {results_dir}")

	ok = 0
	failed = 0
	for idx, nef in enumerate(nef_files, start=1):
		try:
			rel = nef.parent.relative_to(base_dir)
			out_dir = results_dir / rel
			out_path = out_dir / (nef.stem + ".jpg")
			print(f"[{idx}/{total}] {nef} -> {out_path}")
			convert_nef_to_jpg(nef, out_path)
			ok += 1
		except Exception as e:  # keep going on errors
			failed += 1
			print(f"ERROR: failed to convert {nef}: {e}")

	print(f"Done. Converted: {ok}, Failed: {failed}. Output in: {results_dir}")
	if is_frozen():
		input("Press Enter to close...")
	return 0 if failed == 0 else 1


if __name__ == "__main__":
	raise SystemExit(main())

