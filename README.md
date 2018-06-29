# Employee Registration App

A simple Python Flask application running in a Docker container and connecting via SQLAlchemy to a PostgreSQL database, using the Azure Cognitive Services Face API to ensure that a valid employee photo is uploaded and then storing the photo in Azure blob storage.

The database connection information is specified via environment variables `DBHOST`, `DBPASS`, `DBUSER`, and `DBNAME`. This app always uses the default PostgreSQL port.

Run in Docker locally via:

```
docker build -t docker-flask-sample .
docker run -it --env DBPASS="<PASSWORD>" --env DBHOST="<SERVER_HOST_NAME>" --env DBUSER="<USERNAME>" --env DBNAME="<DATABASE_NAME>" -p 5000:5000 docker-flask-sample`
```
The app can be reached in your browser at `http://127.0.0.1:5000`.

