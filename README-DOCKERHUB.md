# Publish the Docker image

```powershell
docker login
docker build -t kaushiks93/library-admin:latest .
docker push kaushiks93/library-admin:latest
```

After pushing, give your friend [README-WINDOWS.md](README-WINDOWS.md) and replace the placeholder username in its commands.

The container listens on port `8000`, runs database migrations on startup, and stores SQLite data in `/data`. The Windows instructions mount that directory to the named Docker volume `library-admin-data`.
