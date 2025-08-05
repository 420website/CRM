#!/bin/bash

# Robust Production Startup Script with Data Protection
# Ensures all data is properly restored and protected during production startup

set -e

echo "=== PRODUCTION DATA PROTECTION STARTUP ==="
echo "Starting at: $(date)"

# Set environment variables
export MONGO_URL=${MONGO_URL:-"mongodb://localhost:27017"}
export DB_NAME=${DB_NAME:-"my420_ca_db"}

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
timeout=30
counter=0
while ! mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        echo "MongoDB failed to start within $timeout seconds"
        exit 1
    fi
    echo "MongoDB not ready, waiting... ($counter/$timeout)"
    sleep 1
    ((counter++))
done

echo "MongoDB is ready!"

# Check if client data exists and is properly formatted
echo "Checking client data integrity..."
cd /app/scripts

# Run data verification
python3 restore-client-data.py --verify

# Check if we need to restore data
CLIENT_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').admin_registrations.countDocuments({})")
echo "Current client records: $CLIENT_COUNT"

# If no client data or data integrity issues, attempt restoration
if [ "$CLIENT_COUNT" -eq 0 ] || [ "$CLIENT_COUNT" -lt 3 ]; then
    echo "WARNING: Low client record count, attempting restoration..."
    
    # Check if backup exists
    if [ -d "/app/persistent-data/client-backups" ] && [ "$(ls -A /app/persistent-data/client-backups/*.json 2>/dev/null | wc -l)" -gt 0 ]; then
        echo "Found backup files, restoring..."
        python3 restore-client-data.py --force
        
        # Verify restoration
        NEW_CLIENT_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').admin_registrations.countDocuments({})")
        echo "After restoration: $NEW_CLIENT_COUNT client records"
        
        if [ "$NEW_CLIENT_COUNT" -gt 0 ]; then
            echo "✓ Client data successfully restored"
        else
            echo "✗ WARNING: Client data restoration failed"
        fi
    else
        echo "No backup files found - this may be a fresh installation"
    fi
fi

# Restore other data collections
echo "Restoring other data collections..."

# Restore clinical templates
if [ -f "/app/persistent-data/backups/clinical-templates-backup.json" ]; then
    echo "Restoring clinical templates..."
    mongosh --quiet --eval "
        db.getSiblingDB('${DB_NAME}').clinical_templates.drop();
        const templates = JSON.parse(cat('/app/persistent-data/backups/clinical-templates-backup.json'));
        if (templates.length > 0) {
            db.getSiblingDB('${DB_NAME}').clinical_templates.insertMany(templates);
            print('Clinical templates restored: ' + templates.length);
        }
    "
fi

# Restore notes templates
if [ -f "/app/persistent-data/backups/notes-templates-backup.json" ]; then
    echo "Restoring notes templates..."
    mongosh --quiet --eval "
        db.getSiblingDB('${DB_NAME}').notes_templates.drop();
        const templates = JSON.parse(cat('/app/persistent-data/backups/notes-templates-backup.json'));
        if (templates.length > 0) {
            db.getSiblingDB('${DB_NAME}').notes_templates.insertMany(templates);
            print('Notes templates restored: ' + templates.length);
        }
    "
fi

# Restore dispositions
if [ -f "/app/persistent-data/backups/dispositions-backup.json" ]; then
    echo "Restoring dispositions..."
    mongosh --quiet --eval "
        db.getSiblingDB('${DB_NAME}').dispositions.drop();
        const dispositions = JSON.parse(cat('/app/persistent-data/backups/dispositions-backup.json'));
        if (dispositions.length > 0) {
            db.getSiblingDB('${DB_NAME}').dispositions.insertMany(dispositions);
            print('Dispositions restored: ' + dispositions.length);
        }
    "
fi

# Restore referral sites
if [ -f "/app/persistent-data/backups/referral-sites-backup.json" ]; then
    echo "Restoring referral sites..."
    mongosh --quiet --eval "
        db.getSiblingDB('${DB_NAME}').referral_sites.drop();
        const sites = JSON.parse(cat('/app/persistent-data/backups/referral-sites-backup.json'));
        if (sites.length > 0) {
            db.getSiblingDB('${DB_NAME}').referral_sites.insertMany(sites);
            print('Referral sites restored: ' + sites.length);
        }
    "
fi

# Final data verification
echo "=== FINAL DATA VERIFICATION ==="
mongosh --quiet --eval "
    const db = db.getSiblingDB('${DB_NAME}');
    print('Client registrations: ' + db.admin_registrations.countDocuments({}));
    print('Clinical templates: ' + db.clinical_templates.countDocuments({}));
    print('Notes templates: ' + db.notes_templates.countDocuments({}));
    print('Dispositions: ' + db.dispositions.countDocuments({}));
    print('Referral sites: ' + db.referral_sites.countDocuments({}));
"

# Create immediate backup after restoration
echo "Creating post-restoration backup..."
cd /app/scripts
/root/.venv/bin/python comprehensive-backup.py --backup

echo "=== PRODUCTION STARTUP COMPLETE ==="
echo "Completed at: $(date)"
echo "All data protection measures are in place"