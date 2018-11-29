import enum
import typing as T
from pathlib import Path

import regex
from flask import abort, redirect, render_template, request, session

from .app import app
from .const import IMG_DIR, IMG_EXT, RULES_PATH


class Mod(enum.Enum):
    add = 1
    delete = 2
    reset = 3


def get_rules() -> T.Iterable[T.Tuple[str, Mod, T.List[str]]]:
    with RULES_PATH.open() as handle:
        for line in handle:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue

            pattern, users = regex.split(r":\s*", line, 1)
            if users.startswith("+"):
                yield pattern, Mod.add, users[1:].split(",")
            elif users.startswith("-"):
                yield pattern, Mod.delete, users[1:].split(",")
            else:
                yield pattern, Mod.reset, users.split(",")


def can_browse(
    rules: T.Iterable[T.Tuple[str, Mod, T.List[str]]], path: Path, user: str
) -> bool:
    allowed_users = set()

    for pattern, mod, users in rules:
        match = regex.fullmatch(pattern, str(path), flags=regex.I)
        if match:
            if mod == Mod.add:
                allowed_users.update(users)
            elif mod == Mod.delete:
                allowed_users.difference_update(users)
            elif mod == Mod.reset:
                allowed_users.clear()
                allowed_users.update(users)
            else:
                raise AssertionError

    return user in allowed_users


@app.route("/")
@app.route("/album/<path:name>")
def rt_index(name: str = "") -> T.Any:
    username = session.get("user")
    if not username:
        return redirect("/login")

    path = IMG_DIR / name
    if not path.exists():
        abort(404)

    if not path.is_dir():
        abort(501)

    if name and not name.endswith("/"):
        return redirect(request.path + "/")

    rules = list(get_rules())
    if not can_browse(rules, path.relative_to(IMG_DIR), username):
        abort(403)

    app.logger.info("Listing %s for %s", path, username)

    child_albums = []
    photos = []
    for subpath in path.iterdir():
        if not can_browse(rules, subpath.relative_to(IMG_DIR), username):
            continue
        if subpath.is_dir():
            child_albums.append(subpath.relative_to(IMG_DIR))
        elif subpath.is_file() and subpath.suffix.lower() in IMG_EXT:
            photos.append(subpath.relative_to(IMG_DIR))

    child_albums.sort(key=lambda subpath: subpath.name, reverse=True)
    photos.sort(key=lambda subpath: subpath.name, reverse=True)

    return render_template(
        "index.html",
        path=path.relative_to(IMG_DIR),
        photos=photos,
        child_albums=child_albums,
    )
