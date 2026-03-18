# career-claw

`career-claw` is the main monorepo for the service. The public-facing entrypoint is a Kotlin + Spring Boot application, with OpenClaw running as internal-only infrastructure for agent workflows. In production on the shared EC2 host, the existing `didimlog` Nginx and Certbot stack is expected to front this service.

## Repository layout

```text
career-claw/
├─ app/                     # Kotlin + Spring Boot application
├─ infra/
│  ├─ nginx/
│  │  └─ default.conf
│  ├─ openclaw/
│  │  ├─ openclaw.json
│  │  └─ workspace/
│  ├─ scripts/
│  │  └─ deploy.sh
│  └─ compose.yaml
├─ .github/
│  └─ workflows/
│     ├─ ci.yml
│     └─ deploy.yml
├─ .env.example
├─ .gitignore
└─ README.md
```

## Architecture

- `app` is the Kotlin + Spring Boot service and runs in Docker on container port `8080`.
- In production, the app is published on host port `8082` by default so the existing `didimlog` Nginx can proxy traffic for `claw.stdiodh.xyz`.
- `openclaw` is included as internal infrastructure and is not publicly exposed. Its gateway port is bound to `127.0.0.1` on the host only.
- Docker Compose is the orchestration layer for local, development, and EC2 deployment workflows.
- Production deployment uses a prebuilt app image from Docker Hub, while local development can still build the app image directly.

Request flow:

```text
Internet -> existing didimlog Nginx -> career-claw app
```

OpenClaw stays outside the public request path.

## Spring Boot app

The existing Spring Boot project now lives under `app/` and keeps its Gradle Kotlin DSL setup, wrapper, Java 21 toolchain, and Kotlin source layout. A lightweight application health endpoint is available at `GET /health`, and Spring Boot Actuator health is exposed at `GET /actuator/health`.

To run the app locally without Docker:

```bash
cd app
./gradlew bootRun
```

## Local Docker Compose usage

1. Create a local environment file:

```bash
cp .env.example .env
```

2. Fill in any required values in `.env`. Do not commit that file.

3. Start the stack:

```bash
docker compose --env-file .env -f infra/compose.yaml up --build
```

Useful commands:

```bash
docker compose --env-file .env -f infra/compose.yaml up -d
docker compose --env-file .env -f infra/compose.yaml logs -f app
docker compose --env-file .env -f infra/compose.yaml down
```

Local endpoints:

- App: `http://localhost:8082`
- Direct app health: `http://localhost:8082/health`
- Actuator health: `http://localhost:8082/actuator/health`
- OpenClaw gateway, host-local only: `http://127.0.0.1:18789`

## CI/CD

### CI

`.github/workflows/ci.yml` runs on pushes to `main` and on pull requests. It sets up Java 21 and runs the Gradle build from `app/`.

### Deploy

`.github/workflows/deploy.yml` deploys to EC2 on pushes to `main` and via manual trigger.

Expected GitHub secrets:

- `AWS_HOST`
- `AWS_USER`
- `AWS_SSH_KEY`
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `DOCKER_REPONAME`
- `GEMINI_API_KEY`
- `DISCORD_TOKEN`
- `OPENCLAW_AUTH_TOKEN`
- `DOMAIN`

The workflow:

- checks out the repository
- builds the Spring Boot app image and pushes it to Docker Hub
- configures SSH access
- generates the server `.env` file from GitHub Secrets
- syncs `infra/` to `/opt/career-claw` on the EC2 instance
- runs `docker compose pull` and `docker compose up -d` directly on EC2

The EC2 deployment step runs Docker Compose from `infra/` with:

```bash
docker compose pull
docker compose up -d --remove-orphans
```

## EC2 deployment notes

- Install Docker Engine and Docker Compose v2 on the EC2 host.
- The deploy workflow uploads `/opt/career-claw/.env` from GitHub Secrets on each deployment.
- The app image is pulled from Docker Hub. Keeping the Docker Hub repository public is the simplest setup because the EC2 host can pull without an extra `docker login`.
- If the EC2 host already uses another Nginx/Certbot stack on `80/443`, do not run a second Nginx container for `career-claw`.
- Keep the host `APP_PORT` on a non-conflicting port such as `8082`, then proxy `claw.stdiodh.xyz` from the existing Nginx stack to that port.
- Keep OpenClaw internal-only. Its Docker port binding is loopback-only, so it is not exposed through the instance's public interface.
- Certbot/HTTPS is not wired yet, but the Nginx layout is intentionally simple so TLS and certificate volumes can be layered in later.

## Next extensions

This layout is intentionally minimal and ready for future additions like PostgreSQL, Redis, background jobs, and HTTPS automation without requiring a repository reshuffle later.
