# Development Environment Setup Guide

## Overview

This guide walks through setting up a complete local development environment for the project. It supports **Windows (via WSL)**, **Linux (Ubuntu/Debian on AMD64)**, and **macOS (Intel & Apple Silicon)** using a **Docker Compose–based dev environment**.

> ⚠️ **Important**: This setup is resource-intensive. Ensure you have sufficient disk space and system resources before proceeding.

---

## System Requirements

### Minimum Recommended Specs

* **Disk space**: 100 GB free (setup may consume ~60–70 GB)
* **RAM**: 16 GB (32 GB recommended)
* **CPU**: 4+ cores
* **OS**:

  * Windows 10/11 (with WSL2)
  * macOS Sonoma (Intel or ARM)
  * Linux (Ubuntu / Debian)

---

## Prerequisites

### macOS (Sonoma – Intel & Apple Silicon)

> Tested on macOS Sonoma. Apple Silicon (ARM) uses AMD64 emulation where required.

1. **Install Homebrew**

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

   ```bash
   brew doctor
   brew update
   ```

   * [ ] Homebrew installed and healthy

2. **Install Docker & Docker Compose (via Colima)**

   ```bash
   brew install docker docker-compose colima
   colima start
   ```

   * [ ] Docker & docker-compose available
   * [ ] Colima running

3. **Install Git**

   ```bash
   brew install git
   ```

   * [ ] Git installed

4. **Install PostgreSQL Client**

   ```bash
   brew install postgresql@14
   ```

   * [ ] PostgreSQL client installed

5. **Install AWS CLI**

   ```bash
   brew install awscli
   aws configure
   ```

   * [ ] AWS CLI installed and configured

6. **Install Make**

   ```bash
   brew install make
   ```

   * [ ] Make installed

7. **Apple Silicon Only**

   * Ensure **Rosetta 2** is enabled if Docker Desktop was previously installed
   * [https://support.apple.com/en-us/HT211861](https://support.apple.com/en-us/HT211861)

---

1. **Install Git**

   * Download from [https://git-scm.com/](https://git-scm.com/)
   * Verify:

     ```bash
     git --version
     ```
   * [ ] Git is installed and accessible

2. **Install Python (3.8+)**

   * Download from [https://python.org/](https://python.org/)
   * Verify:

     ```bash
     python --version
     ```
   * [ ] Python is installed and accessible

3. **Install Node.js**

   * Download from [https://nodejs.org/](https://nodejs.org/)
   * Verify:

     ```bash
     node --version
     npm --version
     ```
   * [ ] Node.js and npm are installed

4. **Install Docker & Docker Compose**

   * Install Docker Desktop: [https://docker.com/](https://docker.com/)
   * **Windows**: Configure Docker to run using **WSL2**
   * Verify:

     ```bash
     docker --version
     docker compose version
     ```
   * [ ] Docker is installed and running

5. **Install AWS CLI (inside WSL on Windows)**

   * Follow: [https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
   * Verify:

     ```bash
     aws --version
     ```
   * [ ] AWS CLI installed

6. **Setup IDE**

   * Recommended: VS Code
   * Install Docker, Python, and ESLint extensions
   * [ ] IDE configured

---

## Environment & Access Setup

### GitHub Access

* You must have access to the required GitHub repositories
* Create a **GitHub Personal Access Token (classic)**

#### Configure `.netrc`

Create a `.netrc` file in your home directory:

```text
machine github.com
login <YOUR_GITHUB_TOKEN>
password x-oauth-basic

machine api.github.com
login <YOUR_GITHUB_TOKEN>
password x-oauth-basic
```

> **Windows (WSL)**: Place `.netrc` in the WSL home directory

---

### AWS Credentials

Set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

Also set:

```bash
export GOPRIVATE=github.com/treetopllc
```

---

## Repository Setup

Clone all required repositories:

```bash
git clone https://github.com/treetopllc/gonoble.git
git clone https://github.com/treetopllc/alert-svc.git
git clone https://github.com/treetopllc/reportExport-svc.git
git clone https://github.com/treetopllc/collaboratory-www.git
git clone https://github.com/treetopllc/starkiller-base.git
```

### Branch Configuration

```bash
cd alert-svc
git checkout API-3936
```

---

## Host Configuration

Add the following entries to `/etc/hosts`:

```text
127.0.0.1 postgres
127.0.0.1 consulserver
127.0.0.1 redis
127.0.0.1 rabbitmq
127.0.0.1 mailcatcher
127.0.0.1 alert-svc
127.0.0.1 collab
127.0.0.1 gonoble
127.0.0.1 ical-svc
```

---

## Docker Development Environment

### Pre-Docker Setup

```bash
cp ~/.netrc gonoble/docker-dev/netrc.txt
```

Login to AWS ECR:

```bash
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin <ECR_URL>
```

---

### Configure Docker Compose

Edit:

```bash
cd gonoble/docker-dev
nano compose.yml
```

* Comment out `collab-prebuild`
* Uncomment `collab`

Edit `collab_config.json`:

```json
{
  "base_url": "",
  "external_url": ""
}
```

---

### Database Restore

```bash
mkdir -p gonoble/docker-dev/database
cd gonoble/docker-dev/database
aws s3 cp s3://treetop-junk/noblehour.sql .
```

Start Postgres container:

```bash
docker compose -f docker-dev/compose.yml up postgres
```

Monitor logs until completion:

```bash
docker compose -f docker-dev/compose.yml logs -f postgres
```

---

### Database Permissions

Install PostgreSQL client:

```bash
sudo apt install postgresql-client make
```

For macOS, update `PGSQL_ROOT` if needed:

```bash
export PGSQL_ROOT=/usr/local/bin
```

---

## Running the Full Stack

```bash
cd gonoble
docker compose -f docker-dev/compose.yml up -d
```

Check logs:

```bash
docker compose -f docker-dev/compose.yml logs
```

Access the application:

* [http://gonoble:8000/](http://gonoble:8000/)

---

## Frontend (Collaboratory)

If frontend issues occur:

```bash
docker compose -f docker-dev/compose.yml run collab /bin/bash
npm install
exit
```

Restart container:

```bash
docker compose -f docker-dev/compose.yml restart collab
```

---

## Troubleshooting & Common Errors

### Port Conflicts

* Ensure PostgreSQL is **not running locally on port 5432**

### Out of Memory Errors

* Increase container memory to **3–4 GB** in `compose.yml`

### Node / Python Build Errors

* Switch base image to `debian:bullseye` if Python2 issues occur
* Re-run:

```bash
export GOPRIVATE=github.com/treetopllc
```

### Miscellaneous

* Collaboratory directory is mounted; changes auto-reload
* See `docker-dev/README.md` for advanced commands

---

## Verification Checklist

* [ ] All containers running
* [ ] No critical errors in logs
* [ ] Application loads at [http://gonoble:8000/](http://gonoble:8000/)
* [ ] Database connections work
* [ ] APIs respond correctly

---

## Notes

* This environment is designed for **local development only**
* Expect long initial build times
* Subsequent runs are much faster
