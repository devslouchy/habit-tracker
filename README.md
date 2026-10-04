# Habit Tracker

A self-hosted habit tracking web application built with Python and FastAPI.

This project began as a Python CLI application for learning application development and testing. It was then expanded into a web application and used as a practical DevOps project covering automated testing, containerisation, security scanning, CI/CD, SSH authentication and deployment to a self-hosted Linux server.

## Features

- Add habits
- Complete habits
- Delete habits
- Weekly habit tracking interface
- SQLite data persistence
- FastAPI backend
- Jinja2 templates
- Dockerised deployment
- Automated testing
- Automated CI/CD deployment

## Tech Stack

- Python 3.12
- FastAPI
- SQLite
- Jinja2
- pytest
- Docker
- Docker Compose
- GitHub Actions
- Gitleaks
- pip-audit
- Trivy

## CI/CD Pipeline

Every push to `main` triggers a GitHub Actions workflow.

The pipeline:

1. Runs the pytest test suite
2. Scans the repository for secrets using Gitleaks
3. Audits Python dependencies using pip-audit
4. Builds the Docker image
5. Scans the image for HIGH and CRITICAL vulnerabilities using Trivy
6. Deploys to a self-hosted Linux server only after the preceding CI jobs succeed

The deployment job fetches the repository using a dedicated read-only SSH deploy key and checks out the exact commit SHA associated with the successful workflow.

Docker Compose then rebuilds and recreates the application container from that version of the source code.

```text
                       Push to main
                            |
             +--------------+--------------+
             |              |              |
           pytest        Gitleaks       pip-audit
             |              |              |
             +--------------+--------------+
                            |
                       Docker build
                            |
                       Trivy scan
                            |
                            v
                   Self-hosted runner
                            |
                      git fetch origin
                            |
                  Checkout exact CI SHA
                            |
                            v
                  Docker Compose build
                            |
                            v
                    FastAPI application
```

## Deployment Design

The production server runs a self-hosted GitHub Actions runner as a system service.

The runner waits for deployment jobs from GitHub Actions. Deployment is gated behind the testing, security scanning and Docker build stages of the workflow.

Rather than running `git pull` and deploying whatever happens to be the latest version of `main`, the deployment process uses the commit SHA supplied by the GitHub Actions workflow.

This means the server deploys the exact source revision that passed that CI run.

The production checkout therefore intentionally uses a detached `HEAD` pointing at the deployed commit.

## Git and SSH Security

Automated deployment and interactive development use separate Git identities.

### Deployment identity

The Linux server has a dedicated SSH deploy key registered specifically against the Habit Tracker repository.

The key is:

- Repository scoped
- Read-only
- Available without a developer workstation being connected
- Used by the deployment process to fetch source code

The deployment identity cannot push changes to the GitHub repository.

### Personal identity

Interactive Git operations use a separate personal SSH key managed by the 1Password SSH Agent.

When developing remotely on the server, SSH agent forwarding allows the server to request authentication using the developer's 1Password-managed key without copying the private key onto the server.

This separates human and machine authentication:

```text
Automated deployment
        |
        v
Server deploy key
        |
        v
Read-only repository access


Interactive development
        |
        v
1Password SSH Agent
        |
        v
SSH agent forwarding
        |
        v
Personal GitHub access
```

## Running with Docker

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd habit-tracker
```

Build and start the application:

```bash
docker compose up -d --build
```

The application is exposed on port `8000`.

The container uses:

```yaml
restart: unless-stopped
```

so it automatically starts again after Docker or the host machine restarts unless the container was deliberately stopped.

## Data Persistence

Habit data is stored in SQLite.

The Compose configuration bind-mounts the local `data` directory into the application container:

```yaml
volumes:
  - ./data:/app/data
```

This separates application data from the lifecycle of the container.

The Docker image and container can therefore be rebuilt or replaced without deleting the SQLite database.

The application also creates the required data directory and initialises the database when required.

## Running Without Docker

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application with Uvicorn:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

The application will then be available on port `8000`.

## Testing

Install the project dependencies and run:

```bash
python -m pytest
```

Tests are also executed automatically by GitHub Actions on every push to `main`.

A failed test prevents the downstream Docker build and deployment jobs from running.

## Security Scanning

The CI pipeline performs several automated security checks.

### Gitleaks

Gitleaks scans the Git repository and history for accidentally committed secrets.

### pip-audit

`pip-audit` checks the Python dependencies listed in `requirements.txt` for known vulnerabilities.

### Trivy

After the Docker image is built, Trivy scans the resulting image.

The workflow fails when HIGH or CRITICAL vulnerabilities that meet the configured scan criteria are detected, preventing deployment.

## CI/CD Workflow

The dependency structure of the workflow is:

```text
test ------------------+
                       |
secret-scan -----------+----> docker-build ----> deploy
                       |
dependency-scan -------+
```

`docker-build` cannot run until the three preceding jobs succeed.

`deploy` cannot run until `docker-build` succeeds.

As a result, code that fails testing or the configured security checks is not automatically deployed.

## Deployment Process

A successful deployment performs the equivalent of:

```bash
git fetch origin
git checkout --detach <tested-commit-sha>
docker compose up -d --build
```

The GitHub Actions workflow supplies the exact commit SHA using:

```yaml
${{ github.sha }}
```

This avoids a race condition where a newer commit could reach `main` while an earlier workflow is still running.

## Self-Hosted Infrastructure

The application currently runs on a self-hosted Linux server.

The server runs:

- Docker
- Docker Compose
- GitHub Actions self-hosted runner
- Habit Tracker container

The GitHub Actions runner is installed as a system service, allowing it to reconnect to GitHub automatically after the server restarts.

The Habit Tracker container uses Docker's `unless-stopped` restart policy for the same reason.

## Project Goals

The application itself is intentionally small.

The primary purpose of the project is to build practical experience across the application and deployment lifecycle:

```text
Python application
        |
        v
Automated testing
        |
        v
Web application
        |
        v
Docker
        |
        v
CI
        |
        v
Security scanning
        |
        v
Self-hosted runner
        |
        v
Continuous deployment
```

This keeps the application simple enough to understand while allowing the infrastructure and deployment process to become progressively more realistic.

## Future Improvements

Planned areas for further development include:

- Infrastructure as Code with Terraform
- AWS deployment
- Application health checks
- Deployment health verification
- Monitoring and observability
- Improved production logging