# animation

[Manim Community](https://docs.manim.community/) project for generating animations/images used in blog posts.

## Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/) and already installed in `.venv`.
System deps (already installed via Homebrew): `ffmpeg`, `cairo`, `pango`.

## Usage

Scenes live in `scenes/`. Output goes to `media/` (gitignored).

Use the Makefile instead of typing out `uv run manim` commands. By default it
targets `scenes/example.py Example`; override with `FILE=` / `SCENE=`.

Render a video (medium quality):

```sh
make video
```

Render a single PNG (e.g. for embedding a still image in a blog post):

```sh
make png
```

Render high quality video:

```sh
make hq
```

Target a different scene:

```sh
make png FILE=scenes/sliding_window.py SCENE=SlidingWindow
```

Remove rendered output:

```sh
make clean
```

Output files land in `media/videos/<scene_file>/<quality>/` or `media/images/<scene_file>/` for stills.
Copy the finished asset into `postimages/` (or the relevant post's image folder) to use it in a post.
