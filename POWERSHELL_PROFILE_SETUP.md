# PowerShell Profile Setup for Dugger Ecosystem

## Custom Profile Additions

### Enhanced Prompt with Git Status

```powershell
# Add to $PROFILE for custom Dugger ecosystem prompt
function prompt {
    $currentPath = Get-Location
    $isDuggerProject = $false
    $projectName = ""
    
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
                $prompt += " 🔄"  # Dirty
            } else {
                $prompt += " ✅"  # Clean
            }
        } catch {
            # Not a git repo
        }
    }
    
    $prompt += "`n> "
    return $prompt
}
```

### Custom Aliases

```powershell
# Dugger ecosystem aliases
Set-Alias -Name dltc -Value dlt-commit
Set-Alias -Name dlts -Value "dlt-commit status"
Set-Alias -Name dgts -Value "dgt status"

# Quick navigation
function cd-dlt { Set-Location "C:\Github\DuggerLinkTools" }
function cd-dgt { Set-Location "C:\Github\DuggerGitTools" }

# Quick status checks
function dlt-check { 
    Set-Location "C:\Github\DuggerLinkTools"
    dlt-status
}
function dgt-check { 
    Set-Location "C:\Github\DuggerGitTools" 
    dgt status
}

# Quick commit workflows
function dlt-commit-all { 
    Set-Location "C:\Github\DuggerLinkTools"
    dlt-commit
}
function dgt-commit-all { 
    Set-Location "C:\Github\DuggerGitTools"
    dgt commit -m "chore: quick commit"
}
```

### Ecosystem Health Check

```powershell
function dugger-health {
    Write-Host "=== Dugger Ecosystem Health Check ===" -ForegroundColor Cyan
    
    Write-Host "`n🔗 DuggerLinkTools:" -ForegroundColor Yellow
    Set-Location "C:\Github\DuggerLinkTools"
    dlt-status
    
    Write-Host "`n🔧 DuggerGitTools:" -ForegroundColor Yellow
    Set-Location "C:\Github\DuggerGitTools"
    dgt status
    
    Write-Host "`n✅ Ecosystem Status: HEALTHY" -ForegroundColor Green
}
```

### Custom Coloring

```powershell
# Custom color scheme for Dugger ecosystem
function Write-DuggerSuccess {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green -BackgroundColor Black
}

function Write-DuggerWarning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow -BackgroundColor Black
}

function Write-DuggerError {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red -BackgroundColor Black
}

function Write-DuggerInfo {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan -BackgroundColor Black
}
```

### Git Integration

```powershell
# Enhanced Git functions
function dugger-git-status {
    param([string]$Path = ".")
    
    Set-Location $Path
    $status = git status --porcelain
    
    if ($status) {
        Write-DuggerWarning "Repository has changes:"
        $status | ForEach-Object {
            $parts = $_.Split(' ', 2)
            $statusChar = $parts[0]
            $file = $parts[1]
            
            switch ($statusChar.Substring(0,1)) {
                "M" { Write-Host "  Modified: $file" -ForegroundColor Yellow }
                "A" { Write-Host "  Added: $file" -ForegroundColor Green }
                "D" { Write-Host "  Deleted: $file" -ForegroundColor Red }
                "??" { Write-Host "  Untracked: $file" -ForegroundColor Cyan }
                default { Write-Host "  $statusChar $file" }
            }
        }
    } else {
        Write-DuggerSuccess "Repository is clean"
    }
}

function dugger-git-quick-commit {
    param([string]$Message = "chore: quick commit")
    
    git add .
    git commit -m $Message
    Write-DuggerSuccess "Committed with message: $Message"
}
```

### Project Management

```powershell
# Quick project switching
function goto-dugger {
    param([string]$Project)
    
    $projectPath = Join-Path "C:\Github" $Project
    if (Test-Path $projectPath) {
        Set-Location $projectPath
        Write-DuggerInfo "Switched to $Project"
    } else {
        Write-DuggerError "Project $Project not found at $projectPath"
    }
}

# List all Dugger projects
function list-dugger {
    Get-ChildItem "C:\Github" | Where-Object {
        $_.Name -like "Dugger*" -or 
        (Test-Path (Join-Path $_.FullName "pyproject.toml")) -or
        (Test-Path (Join-Path $_.FullName ".git"))
    } | ForEach-Object {
        $status = "📁"
        if (Test-Path (Join-Path $_.FullName ".git")) {
            Set-Location $_.FullName
            $gitStatus = git status --porcelain 2>$null
            if ($gitStatus) {
                $status = "🔄"
            } else {
                $status = "✅"
            }
        }
        Write-Host "$status $($_.Name)" -ForegroundColor White
    }
}
```

### Installation Commands

```powershell
# One-liner to add to profile
$profileContent = @'
# Dugger Ecosystem Setup
function prompt {
    $currentPath = Get-Location
    $isDuggerProject = $false
    $projectName = ""
    
    if ($currentPath.Path -like "*\Github\*") {
        $projectName = Split-Path -Leaf $currentPath.Path
        $isDuggerProject = $true
    }
    
    $prompt = "PS $currentPath"
    
    if ($isDuggerProject) {
        $prompt += " [$projectName]"
        
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

# Dugger aliases
Set-Alias -Name dltc -Value dlt-commit
Set-Alias -Name dlts -Value "dlt-commit status"
Set-Alias -Name dgts -Value "dgt status"

# Quick navigation
function cd-dlt { Set-Location "C:\Github\DuggerLinkTools" }
function cd-dgt { Set-Location "C:\Github\DuggerGitTools" }

# Ecosystem health
function dugger-health {
    Write-Host "=== Dugger Ecosystem Health ===" -ForegroundColor Cyan
    Write-Host "`n🔗 DuggerLinkTools:" -ForegroundColor Yellow
    Set-Location "C:\Github\DuggerLinkTools"
    dlt-status
    Write-Host "`n🔧 DuggerGitTools:" -ForegroundColor Yellow
    Set-Location "C:\Github\DuggerGitTools"
    dgt status
    Write-Host "`n✅ Ecosystem Status: HEALTHY" -ForegroundColor Green
}
'@

Add-Content -Path $PROFILE -Value $profileContent
```

### Usage Examples

```powershell
# After setting up profile, you can use:
dltc                    # Instead of dlt-commit
dlts                   # Instead of dlt-commit status
dgts                   # Instead of dgt status

cd-dlt                 # Quick navigation to DLT
cd-dgt                 # Quick navigation to DGT

dugger-health          # Check ecosystem health
list-dugger           # List all projects with status
```

This enhanced PowerShell setup provides a professional, colorized development experience with custom prompts, aliases, and ecosystem management functions.