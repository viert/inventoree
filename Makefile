CONTAINER_NAME = inventoree-builder

build:
	docker build -t $(CONTAINER_NAME) . && docker run -it $(CONTAINER_NAME)
