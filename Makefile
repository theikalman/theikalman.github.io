.PHONY: help run stop clean new-post taxonomy

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make run        Start the Jekyll dev server"
	@echo "  make stop       Stop the running Jekyll container"
	@echo "  make clean      Prune unused Docker resources"
	@echo "  make new-post   Create a new post (TITLE=... CATEGORIES=... TAGS=...)"
	@echo "  make taxonomy   List existing categories and tags (MODE=categories|tags|all)"

run:
	docker run --rm -it \
		-p 4000:4000 \
		-v "$$PWD:/srv/jekyll" \
		-v jekyll-gems:/usr/local/bundle \
		-e JEKYLL_ENV=development \
		jekyll/jekyll:4.0.1 \
		bash -c "bundle install && jekyll serve --force_polling -H 0.0.0.0 -t"

stop:
	docker stop jekyll

clean:
	docker system prune -f

new-post:
	tools/new_post.sh "$(TITLE)" "$(CATEGORIES)" $(TAGS)

taxonomy:
	tools/list_taxonomy.sh $(MODE)
