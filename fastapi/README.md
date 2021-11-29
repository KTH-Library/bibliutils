# FastAPI example

## Building and running

To build the docker image with the FastAPI application locally, use:

		make build

To start the services locally, use:

		make up

One the services are up, navigate to "http://localhost:8080", for example:

		firefox http://localhost:8080/docs &

To view log files, use:

		docker-compose logs -f

To remove and clean up services use:

		docker-compose down


