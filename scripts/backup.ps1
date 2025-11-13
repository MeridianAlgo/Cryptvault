# CryptVault Backup Script (PowerShell)
# Creates backups of logs, data, and configuration

# Configuration
$BackupDir = "backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir\cryptvault_backup_$Timestamp.zip"
$KeepBackups = 10

# Create backup directory
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "========================================" -ForegroundColor Blue
Write-Host "CryptVault Backup Script" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Backup data
Write-Host "Creating backup: $BackupFile" -ForegroundColor Cyan

# Items to backup
$itemsToBackup = @()
if (Test-Path "logs") { $itemsToBackup += "logs" }
if (Test-Path "data") { $itemsToBackup += "data" }
if (Test-Path ".cryptvault_predictions") { $itemsToBackup += ".cryptvault_predictions" }
if (Test-Path "config") { $itemsToBackup += "config" }
if (Test-Path ".env") { $itemsToBackup += ".env" }

if ($itemsToBackup.Count -gt 0) {
    try {
        Compress-Archive -Path $itemsToBackup -DestinationPath $BackupFile -Force
        $backupSize = (Get-Item $BackupFile).Length / 1MB
        Write-Host "✓ Backup created: $BackupFile ($([math]::Round($backupSize, 2)) MB)" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Backup creation failed: $_" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "⚠ No data to backup" -ForegroundColor Yellow
    exit 0
}

# Clean old backups
Write-Host ""
Write-Host "Cleaning old backups (keeping last $KeepBackups)..." -ForegroundColor Cyan

$backups = Get-ChildItem "$BackupDir\cryptvault_backup_*.zip" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending

if ($backups.Count -gt $KeepBackups) {
    $toRemove = $backups | Select-Object -Skip $KeepBackups
    $toRemove | Remove-Item -Force
    Write-Host "✓ Removed $($toRemove.Count) old backup(s)" -ForegroundColor Green
} else {
    Write-Host "✓ No old backups to remove" -ForegroundColor Green
}

# List all backups
Write-Host ""
Write-Host "Available backups:" -ForegroundColor Cyan
Get-ChildItem "$BackupDir\cryptvault_backup_*.zip" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending |
    ForEach-Object {
        $size = [math]::Round($_.Length / 1MB, 2)
        Write-Host "  $($_.Name) ($size MB)"
    }

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backup Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
