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
- exifread (for orientation correction)

Notes:
- If double-clicking the EXE, a prompt at the end will keep the console open.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Iterable, Optional


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


def _save_jpeg_array(arr, out_path: Path, quality: int) -> Path:
	from PIL import Image  # type: ignore
	import exifread  # type: ignore

	img = Image.fromarray(arr)

	# Try to read EXIF orientation from the NEF file and apply it
	try:
		nef_path = out_path.with_suffix('.nef')
		if nef_path.exists():
			with open(nef_path, 'rb') as f:
				tags = exifread.process_file(f, stop_tag="Orientation", details=False)
				orientation = tags.get("Image Orientation")
				if orientation:
					val = str(orientation)
					if val == "Rotated 180":
						img = img.rotate(180, expand=True)
					elif val == "Rotated 90 CW":
						img = img.rotate(270, expand=True)
					elif val == "Rotated 90 CCW":
						img = img.rotate(90, expand=True)
					elif val == "Mirrored":
						img = img.transpose(Image.FLIP_LEFT_RIGHT)
					elif val == "Mirrored horizontal and rotated 90 CW":
						img = img.transpose(Image.FLIP_TOP_BOTTOM).rotate(270, expand=True)
					elif val == "Mirrored horizontal and rotated 90 CCW":
						img = img.transpose(Image.FLIP_TOP_BOTTOM).rotate(90, expand=True)
					elif val == "Mirrored vertical":
						img = img.transpose(Image.FLIP_TOP_BOTTOM)
	except Exception:
		pass  # If exifread or orientation fails, just save as is

	target = unique_path(out_path.with_suffix(".jpg"))
	target.parent.mkdir(parents=True, exist_ok=True)
	img.save(target, format="JPEG", quality=quality, optimize=True, subsampling=0)
	return target


def _try_raw_full(raw, out_path: Path, quality: int) -> Optional[Path]:
	try:
		rgb = raw.postprocess(
			use_auto_wb=True,
			no_auto_bright=True,
			output_bps=8,
			gamma=(2.222, 4.5),
		)
		return _save_jpeg_array(rgb, out_path, quality)
	except Exception:
		return None


def _try_raw_half(raw, out_path: Path, quality: int) -> Optional[Path]:
	try:
		rgb = raw.postprocess(
			use_auto_wb=True,
			no_auto_bright=True,
			output_bps=8,
			half_size=True,
		)
		return _save_jpeg_array(rgb, out_path, quality)
	except Exception:
		return None


def _try_libraw_thumb(raw, out_path: Path) -> Optional[Path]:
	import rawpy  # type: ignore

	try:
		thumb = raw.extract_thumb()
		target = unique_path(out_path.with_suffix(".jpg"))
		target.parent.mkdir(parents=True, exist_ok=True)
		if getattr(thumb, "format", None) == getattr(rawpy, "ThumbFormat").JPEG:
			with open(target, "wb") as f:
				f.write(thumb.data)
			return target
		else:
			# Some thumbnails are RGB arrays
			return _save_jpeg_array(thumb.data, out_path, 90)
	except Exception:
		return None


def _try_scan_embedded_jpeg(in_path: Path, out_path: Path) -> Optional[Path]:
	data = in_path.read_bytes()
	soi = b"\xFF\xD8\xFF"
	eoi = b"\xFF\xD9"
	starts = []
	i = 0
	while True:
		j = data.find(soi, i)
		if j == -1:
			break
		starts.append(j)
		i = j + 1

	candidates: list[tuple[int, int]] = []
	for s in starts:
		j = data.find(eoi, s + 2)
		if j != -1:
			candidates.append((s, j + len(eoi)))

	if candidates:
		s, e = max(candidates, key=lambda p: p[1] - p[0])
		target = unique_path(out_path.with_suffix(".jpg"))
		target.parent.mkdir(parents=True, exist_ok=True)
		with open(target, "wb") as f:
			f.write(data[s:e])
		return target
	return None


def convert_nef_to_jpg(in_path: Path, out_path: Path, quality: int = 90, mode: str = "auto", verbose: bool = False) -> None:
	"""Convert a single NEF to JPG.

	mode:
	  - auto: try RAW decode then fallbacks
	  - raw: only RAW decode attempts
	  - embedded: only embedded JPEG extraction attempts
	"""
	import rawpy  # type: ignore

	if verbose:
		print(f"Converting: {in_path}")

	out_path = out_path.with_suffix(".jpg")

	if mode in ("auto", "raw"):
		try:
			with rawpy.imread(str(in_path)) as raw:
				if verbose:
					print(" - Trying RAW full postprocess…")
				p = _try_raw_full(raw, out_path, quality)
				if p:
					return
				if verbose:
					print(" - RAW full failed; trying RAW half-size…")
				p = _try_raw_half(raw, out_path, quality)
				if p:
					return
				if mode == "raw":
					raise RuntimeError("RAW-only mode failed (full and half-size).")
				if verbose:
					print(" - RAW half failed; trying LibRaw thumbnail…")
				p = _try_libraw_thumb(raw, out_path)
				if p:
					return
		except Exception as e:
			if verbose:
				print(f" - RAW open/processing failed: {e}")

	if mode in ("auto", "embedded"):
		if verbose:
			print(" - Trying embedded JPEG scan…")
		p = _try_scan_embedded_jpeg(in_path, out_path)
		if p:
			return
		if mode == "embedded":
			raise RuntimeError("Embedded-only mode failed to locate a JPEG.")

	raise RuntimeError("All conversion attempts failed.")


def main() -> int:
	import argparse

	parser = argparse.ArgumentParser(description="NEF to JPG Converter")
	parser.add_argument("--mode", choices=["auto", "raw", "embedded"], default="auto", help="Conversion strategy")
	parser.add_argument("--quality", type=int, default=90, help="JPEG quality (1-100)")
	parser.add_argument("--verbose", action="store_true", help="Verbose output")
	args = parser.parse_args()

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
			convert_nef_to_jpg(nef, out_path, quality=args.quality, mode=args.mode, verbose=args.verbose)
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

