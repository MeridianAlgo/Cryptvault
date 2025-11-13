#!/bin/bash
# CryptVault Backup Script
# Creates backups of logs, data, and configuration

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/cryptvault_backup_${TIMESTAMP}.tar.gz"
KEEP_BACKUPS=10

# Create backup directory
mkdir -p "${BACKUP_DIR}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CryptVault Backup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Backup data
echo -e "${BLUE}Creating backup: ${BACKUP_FILE}${NC}"

# Items to backup
ITEMS_TO_BACKUP=""
[ -d "logs" ] && ITEMS_TO_BACKUP="${ITEMS_TO_BACKUP} logs/"
[ -d "data" ] && ITEMS_TO_BACKUP="${ITEMS_TO_BACKUP} data/"
[ -d ".cryptvault_predictions" ] && ITEMS_TO_BACKUP="${ITEMS_TO_BACKUP} .cryptvault_predictions/"
[ -d "config" ] && ITEMS_TO_BACKUP="${ITEMS_TO_BACKUP} config/"
[ -f ".env" ] && ITEMS_TO_BACKUP="${ITEMS_TO_BACKUP} .env"

if [ -n "$ITEMS_TO_BACKUP" ]; then
    tar -czf "${BACKUP_FILE}" ${ITEMS_TO_BACKUP} 2>/dev/null || true
    
    if [ -f "${BACKUP_FILE}" ]; then
        BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
        echo -e "${GREEN}✓ Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})${NC}"
    else
        echo -e "${YELLOW}⚠ Backup creation failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ No data to backup${NC}"
    exit 0
fi

# Clean old backups
echo ""
echo -e "${BLUE}Cleaning old backups (keeping last ${KEEP_BACKUPS})...${NC}"
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/cryptvault_backup_*.tar.gz 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt "$KEEP_BACKUPS" ]; then
    ls -t "${BACKUP_DIR}"/cryptvault_backup_*.tar.gz | tail -n +$((KEEP_BACKUPS + 1)) | xargs rm -f
    REMOVED=$((BACKUP_COUNT - KEEP_BACKUPS))
    echo -e "${GREEN}✓ Removed ${REMOVED} old backup(s)${NC}"
else
    echo -e "${GREEN}✓ No old backups to remove${NC}"
fi

# List all backups
echo ""
echo -e "${BLUE}Available backups:${NC}"
ls -lh "${BACKUP_DIR}"/cryptvault_backup_*.tar.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Backup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
