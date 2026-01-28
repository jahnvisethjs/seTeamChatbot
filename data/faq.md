# Common Development Setup Errors and Solutions

## Git Issues
**Error: 'git' is not recognized**
- Solution: Install Git from https://git-scm.com/
- Verify PATH environment variable includes Git

**Error: Permission denied**
- Solution: Run as administrator or check file permissions
- Use `sudo` on Linux/Mac

## Python Issues
**Error: 'python' is not recognized**
- Solution: Install Python and add to PATH
- Try `python3` instead of `python`

**Error: Module not found**
- Solution: Install missing packages with `pip install package_name`
- Check virtual environment activation

## Node.js Issues
**Error: 'node' is not recognized**
- Solution: Install Node.js from https://nodejs.org/
- Restart terminal after installation

**Error: npm install fails**
- Solution: Clear npm cache: `npm cache clean --force`
- Check network connectivity
- Try using a different npm registry

## Docker Issues
**Error: Docker daemon not running**
- Solution: Start Docker Desktop
- Check if Docker service is running

**Error: Permission denied on Docker commands**
- Solution: Add user to docker group
- Run with sudo (Linux/Mac)

## Database Issues
**Error: Database connection failed**
- Solution: Check database service is running
- Verify connection settings in .env file
- Ensure database exists

## General Issues
**Error: Port already in use**
- Solution: Find and kill process using the port
- Use different port: `python manage.py runserver 8001`

**Error: File not found**
- Solution: Check current directory
- Verify file paths are correct
- Ensure files exist in expected locations
