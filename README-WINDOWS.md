# Library Admin on Windows

This guide runs the published Docker image locally. No Python installation is required.

## 1. Install Docker Desktop

Install Docker Desktop for Windows, start it, and wait until Docker Desktop says it is running:

<https://www.docker.com/products/docker-desktop/>

## 2. Download and start the application

Open PowerShell and run these commands.

```powershell
docker pull kaushiks93/library-admin:latest
docker volume create library-admin-data
docker run -d --name library-admin -p 8000:8000 -v library-admin-data:/data kaushiks93/library-admin:latest
```

## 3. Open the admin panel

Open this address in a browser:

<http://localhost:8000/admin>

The API health check is available at <http://localhost:8000/health>.

## Useful commands

View application logs:

```powershell
docker logs -f library-admin
```

Stop the application:

```powershell
docker stop library-admin
```

Start it again later:

```powershell
docker start library-admin
```

Remove the stopped container without deleting the database:

```powershell
docker rm -f library-admin
```

To run a newer image, remove the old container, pull the image, and run the start command again:

```powershell
docker rm -f library-admin
docker pull kaushiks93/library-admin:latest
docker run -d --name library-admin -p 8000:8000 -v library-admin-data:/data kaushiks93/library-admin:latest
```

Do not run `docker volume rm library-admin-data` unless you intentionally want to delete the stored database.

> The current application exposes the admin panel without a login screen. Only run it on a trusted local computer or private network.
