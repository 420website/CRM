# Template Management Workflow Guide

## 🔄 **COMPLETE TEMPLATE WORKFLOW: Testing → Production**

### **IMPORTANT CLARIFICATION:**

**Q: If I modify templates in testing, do they automatically pull through to production?**
**A: NO - Template changes need to be explicitly migrated from testing to production.**

---

## 📋 **RECOMMENDED WORKFLOW:**

### **Option 1: Template Migration System (RECOMMENDED)**

#### **Step 1: Make Changes in Testing Environment**
```bash
# Make your template changes in the testing environment UI
# Test thoroughly to ensure templates work as expected
```

#### **Step 2: Export Templates from Testing**
```bash
# In testing environment, export all templates to migration file
cd /app && node scripts/template-migration.js export
```
This creates a migration file like: `/app/template-migration-1736891234567.json`

#### **Step 3: Deploy to Production**
```bash
# Deploy your code changes to production as usual
# The migration file will be included in the deployment
```

#### **Step 4: Import Templates in Production**
```bash
# In production environment, import templates from migration file
cd /app && node scripts/template-migration.js import template-migration-1736891234567.json
```

#### **Step 5: Verify Template Import**
```bash
# Check that templates are properly imported
cd /app && bash scripts/comprehensive-template-persistence.sh
```

---

### **Option 2: Direct Production Changes (ALTERNATIVE)**

#### **Make Changes Directly in Production**
```bash
# Make template changes directly in production environment
# Templates will be automatically backed up and persist across deployments
```

---

## 🛡️ **PERSISTENCE GUARANTEES:**

### **What WILL Persist:**
✅ **Templates modified directly in production environment**
✅ **Templates imported via migration system**
✅ **Templates backed up before deployment**

### **What WILL NOT Persist:**
❌ **Templates modified only in testing (without migration)**
❌ **Templates not backed up before deployment**

---

## 🔧 **AVAILABLE COMMANDS:**

### **Template Migration:**
```bash
# Export templates from current environment
node scripts/template-migration.js export

# Import templates to current environment
node scripts/template-migration.js import <migration-file>
```

### **Manual Backup/Restore:**
```bash
# Comprehensive backup and restore
bash scripts/comprehensive-template-persistence.sh

# Clinical templates only
node scripts/template-persistence.js backup
node scripts/template-persistence.js restore

# Notes templates only
node scripts/notes-template-persistence.js backup
node scripts/notes-template-persistence.js restore
```

---

## 🎯 **BEST PRACTICES:**

1. **Always test template changes thoroughly in testing environment**
2. **Use migration system to transfer tested changes to production**
3. **Make template changes during low-traffic periods**
4. **Always verify templates after deployment**
5. **Keep migration files for rollback purposes**

---

## 🚨 **EMERGENCY ROLLBACK:**

If templates get corrupted or lost:

```bash
# Restore from persistent backups
cd /app && bash scripts/comprehensive-template-persistence.sh

# Or restore from specific migration file
cd /app && node scripts/template-migration.js import <previous-migration-file>
```