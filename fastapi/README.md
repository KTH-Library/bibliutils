# FastAPI example

An example API-app using the FastAPI framework.

Some links with info about FastAPI versus Flask and other REST API frameworks:

- [Simplest stack to build pyweb apps with in 2021?](https://news.ycombinator.com/item?id=29311761)
- [Flask versus FastAPI](https://christophergs.com/python/2021/06/16/python-flask-fastapi/)

And a nice presentation from DockerCon 2022 showing usage of FastAPI within containers:

- https://docker.events.cube365.net/dockercon/2022/content/Videos/FznJCYerdb9Za3W9Q

## Building and running

To build the docker image with the FastAPI application locally, use:

		make build

To start the services locally, use:

		make up

Once the services are up, navigate to "http://localhost:8080", for example:

		firefox http://localhost:8080/docs &

		# or use curl to call one of the endpoints directly
		curl -X 'GET' \
  			'http://localhost:8080/validate/u1234567' \
  			-H 'accept: application/json'

To view log files, use:

		docker-compose logs -f

To remove and clean up services use:

		docker-compose down


## Hot reload

To make changes to your API iteratively (when using Dockerfile.devel and hot reload), first start the service with "make up".

Then edit the app/main.py file and refresh to see results from changes in your browser at "http://localhost:8080/docs" (or by issuing curl requests).

