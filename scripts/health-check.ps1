# CryptVault Health Check Script (PowerShell)
# Checks the health of CryptVault deployment

# Configuration
$ContainerName = if ($env:CONTAINER_NAME) { $env:CONTAINER_NAME } else { "cryptvault" }
$ImageName = if ($env:IMAGE_NAME) { $env:IMAGE_NAME } else { "cryptvault:latest" }

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

# Check Docker
function Test-Docker {
    Write-Header "Docker Status"
    
    $exitCode = 0
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-ErrorMsg "Docker is not installed"
        $exitCode = 1
    } else {
        Write-Success "Docker is installed"
    }
    
    try {
        docker info | Out-Null
        Write-Success "Docker daemon is running"
    } catch {
        Write-ErrorMsg "Docker daemon is not running"
        $exitCode = 1
    }
    
    Write-Host ""
    return $exitCode
}

# Check image
function Test-Image {
    Write-Header "Image Status"
    
    $images = docker images $ImageName --format "{{.Repository}}:{{.Tag}}"
    if ($images -match $ImageName) {
        Write-Success "Image $ImageName exists"
        
        $imageSize = docker images $ImageName --format "{{.Size}}"
        $imageCreated = docker images $ImageName --format "{{.CreatedSince}}"
        Write-Info "Size: $imageSize"
        Write-Info "Created: $imageCreated"
    } else {
        Write-Warning "Image $ImageName not found"
    }
    
    Write-Host ""
}

# Check container
function Test-Container {
    Write-Header "Container Status"
    
    $allContainers = docker ps -a --filter "name=$ContainerName" --format "{{.Names}}"
    if ($allContainers -match $ContainerName) {
        Write-Success "Container $ContainerName exists"
        
        # Check if running
        $runningContainers = docker ps --filter "name=$ContainerName" --format "{{.Names}}"
        if ($runningContainers -match $ContainerName) {
            Write-Success "Container is running"
            
            # Get container stats
            $containerStatus = docker ps --filter "name=$ContainerName" --format "{{.Status}}"
            Write-Info "Status: $containerStatus"
            
            # Check health
            try {
                $health = docker inspect --format='{{.State.Health.Status}}' $ContainerName 2>$null
                if ($health -eq "healthy") {
                    Write-Success "Health check: healthy"
                } elseif ($health -eq "none" -or -not $health) {
                    Write-Info "Health check: not configured"
                } else {
                    Write-Warning "Health check: $health"
                }
            } catch {
                Write-Info "Health check: not configured"
            }
        } else {
            Write-Warning "Container is not running"
            $containerStatus = docker ps -a --filter "name=$ContainerName" --format "{{.Status}}"
            Write-Info "Status: $containerStatus"
        }
    } else {
        Write-Warning "Container $ContainerName not found"
    }
    
    Write-Host ""
}

# Check Docker Compose
function Test-Compose {
    Write-Header "Docker Compose Status"
    
    if (Test-Path "docker-compose.yml") {
        Write-Success "docker-compose.yml exists"
        
        if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
            Write-Success "Docker Compose is installed"
            
            # Check services
            $services = docker-compose ps 2>$null
            if ($services -match "cryptvault") {
                Write-Success "Services are defined"
                
                # Show service status
                Write-Host ""
                Write-Info "Service status:"
                docker-compose ps
            } else {
                Write-Warning "No services running"
            }
        } else {
            Write-Warning "Docker Compose is not installed"
        }
    } else {
        Write-Warning "docker-compose.yml not found"
    }
    
    Write-Host ""
}

# Check logs
function Test-Logs {
    Write-Header "Recent Logs"
    
    $runningContainers = docker ps --filter "name=$ContainerName" --format "{{.Names}}"
    if ($runningContainers -match $ContainerName) {
        Write-Info "Last 10 log entries:"
        Write-Host ""
        docker logs --tail=10 $ContainerName 2>&1
        
        # Check for errors
        $logs = docker logs --tail=100 $ContainerName 2>&1
        $errorCount = ($logs | Select-String -Pattern "error" -AllMatches).Matches.Count
        if ($errorCount -gt 0) {
            Write-Warning "Found $errorCount error(s) in recent logs"
        } else {
            Write-Success "No errors in recent logs"
        }
    } else {
        Write-Warning "Container not running, cannot check logs"
    }
    
    Write-Host ""
}

# Check resources
function Test-Resources {
    Write-Header "Resource Usage"
    
    $runningContainers = docker ps --filter "name=$ContainerName" --format "{{.Names}}"
    if ($runningContainers -match $ContainerName) {
        Write-Info "Container resource usage:"
        Write-Host ""
        docker stats --no-stream $ContainerName
    } else {
        Write-Warning "Container not running, cannot check resources"
    }
    
    Write-Host ""
}

# Check volumes
function Test-Volumes {
    Write-Header "Volume Status"
    
    if (Test-Path "logs") {
        $logSize = (Get-ChildItem -Path "logs" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Success "Logs directory exists ($([math]::Round($logSize, 2)) MB)"
    } else {
        Write-Warning "Logs directory not found"
    }
    
    if (Test-Path "data") {
        $dataSize = (Get-ChildItem -Path "data" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Success "Data directory exists ($([math]::Round($dataSize, 2)) MB)"
    } else {
        Write-Warning "Data directory not found"
    }
    
    if (Test-Path ".cryptvault_predictions") {
        $cacheSize = (Get-ChildItem -Path ".cryptvault_predictions" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Success "Cache directory exists ($([math]::Round($cacheSize, 2)) MB)"
    } else {
        Write-Warning "Cache directory not found"
    }
    
    Write-Host ""
}

# Check configuration
function Test-Config {
    Write-Header "Configuration Status"
    
    if (Test-Path ".env") {
        Write-Success ".env file exists"
    } else {
        Write-Warning ".env file not found"
        if (Test-Path ".env.example") {
            Write-Info "Use: Copy-Item .env.example .env"
        }
    }
    
    if (Test-Path "config") {
        Write-Success "Config directory exists"
        $configFiles = (Get-ChildItem "config\*.yaml" -ErrorAction SilentlyContinue).Count
        Write-Info "Found $configFiles configuration file(s)"
    } else {
        Write-Warning "Config directory not found"
    }
    
    Write-Host ""
}

# Main health check
Write-Header "CryptVault Health Check"
Write-Host ""

$exitCode = 0

$exitCode = Test-Docker
Test-Image
Test-Container
Test-Compose
Test-Volumes
Test-Config
Test-Logs
Test-Resources

Write-Header "Health Check Summary"

if ($exitCode -eq 0) {
    Write-Success "All critical checks passed"
} else {
    Write-ErrorMsg "Some critical checks failed"
}

exit $exitCode
