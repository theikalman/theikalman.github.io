# animation

[Manim Community](https://docs.manim.community/) project for generating animations/images used in blog posts.

## Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/) and already installed in `.venv`.
System deps (already installed via Homebrew): `ffmpeg`, `cairo`, `pango`.

## Usage

Scenes live in `scenes/`. Output goes to `media/` (gitignored).

Render a video (medium quality):

```sh
uv run manim -qm scenes/example.py Example
```

Render a single PNG (e.g. for embedding a still image in a blog post):

```sh
uv run manim -s -qh scenes/example.py Example
```

Render high quality video:

```sh
uv run manim -qh scenes/example.py Example
```

Output files land in `media/videos/<scene_file>/<quality>/` or `media/images/<scene_file>/` for stills.
Copy the finished asset into `postimages/` (or the relevant post's image folder) to use it in a post.
