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

1. **Install Git**

   **macOS:**
   ```bash
   brew install git
   ```

   **Windows:**
   * Download from [https://git-scm.com/](https://git-scm.com/) and run the installer
   * During installation, select "Git from the command line and also from 3rd-party software"
   * Verify in PowerShell or Command Prompt:
   ```powershell
   git --version
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update && sudo apt install git
   ```

   * [ ] Git is installed and accessible

2. **Install Python (3.8+)**

   **macOS:**
   ```bash
   brew install python@3.11
   ```

   **Windows:**
   * Download from [https://python.org/](https://python.org/)
   * **Important**: Check "Add Python to PATH" during installation
   * Verify in PowerShell:
   ```powershell
   python --version
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt install python3 python3-pip
   ```

   * [ ] Python is installed and accessible

3. **Install Node.js**

   **macOS:**
   ```bash
   brew install node
   ```

   **Windows:**
   * Download from [https://nodejs.org/](https://nodejs.org/) and run the installer
   * Verify in PowerShell:
   ```powershell
   node --version
   npm --version
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt install nodejs
   ```

   * [ ] Node.js and npm are installed

4. **Install Docker & Docker Compose**

   **macOS (via Colima):**
   ```bash
   brew install docker docker-compose colima
   colima start
   ```
   * [ ] Colima running

   **macOS (via Docker Desktop):**
   * Download Docker Desktop from [https://docker.com/](https://docker.com/)

   **Windows:**
   * Install **WSL2** first (if not already installed):
   ```powershell
   wsl --install
   ```
   * Restart your PC after WSL installation
   * Download and install **Docker Desktop** from [https://docker.com/](https://docker.com/)
   * In Docker Desktop Settings, enable **"Use the WSL 2 based engine"**
   * Verify in PowerShell:
   ```powershell
   docker --version
   docker compose version
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt install docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   ```
   * Log out and back in for the group change to take effect

   * [ ] Docker is installed and running

5. **Install AWS CLI**

   **macOS:**
   ```bash
   brew install awscli
   aws configure
   ```

   **Windows:**
   * Download the MSI installer from [https://aws.amazon.com/cli/](https://aws.amazon.com/cli/)
   * Or install inside WSL:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```
   * Verify:
   ```powershell
   aws --version
   ```

   **Linux (Ubuntu/Debian):**
   * Follow: [https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

   * [ ] AWS CLI installed and configured

6. **Install PostgreSQL Client**

   **macOS:**
   ```bash
   brew install postgresql@14
   ```

   **Windows (inside WSL):**
   ```bash
   sudo apt install postgresql-client
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt install postgresql-client
   ```

   * [ ] PostgreSQL client installed

7. **Install Make**

   **macOS:**
   ```bash
   brew install make
   ```

   **Windows (inside WSL):**
   ```bash
   sudo apt install make
   ```
   * Alternatively, install [GnuWin32 Make](http://gnuwin32.sourceforge.net/packages/make.htm) for native Windows

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt install make
   ```

   * [ ] Make installed

8. **Setup IDE**

   * Recommended: **VS Code** — download from [https://code.visualstudio.com/](https://code.visualstudio.com/)
   * Install recommended extensions: Docker, Python, ESLint
   * **Windows**: Install the "WSL" extension so VS Code can open projects inside WSL
   * [ ] IDE configured

9. **Apple Silicon Only (macOS)**

   * Ensure **Rosetta 2** is enabled if Docker Desktop was previously installed
   * [https://support.apple.com/en-us/HT211861](https://support.apple.com/en-us/HT211861)

---

## Environment & Access Setup

### GitHub Access

* You must have access to the required GitHub repositories
* Create a **GitHub Personal Access Token (classic)**

#### Configure `.netrc`

Create a `.netrc` file in your home directory:

**macOS / Linux / WSL:**
```text
machine github.com
login <YOUR_GITHUB_TOKEN>
password x-oauth-basic

machine api.github.com
login <YOUR_GITHUB_TOKEN>
password x-oauth-basic
```

File location:
* **macOS / Linux**: `~/.netrc`
* **Windows (WSL)**: Place `.netrc` in the WSL home directory (`~/.netrc` inside WSL)
* **Windows (native)**: Place in `%USERPROFILE%\_netrc`

---

### AWS Credentials

**macOS / Linux / WSL (bash/zsh):**
```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export GOPRIVATE=github.com/treetopllc
```

**Windows (PowerShell):**
```powershell
$env:AWS_ACCESS_KEY_ID = "..."
$env:AWS_SECRET_ACCESS_KEY = "..."
$env:GOPRIVATE = "github.com/treetopllc"
```

**Windows (Command Prompt):**
```cmd
set AWS_ACCESS_KEY_ID=...
set AWS_SECRET_ACCESS_KEY=...
set GOPRIVATE=github.com/treetopllc
```

---

## Repository Setup

10. **Clone Required Repositories**

    ```bash
    git clone https://github.com/treetopllc/gonoble.git
    git clone https://github.com/treetopllc/alert-svc.git
    git clone https://github.com/treetopllc/reportExport-svc.git
    git clone https://github.com/treetopllc/collaboratory-www.git
    git clone https://github.com/treetopllc/starkiller-base.git
    ```

    * [ ] All repositories cloned

11. **Branch Configuration**

    ```bash
    cd alert-svc
    git checkout API-3936
    ```

    * [ ] Correct branch checked out

---

## Host Configuration

12. **Update Hosts File**

    Add the following entries:

    **macOS / Linux / WSL:**
    Edit `/etc/hosts`:
    ```bash
    sudo nano /etc/hosts
    ```

    **Windows (native):**
    Edit `C:\Windows\System32\drivers\etc\hosts` as Administrator:
    ```powershell
    notepad C:\Windows\System32\drivers\etc\hosts
    ```
    (Right-click Notepad → "Run as administrator" first)

    Add these lines:
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

    * [ ] Hosts file updated

---

## Docker Development Environment

13. **Pre-Docker Setup**

    Copy your `.netrc` to the project:
    ```bash
    cp ~/.netrc gonoble/docker-dev/netrc.txt
    ```

    **Windows (PowerShell, if not using WSL):**
    ```powershell
    Copy-Item "$env:USERPROFILE\_netrc" "gonoble\docker-dev\netrc.txt"
    ```

    Login to AWS ECR:
    ```bash
    aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <ECR_URL>
    ```

    * [ ] Pre-Docker setup complete

14. **Configure Docker Compose**

    ```bash
    cd gonoble/docker-dev
    nano compose.yml
    ```

    **Windows (if not in WSL):**
    ```powershell
    cd gonoble\docker-dev
    notepad compose.yml
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

    * [ ] Docker Compose configured

15. **Database Restore**

    ```bash
    mkdir -p gonoble/docker-dev/database
    cd gonoble/docker-dev/database
    aws s3 cp s3://treetop-junk/noblehour.sql .
    ```

    **Windows (PowerShell, if not in WSL):**
    ```powershell
    New-Item -ItemType Directory -Force -Path "gonoble\docker-dev\database"
    cd gonoble\docker-dev\database
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

    * [ ] Database restored

16. **Database Permissions**

    Install PostgreSQL client (if not done in step 6):

    **Linux / WSL:**
    ```bash
    sudo apt install postgresql-client make
    ```

    **macOS** — update `PGSQL_ROOT` if needed:
    ```bash
    export PGSQL_ROOT=/usr/local/bin
    ```

    * [ ] Database permissions set

---

## Running the Full Stack

17. **Start All Services**

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

    * [ ] All services running

---

## Frontend (Collaboratory)

18. **Fix Frontend Issues (if needed)**

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

    * [ ] Frontend working

---

## Troubleshooting & Common Errors

### Port Conflicts
* Ensure PostgreSQL is **not running locally on port 5432**
* **Windows**: Check with `netstat -ano | findstr :5432`
* **macOS/Linux**: Check with `lsof -i :5432`

### Out of Memory Errors
* Increase container memory to **3–4 GB** in `compose.yml`
* **Windows**: Adjust WSL memory in `%USERPROFILE%\.wslconfig`:
  ```ini
  [wsl2]
  memory=8GB
  ```

### Node / Python Build Errors
* Switch base image to `debian:bullseye` if Python2 issues occur
* Re-run:
  ```bash
  export GOPRIVATE=github.com/treetopllc
  ```
  **Windows (PowerShell):**
  ```powershell
  $env:GOPRIVATE = "github.com/treetopllc"
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
