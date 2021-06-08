req: requirements
requirements:
	pipreqs --force

docker: requirements
	docker build -t pixil/meeting-assistant .

docker-run: docker
	docker run --rm pixil/meeting-assistant