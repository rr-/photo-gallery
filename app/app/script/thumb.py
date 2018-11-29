#!/usr/bin/env python3
import typing as T
from pathlib import Path

from app.const import IMG_DIR, IMG_EXT, THUMB_DIR, THUMB_SIZES
from app.thumb import gen_thumb


def collect_images() -> T.Iterable[Path]:
    dirs = [IMG_DIR]
    while dirs:
        root = dirs.pop()
        for child in sorted(root.iterdir(), key=lambda child: child.name):
            if child.is_dir():
                dirs.append(child)
            elif child.is_file() and child.suffix.lower() in IMG_EXT:
                yield child


def main() -> None:
    for src_path in collect_images():
        for width, height in THUMB_SIZES:
            dst_path = (
                THUMB_DIR / f"{width}x{height}" / src_path.relative_to(IMG_DIR)
            )
            print(src_path, "→", dst_path, end="… ")
            try:
                gen_thumb(src_path, dst_path, width, height)
                print("ok")
            except OSError as ex:
                print(f"error ({ex})")


if __name__ == "__main__":
    main()
