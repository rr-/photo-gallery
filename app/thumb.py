from pathlib import Path
import typing as T

from flask import abort, send_file
from PIL import Image

from .app import app
from .const import IMG_DIR, IMG_EXT, THUMB_DIR, THUMB_SIZES


def gen_thumb(
    src_path: Path, dst_path: Path, min_width: int, min_height: int
) -> None:
    if dst_path.exists():
        return

    image = Image.open(src_path)

    ratio = max(min_width / image.size[0], min_height / image.size[1])
    new_width = int(image.size[0] * ratio)
    new_height = int(image.size[1] * ratio)
    image = image.resize((new_width, new_height), Image.ANTIALIAS)

    dst_path.parent.mkdir(exist_ok=True, parents=True)
    image.save(str(dst_path), quality=75)


@app.route("/static/thumb/<int:min_width>x<int:min_height>/<path:name>")
def rt_gen_thumb(min_width: int, min_height: int, name: str) -> T.Any:
    if (min_width, min_height) not in THUMB_SIZES:
        abort(
            403,
            "Can generate only thumbnails of size " + str(THUMB_SIZES) + ".",
        )

    src_path = IMG_DIR / name
    dst_path = THUMB_DIR / f"{min_width}x{min_height}" / name
    if not src_path.exists():
        abort(404)
    if dst_path.exists():
        return send_file(str(dst_path))

    gen_thumb(src_path, dst_path, min_width, min_height)

    return send_file(str(dst_path))
