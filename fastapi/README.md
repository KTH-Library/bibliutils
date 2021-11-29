# FastAPI example

An example API-app using the FastAPI framework.

Some links with info about FastAPI versus Flask and other REST API frameworks:

- [Simplest stack to build pyweb apps with in 2021?](https://news.ycombinator.com/item?id=29311761)
- [Flask versus FastAPI](https://christophergs.com/python/2021/06/16/python-flask-fastapi/)

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


