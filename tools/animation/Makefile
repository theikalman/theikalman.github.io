FILE  ?= scenes/example.py
SCENE ?= Example

.PHONY: video hq png clean help

help:
	@echo "Usage: make <target> [FILE=scenes/foo.py] [SCENE=SceneName]"
	@echo ""
	@echo "  video  render medium-quality video (default)"
	@echo "  hq     render high-quality video"
	@echo "  png    render a single still image (high quality)"
	@echo "  clean  remove rendered output in media/"

video:
	uv run manim -qm $(FILE) $(SCENE)

hq:
	uv run manim -qh $(FILE) $(SCENE)

png:
	uv run manim -s -qh $(FILE) $(SCENE)

clean:
	rm -rf media
