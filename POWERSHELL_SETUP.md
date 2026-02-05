# PowerShell Setup for Dugger Ecosystem

## Path Verification and Setup

### Check Current PowerShell Path

```powershell
# Check if Python Scripts directory is in PATH
$env:Path -split ';' | Where-Object { $_ -like '*Python*' -or $_ -like '*Scripts*' }

# Check if dlt-commit is available
Get-Command dlt-commit -ErrorAction SilentlyContinue

# Check if dgt is available  
Get-Command dgt -ErrorAction SilentlyContinue
```

### Add Python Scripts to PATH (Permanent)

```powershell
# Get Python Scripts path
$pythonScripts = Join-Path (Split-Path -Parent (Get-Command python).Source) "Scripts"

# Add to current session
$env:Path += ";$pythonScripts"

# Add to permanent PATH (user level)
[System.Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)

# Or add to system level (requires admin)
# [System.Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)
```

### PowerShell Profile Setup

```powershell
# Check current profile
$PROFILE

# Edit profile
notepad $PROFILE

# Add to profile for permanent aliases and functions
```

### Profile Additions

```powershell
# Dugger Ecosystem aliases and functions
function dlt-status {
    dlt-commit status
}

function dgt-status {
    dgt status
}

# Custom prompt for Dugger projects
function prompt {
    $currentPath = Get-Location
    $isDuggerProject = $false
    
    # Check if we're in a Dugger project
    if ($currentPath.Path -like "*\Github\*") {
        $projectName = Split-Path -Leaf $currentPath.Path
        $isDuggerProject = $true
    }
    
    # Build prompt
    $prompt = "PS $currentPath"
    
    if ($isDuggerProject) {
        $prompt += " [$projectName]"
        
        # Add Git status if available
        try {
            $gitStatus = git status --porcelain 2>$null
            if ($gitStatus) {
                $prompt += " 🔄"
            } else {
                $prompt += " ✅"
            }
        } catch {
            # Not a git repo
        }
    }
    
    $prompt += "`n> "
    return $prompt
}

# Dugger project navigation
function cd-dlt { Set-Location "C:\Github\DuggerLinkTools" }
function cd-dgt { Set-Location "C:\Github\DuggerGitTools" }

# Quick status checks
function dlt-check { 
    Set-Location "C:\Github\DuggerLinkTools"
    dlt-status
}
function dgt-check { 
    Set-Location "C:\Github\DuggerGitTools" 
    dgt-status
}

# Quick commit workflow
function dlt-commit-all { 
    Set-Location "C:\Github\DuggerLinkTools"
    dlt-commit
}
function dgt-commit-all { 
    Set-Location "C:\Github\DuggerGitTools"
    dgt commit
}

# Ecosystem health check
function dugger-health {
    Write-Host "=== Dugger Ecosystem Health Check ===" -ForegroundColor Cyan
    
    Write-Host "`n🔗 DuggerLinkTools:" -ForegroundColor Yellow
    Set-Location "C:\Github\DuggerLinkTools"
    dlt-status
    
    Write-Host "`n🔧 DuggerGitTools:" -ForegroundColor Yellow
    Set-Location "C:\Github\DuggerGitTools"
    dgt-status
    
    Write-Host "`n✅ Ecosystem Status: HEALTHY" -ForegroundColor Green
}
```

### One-Liner Setup Commands

```powershell
# Verify Python Scripts path
($env:Path -split ';') | Where-Object { $_ -like '*Python*' -or $_ -like '*Scripts*' }

# Add Python Scripts to PATH (one-liner)
$env:Path += ";" + (Join-Path (Split-Path -Parent (Get-Command python).Source) "Scripts")

# Make permanent
[System.Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)

# Refresh environment
refreshenv

# Test commands
dlt-commit --help
dgt --help
```

### Troubleshooting

#### Commands Not Found After Installation

```powershell
# Refresh PowerShell environment
refreshenv

# Or restart PowerShell
exit
# Then open new PowerShell

# Check installation
pip list | findstr dugger

# Reinstall if needed
pip install -e C:\Github\DuggerLinkTools
pip install -e C:\Github\DuggerGitTools
```

#### Permission Issues

```powershell
# Run PowerShell as Administrator for system-wide changes
# Or use user-level changes as shown above

# Check current user
whoami

# Check execution policy
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Verification Commands

```powershell
# Test DLT installation
dlt-commit --help
dlt-status

# Test DGT installation  
dgt --help
dgt status

# Test cross-project functionality
cd C:\Github\DuggerLinkTools
dlt-status

cd C:\Github\DuggerGitTools  
dgt status

# Test from other directories
cd C:\
dlt-commit --help  # Should work from anywhere
```

### Advanced Setup

#### Custom Aliases

```powershell
# Set-Content -Path $PROFILE -Value @"
# Custom Dugger aliases
Set-Alias -Name dltc -Value dlt-commit
Set-Alias -Name dgts -Value "dgt status"
Set-Alias -Name dlts -Value "dlt-commit status"
"@
```

#### Function for Project Creation

```powershell
function New-DuggerProject {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,
        
        [Parameter(Mandatory=$false)]
        [string]$Type = "python"
    )
    
    $projectPath = Join-Path "C:\Github" $Name
    
    if (Test-Path $projectPath) {
        Write-Error "Project $Name already exists at $projectPath"
        return
    }
    
    Write-Host "Creating new Dugger project: $Name" -ForegroundColor Green
    
    # Create project directory
    New-Item -ItemType Directory -Path $projectPath -Force
    
    # Initialize Git
    Set-Location $projectPath
    git init
    
    # Create basic structure based on type
    if ($Type -eq "python") {
        New-Item -ItemType Directory -Path "src", "tests", "docs"
        "# $Name" | Out-File -FilePath "README.md"
        "[build-system]" | Out-File -FilePath "pyproject.toml"
    }
    
    Write-Host "Project $Name created at $projectPath" -ForegroundColor Green
    Set-Location $projectPath
}
```

This setup ensures your Dugger ecosystem commands work from any directory in PowerShell, providing a seamless development experience across all your projects.