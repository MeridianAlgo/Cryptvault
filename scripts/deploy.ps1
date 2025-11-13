# CryptVault Deployment Script (PowerShell)
# Automates Docker build, test, and deployment process

param(
    [switch]$SkipBuild,
    [switch]$SkipTest,
    [switch]$SkipPush,
    [switch]$SkipDeploy,
    [switch]$Backup,
    [switch]$Cleanup,
    [switch]$Help
)

# Configuration
$ImageName = "cryptvault"
$Version = "latest"
$Registry = $env:DOCKER_REGISTRY
$Environment = if ($env:DEPLOY_ENV) { $env:DEPLOY_ENV } else { "production" }

# Try to get version from Python
try {
    $Version = python -c "from cryptvault.__version__ import __version__; print(__version__)" 2>$null
    if (-not $Version) { $Version = "latest" }
} catch {
    $Version = "latest"
}

# Functions
function Write-Header {
    param([string]$Message)
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# Show help
if ($Help) {
    Write-Host "CryptVault Deployment Script"
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipBuild     Skip Docker image build"
    Write-Host "  -SkipTest      Skip image testing"
    Write-Host "  -SkipPush      Skip pushing to registry"
    Write-Host "  -SkipDeploy    Skip deployment"
    Write-Host "  -Backup        Create backup before deployment"
    Write-Host "  -Cleanup       Cleanup unused Docker resources"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Environment Variables:"
    Write-Host "  DOCKER_REGISTRY   Docker registry URL"
    Write-Host "  DEPLOY_ENV        Deployment environment (default: production)"
    Write-Host ""
    exit 0
}

# Check prerequisites
function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    # Check Docker
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-ErrorMsg "Docker is not installed"
        exit 1
    }
    Write-Success "Docker is installed"
    
    # Check Docker Compose
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Warning "Docker Compose is not installed (optional)"
    } else {
        Write-Success "Docker Compose is installed"
    }
    
    # Check if Docker daemon is running
    try {
        docker info | Out-Null
        Write-Success "Docker daemon is running"
    } catch {
        Write-ErrorMsg "Docker daemon is not running"
        exit 1
    }
    
    Write-Host ""
}

# Build Docker image
function Build-Image {
    Write-Header "Building Docker Image"
    
    Write-Info "Building ${ImageName}:${Version}..."
    
    $buildResult = docker build -t "${ImageName}:${Version}" -t "${ImageName}:latest" .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Image built successfully"
    } else {
        Write-ErrorMsg "Image build failed"
        exit 1
    }
    
    # Show image size
    $imageInfo = docker images "${ImageName}:${Version}" --format "{{.Size}}"
    Write-Info "Image size: $imageInfo"
    
    Write-Host ""
}

# Test Docker image
function Test-Image {
    Write-Header "Testing Docker Image"
    
    # Test 1: Version check
    Write-Info "Test 1: Version check"
    $versionResult = docker run --rm "${ImageName}:${Version}" --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Version check passed"
    } else {
        Write-ErrorMsg "Version check failed"
        exit 1
    }
    
    # Test 2: Help command
    Write-Info "Test 2: Help command"
    $helpResult = docker run --rm "${ImageName}:${Version}" --help 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Help command passed"
    } else {
        Write-ErrorMsg "Help command failed"
        exit 1
    }
    
    # Test 3: Health check
    Write-Info "Test 3: Health check"
    $statusResult = docker run --rm "${ImageName}:${Version}" --status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Health check passed"
    } else {
        Write-Warning "Health check failed (may require API access)"
    }
    
    Write-Host ""
}

# Tag image for registry
function Set-ImageTag {
    if ($Registry) {
        Write-Header "Tagging Image for Registry"
        
        Write-Info "Tagging ${ImageName}:${Version} as ${Registry}/${ImageName}:${Version}"
        docker tag "${ImageName}:${Version}" "${Registry}/${ImageName}:${Version}"
        docker tag "${ImageName}:${Version}" "${Registry}/${ImageName}:latest"
        
        Write-Success "Image tagged for registry"
        Write-Host ""
    }
}

# Push image to registry
function Push-Image {
    if ($Registry) {
        Write-Header "Pushing Image to Registry"
        
        Write-Info "Pushing ${Registry}/${ImageName}:${Version}..."
        docker push "${Registry}/${ImageName}:${Version}"
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Version tag pushed"
        } else {
            Write-ErrorMsg "Failed to push version tag"
            exit 1
        }
        
        Write-Info "Pushing ${Registry}/${ImageName}:latest..."
        docker push "${Registry}/${ImageName}:latest"
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Latest tag pushed"
        } else {
            Write-ErrorMsg "Failed to push latest tag"
            exit 1
        }
        
        Write-Host ""
    }
}

# Deploy with Docker Compose
function Start-Deployment {
    Write-Header "Deploying with Docker Compose"
    
    if (-not (Test-Path "docker-compose.yml")) {
        Write-ErrorMsg "docker-compose.yml not found"
        exit 1
    }
    
    # Check for .env file
    if (-not (Test-Path ".env")) {
        Write-Warning ".env file not found, using .env.example"
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Info "Created .env from .env.example"
        }
    }
    
    # Pull/build images
    Write-Info "Preparing services..."
    docker-compose build
    
    # Start services
    Write-Info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    Write-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 5
    
    # Check service status
    $services = docker-compose ps
    if ($services -match "Up") {
        Write-Success "Services deployed successfully"
        docker-compose ps
    } else {
        Write-ErrorMsg "Service deployment failed"
        docker-compose logs
        exit 1
    }
    
    Write-Host ""
}

# Create backup
function New-Backup {
    Write-Header "Creating Backup"
    
    $BackupDir = "backups"
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupFile = "$BackupDir\cryptvault_backup_$Timestamp.zip"
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    Write-Info "Creating backup: $BackupFile"
    
    # Backup logs, data, and configuration
    $itemsToBackup = @()
    if (Test-Path "logs") { $itemsToBackup += "logs" }
    if (Test-Path "data") { $itemsToBackup += "data" }
    if (Test-Path ".cryptvault_predictions") { $itemsToBackup += ".cryptvault_predictions" }
    if (Test-Path "config") { $itemsToBackup += "config" }
    if (Test-Path ".env") { $itemsToBackup += ".env" }
    
    if ($itemsToBackup.Count -gt 0) {
        Compress-Archive -Path $itemsToBackup -DestinationPath $BackupFile -Force
        $backupSize = (Get-Item $BackupFile).Length / 1MB
        Write-Success "Backup created: $BackupFile ($([math]::Round($backupSize, 2)) MB)"
    } else {
        Write-Warning "No data to backup"
    }
    
    # Keep only last 5 backups
    Write-Info "Cleaning old backups (keeping last 5)..."
    Get-ChildItem "$BackupDir\cryptvault_backup_*.zip" | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -Skip 5 | 
        Remove-Item -Force
    
    Write-Host ""
}

# Health check
function Test-Health {
    Write-Header "Health Check"
    
    $services = docker-compose ps 2>$null
    if ($services -match "cryptvault") {
        Write-Info "Checking service health..."
        
        # Check if container is running
        if ($services -match "Up") {
            Write-Success "Service is running"
            
            # Check logs for errors
            $logs = docker-compose logs --tail=50 cryptvault
            if ($logs -match "error") {
                Write-Warning "Errors found in logs"
                docker-compose logs --tail=20 cryptvault
            } else {
                Write-Success "No errors in recent logs"
            }
        } else {
            Write-ErrorMsg "Service is not running"
            docker-compose logs --tail=50 cryptvault
            exit 1
        }
    } else {
        Write-Warning "Service not deployed with Docker Compose"
    }
    
    Write-Host ""
}

# Show deployment info
function Show-Info {
    Write-Header "Deployment Information"
    
    Write-Host "Image: ${ImageName}:${Version}"
    Write-Host "Environment: $Environment"
    if ($Registry) {
        Write-Host "Registry: $Registry"
    }
    Write-Host ""
    
    Write-Info "Available commands:"
    Write-Host "  docker run --rm ${ImageName}:${Version} BTC 60 1d"
    Write-Host "  docker-compose up -d"
    Write-Host "  docker-compose logs -f"
    Write-Host "  docker-compose down"
    Write-Host ""
}

# Cleanup
function Invoke-Cleanup {
    Write-Header "Cleanup"
    
    Write-Info "Removing dangling images..."
    docker image prune -f
    
    Write-Info "Removing unused volumes..."
    docker volume prune -f
    
    Write-Success "Cleanup completed"
    Write-Host ""
}

# Main deployment flow
Write-Header "CryptVault Deployment Script"
Write-Host "Version: $Version"
Write-Host "Environment: $Environment"
Write-Host ""

# Execute deployment steps
Test-Prerequisites

if ($Backup) {
    New-Backup
}

if (-not $SkipBuild) {
    Build-Image
}

if (-not $SkipTest) {
    Test-Image
}

if (-not $SkipPush) {
    Set-ImageTag
    Push-Image
}

if (-not $SkipDeploy) {
    Start-Deployment
    Test-Health
}

if ($Cleanup) {
    Invoke-Cleanup
}

Show-Info

Write-Header "Deployment Complete"
Write-Success "CryptVault $Version deployed successfully!"
