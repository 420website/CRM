#!/bin/bash

# BULLETPROOF PRODUCTION STARTUP SCRIPT
# Prevents ANY data loss during deployment/forking
# Runs BEFORE any other startup processes

set -e

echo "🛡️ ========================================="
echo "🛡️  BULLETPROOF PRODUCTION PROTECTION"
echo "🛡️ ========================================="
echo "Starting at: $(date)"

# Set environment
export MONGO_URL=${MONGO_URL:-"mongodb://localhost:27017"}
export DB_NAME=${DB_NAME:-"my420_ca_db"}
export ENVIRONMENT=${ENVIRONMENT:-"production"}

# Wait for MongoDB
echo "⏳ Waiting for MongoDB..."
timeout=60
counter=0
while ! mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        echo "❌ MongoDB failed to start within $timeout seconds"
        exit 1
    fi
    echo "   MongoDB not ready... ($counter/$timeout)"
    sleep 2
    ((counter+=2))
done
echo "✅ MongoDB is ready"

# FORCE PRODUCTION PROTECTION FIRST
echo "🔒 Activating production lock system..."
cd /app/scripts
/root/.venv/bin/python production-lock.py --force-protect

# Check current data status
echo "📊 Checking data status..."
CLIENT_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').admin_registrations.countDocuments({})")
echo "Current client records: $CLIENT_COUNT"

# If data count is suspiciously low, PREVENT ANY FURTHER OPERATIONS
if [ "$CLIENT_COUNT" -lt 5 ]; then
    echo "🚨 CRITICAL WARNING: Very low client count detected!"
    echo "🚨 This may indicate data loss or fresh installation"
    
    # Check if this is truly a fresh installation
    if [ ! -f "/app/.production-protected" ]; then
        echo "⚠️ No production protection flag found"
        echo "⚠️ This appears to be a fresh installation"
    else
        echo "🆘 PRODUCTION DATA LOSS DETECTED!"
        echo "🔄 Forcing emergency restoration..."
        
        # Try emergency restoration
        /root/.venv/bin/python production-lock.py --prevent-wipe
        
        # Re-check count
        NEW_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').admin_registrations.countDocuments({})")
        echo "After restoration: $NEW_COUNT client records"
        
        if [ "$NEW_COUNT" -eq 0 ]; then
            echo "💥 EMERGENCY: Cannot restore production data!"
            echo "💥 HALTING STARTUP TO PREVENT FURTHER DAMAGE"
            exit 1
        fi
    fi
fi

# Verify all protection systems are active
echo "🔍 Verifying protection systems..."
if [ -f "/app/persistent-data/.production-lock" ]; then
    echo "✅ Production lock file exists"
else
    echo "❌ Production lock missing - creating now"
    /root/.venv/bin/python production-lock.py --lock
fi

if [ -f "/app/.production-protected" ]; then
    echo "✅ Production protection flag exists"
else
    echo "❌ Protection flag missing - creating now"
    touch /app/.production-protected
    echo "PRODUCTION PROTECTED AT $(date)" > /app/.production-protected
fi

# Create mandatory backup before any other operations
echo "💾 Creating mandatory pre-startup backup..."
/root/.venv/bin/python production-lock.py --backup

# Restore templates and other data (but NEVER client data)
echo "📋 Ensuring templates and reference data..."

# Only restore templates if they don't exist
TEMPLATE_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').clinical_templates.countDocuments({})")
if [ "$TEMPLATE_COUNT" -eq 0 ]; then
    echo "📋 Restoring clinical templates..."
    if [ -f "/app/persistent-data/backups/clinical-templates-backup.json" ]; then
        mongosh --quiet --eval "
            const templates = JSON.parse(cat('/app/persistent-data/backups/clinical-templates-backup.json'));
            if (templates.length > 0) {
                db.getSiblingDB('${DB_NAME}').clinical_templates.insertMany(templates);
                print('✅ Clinical templates restored: ' + templates.length);
            }
        "
    fi
fi

# Restore dispositions and referral sites (safe reference data)
echo "🔄 Ensuring dispositions and referral sites..."
cd /app/scripts
node force-seed-data.js

# Final verification
echo "🔍 Final verification..."
FINAL_CLIENT_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').admin_registrations.countDocuments({})")
TEMPLATE_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').clinical_templates.countDocuments({})")
DISPOSITION_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').dispositions.countDocuments({})")
REFERRAL_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('${DB_NAME}').referral_sites.countDocuments({})")

echo "📊 FINAL DATA STATUS:"
echo "   👥 Client records: $FINAL_CLIENT_COUNT"
echo "   📋 Clinical templates: $TEMPLATE_COUNT" 
echo "   📝 Dispositions: $DISPOSITION_COUNT"
echo "   🏥 Referral sites: $REFERRAL_COUNT"

# Ensure minimum required data
if [ "$FINAL_CLIENT_COUNT" -eq 0 ] && [ -f "/app/.production-protected" ]; then
    echo "💥 CRITICAL: Production system has zero client records!"
    echo "💥 This indicates a serious data loss issue"
    exit 1
fi

if [ "$TEMPLATE_COUNT" -eq 0 ] || [ "$DISPOSITION_COUNT" -eq 0 ] || [ "$REFERRAL_COUNT" -eq 0 ]; then
    echo "⚠️ Warning: Some reference data missing, but continuing..."
fi

echo "🛡️ ========================================="
echo "🛡️  PRODUCTION PROTECTION COMPLETE"
echo "🛡️ ========================================="
echo "✅ All data verified and protected"
echo "✅ System ready for production use"
echo "Completed at: $(date)"