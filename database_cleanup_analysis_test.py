#!/usr/bin/env python3
"""
Database Cleanup Analysis Test
Analyzes clinical templates, notes templates, and dispositions collections
to identify test entries vs original entries for cleanup recommendations.
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class DatabaseCleanupAnalyzer:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
        self.api_url = f"{self.base_url}/api"
        self.headers = {'Content-Type': 'application/json'}
        
        print(f"🔍 Database Cleanup Analysis")
        print(f"📡 API URL: {self.api_url}")
        print("=" * 80)

    def analyze_clinical_templates(self):
        """Analyze clinical templates collection"""
        print("\n📋 CLINICAL TEMPLATES COLLECTION ANALYSIS")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.api_url}/clinical-templates", headers=self.headers)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch clinical templates: {response.status_code}")
                return
            
            templates = response.json()
            print(f"📊 Total Clinical Templates: {len(templates)}")
            
            # Categorize templates
            original_templates = []
            test_templates = []
            
            for template in templates:
                template_id = template.get('id', 'N/A')
                name = template.get('name', 'N/A')
                content = template.get('content', '')
                content_preview = content[:100] + "..." if len(content) > 100 else content
                is_default = template.get('is_default', False)
                created_at = template.get('created_at', 'N/A')
                
                # Identify test vs original entries
                is_test_entry = self.is_test_entry(name, content)
                
                entry_info = {
                    'id': template_id,
                    'name': name,
                    'content_preview': content_preview,
                    'is_default': is_default,
                    'created_at': created_at,
                    'full_content_length': len(content)
                }
                
                if is_test_entry:
                    test_templates.append(entry_info)
                else:
                    original_templates.append(entry_info)
                
                print(f"\n🏷️  Template: {name}")
                print(f"   ID: {template_id}")
                print(f"   Default: {is_default}")
                print(f"   Created: {created_at}")
                print(f"   Content ({len(content)} chars): {content_preview}")
                print(f"   Category: {'🧪 TEST ENTRY' if is_test_entry else '✅ ORIGINAL/SYSTEM'}")
            
            print(f"\n📈 CLINICAL TEMPLATES SUMMARY:")
            print(f"   ✅ Original/System Templates: {len(original_templates)}")
            print(f"   🧪 Test Templates: {len(test_templates)}")
            
            return {
                'total': len(templates),
                'original': original_templates,
                'test': test_templates
            }
            
        except Exception as e:
            print(f"❌ Error analyzing clinical templates: {str(e)}")
            return None

    def analyze_notes_templates(self):
        """Analyze notes templates collection"""
        print("\n📝 NOTES TEMPLATES COLLECTION ANALYSIS")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.api_url}/notes-templates", headers=self.headers)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch notes templates: {response.status_code}")
                return
            
            templates = response.json()
            print(f"📊 Total Notes Templates: {len(templates)}")
            
            # Categorize templates
            original_templates = []
            test_templates = []
            
            for template in templates:
                template_id = template.get('id', 'N/A')
                name = template.get('name', 'N/A')
                content = template.get('content', '')
                content_preview = content[:100] + "..." if len(content) > 100 else content
                is_default = template.get('is_default', False)
                created_at = template.get('created_at', 'N/A')
                
                # Identify test vs original entries
                is_test_entry = self.is_test_entry(name, content)
                
                entry_info = {
                    'id': template_id,
                    'name': name,
                    'content_preview': content_preview,
                    'is_default': is_default,
                    'created_at': created_at,
                    'full_content_length': len(content)
                }
                
                if is_test_entry:
                    test_templates.append(entry_info)
                else:
                    original_templates.append(entry_info)
                
                print(f"\n📄 Template: {name}")
                print(f"   ID: {template_id}")
                print(f"   Default: {is_default}")
                print(f"   Created: {created_at}")
                print(f"   Content ({len(content)} chars): {content_preview}")
                print(f"   Category: {'🧪 TEST ENTRY' if is_test_entry else '✅ ORIGINAL/SYSTEM'}")
            
            print(f"\n📈 NOTES TEMPLATES SUMMARY:")
            print(f"   ✅ Original/System Templates: {len(original_templates)}")
            print(f"   🧪 Test Templates: {len(test_templates)}")
            
            return {
                'total': len(templates),
                'original': original_templates,
                'test': test_templates
            }
            
        except Exception as e:
            print(f"❌ Error analyzing notes templates: {str(e)}")
            return None

    def analyze_dispositions(self):
        """Analyze dispositions collection"""
        print("\n🎯 DISPOSITIONS COLLECTION ANALYSIS")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.api_url}/dispositions", headers=self.headers)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch dispositions: {response.status_code}")
                return
            
            dispositions = response.json()
            print(f"📊 Total Dispositions: {len(dispositions)}")
            
            # Categorize dispositions
            original_dispositions = []
            test_dispositions = []
            frequent_dispositions = []
            default_dispositions = []
            
            for disposition in dispositions:
                disp_id = disposition.get('id', 'N/A')
                name = disposition.get('name', 'N/A')
                is_frequent = disposition.get('is_frequent', False)
                is_default = disposition.get('is_default', False)
                created_at = disposition.get('created_at', 'N/A')
                
                # Identify test vs original entries
                is_test_entry = self.is_test_disposition(name)
                
                entry_info = {
                    'id': disp_id,
                    'name': name,
                    'is_frequent': is_frequent,
                    'is_default': is_default,
                    'created_at': created_at
                }
                
                if is_test_entry:
                    test_dispositions.append(entry_info)
                else:
                    original_dispositions.append(entry_info)
                
                if is_frequent:
                    frequent_dispositions.append(entry_info)
                
                if is_default:
                    default_dispositions.append(entry_info)
                
                print(f"\n🎯 Disposition: {name}")
                print(f"   ID: {disp_id}")
                print(f"   Frequent: {is_frequent}")
                print(f"   Default: {is_default}")
                print(f"   Created: {created_at}")
                print(f"   Category: {'🧪 TEST ENTRY' if is_test_entry else '✅ ORIGINAL/SYSTEM'}")
            
            print(f"\n📈 DISPOSITIONS SUMMARY:")
            print(f"   ✅ Original/System Dispositions: {len(original_dispositions)}")
            print(f"   🧪 Test Dispositions: {len(test_dispositions)}")
            print(f"   ⭐ Frequent Dispositions: {len(frequent_dispositions)}")
            print(f"   🔧 Default Dispositions: {len(default_dispositions)}")
            
            return {
                'total': len(dispositions),
                'original': original_dispositions,
                'test': test_dispositions,
                'frequent': frequent_dispositions,
                'default': default_dispositions
            }
            
        except Exception as e:
            print(f"❌ Error analyzing dispositions: {str(e)}")
            return None

    def is_test_entry(self, name, content):
        """Determine if a template entry is likely a test entry"""
        test_indicators = [
            'test', 'testing', 'sample', 'example', 'demo', 'temp', 'temporary',
            'bulk', 'custom test', 'new template', 'my template', 'user template',
            'template 1', 'template 2', 'template 3', 'template test',
            'asdf', 'qwerty', 'lorem ipsum', 'placeholder'
        ]
        
        name_lower = name.lower()
        content_lower = content.lower()
        
        # Check name for test indicators
        for indicator in test_indicators:
            if indicator in name_lower:
                return True
        
        # Check content for test indicators (first 200 chars)
        content_check = content_lower[:200]
        for indicator in test_indicators:
            if indicator in content_check:
                return True
        
        # Check for very short content (likely test)
        if len(content.strip()) < 10:
            return True
        
        # Check for generic/placeholder content
        generic_phrases = [
            'this is a test', 'test content', 'sample text',
            'enter text here', 'placeholder text', 'default content'
        ]
        
        for phrase in generic_phrases:
            if phrase in content_lower:
                return True
        
        return False

    def is_test_disposition(self, name):
        """Determine if a disposition entry is likely a test entry"""
        test_indicators = [
            'test', 'testing', 'sample', 'example', 'demo', 'temp', 'temporary',
            'bulk', 'custom', 'new disposition', 'my disposition', 'user disposition',
            'disposition 1', 'disposition 2', 'disposition test',
            'asdf', 'qwerty', 'placeholder'
        ]
        
        name_lower = name.lower()
        
        # Check name for test indicators
        for indicator in test_indicators:
            if indicator in name_lower:
                return True
        
        # Check for non-standard medical disposition patterns
        # Original dispositions are typically medical abbreviations or standard terms
        standard_patterns = [
            'active', 'pending', 'completed', 'discontinued', 'deceased',
            'consult', 'delivery', 'dispensing', 'locate', 'housing',
            'jail', 'lab', 'refused', 'sot', 'hiv', 'external', 'duplicate',
            'cured', 'inactive', 'trillium', 'reimbursement'
        ]
        
        # If it doesn't contain any standard medical terms, might be test
        has_standard_term = any(term in name_lower for term in standard_patterns)
        
        # Very short names without standard terms are likely test
        if len(name.strip()) < 3 and not has_standard_term:
            return True
        
        return False

    def generate_cleanup_recommendations(self, clinical_analysis, notes_analysis, dispositions_analysis):
        """Generate cleanup recommendations based on analysis"""
        print("\n🧹 DATABASE CLEANUP RECOMMENDATIONS")
        print("=" * 80)
        
        total_test_entries = 0
        total_original_entries = 0
        
        if clinical_analysis:
            total_test_entries += len(clinical_analysis['test'])
            total_original_entries += len(clinical_analysis['original'])
            
            print(f"\n📋 CLINICAL TEMPLATES CLEANUP:")
            if clinical_analysis['test']:
                print(f"   🗑️  RECOMMEND DELETION ({len(clinical_analysis['test'])} entries):")
                for template in clinical_analysis['test']:
                    print(f"      - ID: {template['id']} | Name: '{template['name']}' | Created: {template['created_at']}")
            else:
                print(f"   ✅ No test entries found - all templates appear to be original/system")
            
            print(f"   ✅ KEEP ({len(clinical_analysis['original'])} entries):")
            for template in clinical_analysis['original'][:5]:  # Show first 5
                print(f"      - ID: {template['id']} | Name: '{template['name']}' | Default: {template['is_default']}")
            if len(clinical_analysis['original']) > 5:
                print(f"      ... and {len(clinical_analysis['original']) - 5} more original templates")
        
        if notes_analysis:
            total_test_entries += len(notes_analysis['test'])
            total_original_entries += len(notes_analysis['original'])
            
            print(f"\n📝 NOTES TEMPLATES CLEANUP:")
            if notes_analysis['test']:
                print(f"   🗑️  RECOMMEND DELETION ({len(notes_analysis['test'])} entries):")
                for template in notes_analysis['test']:
                    print(f"      - ID: {template['id']} | Name: '{template['name']}' | Created: {template['created_at']}")
            else:
                print(f"   ✅ No test entries found - all templates appear to be original/system")
            
            print(f"   ✅ KEEP ({len(notes_analysis['original'])} entries):")
            for template in notes_analysis['original'][:5]:  # Show first 5
                print(f"      - ID: {template['id']} | Name: '{template['name']}' | Default: {template['is_default']}")
            if len(notes_analysis['original']) > 5:
                print(f"      ... and {len(notes_analysis['original']) - 5} more original templates")
        
        if dispositions_analysis:
            total_test_entries += len(dispositions_analysis['test'])
            total_original_entries += len(dispositions_analysis['original'])
            
            print(f"\n🎯 DISPOSITIONS CLEANUP:")
            if dispositions_analysis['test']:
                print(f"   🗑️  RECOMMEND DELETION ({len(dispositions_analysis['test'])} entries):")
                for disposition in dispositions_analysis['test']:
                    print(f"      - ID: {disposition['id']} | Name: '{disposition['name']}' | Created: {disposition['created_at']}")
            else:
                print(f"   ✅ No test entries found - all dispositions appear to be original/system")
            
            print(f"   ✅ KEEP ({len(dispositions_analysis['original'])} entries):")
            print(f"      - {len(dispositions_analysis['frequent'])} frequent dispositions")
            print(f"      - {len(dispositions_analysis['default'])} default dispositions")
            for disposition in dispositions_analysis['original'][:5]:  # Show first 5
                freq_flag = "⭐" if disposition['is_frequent'] else ""
                default_flag = "🔧" if disposition['is_default'] else ""
                print(f"      - {freq_flag}{default_flag} ID: {disposition['id']} | Name: '{disposition['name']}'")
            if len(dispositions_analysis['original']) > 5:
                print(f"      ... and {len(dispositions_analysis['original']) - 5} more original dispositions")
        
        print(f"\n📊 OVERALL CLEANUP SUMMARY:")
        print(f"   🗑️  Total Test Entries to Delete: {total_test_entries}")
        print(f"   ✅ Total Original Entries to Keep: {total_original_entries}")
        print(f"   📈 Database Cleanup Impact: {total_test_entries}/{total_test_entries + total_original_entries} entries ({(total_test_entries/(total_test_entries + total_original_entries)*100):.1f}% reduction)")
        
        print(f"\n⚠️  CLEANUP SAFETY NOTES:")
        print(f"   - Always backup database before deletion")
        print(f"   - Verify test entries are not referenced by active registrations")
        print(f"   - Default templates should never be deleted")
        print(f"   - Consider archiving instead of permanent deletion")

    def run_complete_analysis(self):
        """Run complete database cleanup analysis"""
        print("🚀 Starting Complete Database Cleanup Analysis...")
        
        # Analyze each collection
        clinical_analysis = self.analyze_clinical_templates()
        notes_analysis = self.analyze_notes_templates()
        dispositions_analysis = self.analyze_dispositions()
        
        # Generate cleanup recommendations
        self.generate_cleanup_recommendations(clinical_analysis, notes_analysis, dispositions_analysis)
        
        print(f"\n✅ Database Cleanup Analysis Complete!")
        return {
            'clinical_templates': clinical_analysis,
            'notes_templates': notes_analysis,
            'dispositions': dispositions_analysis
        }

if __name__ == "__main__":
    analyzer = DatabaseCleanupAnalyzer()
    results = analyzer.run_complete_analysis()