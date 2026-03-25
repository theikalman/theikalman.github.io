.PHONY: run stop clean

run:
	docker run --rm -it \
		-p 4000:4000 \
		-v "$$PWD:/srv/jekyll" \
		-e JEKYLL_ENV=development \
		jekyll/jekyll:4 \
		jekyll serve --force_polling -H 0.0.0.0 -t

stop:
	docker stop jekyll

clean:
	docker system prune -f
