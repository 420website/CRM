#!/bin/bash

# DEPLOYMENT PROTECTION HOOK
# This script prevents accidental "brand new" selection during deployment
# It intercepts any attempt to wipe production data

set -e

echo "🚨 DEPLOYMENT PROTECTION ACTIVE"
echo "==============================================="

# Check if production lock exists
if [ -f "/app/persistent-data/.production-lock" ]; then
    echo "🔒 Production lock detected - PREVENTING data wipe"
    
    # Read lock file
    echo "📋 Lock file contents:"
    cat /app/persistent-data/.production-lock
    
    # Count current records
    CLIENT_COUNT=$(mongosh --quiet --eval "db.getSiblingDB('my420_ca_db').admin_registrations.countDocuments({})" 2>/dev/null || echo "0")
    echo "🔢 Current client records: $CLIENT_COUNT"
    
    if [ "$CLIENT_COUNT" -gt 0 ]; then
        echo "✅ Production data verified - preventing any wipe operations"
        
        # Create additional protection files
        touch /app/.PRODUCTION-DO-NOT-WIPE
        touch /app/.DEPLOYMENT-PROTECTION-ACTIVE
        
        # Override any seed/wipe commands
        if [ -f "/app/scripts/force-seed-data.js" ]; then
            cp /app/scripts/force-seed-data.js /app/scripts/force-seed-data.js.backup
            echo "console.log('🛡️ PRODUCTION PROTECTED - Seeding blocked');" > /app/scripts/force-seed-data.js.temp
            echo "process.exit(0);" >> /app/scripts/force-seed-data.js.temp
            mv /app/scripts/force-seed-data.js.temp /app/scripts/force-seed-data.js
        fi
        
        echo "🛡️ All wipe operations blocked"
        echo "🛡️ Production data is SAFE"
    else
        echo "⚠️ No client data found - this may be legitimate fresh install"
    fi
else
    echo "⚠️ No production lock found - creating one now"
    /app/scripts/production-lock.py --force-protect
fi

echo "==============================================="
echo "🛡️ DEPLOYMENT PROTECTION COMPLETE"