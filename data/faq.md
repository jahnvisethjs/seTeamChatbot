# Common Development Setup Errors and Solutions

## Git Issues
**Error: 'git' is not recognized**
- **Windows**: Download and install Git from https://git-scm.com/ — ensure "Add to PATH" is checked during install
- **macOS**: Run `xcode-select --install` or install via Homebrew: `brew install git`
- **Linux**: `sudo apt install git`

**Error: Permission denied**
- **Windows**: Run PowerShell or Command Prompt as Administrator
- **macOS/Linux**: Use `sudo` or check file permissions with `ls -la`

## Python Issues
**Error: 'python' is not recognized**
- **Windows**: Reinstall Python from https://python.org/ and check "Add Python to PATH"
- **Windows**: Try `py` instead of `python` (Python Launcher for Windows)
- **macOS**: Try `python3` instead of `python`; install via `brew install python@3.11`
- **Linux**: `sudo apt install python3`

**Error: Module not found**
- Install missing packages: `pip install package_name`
- **Windows**: Use `pip` or `py -m pip install package_name`
- Check virtual environment activation (`source venv/bin/activate` or `.\venv\Scripts\Activate.ps1` on Windows)

## Node.js Issues
**Error: 'node' is not recognized**
- **Windows**: Download and install from https://nodejs.org/ — restart terminal after installation
- **macOS**: `brew install node`
- **Linux**: Use the NodeSource installer

**Error: npm install fails**
- Clear npm cache: `npm cache clean --force`
- Check network connectivity
- Try using a different npm registry
- **Windows**: If permission errors, try running as Administrator

## Docker Issues
**Error: Docker daemon not running**
- **Windows**: Start Docker Desktop — ensure WSL2 backend is enabled in Settings
- **macOS**: Start Docker Desktop or run `colima start`
- **Linux**: `sudo systemctl start docker`

**Error: Permission denied on Docker commands**
- **Windows**: Run as Administrator or ensure Docker Desktop is running
- **Linux**: Add user to docker group: `sudo usermod -aG docker $USER` (then log out/in)
- **macOS**: This typically shouldn't happen with Docker Desktop or Colima

**Error: WSL not installed (Windows)**
- Run in PowerShell (as Admin): `wsl --install`
- Restart your PC after installation
- Set WSL2 as default: `wsl --set-default-version 2`

## Database Issues
**Error: Database connection failed**
- Check database service is running: `docker compose ps`
- Verify connection settings in `.env` file
- Ensure database exists
- **Windows**: Make sure localhost entries are in `C:\Windows\System32\drivers\etc\hosts`

## General Issues
**Error: Port already in use**
- **Windows**: Find process: `netstat -ano | findstr :5432` then kill: `taskkill /PID <pid> /F`
- **macOS/Linux**: Find process: `lsof -i :5432` then kill: `kill -9 <pid>`
- Or use a different port

**Error: File not found**
- Check current directory with `pwd` (macOS/Linux) or `Get-Location` (PowerShell)
- Verify file paths are correct
- Ensure files exist in expected locations
- **Windows**: Remember path separators are `\` not `/` (unless in WSL)

**Error: Environment variables not set**
- **Windows (PowerShell)**: Use `$env:VAR_NAME = "value"`
- **Windows (CMD)**: Use `set VAR_NAME=value`
- **macOS/Linux**: Use `export VAR_NAME=value`
- Add to shell profile for persistence (`.bashrc`, `.zshrc`, or PowerShell `$PROFILE`)
