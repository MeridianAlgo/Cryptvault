param(
    [string]$Mode = 'help'
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host ""
    Write-Host "CryptVault Deployment Script"
    Write-Host "============================="
    Write-Host ""
    Write-Host "Usage: ./deploy.ps1 [mode]"
    Write-Host ""
    Write-Host "Modes:"
    Write-Host "  docker    - Build and run with Docker (recommended)"
    Write-Host "  local     - Install locally with virtual environment"
    Write-Host "  pip       - Install as Python package"
    Write-Host "  help      - Show this help message"
    Write-Host ""
}

function Deploy-Docker {
    Write-Host "Deploying with Docker..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "Error: Docker is not installed."
        exit 1
    }
    
    Write-Host "Building Docker image..."
    docker build -t cryptvault:latest .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker image built successfully!"
        Write-Host "Run with: docker run --rm cryptvault:latest BTC 60 1d"
    } else {
        Write-Host "Error: Docker build failed!"
        exit 1
    }
}

function Deploy-Local {
    Write-Host "Deploying locally..."
    
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Error: Python is not installed."
        exit 1
    }

    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..."
        python -m venv venv
    }
    
    Write-Host "Installing dependencies..."
    # We can't easily activate the venv in the same process for the user, 
    # so we'll use the venv's pip directly
    if ($IsWindows -or $env:OS -match "Windows") {
        .\venv\Scripts\pip install --upgrade pip
        .\venv\Scripts\pip install -r requirements.txt
        
        Write-Host "Local installation complete!"
        Write-Host "To run:"
        Write-Host "1. .\venv\Scripts\activate"
        Write-Host "2. python cryptvault_cli.py BTC 60 1d"
    } else {
        ./venv/bin/pip install --upgrade pip
        ./venv/bin/pip install -r requirements.txt
        
        Write-Host "Local installation complete!"
        Write-Host "To run:"
        Write-Host "1. source venv/bin/activate"
        Write-Host "2. python cryptvault_cli.py BTC 60 1d"
    }
}

function Deploy-Pip {
    Write-Host "Installing as Python package..."
    pip install --upgrade pip
    pip install -e .
    Write-Host "Package installation complete!"
    Write-Host "Run with: cryptvault BTC 60 1d"
}

if ($Mode -eq 'docker') {
    Deploy-Docker
} elseif ($Mode -eq 'local') {
    Deploy-Local
} elseif ($Mode -eq 'pip') {
    Deploy-Pip
} else {
    Show-Help
}
