import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import AddressAutocomplete from '../components/AddressAutocomplete';

const AdminRegister = () => {
  const navigate = useNavigate();
  
  // Get current user permissions
  const getCurrentUserPermissions = () => {
    try {
      const currentUser = sessionStorage.getItem('current_user');
      if (currentUser) {
        const userData = JSON.parse(currentUser);
        return userData.permissions || {};
      }
    } catch (error) {
      console.error('Error getting user permissions:', error);
    }
    return {};
  };

  // Check if user has permission for a tab
  const hasTabPermission = (tabName) => {
    const permissions = getCurrentUserPermissions();
    
    // Special handling for admin user (PIN 0224) - always has all permissions
    try {
      const currentUser = sessionStorage.getItem('current_user');
      if (currentUser) {
        const userData = JSON.parse(currentUser);
        if (userData.user_id === "admin" && userData.user_type === "admin") {
          return true; // Admin has access to all tabs
        }
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
    }
    
    // For regular users, only allow access if permission is explicitly set to true
    return permissions[tabName] === true;
  };

  // Get allowed tabs based on user permissions
  const getAllowedTabs = () => {
    const allTabs = [
      { id: 'patient', name: 'Client' },
      { id: 'tests', name: 'Tests' },
      { id: 'medication', name: 'Medication' },
      { id: 'dispensing', name: 'Dispensing' },
      { id: 'notes', name: 'Notes' },
      { id: 'activities', name: 'Activities' },
      { id: 'interactions', name: 'Interactions' },
      { id: 'attachments', name: 'Attachments' }
    ];
    
    const allowedTabs = allTabs.filter(tab => hasTabPermission(tab.name));
    
    // Ensure at least one tab is always available (default to Client if no permissions)
    if (allowedTabs.length === 0) {
      return [{ id: 'patient', name: 'Client' }];
    }
    
    return allowedTabs;
  };

  const [pinVerified, setPinVerified] = useState(false);
  const [pinInput, setPinInput] = useState("");
  const [pinError, setPinError] = useState("");
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    dob: "",
    patientConsent: "verbal", // Default to verbal
    gender: "",
    province: "Ontario", // Default to Ontario
    disposition: "",
    aka: "",
    age: "",
    regDate: new Date().toISOString().split('T')[0], // Default to current date
    healthCard: "",
    healthCardVersion: "", // Add health card version code
    referralSite: "",
    address: "",
    unitNumber: "",
    city: "",
    postalCode: "",
    phone1: "",
    phone2: "",
    leaveMessage: false,
    voicemail: false,
    text: false,
    preferredTime: "",
    email: "",
    language: "English", // Default to English
    specialAttention: "",
    instructions: "", // Add instructions field
    photo: null, // Add photo field
    summaryTemplate: "", // Will be populated from template selection
    physician: "Dr. David Fletcher", // Add physician field with default
    rnaAvailable: "No", // Add RNA available field
    rnaSampleDate: "", // Add RNA sample date field
    rnaResult: "Positive", // Add RNA result field
    coverageType: "Select", // Add coverage type field
    referralPerson: "", // Add referral person field
    testType: "Tests", // Add test type field with default
    // HIV Test Fields
    hivDate: new Date().toISOString().split('T')[0], // Current date for HIV test
    hivResult: "negative", // HIV test result (default to negative)
    hivType: "", // HIV type (Type 1 or Type 2)
    hivTester: "CM" // HIV tester initials (default CM)
  });

  const [submitStatus, setSubmitStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Clinical Summary Template States
  const [selectedTemplate, setSelectedTemplate] = useState('Select');
  const [templates, setTemplates] = useState({});
  const [isEditingTemplate, setIsEditingTemplate] = useState(false);
  const [availableClinicalTemplates, setAvailableClinicalTemplates] = useState([]);
  const [showClinicalTemplateManager, setShowClinicalTemplateManager] = useState(false);
  const [newClinicalTemplateName, setNewClinicalTemplateName] = useState('');
  const [newClinicalTemplateContent, setNewClinicalTemplateContent] = useState('');
  const [editingClinicalTemplateId, setEditingClinicalTemplateId] = useState(null);
  
  // Notes Template States (identical functionality to Clinical Summary)
  const [selectedNotesTemplate, setSelectedNotesTemplate] = useState('Select');
  const [notesTemplates, setNotesTemplates] = useState({});
  const [isEditingNotesTemplate, setIsEditingNotesTemplate] = useState(false);
  const [availableNotesTemplates, setAvailableNotesTemplates] = useState([]);
  const [showTemplateManager, setShowTemplateManager] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [newTemplateContent, setNewTemplateContent] = useState('');
  const [editingTemplateId, setEditingTemplateId] = useState(null);
  
  // Special Attention Template States
  const [selectedSpecialAttentionTemplate, setSelectedSpecialAttentionTemplate] = useState('Select');
  const [specialAttentionTemplates, setSpecialAttentionTemplates] = useState({});
  const [isEditingSpecialAttentionTemplate, setIsEditingSpecialAttentionTemplate] = useState(false);
  
  // Disposition Management States
  const [availableDispositions, setAvailableDispositions] = useState([]);
  const [showDispositionManager, setShowDispositionManager] = useState(false);
  const [newDispositionName, setNewDispositionName] = useState('');
  const [newDispositionIsFrequent, setNewDispositionIsFrequent] = useState(false);
  const [editingDisposition, setEditingDisposition] = useState(null);
  const [showEditPopup, setShowEditPopup] = useState(false);
  const [dispositionSearch, setDispositionSearch] = useState('');
  
  // Referral Site Management States
  const [availableReferralSites, setAvailableReferralSites] = useState([]);
  const [showReferralSiteManager, setShowReferralSiteManager] = useState(false);
  const [newReferralSiteName, setNewReferralSiteName] = useState('');
  const [newReferralSiteIsFrequent, setNewReferralSiteIsFrequent] = useState(false);
  const [editingReferralSite, setEditingReferralSite] = useState(null);
  const [showReferralSiteEditPopup, setShowReferralSiteEditPopup] = useState(false);
  const [referralSiteSearch, setReferralSiteSearch] = useState('');
  
  // Initialize templates with better localStorage handling
  const getStoredTemplates = () => {
    try {
      const saved = localStorage.getItem('clinicalSummaryTemplates');
      if (saved) {
        const parsed = JSON.parse(saved);
        console.log('✅ Loaded templates from localStorage:', parsed);
        return parsed;
      }
    } catch (error) {
      console.error('❌ Error loading templates from localStorage:', error);
    }
    
    // Return default templates if none saved
    const defaultTemplates = {
      'Positive': "Dx 10+ years ago and treated. RNA - no labs available. However, has had ongoing risk factors with sharing pipes and straws. Counselled regarding risk factors. Point of care test was completed for HCV and tested positive at approximately two minutes with a dark line. HIV testing came back negative. Collected a DBS specimen and advised that it will take approximately 7 to 10 days for results. Referral: none. Client does have a valid address and has also provided a phone number for results.",
      'Negative - Pipes': "",
      'Negative - Pipes/Straws': "",
      'Negative - Pipes/Straws/Needles': ""
    };
    console.log('📋 Using default templates');
    return defaultTemplates;
  };
  
  // Template Management Functions - FIXED FOR PROPER TEMPLATE SELECTION
  const handleTemplateChange = async (templateName) => {
    console.log(`🔄 Changing template to: ${templateName}`);
    setSelectedTemplate(templateName);
    
    if (templateName === 'Select') {
      // Clear template when Select is chosen - this should be the default
      setFormData(prev => ({
        ...prev,
        summaryTemplate: ""
      }));
      console.log(`✅ Cleared template for Select - form now empty`);
    } else if (templateName === 'Positive') {
      // Only generate dynamic template when explicitly selected by user
      const dynamicTemplate = await updateClinicalSummary(formData);
      setFormData(prev => ({
        ...prev,
        summaryTemplate: dynamicTemplate
      }));
      console.log(`✅ Set Positive template content - user explicitly selected`);
    } else {
      // Load saved template content from database for other templates
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${API}/api/clinical-templates`);
        
        if (response.ok) {
          const templatesArray = await response.json();
          const templatesObject = {};
          
          // Convert array to object for easier access
          templatesArray.forEach(template => {
            templatesObject[template.name] = template.content;
          });
          
          const templateContent = templatesObject[templateName] || "";
          console.log(`📋 Loading "${templateName}" from database:`, templateContent.substring(0, 100));
          
          setFormData(prev => ({
            ...prev,
            summaryTemplate: templateContent
          }));
          
          // Update templates state
          setTemplates(templatesObject);
        } else {
          console.log(`⚠️ Failed to load templates from database, using empty content`);
          setFormData(prev => ({
            ...prev,
            summaryTemplate: ""
          }));
        }
      } catch (error) {
        console.error(`❌ Error loading template from database:`, error);
        setFormData(prev => ({
          ...prev,
          summaryTemplate: ""
        }));
      }
    }
  };

  const saveTemplate = async () => {
    if (selectedTemplate !== 'Positive' && selectedTemplate !== 'Select' && formData.summaryTemplate.trim() !== '') {
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        
        // Save template to database
        const response = await fetch(`${API}/api/clinical-templates/save-all`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            [selectedTemplate]: formData.summaryTemplate
          }),
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log(`✅ Template "${selectedTemplate}" saved to database:`, result);
          
          // Update local state
          setTemplates(prev => ({
            ...prev,
            [selectedTemplate]: formData.summaryTemplate
          }));
          
          setIsEditingTemplate(false);
          alert(`Template "${selectedTemplate}" saved successfully!`);
        } else {
          throw new Error(`Failed to save template: ${response.statusText}`);
        }
      } catch (error) {
        console.error(`❌ Error saving template to database:`, error);
        alert(`Error saving template: ${error.message}`);
      }
    } else {
      alert('Please select a valid template and ensure content is not empty.');
    }
  };

  const cancelTemplateEdit = async () => {
    // Restore original template content
    if (selectedTemplate === 'Positive') {
      const dynamicTemplate = await updateClinicalSummary(formData);
      setFormData(prev => ({
        ...prev,
        summaryTemplate: dynamicTemplate
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        summaryTemplate: templates[selectedTemplate] || ""
      }));
    }
    setIsEditingTemplate(false);
  };

  const resetAllTemplates = async () => {
    if (confirm('Are you sure you want to reset all templates? This will delete all your saved custom templates and restore defaults.')) {
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        
        const defaultTemplates = {
          'Positive': "Dx 10+ years ago and treated. RNA - no labs available. However, has had ongoing risk factors with sharing pipes and straws. Counselled regarding risk factors. Point of care test was completed for HCV and tested positive at approximately two minutes with a dark line. HIV testing came back negative. Collected a DBS specimen and advised that it will take approximately 7 to 10 days for results. Referral: none. Client does have a valid address and has also provided a phone number for results.",
          'Negative - Pipes': "",
          'Negative - Pipes/Straws': "",
          'Negative - Pipes/Straws/Needles': ""
        };
        
        // Save default templates to database
        const response = await fetch(`${API}/api/clinical-templates/save-all`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(defaultTemplates),
        });
        
        if (response.ok) {
          setTemplates(defaultTemplates);
          setSelectedTemplate('Select');
          setFormData(prev => ({
            ...prev,
            summaryTemplate: ""
          }));
          
          console.log('✅ Templates reset to defaults and saved to database');
          alert('Templates have been reset to defaults and saved to database!');
        } else {
          throw new Error(`Failed to reset templates: ${response.statusText}`);
        }
      } catch (error) {
        console.error('❌ Error resetting templates:', error);
        alert(`Error resetting templates: ${error.message}`);
      }
    }
  };

  // Force refresh templates from localStorage on component mount
  // Load templates from database on component mount
  React.useEffect(() => {
    const loadTemplatesFromDatabase = async () => {
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${API}/api/clinical-templates`);
        
        if (response.ok) {
          const templatesArray = await response.json();
          const templatesObject = {};
          
          // Convert array to object for easier access
          templatesArray.forEach(template => {
            templatesObject[template.name] = template.content;
          });
          
          setTemplates(templatesObject);
          setAvailableClinicalTemplates(templatesArray); // Set available templates for dropdown
          console.log('📥 Loaded templates from database:', templatesObject);
        } else {
          console.log('⚠️ No templates found in database, using defaults');
        }
      } catch (error) {
        console.error('❌ Error loading templates from database:', error);
      }
    };
    
    loadTemplatesFromDatabase();
  }, []); // Only run on mount

  // Template content is now handled by handleTemplateChange function and database loading
  // Removed localStorage-based useEffect to prevent conflicts

  // Notes Template Management Functions (identical to Clinical Summary)
  const handleNotesTemplateChange = async (templateName) => {
    console.log(`🔄 Notes template change to: ${templateName}`);
    setSelectedNotesTemplate(templateName);
    
    if (templateName === 'Select') {
      setNotesData(prev => ({
        ...prev,
        noteText: ""
      }));
      console.log(`✅ Notes template cleared - Select chosen`);
    } else {
      // Load saved template content from database for Notes templates
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${API}/api/notes-templates`);
        
        if (response.ok) {
          const templatesArray = await response.json();
          const templatesObject = {};
          
          // Convert array to object for easier access
          templatesArray.forEach(template => {
            templatesObject[template.name] = template.content;
          });
          
          const templateContent = templatesObject[templateName] || "";
          console.log(`📋 Loading Notes "${templateName}" from database:`, templateContent.substring(0, 100));
          
          setNotesData(prev => ({
            ...prev,
            noteText: templateContent
          }));
          
          // Update templates state
          setNotesTemplates(templatesObject);
        } else {
          console.log(`⚠️ Failed to load Notes templates from database, using empty content`);
          setNotesData(prev => ({
            ...prev,
            noteText: ""
          }));
        }
      } catch (error) {
        console.error(`❌ Error loading Notes template from database:`, error);
        setNotesData(prev => ({
          ...prev,
          noteText: ""
        }));
      }
    }
  };

  const saveNotesTemplate = async () => {
    if (selectedNotesTemplate !== 'Select' && notesData.noteText.trim() !== '') {
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        
        // Save Notes template to database
        const response = await fetch(`${API}/api/notes-templates/save-all`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            [selectedNotesTemplate]: notesData.noteText
          }),
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log(`✅ Notes template "${selectedNotesTemplate}" saved to database:`, result);
          
          // Update local state
          setNotesTemplates(prev => ({
            ...prev,
            [selectedNotesTemplate]: notesData.noteText
          }));
          
          setIsEditingNotesTemplate(false);
          alert(`Notes template "${selectedNotesTemplate}" saved successfully!`);
        } else {
          throw new Error(`Failed to save Notes template: ${response.statusText}`);
        }
      } catch (error) {
        console.error(`❌ Error saving Notes template to database:`, error);
        alert(`Error saving Notes template: ${error.message}`);
      }
    } else {
      alert('Please select a valid template and ensure content is not empty.');
    }
  };

  const cancelNotesTemplateEdit = () => {
    // Restore original template content for Notes
    if (selectedNotesTemplate !== 'Select') {
      setNotesData(prev => ({
        ...prev,
        noteText: notesTemplates[selectedNotesTemplate] || ""
      }));
    }
    setIsEditingNotesTemplate(false);
  };

  const resetAllNotesTemplates = async () => {
    if (confirm('Are you sure you want to reset all Notes templates? This will delete all your saved custom Notes templates and restore defaults.')) {
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        
        const defaultNotesTemplates = {
          'Consultation': "",
          'Lab': "",
          'Prescription': ""
        };
        
        // Save default Notes templates to database
        const response = await fetch(`${API}/api/notes-templates/save-all`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(defaultNotesTemplates),
        });
        
        if (response.ok) {
          setNotesTemplates(defaultNotesTemplates);
          setSelectedNotesTemplate('Select');
          setNotesData(prev => ({
            ...prev,
            noteText: ""
          }));
          
          console.log('✅ Notes templates reset to defaults and saved to database');
          alert('Notes templates have been reset to defaults and saved to database!');
        } else {
          throw new Error(`Failed to reset Notes templates: ${response.statusText}`);
        }
      } catch (error) {
        console.error('❌ Error resetting Notes templates:', error);
        alert(`Error resetting Notes templates: ${error.message}`);
      }
    }
  };

  // Load Notes templates from database on component mount
  React.useEffect(() => {
    const loadNotesTemplatesFromDatabase = async () => {
      try {
        const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${API}/api/notes-templates`);
        
        if (response.ok) {
          const templatesArray = await response.json();
          const templatesObject = {};
          
          // Convert array to object for easier access
          templatesArray.forEach(template => {
            templatesObject[template.name] = template.content;
          });
          
          setNotesTemplates(templatesObject);
          setAvailableNotesTemplates(templatesArray); // Set available templates for dropdown
          console.log('📥 Loaded Notes templates from database:', templatesObject);
        } else {
          console.log('⚠️ No Notes templates found in database, using defaults');
        }
      } catch (error) {
        console.error('❌ Error loading Notes templates from database:', error);
      }
    };
    
    loadNotesTemplatesFromDatabase();
  }, []); // Only run on mount

  // Disposition Management Functions
  const loadDispositionsFromDatabase = async () => {
    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/dispositions`);
      
      if (response.ok) {
        const dispositionsArray = await response.json();
        setAvailableDispositions(dispositionsArray);
        console.log('📥 Loaded dispositions from database:', dispositionsArray.length);
      } else {
        console.log('⚠️ No dispositions found in database');
      }
    } catch (error) {
      console.error('❌ Error loading dispositions from database:', error);
    }
  };

  const addNewDisposition = async () => {
    if (!newDispositionName.trim()) {
      alert('Please enter a disposition name');
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/dispositions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newDispositionName.trim(),
          is_frequent: newDispositionIsFrequent,
          is_default: false
        }),
      });

      if (response.ok) {
        const newDisposition = await response.json();
        setAvailableDispositions(prev => [...prev, newDisposition]);
        setNewDispositionName('');
        setNewDispositionIsFrequent(false);
        alert('Disposition added successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add disposition');
      }
    } catch (error) {
      console.error('Error adding disposition:', error);
      alert('Failed to add disposition: ' + error.message);
    }
  };

  const updateDisposition = async (dispositionId, name, isFrequent) => {
    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/dispositions/${dispositionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          is_frequent: isFrequent
        }),
      });

      if (response.ok) {
        const updatedDisposition = await response.json();
        setAvailableDispositions(prev => 
          prev.map(disposition => 
            disposition.id === dispositionId ? updatedDisposition : disposition
          )
        );
        setEditingDisposition(null);
        setShowEditPopup(false);
        alert('Disposition updated successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update disposition');
      }
    } catch (error) {
      console.error('Error updating disposition:', error);
      alert('Failed to update disposition: ' + error.message);
    }
  };

  const deleteDisposition = async (dispositionId, dispositionName) => {
    if (!window.confirm(`Are you sure you want to delete the "${dispositionName}" disposition?`)) {
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/dispositions/${dispositionId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setAvailableDispositions(prev => prev.filter(disposition => disposition.id !== dispositionId));
        setEditingDisposition(null);
        setShowEditPopup(false);
        alert('Disposition deleted successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete disposition');
      }
    } catch (error) {
      console.error('Error deleting disposition:', error);
      alert('Failed to delete disposition: ' + error.message);
    }
  };

  const openEditDisposition = (disposition) => {
    console.log('Opening edit popup for disposition:', disposition);
    setEditingDisposition(disposition);
    setShowEditPopup(true);
  };

  const closeDispositionManager = () => {
    setShowDispositionManager(false);
    setNewDispositionName('');
    setNewDispositionIsFrequent(false);
    setEditingDisposition(null);
    setShowEditPopup(false);
    setDispositionSearch('');
  };

  // Filter dispositions based on search
  const getFilteredDispositions = () => {
    if (!dispositionSearch.trim()) {
      return availableDispositions;
    }
    
    const searchTerm = dispositionSearch.toLowerCase();
    return availableDispositions.filter(disposition => 
      disposition.name.toLowerCase().includes(searchTerm)
    );
  };

  // Load dispositions from database on component mount
  React.useEffect(() => {
    loadDispositionsFromDatabase();
  }, []); // Only run on mount

  // Referral Site Management Functions
  const loadReferralSitesFromDatabase = async () => {
    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/referral-sites`);
      
      if (response.ok) {
        const referralSitesArray = await response.json();
        setAvailableReferralSites(referralSitesArray);
        console.log('📥 Loaded referral sites from database:', referralSitesArray.length);
      } else {
        console.log('⚠️ No referral sites found in database');
      }
    } catch (error) {
      console.error('❌ Error loading referral sites from database:', error);
    }
  };

  const addNewReferralSite = async () => {
    if (!newReferralSiteName.trim()) {
      alert('Please enter a referral site name');
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/referral-sites`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newReferralSiteName.trim(),
          is_frequent: newReferralSiteIsFrequent,
          is_default: false
        }),
      });

      if (response.ok) {
        const newReferralSite = await response.json();
        setAvailableReferralSites(prev => [...prev, newReferralSite]);
        setNewReferralSiteName('');
        setNewReferralSiteIsFrequent(false);
        alert('Referral site added successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add referral site');
      }
    } catch (error) {
      console.error('Error adding referral site:', error);
      alert('Failed to add referral site: ' + error.message);
    }
  };

  const updateReferralSite = async (referralSiteId, name, isFrequent) => {
    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/referral-sites/${referralSiteId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          is_frequent: isFrequent
        }),
      });

      if (response.ok) {
        const updatedReferralSite = await response.json();
        setAvailableReferralSites(prev => 
          prev.map(site => 
            site.id === referralSiteId ? updatedReferralSite : site
          )
        );
        setEditingReferralSite(null);
        setShowReferralSiteEditPopup(false);
        alert('Referral site updated successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update referral site');
      }
    } catch (error) {
      console.error('Error updating referral site:', error);
      alert('Failed to update referral site: ' + error.message);
    }
  };

  const deleteReferralSite = async (referralSiteId, referralSiteName) => {
    if (!window.confirm(`Are you sure you want to delete the "${referralSiteName}" referral site?`)) {
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/referral-sites/${referralSiteId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setAvailableReferralSites(prev => prev.filter(site => site.id !== referralSiteId));
        setEditingReferralSite(null);
        setShowReferralSiteEditPopup(false);
        alert('Referral site deleted successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete referral site');
      }
    } catch (error) {
      console.error('Error deleting referral site:', error);
      alert('Failed to delete referral site: ' + error.message);
    }
  };

  const openEditReferralSite = (referralSite) => {
    console.log('Opening edit popup for referral site:', referralSite);
    setEditingReferralSite(referralSite);
    setShowReferralSiteEditPopup(true);
  };

  const closeReferralSiteManager = () => {
    setShowReferralSiteManager(false);
    setNewReferralSiteName('');
    setNewReferralSiteIsFrequent(false);
    setEditingReferralSite(null);
    setShowReferralSiteEditPopup(false);
    setReferralSiteSearch('');
  };

  // Filter referral sites based on search
  const getFilteredReferralSites = () => {
    if (!referralSiteSearch.trim()) {
      return availableReferralSites;
    }
    
    const searchTerm = referralSiteSearch.toLowerCase();
    return availableReferralSites.filter(site => 
      site.name.toLowerCase().includes(searchTerm)
    );
  };

  // Load referral sites from database on component mount
  React.useEffect(() => {
    loadReferralSitesFromDatabase();
  }, []); // Only run on mount

  // Postal code formatting function (Canadian format: A1A 1A1)
  // Format postal code to Canadian format (A1A 1A1)
  const formatPostalCode = (postalCode) => {
    if (!postalCode) return '';
    
    // Remove all non-alphanumeric characters and convert to uppercase
    const cleaned = postalCode.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
    
    // Limit to 6 characters
    const limitedPostalCode = cleaned.substring(0, 6);
    
    // Format based on length
    if (limitedPostalCode.length === 0) {
      return '';
    } else if (limitedPostalCode.length <= 3) {
      return limitedPostalCode;
    } else {
      return `${limitedPostalCode.substring(0, 3)} ${limitedPostalCode.substring(3)}`;
    }
  };
  
  // Copy form data function with test summary
  const copyFormData = async () => {
    try {
      // Debug information
      console.log('🔄 Copy button clicked');
      console.log('📋 Current Registration ID:', currentRegistrationId);
      
      // Get fresh test data directly from API
      let currentTests = [];
      if (currentRegistrationId) {
        console.log('🔄 Fetching fresh test data...');
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/tests`);
          if (response.ok) {
            const data = await response.json();
            currentTests = data.tests || [];
            console.log('✅ Fresh test data loaded:', currentTests);
          } else {
            console.warn('⚠️ Failed to load test data, proceeding without tests');
          }
        } catch (error) {
          console.warn('⚠️ Error loading test data, proceeding without tests:', error);
        }
      }
      
      // Format date of birth
      let formattedDOB = '';
      if (formData.dob) {
        // Create date in local timezone to avoid timezone conversion issues
        const dateParts = formData.dob.split('-');
        const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]); // year, month (0-indexed), day
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        formattedDOB = `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
      }

      // Format test summary using fresh data
      let testSummary = '';
      if (currentTests && currentTests.length > 0) {
        console.log('✅ Including test summary in copy');
        testSummary = '\n\nTEST SUMMARY:\n';
        currentTests.forEach((test, index) => {
          console.log(`📝 Processing test ${index + 1}:`, test);
          const testDate = test.test_date ? new Date(test.test_date).toLocaleDateString() : 'No date';
          testSummary += `\nTest ${index + 1} (${testDate}):\n`;
          testSummary += `Type: ${test.test_type || 'Not specified'}\n`;
          
          if (test.test_type === 'HIV' || test.test_type === 'Combined') {
            testSummary += `HIV Result: ${test.hiv_result || 'Not specified'}`;
            if (test.hiv_result === 'positive' && test.hiv_type) {
              testSummary += ` (${test.hiv_type})`;
            }
            testSummary += `\nHIV Tester: ${test.hiv_tester || 'Not specified'}\n`;
          }
          
          if (test.test_type === 'HCV' || test.test_type === 'Combined') {
            testSummary += `HCV Result: ${test.hcv_result || 'Not specified'}\n`;
            testSummary += `HCV Tester: ${test.hcv_tester || 'Not specified'}\n`;
          }
          
          if (test.bloodwork_type) {
            testSummary += `Bloodwork Type: ${test.bloodwork_type}`;
            if (test.bloodwork_type === 'DBS' && test.bloodwork_circles) {
              testSummary += ` (${test.bloodwork_circles} circles)`;
            }
            testSummary += '\n';
          }
        });
      } else {
        console.log('⚠️ No test data available for copy');
      }

      // Format data with actual form values and test summary
      const formattedData = `${formData.lastName}, ${formData.firstName}
${formattedDOB}
HCN # ${formData.healthCard || ''} ${formData.healthCardVersion || ''}
Tel: ${formData.phone1 || ''}
${formData.address || ''}
${formData.city || ''}, ${formData.province?.toUpperCase().substring(0, 2) || ''}, ${formData.postalCode || ''}

MEDICAL INFORMATION:
${formData.summaryTemplate || ''}${testSummary}`;

      // Try modern clipboard API first, fallback to legacy method
      let copySuccess = false;
      
      // For iOS Safari, we need to use the more compatible approach
      if (navigator.clipboard && navigator.clipboard.writeText) {
        try {
          await navigator.clipboard.writeText(formattedData);
          copySuccess = true;
          console.log('✅ Copy successful using modern clipboard API');
        } catch (error) {
          console.warn('⚠️ Modern clipboard API failed, trying fallback method:', error);
        }
      }
      
      // Enhanced fallback method with better mobile support
      if (!copySuccess) {
        try {
          const textArea = document.createElement('textarea');
          textArea.value = formattedData;
          textArea.style.position = 'fixed';
          textArea.style.left = '-999999px';
          textArea.style.top = '-999999px';
          textArea.style.opacity = '0';
          textArea.setAttribute('readonly', '');
          textArea.setAttribute('contenteditable', 'true');
          document.body.appendChild(textArea);
          
          // For iOS, we need to handle selection differently
          if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            textArea.contentEditable = true;
            textArea.readOnly = false;
            const range = document.createRange();
            range.selectNodeContents(textArea);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            textArea.setSelectionRange(0, 999999);
          } else {
            textArea.focus();
            textArea.select();
          }
          
          const successful = document.execCommand('copy');
          document.body.removeChild(textArea);
          
          if (successful) {
            copySuccess = true;
            console.log('✅ Copy successful using enhanced fallback method');
          } else {
            console.error('❌ Enhanced fallback copy method failed');
          }
        } catch (error) {
          console.error('❌ Enhanced fallback copy method error:', error);
        }
      }
      
      if (copySuccess) {
        alert('✅ Client data copied to clipboard!');
        console.log('✅ Copy successful:', formattedData);
      } else {
        alert('❌ Failed to copy data to clipboard. Please try again or copy manually.');
        console.error('❌ All copy methods failed');
      }
      
    } catch (error) {
      console.error('Copy failed:', error);
      alert('❌ Failed to copy data to clipboard: ' + error.message);
    }
  };

  // Format labels data helper function
  const getFormattedLabelsData = () => {
    try {
      // Format date of birth for labels (YYYY-MM-DD format)
      let formattedDOB = '';
      if (formData.dob) {
        // Create date in local timezone to avoid timezone conversion issues
        const dateParts = formData.dob.split('-');
        const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]); // year, month (0-indexed), day
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const year = date.getFullYear();
        formattedDOB = `${year}-${month}-${day}`;
      }

      // Get current date and time
      const now = new Date();
      const currentMonth = (now.getMonth() + 1).toString().padStart(2, '0');
      const currentDay = now.getDate().toString().padStart(2, '0');
      const currentYear = now.getFullYear();
      const currentDate = `${currentYear}-${currentMonth}-${currentDay}`;
      const currentTime = now.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit', 
        hour12: true 
      });

      // Format labels data
      const labelsData = `HCN: ${formData.healthCard || ''} ${formData.healthCardVersion || ''}  Sex: ${formData.gender === 'Male' ? 'M' : formData.gender === 'Female' ? 'F' : formData.gender || ''}
${formData.lastName}, ${formData.firstName}
DOB: ${formattedDOB}
${formData.address ? `Address: ${formData.address}` : 'Address not available'}
${formData.city || ''}, ${formData.province?.toUpperCase().substring(0, 2) || ''} ${formData.postalCode || ''}
${formData.phone1 ? `Phone: ${formData.phone1}` : 'Phone number not available'}
${currentDate} ${currentTime}`;

      return labelsData;
    } catch (error) {
      console.error('Error formatting labels data:', error);
      return '';
    }
  };

  // Copy labels function - Copy to clipboard only
  const copyLabelsData = () => {
    try {
      const labelsData = getFormattedLabelsData();
      if (labelsData) {
        navigator.clipboard.writeText(labelsData);
        alert('✅ Label data copied to clipboard!');
      }
    } catch (error) {
      alert('❌ Error copying label data: ' + error.message);
      console.error('Labels copy failed:', error);
    }
  };


  
  // Handle scroll to top when success status changes (same pattern as client registration)
  useEffect(() => {
    if (submitStatus?.type === 'success') {
      window.scrollTo(0, 0);
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    }
  }, [submitStatus]);
  
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoUploadStatus, setPhotoUploadStatus] = useState(null);
  const [systemTestStatus, setSystemTestStatus] = useState(null);
  const [fieldValidation, setFieldValidation] = useState({});
  const [touchedFields, setTouchedFields] = useState({});
  const [activeTab, setActiveTab] = useState('patient');

  // Set default active tab based on user permissions
  useEffect(() => {
    const allowedTabs = getAllowedTabs();
    if (allowedTabs.length > 0) {
      // If current active tab is not allowed, switch to first allowed tab
      const isCurrentTabAllowed = allowedTabs.some(tab => tab.id === activeTab);
      if (!isCurrentTabAllowed) {
        setActiveTab(allowedTabs[0].id);
      }
    }
  }, [activeTab]);
  
  // Attachment states
  const [documentType, setDocumentType] = useState('');
  const [documentUrl, setDocumentUrl] = useState('');
  const [documentFile, setDocumentFile] = useState(null);
  const [documentPreview, setDocumentPreview] = useState(null);
  const [isLoadingDocument, setIsLoadingDocument] = useState(false);
  const [isFullScreenPreview, setIsFullScreenPreview] = useState(false);
  const [savedAttachments, setSavedAttachments] = useState([]);
  const [currentRegistrationId, setCurrentRegistrationId] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Test management states
  const [savedTests, setSavedTests] = useState([]);
  const [editingTestId, setEditingTestId] = useState(null);
  const [testFormData, setTestFormData] = useState({
    test_type: '',
    test_date: new Date().toISOString().split('T')[0],
    hiv_result: 'negative',
    hiv_type: '',
    hiv_tester: 'CM',
    hcv_result: 'negative',
    hcv_tester: 'CM',
    bloodwork_type: '',
    bloodwork_circles: '',
    bloodwork_result: 'Pending',
    bloodwork_date_submitted: '',
    bloodwork_tester: 'CM'
  });

  // Sharing functionality state
  const [shareUrl, setShareUrl] = useState('');
  const [isSharing, setIsSharing] = useState(false);
  const [shareStatus, setShareStatus] = useState('');

  // Notes tab independent state
  const [notesData, setNotesData] = useState({
    noteDate: new Date().toISOString().split('T')[0],
    noteText: ''
  });
  const [savedNotes, setSavedNotes] = useState([]);
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [speechStatus, setSpeechStatus] = useState('');
  const [recordingTimeout, setRecordingTimeout] = useState(null);
  const [notesFilter, setNotesFilter] = useState('all');
  const [notesSearch, setNotesSearch] = useState('');
  const [notesPage, setNotesPage] = useState(1);
  const [notesPerPage, setNotesPerPage] = useState(10);

  // Medications search and filter states
  const [medicationsFilter, setMedicationsFilter] = useState('all');
  const [medicationsSearch, setMedicationsSearch] = useState('');

  // Voice-to-text input states (like Notes tab)
  const [voiceInputText, setVoiceInputText] = useState('');
  const [isVoiceRecording, setIsVoiceRecording] = useState(false);
  const [voiceInputStatus, setVoiceInputStatus] = useState('');
  const [hasAutoFilledData, setHasAutoFilledData] = useState(false);
  
  // Voice assistant states
  const [voiceAssistantStatus, setVoiceAssistantStatus] = useState('');
  const [isAutoVoiceActive, setIsAutoVoiceActive] = useState(false);
  const [currentFieldIndex, setCurrentFieldIndex] = useState(0);
  const [currentRecordingField, setCurrentRecordingField] = useState(null);

  // Date-specific voice input state
  const [isDateRecording, setIsDateRecording] = useState(null); // 'regDate' or 'dob'
  const [dateRecognition, setDateRecognition] = useState(null);
  const [showVoiceDateModal, setShowVoiceDateModal] = useState(false);
  const [currentVoiceDateField, setCurrentVoiceDateField] = useState('');
  const [voiceDateInput, setVoiceDateInput] = useState('');

  // Toggle voice input (exactly like Notes tab)
  const toggleVoiceInput = () => {
    if (!recognition || !speechSupported) {
      setVoiceInputStatus('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    if (isVoiceRecording) {
      recognition.stop();
      setIsVoiceRecording(false);
      setVoiceInputStatus('');
      
      // Clear timeout
      if (recordingTimeout) {
        clearTimeout(recordingTimeout);
        setRecordingTimeout(null);
      }
    } else {
      // Request microphone permission first - EXACT same as working Notes
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(() => {
            try {
              recognition.start();
            } catch (error) {
              console.error('Error starting recognition:', error);
              setVoiceInputStatus('❌ Error starting speech recognition');
              setTimeout(() => setVoiceInputStatus(''), 3000);
            }
          })
          .catch((error) => {
            console.error('Microphone permission denied:', error);
            setVoiceInputStatus('❌ Microphone access denied. Please enable microphone permissions and try again.');
            setTimeout(() => setVoiceInputStatus(''), 5000);
          });
      } else {
        // Fallback for older browsers
        try {
          recognition.start();
        } catch (error) {
          console.error('Error starting recognition:', error);
          setVoiceInputStatus('❌ Error starting speech recognition');
          setTimeout(() => setVoiceInputStatus(''), 3000);
        }
      }
    }
  };

  // Auto-fill form fields directly from voice text or clear if already filled
  const autoFillFromVoiceText = () => {
    // If data has been auto-filled, clear it
    if (hasAutoFilledData) {
      setVoiceInputText('');
      setVoiceInputStatus('');
      setHasAutoFilledData(false);
      // Clear the form fields that were auto-filled
      setFormData(prev => ({
        ...prev,
        firstName: '',
        lastName: '',
        dob: '',
        gender: '',
        healthCard: '',
        healthCardVersion: '',
        disposition: '',
        age: ''
      }));
      return;
    }

    if (!voiceInputText.trim()) {
      setVoiceInputStatus('❌ No text to process. Please record some voice input first.');
      return;
    }

    const text = voiceInputText.toLowerCase();
    
    // Process all fields directly without phonetic spelling
    processAllFields(text);
  };

  // Process all fields from voice text
  const processAllFields = (text) => {
    const updates = {};
    
    // Extract names from voice text (handle accented characters)
    const namePattern = text.match(/^([a-zA-ZÀ-ÿ\u0100-\u017F]+)\s+([a-zA-ZÀ-ÿ\u0100-\u017F\s]+)/);
    if (namePattern) {
      const firstName = namePattern[1].charAt(0).toUpperCase() + namePattern[1].slice(1).toLowerCase();
      const lastName = namePattern[2].charAt(0).toUpperCase() + namePattern[2].slice(1).toLowerCase();
      updates.firstName = firstName;
      updates.lastName = lastName;
      console.log('Voice processing found names:', { firstName, lastName });
    } else {
      console.log('No names found in voice text:', text);
    }
    
    // Extract date of birth
    const dobPattern1 = text.match(/(?:date of birth|dob|born)\s+([a-zA-Z]+\s+\d{1,2},?\s+\d{4})/i);
    const dobPattern2 = text.match(/([a-zA-Z]+\s+\d{1,2},?\s+\d{4})/i);
    
    if (dobPattern1) {
      try {
        const dateStr = dobPattern1[1];
        const date = new Date(dateStr);
        if (!isNaN(date.getTime())) {
          updates.dob = date.toISOString().split('T')[0];
        }
      } catch (error) {
        console.error('Error parsing date:', error);
      }
    } else if (dobPattern2) {
      try {
        const dateStr = dobPattern2[1];
        const date = new Date(dateStr);
        if (!isNaN(date.getTime())) {
          updates.dob = date.toISOString().split('T')[0];
        }
      } catch (error) {
        console.error('Error parsing date:', error);
      }
    }
    
    // Extract gender
    if (text.includes(' mail ') || text.includes(' male ') || text.includes('man ') || text.includes(' mail') || text.includes(' male')) {
      updates.gender = 'Male';
    } else if (text.includes('female') || text.includes('woman') || text.includes('femail')) {
      updates.gender = 'Female';
    }
    
    // Extract health card
    const healthCardPattern = text.match(/health card number\s+(\d+)\s*([a-zA-Z]+)?/i);
    if (healthCardPattern) {
      updates.healthCard = healthCardPattern[1];
      if (healthCardPattern[2]) {
        updates.healthCardVersion = healthCardPattern[2].toUpperCase();
      }
    }
    
    // Extract disposition
    if (text.includes('pending')) {
      updates.disposition = 'PENDING';
    } else if (text.includes('active')) {
      updates.disposition = 'ACTIVE';
    } else if (text.includes('dispensing')) {
      updates.disposition = 'DISPENSING';
    } else if (text.includes('delivery')) {
      updates.disposition = 'DELIVERY';
    }
    
    // Update form data
    console.log('Voice processing updates:', updates);
    setFormData(prev => {
      const newFormData = { ...prev, ...updates };
      console.log('Updated form data:', newFormData);
      return newFormData;
    });
    
    // Calculate age if DOB was updated
    if (updates.dob) {
      const calculatedAge = calculateAge(updates.dob);
      if (calculatedAge !== null) {
        setFormData(prev => ({ ...prev, age: calculatedAge.toString() }));
      }
    }
    
    // Show success message
    setVoiceInputStatus(`✅ Registration information auto-populated successfully.`);
    setHasAutoFilledData(true);
  };

  // Define fields for auto voice assistant (starting with First Name and Last Name)
  const autoVoiceFields = [
    { name: 'firstName', label: 'First Name', required: true },
    { name: 'lastName', label: 'Last Name', required: true }
  ];

  // Start the auto voice assistant with upfront permission request
  const startAutoVoiceAssistant = () => {
    if (!recognition || !speechSupported) {
      setVoiceAssistantStatus('❌ Speech recognition not supported. Please use Chrome, Edge, or Safari.');
      return;
    }

    // Request microphone permission ONCE at the start
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
          setIsAutoVoiceActive(true);
          setCurrentFieldIndex(0);
          setVoiceAssistantStatus('🎤 Microphone permission granted! Starting automatic voice assistant...');
          
          setTimeout(() => {
            focusAndPromptCurrentField(0);
          }, 1000);
        })
        .catch((error) => {
          console.error('Microphone permission denied:', error);
          setVoiceAssistantStatus('❌ Microphone permission required. Please grant permission and try again.');
        });
    } else {
      // Fallback - try to start directly
      setIsAutoVoiceActive(true);
      setCurrentFieldIndex(0);
      setVoiceAssistantStatus('Starting voice assistant...');
      
      setTimeout(() => {
        focusAndPromptCurrentField(0);
      }, 1000);
    }
  };

  // Stop the auto voice assistant
  const stopAutoVoiceAssistant = () => {
    setIsAutoVoiceActive(false);
    setCurrentFieldIndex(0);
    setVoiceAssistantStatus('');
  };

  // Focus a specific field and show the record button for that field
  const focusAndPromptCurrentField = (fieldIndex) => {
    if (fieldIndex >= autoVoiceFields.length) {
      // All fields completed
      setVoiceAssistantStatus('🎉 All fields completed! Voice assistant finished.');
      setIsAutoVoiceActive(false);
      setTimeout(() => setVoiceAssistantStatus(''), 3000);
      return;
    }

    const field = autoVoiceFields[fieldIndex];
    const fieldElement = document.getElementById(field.name);
    
    if (fieldElement) {
      // Scroll to field and focus it
      fieldElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      setTimeout(() => {
        fieldElement.focus();
        
        // Highlight the field
        fieldElement.style.outline = '4px solid #3B82F6';
        fieldElement.style.backgroundColor = '#EFF6FF';
        fieldElement.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.3)';
        
        setVoiceAssistantStatus(`✅ ${field.label} field focused. Click the "Record ${field.label}" button below to start voice input.`);
      }, 500);
    }
  };

  // Record speech for the current field (user clicks the button)
  const recordCurrentField = () => {
    if (!recognition || !speechSupported) {
      setVoiceAssistantStatus('❌ Speech recognition not supported. Please use Chrome, Edge, or Safari.');
      return;
    }

    const field = autoVoiceFields[currentFieldIndex];
    setCurrentRecordingField(field.name);
    
    // Start recording when user clicks the button
    try {
      recognition.start();
      setVoiceAssistantStatus(`🎤 Recording ${field.label}... Speak now!`);
    } catch (error) {
      console.error('Recording failed:', error);
      setVoiceAssistantStatus(`❌ Could not start recording for ${field.label}. Please try again.`);
    }
  };

  // Start recording for current field (user-initiated)
  const startRecordingForCurrentField = () => {
    if (!recognition || !speechSupported) {
      setVoiceAssistantStatus('❌ Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    const field = autoVoiceFields[currentFieldIndex];
    setCurrentRecordingField(field.name);
    
    // Request microphone permission and start recording (user-initiated)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
          try {
            recognition.start();
            setVoiceAssistantStatus(`🎤 Listening for ${field.label}... Speak now!`);
          } catch (error) {
            console.error('Error starting recognition:', error);
            setVoiceAssistantStatus('❌ Error starting speech recognition. Please try again.');
          }
        })
        .catch((error) => {
          console.error('Microphone permission denied:', error);
          setVoiceAssistantStatus('❌ Microphone access denied. Please enable microphone permissions in your browser settings and try again.');
        });
    } else {
      // Fallback for older browsers
      try {
        recognition.start();
        setVoiceAssistantStatus(`🎤 Listening for ${field.label}... Speak now!`);
      } catch (error) {
        console.error('Error starting recognition:', error);
        setVoiceAssistantStatus('❌ Error starting speech recognition. Please try again.');
      }
    }
  };

  // Move to the next field
  const proceedToNextField = () => {
    if (!isAutoVoiceActive) return;
    
    const currentField = autoVoiceFields[currentFieldIndex];
    const fieldElement = document.getElementById(currentField.name);
    
    // Clear highlight from current field
    if (fieldElement) {
      fieldElement.style.outline = '';
      fieldElement.style.backgroundColor = '';
      fieldElement.style.boxShadow = '';
    }
    
    const nextIndex = currentFieldIndex + 1;
    setCurrentFieldIndex(nextIndex);
    
    if (nextIndex < autoVoiceFields.length) {
      setVoiceAssistantStatus('Moving to next field...');
      setTimeout(() => {
        focusAndPromptCurrentField(nextIndex);
      }, 1000);
    } else {
      // All fields completed
      setVoiceAssistantStatus('🎉 All fields completed! Voice assistant finished.');
      setIsAutoVoiceActive(false);
      setTimeout(() => setVoiceAssistantStatus(''), 3000);
    }
  };

  // Create individual microphone button for each field (exact same as Notes tab)
  const createFieldMicButton = (fieldName, placeholder = '') => {
    const isFieldRecording = isRecording && currentRecordingField === fieldName;
    
    const startFieldRecording = () => {
      if (!recognition || !speechSupported) {
        setVoiceAssistantStatus('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
        return;
      }
      
      if (isFieldRecording) {
        recognition.stop();
        setIsRecording(false);
        setCurrentRecordingField(null);
        setVoiceAssistantStatus('');
        
        // Clear timeout
        if (recordingTimeout) {
          clearTimeout(recordingTimeout);
          setRecordingTimeout(null);
        }
      } else {
        // Set current recording field and start recording
        setCurrentRecordingField(fieldName);
        
        // Request microphone permission first - EXACT same as working Notes
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          navigator.mediaDevices.getUserMedia({ audio: true })
            .then(() => {
              try {
                recognition.start();
              } catch (error) {
                console.error('Error starting recognition:', error);
                setVoiceAssistantStatus('❌ Error starting speech recognition');
                setTimeout(() => setVoiceAssistantStatus(''), 3000);
              }
            })
            .catch((error) => {
              console.error('Microphone permission denied:', error);
              setVoiceAssistantStatus('❌ Microphone access denied. Please enable microphone permissions and try again.');
              setTimeout(() => setVoiceInputStatus(''), 5000);
            });
        } else {
          // Fallback for older browsers
          try {
            recognition.start();
          } catch (error) {
            console.error('Error starting recognition:', error);
            setVoiceAssistantStatus('❌ Error starting speech recognition');
            setTimeout(() => setVoiceAssistantStatus(''), 3000);
          }
        }
      }
    };

    return (
      <button
        type="button"
        onClick={startFieldRecording}
        disabled={!speechSupported}
        className={`absolute top-2 right-2 p-2 rounded-md transition-colors ${
          !speechSupported 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : isFieldRecording
              ? 'bg-red-500 text-white animate-pulse shadow-lg' 
              : 'bg-gray-200 text-gray-600 hover:bg-gray-300 hover:shadow-md'
        }`}
        title={
          !speechSupported 
            ? 'Speech recognition not supported' 
            : isFieldRecording
              ? 'Click to stop recording' 
              : 'Click to start voice recording'
        }
      >
        {isFieldRecording ? (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a2 2 0 114 0v6a2 2 0 11-4 0V7z" clipRule="evenodd" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7 4a3 3 0 6 16 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 7 15 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
          </svg>
        )}
      </button>
    );
  };

  // Parse voice input and fill form fields
  const parseVoiceInput = (text) => {
    const lowerText = text.toLowerCase();
    const updates = {};
    
    // Extract first name (first word)
    const words = text.trim().split(' ');
    if (words.length > 0) {
      updates.firstName = words[0];
    }
    
    // Extract last name (second word)
    if (words.length > 1) {
      updates.lastName = words[1];
    }
    
    // Extract age
    const ageMatch = lowerText.match(/age (\d+)|(\d+) years old/);
    if (ageMatch) {
      updates.age = ageMatch[1] || ageMatch[2];
    }
    
    // Extract gender
    if (lowerText.includes('male') && !lowerText.includes('female')) {
      updates.gender = 'Male';
    } else if (lowerText.includes('female')) {
      updates.gender = 'Female';
    }
    
    // Extract phone number
    const phoneMatch = text.match(/(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})/);
    if (phoneMatch) {
      updates.phone1 = phoneMatch[1];
    }
    
    // Extract address (look for "lives at", "address", street numbers)
    const addressMatch = text.match(/(?:lives at|address|at) ([^,]+)/i);
    if (addressMatch) {
      updates.address = addressMatch[1].trim();
    }
    
    // Extract city (look for common city indicators)
    const cityMatch = text.match(/(?:in|city|toronto|ottawa|vancouver|montreal|calgary|edmonton|winnipeg|hamilton|quebec|halifax) ([^,]+)/i);
    if (cityMatch) {
      updates.city = cityMatch[1].trim();
    }
    
    // Extract health card (10 digits)
    const healthCardMatch = text.match(/(?:health card|ohip|card number) (\d{10})/i);
    if (healthCardMatch) {
      updates.healthCard = healthCardMatch[1];
    }
    
    return updates;
  };

  // Start field-by-field voice input
  const startFieldByFieldVoice = () => {
    setIsAutoVoiceActive(true);
    setCurrentFieldIndex(0);
    setCurrentRecordingField(autoVoiceFields[0].name);
    highlightCurrentField(autoVoiceFields[0]);
    setVoiceAssistantStatus(`Ready to fill ${autoVoiceFields[0].label}. Click the microphone and speak clearly.`);
  };

  // Stop field-by-field voice input
  const stopFieldByFieldVoice = () => {
    setIsAutoVoiceActive(false);
    setCurrentFieldIndex(0);
    setCurrentRecordingField(null);
    setVoiceAssistantStatus('');
    clearFieldHighlight();
    if (recognition && isRecording) recognition.stop();
  };

  // Highlight the current field being filled
  const highlightCurrentField = (field) => {
    // Clear previous highlights
    clearFieldHighlight();
    
    // Highlight current field
    const element = document.querySelector(`[name="${field.name}"]`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.style.outline = '3px solid #3B82F6';
      element.style.backgroundColor = '#EFF6FF';
    }
  };

  // Clear field highlights
  const clearFieldHighlight = () => {
    autoVoiceFields.forEach(field => {
      const element = document.querySelector(`[name="${field.name}"]`);
      if (element) {
        element.style.outline = '';
        element.style.backgroundColor = '';
      }
    });
  };

  // Move to the next field
  const moveToNextField = () => {
    const nextIndex = currentFieldIndex + 1;
    if (nextIndex >= autoVoiceFields.length) {
      // All fields completed
      setVoiceAssistantStatus('🎉 All fields completed! Voice input finished.');
      setIsAutoVoiceActive(false);
      setCurrentRecordingField(null);
      clearFieldHighlight();
      setTimeout(() => setVoiceAssistantStatus(''), 3000);
    } else {
      setCurrentFieldIndex(nextIndex);
      const nextField = autoVoiceFields[nextIndex];
      setCurrentRecordingField(nextField.name);
      highlightCurrentField(nextField);
      setVoiceAssistantStatus(`Ready to fill ${nextField.label}. Click the microphone and speak clearly.`);
    }
  };

  // Process voice input for current field
  const processFieldVoiceInput = (transcript) => {
    if (!currentRecordingField) return;

    const field = autoVoiceFields[currentFieldIndex];
    let processedValue = transcript.trim();

    // Process based on field type
    switch (field.type) {
      case 'date':
        // Try to parse common date formats
        const dateMatch = transcript.match(/(\w+)\s+(\d{1,2}),?\s+(\d{4})/i);
        if (dateMatch) {
          const [, month, day, year] = dateMatch;
          const monthNum = new Date(`${month} 1, 2000`).getMonth() + 1;
          processedValue = `${year}-${monthNum.toString().padStart(2, '0')}-${day.padStart(2, '0')}`;
        }
        break;
      case 'select':
        // Match against available options
        if (field.name === 'gender') {
          if (transcript.toLowerCase().includes('male') && !transcript.toLowerCase().includes('female')) {
            processedValue = 'Male';
          } else if (transcript.toLowerCase().includes('female')) {
            processedValue = 'Female';
          }
        }
        break;
      default:
        // Regular text processing for other fields
        if (field.name === 'postalCode') {
          // Apply postal code formatting
          processedValue = formatPostalCode(transcript);
        } else {
          // Clean up the text for other fields
          processedValue = transcript.charAt(0).toUpperCase() + transcript.slice(1).toLowerCase();
        }
        break;
    }

    // Update the form data
    setFormData(prev => ({
      ...prev,
      [field.name]: processedValue
    }));

    // Show confirmation and move to next field
    setVoiceAssistantStatus(`✅ Set ${field.label} to: "${processedValue}". Moving to next field...`);
    setTimeout(() => {
      moveToNextField();
    }, 1500);
  };

  // Simple voice input for individual field recording
  const startFieldVoiceRecording = () => {
    if (!recognition || !speechSupported) {
      setVoiceAssistantStatus('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
      setVoiceAssistantStatus(currentRecordingField ? `Ready to fill ${autoVoiceFields[currentFieldIndex]?.label}. Click the microphone and speak clearly.` : '');
      
      // Clear timeout
      if (recordingTimeout) {
        clearTimeout(recordingTimeout);
        setRecordingTimeout(null);
      }
    } else {
      // Request microphone permission first
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(() => {
            try {
              recognition.start();
            } catch (error) {
              console.error('Error starting recognition:', error);
              setVoiceAssistantStatus('❌ Error starting speech recognition');
              setTimeout(() => setVoiceAssistantStatus(''), 3000);
            }
          })
          .catch((error) => {
            console.error('Microphone permission denied:', error);
            setVoiceAssistantStatus('❌ Microphone access denied. Please enable microphone permissions and try again.');
            setTimeout(() => setVoiceInputStatus(''), 5000);
          });
      } else {
        // Fallback for older browsers
        try {
          recognition.start();
        } catch (error) {
          console.error('Error starting recognition:', error);
          setVoiceAssistantStatus('❌ Error starting speech recognition');
          setTimeout(() => setVoiceAssistantStatus(''), 3000);
        }
      }
    }
  };

  // Enable microphone access - EXACT same as Notes
  const enableMicrophone = () => {
    if (!recognition || !speechSupported) {
      setSpeechStatus('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    // Use EXACT same code as Notes button
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
          setSpeechStatus('✅ Microphone access granted! You can now use Voice Intake.');
          setTimeout(() => setSpeechStatus(''), 3000);
        })
        .catch((error) => {
          console.error('Microphone permission denied:', error);
          setSpeechStatus('❌ Microphone access denied. Please enable microphone permissions and try again.');
          setTimeout(() => setSpeechStatus(''), 5000);
        });
    } else {
      // Fallback for older browsers
      setSpeechStatus('❌ Microphone access is not supported in this browser.');
    }
  };

  // Voice Intake function - EXACT same as Notes toggleSpeechRecognition
  // Medication tab independent state
  const [medicationData, setMedicationData] = useState({
    medication: '',
    start_date: '',
    end_date: '',
    outcome: ''
  });
  const [savedMedications, setSavedMedications] = useState([]);
  const [editingMedicationId, setEditingMedicationId] = useState(null);
  const [isSavingMedication, setIsSavingMedication] = useState(false);

  // Interactions tab independent state  
  const [interactionData, setInteractionData] = useState({
    date: new Date().toISOString().split('T')[0], // Default to current date
    description: '',
    referral_id: '',
    amount: '',
    payment_type: '',
    issued: 'Select'
  });
  const [savedInteractions, setSavedInteractions] = useState([]);
  const [editingInteractionId, setEditingInteractionId] = useState(null);
  const [isSavingInteraction, setIsSavingInteraction] = useState(false);
  const [interactionsFilter, setInteractionsFilter] = useState('all');
  const [interactionsSearch, setInteractionsSearch] = useState('');
  const [interactionsPage, setInteractionsPage] = useState(1);
  const [interactionsPerPage, setInteractionsPerPage] = useState(10);

  // Dispensing tab independent state
  const [dispensingData, setDispensingData] = useState({
    medication: '',
    rx: '',
    quantity: '28',
    lot: '',
    product_type: 'Commercial',
    expiry_date: ''
  });
  const [savedDispensing, setSavedDispensing] = useState([]);
  const [editingDispensingId, setEditingDispensingId] = useState(null);
  const [isSavingDispensing, setIsSavingDispensing] = useState(false);

  // Activity tab independent state
  const [activityData, setActivityData] = useState({
    date: new Date().toISOString().split('T')[0], // Default to today
    time: '',
    description: ''
  });
  const [savedActivities, setSavedActivities] = useState([]);
  const [editingActivityId, setEditingActivityId] = useState(null);
  const [isSavingActivity, setIsSavingActivity] = useState(false);

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
    
    // Check if user is already authenticated from previous registration or dashboard
    const isAuthenticated = sessionStorage.getItem('admin_authenticated');
    if (isAuthenticated === 'true') {
      setPinVerified(true);
      // Clear the session flag after use
      sessionStorage.removeItem('admin_authenticated');
    }
  }, []);

  // Initialize speech recognition (DISABLED for Notes)
  useEffect(() => {
    // Set up speech recognition for individual field microphones
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recog = new SpeechRecognition();
      
      // Enhanced configuration for field recording
      recog.continuous = false;
      recog.interimResults = false;
      recog.lang = 'en-US';
      recog.maxAlternatives = 1;
      
      recog.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        
        if (currentRecordingField && transcript) {
          let processedValue = transcript.trim();
          
          // Special handling for postal code
          if (currentRecordingField === 'postalCode') {
            // Apply postal code formatting
            processedValue = formatPostalCode(transcript);
          } else {
            // For other fields, just clean up the text
            processedValue = transcript.charAt(0).toUpperCase() + transcript.slice(1).toLowerCase();
          }
          
          // Update the form data directly
          setFormData(prev => ({
            ...prev,
            [currentRecordingField]: processedValue
          }));
          
          setVoiceInputStatus(`✅ Recorded: "${processedValue}"`);
          setTimeout(() => setVoiceInputStatus(''), 3000);
        }
      };
      
      recog.onstart = () => {
        setIsRecording(true);
        const fieldLabel = currentRecordingField === 'postalCode' 
          ? 'postal code (you can use phonetic alphabet)'
          : currentRecordingField;
        setVoiceInputStatus(`🎤 Recording ${fieldLabel}... Speak clearly`);
      };
      
      recog.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        setCurrentRecordingField(null);
        
        // User-friendly error messages
        switch (event.error) {
          case 'no-speech':
            setVoiceInputStatus('⚠️ No speech detected. Try again.');
            break;
          case 'audio-capture':
            setVoiceInputStatus('❌ Microphone not accessible. Check permissions.');
            break;
          case 'not-allowed':
            setVoiceInputStatus('❌ Microphone access denied. Please enable microphone permissions.');
            break;
          default:
            setVoiceInputStatus(`❌ Error: ${event.error}`);
        }
        
        setTimeout(() => setVoiceInputStatus(''), 5000);
      };
      
      recog.onend = () => {
        setIsRecording(false);
        setCurrentRecordingField(null);
        if (recordingTimeout) {
          clearTimeout(recordingTimeout);
          setRecordingTimeout(null);
        }
      };
      
      setRecognition(recog);
      setSpeechSupported(true);
    } else {
      setSpeechSupported(false);
    }
  }, [currentRecordingField]);

  const testPhotoUploadSystem = async () => {
    setSystemTestStatus({ type: 'testing', message: 'Testing photo upload system...' });
    
    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Test the health endpoint first
      const healthResponse = await fetch(`${API}/api/`);
      
      if (healthResponse.ok) {
        setSystemTestStatus({
          type: 'success',
          message: '✅ System test passed! Backend server is responding correctly. Photo upload and email functionality should work properly. You can safely proceed with your registration.'
        });
      } else {
        setSystemTestStatus({
          type: 'error',
          message: '❌ System test failed. Backend server is not responding properly. Please contact support.'
        });
      }
    } catch (error) {
      setSystemTestStatus({
        type: 'error',
        message: '❌ System test failed due to network error. Please check your connection or contact support.'
      });
    }
  };

  // Parse spoken date into YYYY-MM-DD format
  const parseDateFromSpeech = (spokenText) => {
    const text = spokenText.toLowerCase().trim();
    console.log('🎤 Parsing spoken date:', text);
    
    // Common date patterns people might say
    const patterns = [
      // "January 15th 2024", "January 15 2024"
      /(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})/,
      // "15th of January 2024", "15 of January 2024"  
      /(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(\w+)\s+(\d{4})/,
      // "1/15/2024", "01/15/2024"
      /(\d{1,2})\/(\d{1,2})\/(\d{4})/,
      // "2024-01-15"
      /(\d{4})-(\d{1,2})-(\d{1,2})/,
      // "January 2024" (assume 1st)
      /(\w+)\s+(\d{4})/,
      // "today", "yesterday", "tomorrow"
      /(today|yesterday|tomorrow)/,
      // "15th" (assume current month/year)
      /(\d{1,2})(?:st|nd|rd|th)?$/
    ];
    
    const months = {
      'january': '01', 'jan': '01', 'february': '02', 'feb': '02',
      'march': '03', 'mar': '03', 'april': '04', 'apr': '04',
      'may': '05', 'june': '06', 'jun': '06', 'july': '07', 'jul': '07',
      'august': '08', 'aug': '08', 'september': '09', 'sep': '09',
      'october': '10', 'oct': '10', 'november': '11', 'nov': '11',
      'december': '12', 'dec': '12'
    };
    
    const today = new Date();
    
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        try {
          let year, month, day;
          
          // Pattern 1: "January 15th 2024"
          if (pattern === patterns[0]) {
            const monthName = match[1].toLowerCase();
            month = months[monthName];
            day = match[2].padStart(2, '0');
            year = match[3];
          }
          // Pattern 2: "15th of January 2024"
          else if (pattern === patterns[1]) {
            day = match[1].padStart(2, '0');
            const monthName = match[2].toLowerCase();
            month = months[monthName];
            year = match[3];
          }
          // Pattern 3: "1/15/2024" (MM/DD/YYYY)
          else if (pattern === patterns[2]) {
            month = match[1].padStart(2, '0');
            day = match[2].padStart(2, '0');
            year = match[3];
          }
          // Pattern 4: "2024-01-15" (already in correct format)
          else if (pattern === patterns[3]) {
            year = match[1];
            month = match[2].padStart(2, '0');
            day = match[3].padStart(2, '0');
          }
          // Pattern 5: "January 2024" (assume 1st)
          else if (pattern === patterns[4]) {
            const monthName = match[1].toLowerCase();
            month = months[monthName];
            day = '01';
            year = match[2];
          }
          // Pattern 6: "today", "yesterday", "tomorrow"
          else if (pattern === patterns[5]) {
            const relativeDate = new Date();
            if (match[1] === 'yesterday') {
              relativeDate.setDate(today.getDate() - 1);
            } else if (match[1] === 'tomorrow') {
              relativeDate.setDate(today.getDate() + 1);
            }
            year = relativeDate.getFullYear().toString();
            month = (relativeDate.getMonth() + 1).toString().padStart(2, '0');
            day = relativeDate.getDate().toString().padStart(2, '0');
          }
          // Pattern 7: "15th" (current month/year)
          else if (pattern === patterns[6]) {
            day = match[1].padStart(2, '0');
            month = (today.getMonth() + 1).toString().padStart(2, '0');
            year = today.getFullYear().toString();
          }
          
          if (year && month && day) {
            const parsedDate = `${year}-${month}-${day}`;
            console.log('✅ Parsed date:', parsedDate);
            
            // Validate the date
            const dateObj = new Date(parsedDate);
            if (!isNaN(dateObj.getTime()) && 
                dateObj.getFullYear() == year && 
                (dateObj.getMonth() + 1) == parseInt(month) && 
                dateObj.getDate() == parseInt(day)) {
              return parsedDate;
            }
          }
        } catch (error) {
          console.warn('Error parsing date:', error);
        }
      }
    }
    
    console.warn('❌ Could not parse date from:', text);
    return null;
  };

  // Start date voice recognition
  const startDateVoiceInput = (dateField) => {
    console.log('🎤 Starting voice input for:', dateField);
    console.log('🎤 Speech supported:', speechSupported);
    console.log('🎤 User agent:', navigator.userAgent);
    
    if (!speechSupported) {
      alert('❌ Speech recognition not supported in this browser. Try Chrome or Safari on desktop.');
      return;
    }
    
    // Check if we're on mobile Safari
    const isMobileSafari = /iPhone|iPad|iPod/.test(navigator.userAgent) && /Safari/.test(navigator.userAgent);
    if (isMobileSafari) {
      console.log('⚠️ Mobile Safari detected - speech recognition may be limited');
    }
    
    setIsDateRecording(dateField);
    
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
      console.log('🎤 Date voice recognition started for:', dateField);
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log('🎤 Date voice transcript:', transcript);
      console.log('🎤 Confidence:', event.results[0][0].confidence);
      
      const parsedDate = parseDateFromSpeech(transcript);
      
      if (parsedDate) {
        setFormData(prev => ({
          ...prev,
          [dateField]: parsedDate
        }));
        
        // Trigger age calculation if DOB was set
        if (dateField === 'dob') {
          const age = calculateAge(parsedDate);
          if (age) {
            setFormData(prev => ({
              ...prev,
              age: age.toString()
            }));
          }
        }
        
        alert(`✅ Date set to: ${new Date(parsedDate).toLocaleDateString()}`);
      } else {
        console.error('❌ Could not parse date from transcript:', transcript);
        alert(`❌ Could not understand date: "${transcript}". Try saying it like "January 15th 2024", "15th of January 2024", or "today"`);
      }
    };
    
    recognition.onerror = (event) => {
      console.error('❌ Date voice recognition error:', event.error);
      console.error('❌ Error details:', event);
      
      let errorMessage = 'Voice recognition error: ';
      switch(event.error) {
        case 'no-speech':
          errorMessage += 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage += 'Microphone not available.';
          break;
        case 'not-allowed':
          errorMessage += 'Microphone permission denied.';
          break;
        case 'network':
          errorMessage += 'Network error. Please check your connection.';
          break;
        default:
          errorMessage += event.error;
      }
      
      alert(`❌ ${errorMessage}`);
    };
    
    recognition.onend = () => {
      console.log('🎤 Date voice recognition ended');
      setIsDateRecording(null);
    };
    
    setDateRecognition(recognition);
    
    try {
      recognition.start();
      console.log('🎤 Recognition start() called successfully');
    } catch (error) {
      console.error('❌ Error calling recognition.start():', error);
      alert('❌ Failed to start speech recognition: ' + error.message);
      setIsDateRecording(null);
    }
  };

  // Stop date voice recognition
  const stopDateVoiceInput = () => {
    if (dateRecognition) {
      dateRecognition.stop();
      setDateRecognition(null);
    }
    setIsDateRecording(null);
  };

  // Date voice button component
  const DateVoiceButton = ({ dateField, label }) => {
    const isRecording = isDateRecording === dateField;
    
    return (
      <button
        type="button"
        onClick={isRecording ? stopDateVoiceInput : () => startDateVoiceInput(dateField)}
        disabled={!speechSupported}
        className={`ml-2 p-2 rounded-md transition-colors ${
          !speechSupported 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : isRecording
              ? 'bg-red-500 text-white animate-pulse shadow-lg' 
              : 'bg-blue-500 text-white hover:bg-blue-600 hover:shadow-md'
        }`}
        title={
          !speechSupported 
            ? 'Speech recognition not supported' 
            : isRecording
              ? `Recording ${label} - click to stop` 
              : `Voice input for ${label}`
        }
      >
        {isRecording ? (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a2 2 0 114 0v6a2 2 0 11-4 0V7z" clipRule="evenodd" />
          </svg>
        ) : (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
          </svg>
        )}
      </button>
    );
  };

  const handlePinSubmit = (e) => {
    e.preventDefault();
    if (pinInput === "0224") {
      setPinVerified(true);
      setPinError("");
    } else {
      setPinError("Invalid PIN. Access denied.");
      setPinInput("");
    }
  };

  const calculateAge = (birthDate) => {
    if (!birthDate) return '';
    
    const today = new Date();
    const birth = new Date(birthDate);
    
    // Check if birth date is in the future
    if (birth > today) return '';
    
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    // Adjust age if birthday hasn't occurred yet this year
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age.toString();
  };

  const updateClinicalSummary = async (formData) => {
    const baseTemplate = "Dx 10+ years ago and treated. ";
    
    let rnaSection = "";
    if (formData.rnaAvailable === "No") {
      rnaSection = "RNA - no labs available. ";
    } else if (formData.rnaAvailable === "Yes") {
      const date = formData.rnaSampleDate ? formData.rnaSampleDate : "[date]";
      const result = formData.rnaResult ? formData.rnaResult.toLowerCase() : "positive";
      rnaSection = `RNA - ${date}, ${result}. `;
    }
    
    const middleTemplate = "However, has had ongoing risk factors with sharing pipes and straws. Counselled regarding risk factors. Point of care test was completed for HCV and tested positive at approximately two minutes with a dark line. HIV testing came back negative. Collected a DBS specimen and advised that it will take approximately 7 to 10 days for results. ";
    
    let coverageSection = "";
    if (formData.coverageType && formData.coverageType !== "Select") {
      coverageSection = `${formData.coverageType}. `;
    }
    
    let referralSection = "";
    if (formData.referralPerson && formData.referralPerson.trim() !== "") {
      referralSection = `Referral: ${formData.referralPerson}. `;
    } else {
      referralSection = "Referral: none. ";
    }
    
    // Dynamic address/phone section based on client data
    const hasAddress = formData.address && formData.address.trim() !== "";
    const hasPhone = formData.phone1 && formData.phone1.trim() !== "";
    
    let endTemplate = "";
    if (hasAddress && hasPhone) {
      endTemplate = "Client does have a valid address and has also provided a phone number for results.";
    } else if (hasAddress && !hasPhone) {
      endTemplate = "Client does have a valid address but no phone number for results.";
    } else if (!hasAddress && hasPhone) {
      endTemplate = "Client does not have a valid address but has provided a phone number for results.";
    } else {
      endTemplate = "Client does not have a valid address or phone number for results.";
    }
    
    return baseTemplate + rnaSection + middleTemplate + coverageSection + referralSection + endTemplate;
  };

  const formatPhoneNumber = (value) => {
    // Remove all non-digits
    const phoneNumber = value.replace(/\D/g, '');
    
    // Limit to 10 digits
    const limitedPhoneNumber = phoneNumber.substring(0, 10);
    
    // Format based on length
    if (limitedPhoneNumber.length === 0) {
      return '';
    } else if (limitedPhoneNumber.length <= 3) {
      return `(${limitedPhoneNumber}`;
    } else if (limitedPhoneNumber.length <= 6) {
      return `(${limitedPhoneNumber.substring(0, 3)}) ${limitedPhoneNumber.substring(3)}`;
    } else {
      return `(${limitedPhoneNumber.substring(0, 3)}) ${limitedPhoneNumber.substring(3, 6)}-${limitedPhoneNumber.substring(6)}`;
    }
  };

  // Handle Google Places address selection
  const handlePlaceSelected = (addressData) => {
    console.log('Address selected:', addressData);
    
    // Map Google Places province codes to full province names
    const provinceMap = {
      'ON': 'Ontario',
      'QC': 'Quebec', 
      'BC': 'British Columbia',
      'AB': 'Alberta',
      'MB': 'Manitoba',
      'SK': 'Saskatchewan',
      'NS': 'Nova Scotia',
      'NB': 'New Brunswick',
      'NL': 'Newfoundland and Labrador',
      'PE': 'Prince Edward Island',
      'NT': 'Northwest Territories',
      'NU': 'Nunavut',
      'YT': 'Yukon'
    };
    
    // Get full province name from code or use as-is if already full name
    const fullProvince = provinceMap[addressData.province] || addressData.province || '';
    
    setFormData(prev => ({
      ...prev,
      address: addressData.address,
      city: addressData.city,
      province: fullProvince,
      postalCode: addressData.postal_code
    }));
    
    console.log('Updated form data with province:', fullProvince);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    let processedValue = type === 'checkbox' ? checked : value;
    
    // Format phone numbers
    if (name === 'phone1' || name === 'phone2') {
      processedValue = formatPhoneNumber(value);
    }
    
    // Don't format postal code during typing - only on blur
    
    // Health card should only contain numeric characters
    if (name === 'healthCard') {
      processedValue = value.replace(/\D/g, ''); // Remove all non-digit characters
    }
    
    let newFormData = {
      ...formData,
      [name]: processedValue
    };
    
    // Update clinical summary ONLY if user has explicitly selected Positive template AND changed RNA/coverage fields
    // This prevents auto-population when template is set to 'Select'
    if (selectedTemplate === 'Positive' && (name === 'rnaAvailable' || name === 'rnaSampleDate' || name === 'rnaResult' || name === 'coverageType' || name === 'referralPerson' || name === 'address' || name === 'phone1')) {
      console.log('🔄 Updating Positive template because user selected it and changed relevant fields');
      // Update form data first
      setFormData(newFormData);
      
      // Then update the clinical summary asynchronously
      updateClinicalSummary(newFormData).then(template => {
        setFormData(prev => ({
          ...prev,
          summaryTemplate: template
        }));
      }).catch(error => {
        console.error('Error updating clinical summary:', error);
      });
    } else {
      setFormData(newFormData);
    }
    
    // If DOB is changed, automatically calculate and update age
    if (name === 'dob' && value) {
      const calculatedAge = calculateAge(value);
      newFormData.age = calculatedAge;
    }
    
    // If disposition is changed to POCT NEG, set physician to None
    if (name === 'disposition' && value === 'POCT NEG') {
      newFormData.physician = 'None';
    }
    
    // Clear HIV fields when test type changes
    if (name === 'testType') {
      if (value === 'HIV') {
        // Set HIV date to current date when HIV is selected
        newFormData.hivDate = new Date().toISOString().split('T')[0];
        newFormData.hivResult = 'negative'; // Default to negative
        newFormData.hivType = '';
        newFormData.hivTester = 'CM'; // Set default tester
      } else if (value !== 'HIV') {
        // Clear all HIV fields when switching away from HIV
        newFormData.hivDate = new Date().toISOString().split('T')[0];
        newFormData.hivResult = 'negative';
        newFormData.hivType = '';
        newFormData.hivTester = 'CM'; // Reset to default
      }
    }
    
    // Clear HIV type when result is not positive
    if (name === 'hivResult' && value !== 'positive') {
      newFormData.hivType = '';
    }
    
    setFormData(newFormData);
  };

  // Open voice date input modal
  const openVoiceDateInput = (dateField) => {
    setCurrentVoiceDateField(dateField);
    setVoiceDateInput('');
    setShowVoiceDateModal(true);
  };

  // Handle voice date input submission
  const handleVoiceDateSubmit = () => {
    const parsedDate = parseDateFromSpeech(voiceDateInput);
    
    if (parsedDate) {
      setFormData(prev => {
        const newData = {
          ...prev,
          [currentVoiceDateField]: parsedDate
        };
        
        // Calculate age if DOB
        if (currentVoiceDateField === 'dob') {
          const age = calculateAge(parsedDate);
          if (age) {
            newData.age = age.toString();
          }
        }
        
        return newData;
      });
      
      setShowVoiceDateModal(false);
      setVoiceDateInput('');
    } else {
      alert(`❌ Could not understand date: "${voiceDateInput}". Try saying it like "January 15th 2024" or "today"`);
    }
  };

  // Handle voice date input with both manual and voice input support
  const handleDateInput = (e, dateField) => {
    const value = e.target.value;
    
    // If it's already in YYYY-MM-DD format (manual calendar selection), use as-is
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      setFormData(prev => {
        const newData = {
          ...prev,
          [dateField]: value
        };
        
        // Calculate age if DOB
        if (dateField === 'dob') {
          const age = calculateAge(value);
          if (age) {
            newData.age = age.toString();
          }
        }
        
        return newData;
      });
      return;
    }
    
    // Check if this looks like voice input (natural language)
    if (value && !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      const parsedDate = parseDateFromSpeech(value);
      
      if (parsedDate) {
        // Update the input field with the parsed date
        e.target.value = parsedDate;
        
        setFormData(prev => {
          const newData = {
            ...prev,
            [dateField]: parsedDate
          };
          
          // Calculate age if DOB
          if (dateField === 'dob') {
            const age = calculateAge(parsedDate);
            if (age) {
              newData.age = age.toString();
            }
          }
          
          return newData;
        });
        return;
      }
    }
    
    // Default: store the value and try to calculate age if possible
    setFormData(prev => {
      const newData = {
        ...prev,
        [dateField]: value
      };
      
      // Try to calculate age even with raw text (for DOB)
      if (dateField === 'dob' && value) {
        try {
          const testDate = new Date(value);
          if (!isNaN(testDate.getTime())) {
            const age = calculateAge(testDate.toISOString().split('T')[0]);
            if (age) {
              newData.age = age.toString();
            }
          }
        } catch (error) {
          console.log('Could not calculate age from raw text');
        }
      }
      
      return newData;
    });
  };

  const compressImage = (file, maxSizeKB = 800) => {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        // Calculate new dimensions (increased max resolution for better quality)
        let { width, height } = img;
        const maxWidth = 1200;  // Increased from 800
        const maxHeight = 1600; // Increased from 600
        
        // Only resize if image is larger than max dimensions
        if (width > maxWidth || height > maxHeight) {
          if (width > height) {
            if (width > maxWidth) {
              height = height * (maxWidth / width);
              width = maxWidth;
            }
          } else {
            if (height > maxHeight) {
              width = width * (maxHeight / height);
              height = maxHeight;
            }
          }
        }
        
        canvas.width = width;
        canvas.height = height;
        
        // Draw and compress with higher quality settings
        ctx.drawImage(img, 0, 0, width, height);
        
        // Start with higher quality and reduce if needed
        let quality = 0.92; // Increased from 0.8 for better quality
        let compressedDataUrl;
        
        do {
          compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
          quality -= 0.05; // Smaller steps for more gradual quality reduction
        } while (compressedDataUrl.length > maxSizeKB * 1024 * 1.37 && quality > 0.3); // Reduced minimum quality from 0.1 to 0.3
        
        resolve(compressedDataUrl);
      };
      
      img.src = URL.createObjectURL(file);
    });
  };

  const handlePhotoChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }
      
      // Validate file size (10MB max before compression)
      if (file.size > 10 * 1024 * 1024) {
        alert('Photo is too large. Please choose an image under 10MB.');
        return;
      }

      try {
        // Compress the image
        const compressedImage = await compressImage(file, 500); // Target 500KB
        
        // Final size check
        if (compressedImage.length > 800 * 1024) { // 800KB final limit
          alert('Photo could not be compressed enough. Please choose a smaller image.');
          return;
        }
        
        setPhotoPreview(compressedImage);
        setFormData(prev => ({
          ...prev,
          photo: compressedImage
        }));
        
        console.log(`Photo compressed: ${(file.size / 1024).toFixed(1)}KB → ${(compressedImage.length / 1024).toFixed(1)}KB`);
        
        // Show success message after compression
        setPhotoUploadStatus({ 
          type: 'success', 
          message: `Photo successfully optimized from ${(file.size / 1024).toFixed(1)}KB to ${(compressedImage.length / 1024).toFixed(1)}KB with high quality maintained. Your photo will be attached to the email when you submit the registration.` 
        });
        
      } catch (error) {
        console.error('Error compressing image:', error);
        alert('Error processing image. Please try again.');
      }
    }
  };

  const removePhoto = () => {
    setPhotoPreview(null);
    setPhotoUploadStatus(null);
    setFormData(prev => ({
      ...prev,
      photo: null
    }));
    // Clear both file inputs
    const cameraInput = document.getElementById('photo-camera');
    const uploadInput = document.getElementById('photo-upload');
    if (cameraInput) {
      cameraInput.value = '';
    }
    if (uploadInput) {
      uploadInput.value = '';
    }
  };

  // Document handling functions
  const handleDocumentFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/jpg', 
        'image/png'
      ];
      
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid file type (PDF, DOC, DOCX, JPG, PNG)');
        e.target.value = '';
        return;
      }
      
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File is too large. Please choose a file under 10MB.');
        e.target.value = '';
        return;
      }

      setDocumentFile(file);
      
      // Generate preview for images and PDFs
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setDocumentPreview({
            type: 'image',
            url: e.target.result, // This is already a proper base64 data URI
            filename: file.name
          });
        };
        reader.readAsDataURL(file);
      } else if (file.type === 'application/pdf') {
        // Create blob URL for proper PDF navigation support
        const blobUrl = URL.createObjectURL(file);
        
        // Also convert to base64 for storage
        const reader = new FileReader();
        reader.onload = (e) => {
          const base64Data = e.target.result;
          setDocumentPreview({
            type: 'pdf',
            url: blobUrl, // Use blob URL for viewing
            base64: base64Data, // Store base64 for saving
            filename: file.name,
            isLocal: true
          });
          // Reset page navigation for new PDF
          setCurrentPage(1);
          setTotalPages(50); // User can navigate to check actual pages
        };
        reader.readAsDataURL(file);
      } else {
        setDocumentPreview({
          type: 'document',
          url: null,
          filename: file.name
        });
      }
    }
  };

  const handleLoadUrl = async () => {
    if (!documentUrl.trim()) {
      alert('Please enter a valid URL');
      return;
    }

    setIsLoadingDocument(true);
    
    try {
      // Basic URL validation
      const url = new URL(documentUrl);
      
      // Check if it's a PDF or image URL based on extension
      const extension = url.pathname.split('.').pop().toLowerCase();
      
      if (['pdf'].includes(extension)) {
        setDocumentPreview({
          type: 'pdf',
          url: documentUrl,
          filename: url.pathname.split('/').pop(),
          isLocal: false
        });
      } else if (['jpg', 'jpeg', 'png'].includes(extension)) {
        // For image URLs, we need to handle them differently since they might not load properly
        // For now, just create a preview that links to the original URL
        setDocumentPreview({
          type: 'image',
          url: documentUrl,
          filename: url.pathname.split('/').pop()
        });
      } else {
        setDocumentPreview({
          type: 'link',
          url: documentUrl,
          filename: url.pathname.split('/').pop() || 'Document'
        });
      }
    } catch (error) {
      alert('Please enter a valid URL');
    } finally {
      setIsLoadingDocument(false);
    }
  };

  const clearDocument = () => {
    // Clean up object URL if it's a local file
    if (documentPreview && documentPreview.isLocal && documentPreview.url) {
      URL.revokeObjectURL(documentPreview.url);
    }
    
    setDocumentFile(null);
    setDocumentUrl('');
    setDocumentPreview(null);
    setDocumentType('');
    setIsFullScreenPreview(false); // Also close full-screen preview
    
    // Clear file input
    const fileInput = document.getElementById('documentFile');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  // Load tests for existing registration
  const loadTests = async (registrationId) => {
    if (!registrationId) {
      console.log('No registration ID provided to loadTests');
      return;
    }
    
    console.log('Loading tests for registration ID:', registrationId);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${registrationId}/tests`);
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded tests:', data.tests);
        setSavedTests(data.tests || []);
      } else {
        console.error('Failed to load tests, status:', response.status);
        const errorData = await response.text();
        console.error('Error response:', errorData);
      }
    } catch (error) {
      console.error('Error loading tests:', error);
    }
  };

  // Load tests when registration ID changes
  useEffect(() => {
    if (currentRegistrationId) {
      loadTests(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  const saveTest = async () => {
    if (!testFormData.test_type || testFormData.test_type === '') {
      alert('Please select a test type');
      return;
    }
    
    console.log('Saving test with data:', testFormData);
    console.log('Current registration ID:', currentRegistrationId);
    
    // Check if patient form has been submitted (registration ID exists)
    if (!currentRegistrationId) {
      alert('Please complete and save the Patient tab form first before adding tests.');
      setActiveTab('patient');
      return;
    }
    
    try {
      const endpoint = editingTestId 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/test/${editingTestId}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/test`;
      
      const method = editingTestId ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testFormData),
      });
      
      if (response.ok) {
        // Reload tests
        console.log('Reloading tests for registration:', currentRegistrationId);
        await loadTests(currentRegistrationId);
        
        // Reset form
        setTestFormData({
          test_type: '',
          test_date: new Date().toISOString().split('T')[0],
          hiv_result: 'negative',
          hiv_type: '',
          hiv_tester: 'CM',
          hcv_result: 'negative',
          hcv_tester: 'CM'
        });
        setEditingTestId(null);
        
        alert(editingTestId ? 'Test updated successfully!' : 'Test saved successfully!');
      } else {
        throw new Error('Failed to save test');
      }
      
    } catch (error) {
      console.error('Error saving test:', error);
      alert('Error saving test. Please try again.');
    }
  };

  const editTest = (test) => {
    setTestFormData({
      test_type: test.test_type,
      test_date: test.test_date,
      hiv_result: test.hiv_result || 'negative',
      hiv_type: test.hiv_type || '',
      hiv_tester: test.hiv_tester || 'CM',
      hcv_result: test.hcv_result || 'negative',
      hcv_tester: test.hcv_tester || 'CM'
    });
    setEditingTestId(test.id);
  };

  const deleteTest = async (testId) => {
    if (!window.confirm('Are you sure you want to delete this test? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/test/${testId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        // Reload tests
        await loadTests(currentRegistrationId);
        alert('Test deleted successfully!');
      } else {
        throw new Error('Failed to delete test');
      }
    } catch (error) {
      console.error('Error deleting test:', error);
      alert('Error deleting test. Please try again.');
    }
  };

  const cancelTestEdit = () => {
    setTestFormData({
      test_type: '',
      test_date: new Date().toISOString().split('T')[0],
      hiv_result: 'negative',
      hiv_type: '',
      hiv_tester: 'CM',
      hcv_result: 'negative',
      hcv_tester: 'CM'
    });
    setEditingTestId(null);
  };

  const handleTestChange = (e) => {
    const { name, value } = e.target;
    
    let newTestData = {
      ...testFormData,
      [name]: value
    };
    
    // Clear HIV type when result is not positive
    if (name === 'hiv_result' && value !== 'positive') {
      newTestData.hiv_type = '';
    }
    
    // Set defaults when switching to HIV
    if (name === 'test_type' && value === 'HIV') {
      newTestData.test_date = new Date().toISOString().split('T')[0];
      newTestData.hiv_result = 'negative';
      newTestData.hiv_type = '';
      newTestData.hiv_tester = 'CM';
    }
    
    // Set defaults when switching to HCV
    if (name === 'test_type' && value === 'HCV') {
      newTestData.test_date = new Date().toISOString().split('T')[0];
      newTestData.hcv_result = 'negative';
      newTestData.hcv_tester = 'CM';
    }
    
    setTestFormData(newTestData);
  };

  // Load attachments for existing registration
  const loadAttachments = async (registrationId) => {
    if (!registrationId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${registrationId}/attachments`);
      if (response.ok) {
        const data = await response.json();
        setSavedAttachments(data.attachments || []);
      }
    } catch (error) {
      console.error('Error loading attachments:', error);
    }
  };

  // Load attachments when registration ID changes
  useEffect(() => {
    if (currentRegistrationId) {
      loadAttachments(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  const saveAttachment = async () => {
    if (!documentType) {
      alert('Please select a document type');
      return;
    }
    
    if (!documentFile && !documentUrl.trim()) {
      alert('Please upload a file or provide a URL');
      return;
    }
    
    try {
      // If no current registration, create one first
      if (!currentRegistrationId) {
        // Create a basic registration first
        const basicRegistrationData = {
          firstName: formData.firstName || 'Temp',
          lastName: formData.lastName || 'User',
          patientConsent: 'verbal'
        };
        
        const registrationResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(basicRegistrationData),
        });
        
        if (registrationResponse.ok) {
          const regData = await registrationResponse.json();
          setCurrentRegistrationId(regData.registration_id);
        } else {
          throw new Error('Failed to create registration');
        }
      }
      
      // Create attachment object - use base64 for storage, blob for display
      const attachmentData = {
        type: documentType,
        filename: documentPreview.filename,
        url: documentPreview.base64 || documentPreview.url, // Use base64 for storage
        documentType: documentPreview.type,
        isLocal: documentPreview.isLocal || false,
        originalUrl: documentPreview.base64 || documentPreview.url // Backup of original URL
      };
      
      // Save attachment to backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/attachment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(attachmentData),
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Add to local state with the ID from backend
        const newAttachment = {
          ...attachmentData,
          id: result.attachment_id,
          savedAt: new Date().toLocaleString()
        };
        
        setSavedAttachments(prev => [...prev, newAttachment]);
        
        // Clear current preview
        clearDocument();
        
        alert(`${documentType} saved successfully!`);
      } else {
        throw new Error('Failed to save attachment');
      }
      
    } catch (error) {
      console.error('Error saving attachment:', error);
      alert('Error saving attachment. Please try again.');
    }
  };

  const openFullScreenPreview = () => {
    if (documentPreview && (documentPreview.type === 'pdf' || documentPreview.type === 'image')) {
      setIsFullScreenPreview(true);
    }
  };

  const closeFullScreenPreview = () => {
    setIsFullScreenPreview(false);
  };

  // Page navigation functions
  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const goToPage = (pageNum) => {
    if (pageNum >= 1 && pageNum <= totalPages) {
      setCurrentPage(pageNum);
    }
  };

  // Generate shareable link for attachment
  const generateShareLink = async () => {
    if (!documentPreview) return;
    
    setIsSharing(true);
    try {
      // Call backend API to create temporary shareable link
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/share-attachment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          attachment_data: {
            url: documentPreview.url,
            filename: documentPreview.filename,
            type: documentPreview.type
          },
          expires_in_minutes: 30
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate shareable link');
      }

      const data = await response.json();
      
      setShareUrl(data.share_url);
      setShareStatus('Temporary link generated! Expires in 30 minutes.');
      
      // Auto-clear status after 5 seconds
      setTimeout(() => setShareStatus(''), 5000);
    } catch (error) {
      console.error('Error generating share link:', error);
      setShareStatus('Error generating shareable link');
      setTimeout(() => setShareStatus(''), 3000);
    } finally {
      setIsSharing(false);
    }
  };

  // Copy share link to clipboard or trigger native sharing
  const copyShareLink = async () => {
    if (!shareUrl) {
      await generateShareLink();
      return;
    }
    
    // Try native sharing first (like Emergent platform)
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Shared Document: ${documentPreview?.filename || 'Document'}`,
          text: 'View this document (expires in 30 minutes)',
          url: shareUrl,
        });
        setShareStatus('Shared successfully!');
        setTimeout(() => setShareStatus(''), 3000);
        return;
      } catch (error) {
        if (error.name === 'AbortError') {
          return; // User cancelled, don't show error
        }
        console.log('Native sharing failed, falling back to clipboard');
      }
    }
    
    // Fallback to clipboard
    try {
      await navigator.clipboard.writeText(shareUrl);
      setShareStatus('Link copied to clipboard!');
      setTimeout(() => setShareStatus(''), 3000);
    } catch (error) {
      setShareStatus('Failed to copy link');
      setTimeout(() => setShareStatus(''), 3000);
    }
  };

  // Notes tab independent functions
  const handleNotesChange = (e) => {
    const { name, value } = e.target;
    setNotesData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Initialize enhanced speech recognition (DISABLED)
  React.useEffect(() => {
    // Speech recognition disabled to prevent microphone access issues
  }, []);
  
  // Process voice commands for better formatting
  const processVoiceCommands = (text) => {
    if (!text) return '';
    
    let processed = text;
    
    // Add punctuation based on voice commands
    processed = processed.replace(/\b(period|full stop)\b/gi, '.');
    processed = processed.replace(/\b(comma)\b/gi, ',');
    processed = processed.replace(/\b(question mark)\b/gi, '?');
    processed = processed.replace(/\b(exclamation mark|exclamation point)\b/gi, '!');
    processed = processed.replace(/\b(new line|new paragraph)\b/gi, '\n');
    processed = processed.replace(/\b(colon)\b/gi, ':');
    processed = processed.replace(/\b(semicolon)\b/gi, ';');
    
    // Capitalize first letter of sentences
    processed = processed.replace(/(^\s*\w|[.!?]\s*\w)/g, (match) => match.toUpperCase());
    
    return processed + ' ';
  };

  const toggleSpeechRecognition = () => {
    if (!recognition || !speechSupported) {
      alert('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
      setSpeechStatus('');
      
      // Clear timeout
      if (recordingTimeout) {
        clearTimeout(recordingTimeout);
        setRecordingTimeout(null);
      }
    } else {
      // Request microphone permission first
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(() => {
            try {
              recognition.start();
            } catch (error) {
              console.error('Error starting recognition:', error);
              setSpeechStatus('❌ Error starting speech recognition');
              setTimeout(() => setSpeechStatus(''), 3000);
            }
          })
          .catch((error) => {
            console.error('Microphone permission denied:', error);
            setSpeechStatus('❌ Microphone access denied. Please enable microphone permissions and try again.');
            setTimeout(() => setSpeechStatus(''), 5000);
          });
      } else {
        // Fallback for older browsers
        try {
          recognition.start();
        } catch (error) {
          console.error('Error starting recognition:', error);
          setSpeechStatus('❌ Error starting speech recognition');
          setTimeout(() => setSpeechStatus(''), 3000);
        }
      }
    }
  };

  const saveNote = async () => {
    if (!currentRegistrationId) {
      alert('Please complete the Patient tab first to save notes.');
      setActiveTab('patient');
      return;
    }

    if (!notesData.noteText.trim()) {
      alert('Please enter a note before saving');
      return;
    }

    setIsSavingNotes(true);
    try {
      const endpoint = editingNoteId 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/note/${editingNoteId}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/note`;
      
      const method = editingNoteId ? 'PUT' : 'POST';
      
      // Include the template type with the note data
      const noteDataWithTemplate = {
        ...notesData,
        templateType: selectedNotesTemplate !== 'Select' ? selectedNotesTemplate : 'General Note'
      };
      
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(noteDataWithTemplate),
      });

      if (response.ok) {
        await loadNotes(currentRegistrationId);
        clearNotesForm();
        alert(editingNoteId ? 'Note updated successfully!' : 'Note saved successfully!');
      } else {
        throw new Error('Failed to save note');
      }
    } catch (error) {
      console.error('Error saving note:', error);
      alert('Failed to save note. Please try again.');
    } finally {
      setIsSavingNotes(false);
    }
  };

  const loadNotes = async (regId) => {
    if (!regId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${regId}/notes`);
      if (response.ok) {
        const data = await response.json();
        setSavedNotes(data.notes || []);
      }
    } catch (error) {
      console.error('Error loading notes:', error);
    }
  };

  const editNote = (note) => {
    setNotesData({
      noteDate: note.noteDate || new Date().toISOString().split('T')[0],
      noteText: note.noteText || ''
    });
    setEditingNoteId(note.id);
    // Set template to 'Select' when editing individual notes to allow free editing
    setSelectedNotesTemplate('Select');
    setIsEditingNotesTemplate(false);
    // Scroll to top of notes form
    document.querySelector('#noteText')?.scrollIntoView({ behavior: 'smooth' });
  };

  const deleteNote = async (noteId) => {
    if (!window.confirm('Are you sure you want to delete this note?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/note/${noteId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await loadNotes(currentRegistrationId);
        alert('Note deleted successfully!');
      } else {
        throw new Error('Failed to delete note');
      }
    } catch (error) {
      console.error('Error deleting note:', error);
      alert('Failed to delete note. Please try again.');
    }
  };

  const clearNotesForm = () => {
    setNotesData({
      noteDate: new Date().toISOString().split('T')[0],
      noteText: ''
    });
    setEditingNoteId(null);
    // Reset template selection when clearing form
    setSelectedNotesTemplate('Select');
    setIsEditingNotesTemplate(false);
  };

  // Template Management Functions
  const addNewTemplate = async () => {
    if (!newTemplateName.trim()) {
      alert('Please enter a template name');
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/notes-templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newTemplateName.trim(),
          content: newTemplateContent.trim(),
          is_default: false
        }),
      });

      if (response.ok) {
        const newTemplate = await response.json();
        setAvailableNotesTemplates(prev => [...prev, newTemplate]);
        setNotesTemplates(prev => ({
          ...prev,
          [newTemplate.name]: newTemplate.content
        }));
        setNewTemplateName('');
        setNewTemplateContent('');
        alert('Template added successfully!');
      } else {
        throw new Error('Failed to add template');
      }
    } catch (error) {
      console.error('Error adding template:', error);
      alert('Failed to add template. Please try again.');
    }
  };

  const updateTemplate = async (templateId, name, content) => {
    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/notes-templates/${templateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          content: content.trim()
        }),
      });

      if (response.ok) {
        const updatedTemplate = await response.json();
        setAvailableNotesTemplates(prev => 
          prev.map(template => 
            template.id === templateId ? updatedTemplate : template
          )
        );
        setNotesTemplates(prev => ({
          ...prev,
          [updatedTemplate.name]: updatedTemplate.content
        }));
        setEditingTemplateId(null);
        alert('Template updated successfully!');
      } else {
        throw new Error('Failed to update template');
      }
    } catch (error) {
      console.error('Error updating template:', error);
      alert('Failed to update template. Please try again.');
    }
  };

  const deleteTemplate = async (templateId, templateName) => {
    if (!window.confirm(`Are you sure you want to delete the "${templateName}" template?`)) {
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/notes-templates/${templateId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setAvailableNotesTemplates(prev => prev.filter(template => template.id !== templateId));
        setNotesTemplates(prev => {
          const newTemplates = { ...prev };
          delete newTemplates[templateName];
          return newTemplates;
        });
        
        // Reset selection if deleted template was selected
        if (selectedNotesTemplate === templateName) {
          setSelectedNotesTemplate('Select');
        }
        
        alert('Template deleted successfully!');
      } else {
        throw new Error('Failed to delete template');
      }
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Failed to delete template. Please try again.');
    }
  };

  const closeTemplateManager = () => {
    setShowTemplateManager(false);
    setNewTemplateName('');
    setNewTemplateContent('');
    setEditingTemplateId(null);
  };

  // Clinical Summary Template Management Functions
  const addNewClinicalTemplate = async () => {
    if (!newClinicalTemplateName.trim()) {
      alert('Please enter a template name');
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/clinical-templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newClinicalTemplateName.trim(),
          content: newClinicalTemplateContent.trim(),
          is_default: false
        }),
      });

      if (response.ok) {
        const newTemplate = await response.json();
        setAvailableClinicalTemplates(prev => [...prev, newTemplate]);
        setTemplates(prev => ({
          ...prev,
          [newTemplate.name]: newTemplate.content
        }));
        setNewClinicalTemplateName('');
        setNewClinicalTemplateContent('');
        alert('Clinical Summary template added successfully!');
      } else {
        throw new Error('Failed to add template');
      }
    } catch (error) {
      console.error('Error adding clinical template:', error);
      alert('Failed to add clinical template. Please try again.');
    }
  };

  const updateClinicalTemplate = async (templateId, name, content) => {
    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/clinical-templates/${templateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          content: content.trim()
        }),
      });

      if (response.ok) {
        const updatedTemplate = await response.json();
        setAvailableClinicalTemplates(prev => 
          prev.map(template => 
            template.id === templateId ? updatedTemplate : template
          )
        );
        setTemplates(prev => ({
          ...prev,
          [updatedTemplate.name]: updatedTemplate.content
        }));
        setEditingClinicalTemplateId(null);
        alert('Clinical Summary template updated successfully!');
      } else {
        throw new Error('Failed to update template');
      }
    } catch (error) {
      console.error('Error updating clinical template:', error);
      alert('Failed to update clinical template. Please try again.');
    }
  };

  const deleteClinicalTemplate = async (templateId, templateName) => {
    if (!window.confirm(`Are you sure you want to delete the "${templateName}" template?`)) {
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API}/api/clinical-templates/${templateId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setAvailableClinicalTemplates(prev => prev.filter(template => template.id !== templateId));
        setTemplates(prev => {
          const newTemplates = { ...prev };
          delete newTemplates[templateName];
          return newTemplates;
        });
        
        // Reset selection if deleted template was selected
        if (selectedTemplate === templateName) {
          setSelectedTemplate('Select');
        }
        
        alert('Clinical Summary template deleted successfully!');
      } else {
        throw new Error('Failed to delete template');
      }
    } catch (error) {
      console.error('Error deleting clinical template:', error);
      alert('Failed to delete clinical template. Please try again.');
    }
  };

  const closeClinicalTemplateManager = () => {
    setShowClinicalTemplateManager(false);
    setNewClinicalTemplateName('');
    setNewClinicalTemplateContent('');
    setEditingClinicalTemplateId(null);
  };

  // Activity functions
  const handleActivityChange = (e) => {
    const { name, value } = e.target;
    setActivityData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const saveActivity = async () => {
    if (!currentRegistrationId) {
      alert('Please complete the Client tab first to save activities.');
      setActiveTab('patient');
      return;
    }

    if (!activityData.description.trim()) {
      alert('Please enter an activity description before saving');
      return;
    }

    setIsSavingActivity(true);
    try {
      const endpoint = editingActivityId 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/activity/${editingActivityId}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/activity`;
      
      const method = editingActivityId ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(activityData),
      });

      if (response.ok) {
        await loadActivities(currentRegistrationId);
        clearActivityForm();
        alert(editingActivityId ? 'Activity updated successfully!' : 'Activity saved successfully!');
      } else {
        throw new Error('Failed to save activity');
      }
    } catch (error) {
      console.error('Error saving activity:', error);
      alert('Error saving activity. Please try again.');
    }
    setIsSavingActivity(false);
  };

  const loadActivities = async (regId) => {
    if (!regId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${regId}/activities`);
      if (response.ok) {
        const data = await response.json();
        setSavedActivities(data.activities || []);
      }
    } catch (error) {
      console.error('Error loading activities:', error);
    }
  };

  const editActivity = (activity) => {
    setActivityData({
      date: activity.date || new Date().toISOString().split('T')[0],
      time: activity.time || '',
      description: activity.description || ''
    });
    setEditingActivityId(activity.id);
    // Scroll to top of activity form
    document.querySelector('#activityDescription')?.scrollIntoView({ behavior: 'smooth' });
  };

  const deleteActivity = async (activityId) => {
    if (!window.confirm('Are you sure you want to delete this activity?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/activity/${activityId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await loadActivities(currentRegistrationId);
        alert('Activity deleted successfully!');
      } else {
        throw new Error('Failed to delete activity');
      }
    } catch (error) {
      console.error('Error deleting activity:', error);
      alert('Error deleting activity. Please try again.');
    }
  };

  const clearActivityForm = () => {
    setActivityData({
      date: new Date().toISOString().split('T')[0],
      time: '',
      description: ''
    });
    setEditingActivityId(null);
  };

  // Enhanced filter and search for notes
  const getFilteredNotes = () => {
    let filtered = [...savedNotes];
    
    // Apply date filter
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    switch(notesFilter) {
      case 'today':
        filtered = filtered.filter(note => note.noteDate === todayStr);
        break;
      case 'week':
        filtered = filtered.filter(note => note.noteDate >= weekAgo);
        break;
      case 'month':
        filtered = filtered.filter(note => note.noteDate >= monthAgo);
        break;
      case 'recent':
        filtered = filtered.slice(0, 20);
        break;
      default:
        break;
    }
    
    // Apply search filter
    if (notesSearch.trim()) {
      const searchLower = notesSearch.toLowerCase();
      filtered = filtered.filter(note =>
        note.noteText.toLowerCase().includes(searchLower) ||
        note.noteDate.includes(searchLower) ||
        (note.templateType && note.templateType.toLowerCase().includes(searchLower))
      );
    }
    
    return filtered;
  };

  // Enhanced filter and search for medications
  const getFilteredMedications = () => {
    let filtered = [...savedMedications];
    
    // Apply date filter
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    switch(medicationsFilter) {
      case 'today':
        filtered = filtered.filter(med => med.start_date === todayStr);
        break;
      case 'week':
        filtered = filtered.filter(med => med.start_date >= weekAgo);
        break;
      case 'month':
        filtered = filtered.filter(med => med.start_date >= monthAgo);
        break;
      default:
        break;
    }
    
    // Apply search filter
    if (medicationsSearch.trim()) {
      const searchLower = medicationsSearch.toLowerCase();
      filtered = filtered.filter(med =>
        med.medication.toLowerCase().includes(searchLower) ||
        med.outcome.toLowerCase().includes(searchLower) ||
        (med.start_date && med.start_date.includes(searchLower)) ||
        (med.end_date && med.end_date.includes(searchLower))
      );
    }
    
    return filtered;
  };
  
  // Reset pagination when filter/search changes
  React.useEffect(() => {
    setNotesPage(1);
  }, [notesFilter, notesSearch]);
  
  // Auto-scroll to top when notes page changes
  React.useEffect(() => {
    if (notesPage > 1) {
      document.querySelector('#notes-section')?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [notesPage]);

  // Medication management functions
  const handleMedicationChange = (e) => {
    const { name, value } = e.target;
    setMedicationData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const loadMedications = async (regId) => {
    if (!regId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${regId}/medications`);
      if (response.ok) {
        const data = await response.json();
        setSavedMedications(data.medications || []);
      }
    } catch (error) {
      console.error('Error loading medications:', error);
    }
  };

  const saveMedication = async () => {
    if (!currentRegistrationId) {
      alert('Please complete the Patient tab first to save medications.');
      setActiveTab('patient');
      return;
    }

    if (!medicationData.medication || medicationData.medication === '') {
      alert('Please select a medication');
      return;
    }

    if (!medicationData.outcome || medicationData.outcome === '') {
      alert('Please select an outcome');
      return;
    }

    setIsSavingMedication(true);
    try {
      const endpoint = editingMedicationId 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/medication/${editingMedicationId}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/medication`;
      
      const method = editingMedicationId ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(medicationData),
      });

      if (response.ok) {
        await loadMedications(currentRegistrationId);
        clearMedicationForm();
        alert(editingMedicationId ? 'Medication updated successfully!' : 'Medication saved successfully!');
      } else {
        throw new Error('Failed to save medication');
      }
    } catch (error) {
      console.error('Error saving medication:', error);
      alert('Failed to save medication. Please try again.');
    } finally {
      setIsSavingMedication(false);
    }
  };

  const editMedication = (medication) => {
    setMedicationData({
      medication: medication.medication || '',
      start_date: medication.start_date || '',
      end_date: medication.end_date || '',
      outcome: medication.outcome || ''
    });
    setEditingMedicationId(medication.id);
    // Scroll to top of medication form
    document.querySelector('#medicationForm')?.scrollIntoView({ behavior: 'smooth' });
  };

  const deleteMedication = async (medicationId) => {
    if (!window.confirm('Are you sure you want to delete this medication?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/medication/${medicationId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await loadMedications(currentRegistrationId);
        alert('Medication deleted successfully!');
      } else {
        throw new Error('Failed to delete medication');
      }
    } catch (error) {
      console.error('Error deleting medication:', error);
      alert('Failed to delete medication. Please try again.');
    }
  };

  const clearMedicationForm = () => {
    setMedicationData({
      medication: '',
      start_date: '',
      end_date: '',
      outcome: ''
    });
    setEditingMedicationId(null);
  };

  // Load medications when registration ID changes
  React.useEffect(() => {
    if (currentRegistrationId) {
      loadMedications(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  // Interaction management functions
  const handleInteractionChange = (e) => {
    const { name, value } = e.target;
    setInteractionData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const loadInteractions = async (regId) => {
    if (!regId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${regId}/interactions`);
      if (response.ok) {
        const data = await response.json();
        setSavedInteractions(data.interactions || []);
      }
    } catch (error) {
      console.error('Error loading interactions:', error);
    }
  };

  const saveInteraction = async () => {
    if (!currentRegistrationId) {
      alert('Please complete the Patient tab first to save interactions.');
      setActiveTab('patient');
      return;
    }

    if (!interactionData.description || interactionData.description === '') {
      alert('Please select a description');
      return;
    }

    setIsSavingInteraction(true);
    try {
      const endpoint = editingInteractionId 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/interaction/${editingInteractionId}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/interaction`;
      
      const method = editingInteractionId ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(interactionData),
      });

      if (response.ok) {
        await loadInteractions(currentRegistrationId);
        clearInteractionForm();
        alert(editingInteractionId ? 'Interaction updated successfully!' : 'Interaction saved successfully!');
      } else {
        throw new Error('Failed to save interaction');
      }
    } catch (error) {
      console.error('Error saving interaction:', error);
      alert('Failed to save interaction. Please try again.');
    } finally {
      setIsSavingInteraction(false);
    }
  };

  const editInteraction = (interaction) => {
    setInteractionData({
      date: interaction.date || new Date().toISOString().split('T')[0],
      description: interaction.description || '',
      referral_id: interaction.referral_id || '',
      amount: interaction.amount || '',
      payment_type: interaction.payment_type || '',
      issued: interaction.issued || 'Select'
    });
    setEditingInteractionId(interaction.id);
    // Scroll to top of interaction form
    document.querySelector('#interactionForm')?.scrollIntoView({ behavior: 'smooth' });
  };

  const deleteInteraction = async (interactionId) => {
    if (!window.confirm('Are you sure you want to delete this interaction?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/interaction/${interactionId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await loadInteractions(currentRegistrationId);
        alert('Interaction deleted successfully!');
      } else {
        throw new Error('Failed to delete interaction');
      }
    } catch (error) {
      console.error('Error deleting interaction:', error);
      alert('Failed to delete interaction. Please try again.');
    }
  };

  const clearInteractionForm = () => {
    setInteractionData({
      date: new Date().toISOString().split('T')[0], // Default to current date
      description: '',
      referral_id: '',
      amount: '',
      payment_type: '',
      location: '',
      issued: 'Select'
    });
    setEditingInteractionId(null);
  };

  // Enhanced filter and search for interactions
  const getFilteredInteractions = () => {
    let filtered = [...savedInteractions];
    
    // Apply date filter
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    switch(interactionsFilter) {
      case 'today':
        filtered = filtered.filter(interaction => interaction.date === todayStr);
        break;
      case 'week':
        filtered = filtered.filter(interaction => interaction.date >= weekAgo);
        break;
      case 'month':
        filtered = filtered.filter(interaction => interaction.date >= monthAgo);
        break;
      case 'recent':
        // Show only last 20 interactions for performance
        filtered = filtered.slice(0, 20);
        break;
      default:
        break;
    }
    
    // Apply search filter with enhanced search
    if (interactionsSearch.trim()) {
      const searchTerm = interactionsSearch.toLowerCase();
      filtered = filtered.filter(interaction => 
        interaction.description.toLowerCase().includes(searchTerm) ||
        (interaction.date && interaction.date.includes(searchTerm)) ||
        (interaction.referral_id && interaction.referral_id.toLowerCase().includes(searchTerm)) ||
        (interaction.amount && interaction.amount.toLowerCase().includes(searchTerm)) ||
        (interaction.payment_type && interaction.payment_type.toLowerCase().includes(searchTerm)) ||
        (interaction.issued && interaction.issued.toLowerCase().includes(searchTerm))
      );
    }
    
    // Sort by date and created_at (newest first) - ensure proper chronological order
    filtered.sort((a, b) => {
      // Use the interaction date first, fall back to created_at
      const dateA = new Date(a.date || a.created_at || '1970-01-01');
      const dateB = new Date(b.date || b.created_at || '1970-01-01');
      
      // Sort newest first (descending order)
      return dateB.getTime() - dateA.getTime();
    });
    
    return filtered;
  };

  // Reset pagination when filter/search changes
  React.useEffect(() => {
    setInteractionsPage(1);
  }, [interactionsFilter, interactionsSearch]);

  // Load interactions when registration ID changes
  React.useEffect(() => {
    if (currentRegistrationId) {
      loadInteractions(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  // Dispensing management functions
  const handleDispensingChange = (e) => {
    const { name, value } = e.target;
    setDispensingData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const loadDispensing = async (regId) => {
    if (!regId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${regId}/dispensing`);
      if (response.ok) {
        const data = await response.json();
        setSavedDispensing(data.dispensing || []);
      }
    } catch (error) {
      console.error('Error loading dispensing records:', error);
    }
  };

  const saveDispensing = async () => {
    if (!currentRegistrationId) {
      alert('Please complete the Client tab first to save dispensing records.');
      setActiveTab('patient');
      return;
    }

    if (!dispensingData.medication || dispensingData.medication === '') {
      alert('Please select a medication');
      return;
    }

    setIsSavingDispensing(true);
    try {
      const endpoint = editingDispensingId 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/dispensing/${editingDispensingId}`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/dispensing`;
      
      const method = editingDispensingId ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dispensingData),
      });

      if (response.ok) {
        await loadDispensing(currentRegistrationId);
        clearDispensingForm();
        alert(editingDispensingId ? 'Dispensing record updated successfully!' : 'Dispensing record saved successfully!');
      } else {
        throw new Error('Failed to save dispensing record');
      }
    } catch (error) {
      console.error('Error saving dispensing record:', error);
      alert('Failed to save dispensing record. Please try again.');
    } finally {
      setIsSavingDispensing(false);
    }
  };

  const editDispensing = (dispensing) => {
    setDispensingData({
      medication: dispensing.medication || '',
      rx: dispensing.rx || '',
      quantity: dispensing.quantity || '28',
      lot: dispensing.lot || '',
      product_type: dispensing.product_type || 'Commercial',
      expiry_date: dispensing.expiry_date || ''
    });
    setEditingDispensingId(dispensing.id);
    // Scroll to top of dispensing form
    document.querySelector('#dispensingForm')?.scrollIntoView({ behavior: 'smooth' });
  };

  const deleteDispensing = async (dispensingId) => {
    if (!window.confirm('Are you sure you want to delete this dispensing record?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/dispensing/${dispensingId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await loadDispensing(currentRegistrationId);
        alert('Dispensing record deleted successfully!');
      } else {
        throw new Error('Failed to delete dispensing record');
      }
    } catch (error) {
      console.error('Error deleting dispensing record:', error);
      alert('Failed to delete dispensing record. Please try again.');
    }
  };

  const clearDispensingForm = () => {
    setDispensingData({
      medication: '',
      rx: '',
      quantity: '28',
      lot: '',
      product_type: 'Commercial',
      expiry_date: ''
    });
    setEditingDispensingId(null);
  };

  // Load dispensing when registration ID changes
  React.useEffect(() => {
    if (currentRegistrationId) {
      loadDispensing(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  // Load activities when registration ID changes
  React.useEffect(() => {
    if (currentRegistrationId) {
      loadActivities(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    // Client-side validation for required fields
    if (!formData.firstName.trim()) {
      setSubmitStatus({
        type: 'error',
        message: 'First Name is required.'
      });
      setIsSubmitting(false);
      return;
    }

    if (!formData.lastName.trim()) {
      setSubmitStatus({
        type: 'error',
        message: 'Last Name is required.'
      });
      setIsSubmitting(false);
      return;
    }

    if (!formData.patientConsent) {
      setSubmitStatus({
        type: 'error',
        message: 'Patient Consent is required.'
      });
      setIsSubmitting(false);
      return;
    }

    try {
      const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Check if photo is too large before sending
      if (formData.photo && formData.photo.length > 1200 * 1024) { // Increased from 1MB to 1.2MB
        setSubmitStatus({
          type: 'error',
          message: 'Photo is too large for submission. Please try uploading a different photo.'
        });
        setIsSubmitting(false);
        return;
      }
      
      console.log('Form data being sent:', formData);
      
      // Clean the form data - remove empty strings for optional fields and convert to null
      const cleanedFormData = { ...formData };
      
      // Add selectedTemplate to form data for database storage
      cleanedFormData.selectedTemplate = selectedTemplate;
      
      // Convert empty strings to null for date fields
      if (cleanedFormData.dob === '') {
        cleanedFormData.dob = null;
      }
      if (cleanedFormData.regDate === '') {
        cleanedFormData.regDate = null;
      }
      
      // Convert empty strings to null for optional fields
      Object.keys(cleanedFormData).forEach(key => {
        if (cleanedFormData[key] === '') {
          cleanedFormData[key] = null;
        }
      });
      
      console.log('Cleaned form data being sent:', cleanedFormData);
      
      const response = await fetch(`${API}/api/admin-register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cleanedFormData),
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (response.ok) {
        const result = await response.json();
        console.log('Registration response:', result);
        console.log('Registration ID from response:', result.registration_id);
        
        setCurrentRegistrationId(result.registration_id); // Store the registration ID for attachments and tests
        
        // Verify registration ID was set
        if (result.registration_id) {
          console.log('Registration ID set successfully:', result.registration_id);
          await loadTests(result.registration_id);
          await loadAttachments(result.registration_id);
          await loadNotes(result.registration_id);
          await loadMedications(result.registration_id);
          await loadInteractions(result.registration_id);
          await loadDispensing(result.registration_id);
          await loadActivities(result.registration_id);
        } else {
          console.error('No registration_id in response:', result);
        }
        
        setSubmitStatus({
          type: 'success',
          message: 'Registration saved for review! You can now access the dashboard to review and finalize registrations.',
          id: result.registration_id
        });
        
        // Trigger dashboard refresh
        localStorage.setItem('new_registration_submitted', Date.now().toString());
        
        // Reset form
        setFormData({
          firstName: "",
          lastName: "",
          dob: "",
          patientConsent: "verbal", // Default to verbal
          gender: "",
          province: "Ontario", // Default to Ontario
          disposition: "",
          aka: "",
          age: "",
          regDate: new Date().toISOString().split('T')[0], // Default to current date
          healthCard: "",
          healthCardVersion: "",
          referralSite: "",
          address: "",
          unitNumber: "",
          city: "",
          postalCode: "",
          phone1: "",
          phone2: "",
          leaveMessage: false,
          voicemail: false,
          text: false,
          preferredTime: "",
          email: "",
          language: "English", // Default to English
          specialAttention: "",
          photo: null,
          summaryTemplate: "", // Keep empty until user selects template
          physician: "Dr. David Fletcher",
          rnaAvailable: "No",
          rnaSampleDate: "",
          rnaResult: "Positive",
          coverageType: "Select",
          referralPerson: "",
          testType: "Tests",
          hivDate: new Date().toISOString().split('T')[0],
          hivResult: "negative",
          hivType: "",
          hivTester: "CM"
        });
        setPhotoPreview(null);
        setPhotoUploadStatus(null);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        // Handle specific HTTP status codes
        let errorMessage = 'Registration failed. Please try again.';
        
        console.log('Error response status:', response.status);
        
        if (response.status === 422) {
          try {
            const errorData = await response.json();
            console.log('422 Error details:', errorData);
            console.log('Error detail array:', errorData.detail);
            if (errorData.detail && Array.isArray(errorData.detail)) {
              // Pydantic validation errors
              const missingFields = errorData.detail
                .filter(err => err.type === 'missing')
                .map(err => err.loc[err.loc.length - 1]);
              
              if (missingFields.length > 0) {
                errorMessage = `Please fill in the required fields: ${missingFields.join(', ')}`;
              } else {
                errorMessage = 'Please check your form data and try again.';
              }
            } else if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            }
          } catch (e) {
            console.log('Error parsing 422 response:', e);
            errorMessage = 'Validation error. Please check all required fields are filled correctly.';
          }
        } else if (response.status === 413) {
          errorMessage = 'File too large. Please choose a smaller photo.';
        } else if (response.status >= 500) {
          errorMessage = 'Server error. Please try again later or contact support.';
        } else {
          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
          } catch (e) {
            // Use default message if can't parse response
          }
        }
        
        setSubmitStatus({
          type: 'error',
          message: errorMessage
        });
      }
    } catch (error) {
      console.error('Submission error:', error);
      let errorMessage = 'Network error. Please check your connection and try again.';
      
      // Provide more specific error messages based on the error type
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'Unable to connect to the server. Please check your internet connection.';
      } else if (error.message.includes('timeout')) {
        errorMessage = 'Request timed out. The photo might be too large. Please try with a smaller image.';
      }
      
      setSubmitStatus({
        type: 'error',
        message: errorMessage
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const goBack = () => {
    navigate('/');
  };

  if (!pinVerified) {
    return (
      <div className="bg-gray-50 min-h-screen">
        <div className="pt-20 pb-20">
          <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6 mx-auto">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Admin Access</h2>
              <p className="text-sm text-gray-600">
                This is a secure area for authorized personnel only.
              </p>
            </div>
            <form onSubmit={handlePinSubmit} className="space-y-4">
              <div>
                <label htmlFor="pin" className="block text-sm font-medium text-gray-700 mb-2">
                  Enter PIN to access dashboard:
                </label>
                <input
                  type="password"
                  id="pin"
                  value={pinInput}
                  onChange={(e) => setPinInput(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  maxLength="4"
                  placeholder="••••"
                />
                {pinError && <p className="mt-2 text-sm text-red-600">{pinError}</p>}
              </div>
              <button
                type="submit"
                className="w-full bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors"
              >
                Access Dashboard
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  if (submitStatus?.type === 'success') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-2">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-4 mx-4 text-center">
          <div className="mb-3">
            <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Saved for Review!</h2>
            <p className="text-gray-600 mb-3">{submitStatus.message}</p>
            {submitStatus.id && (
              <p className="text-sm text-gray-500 mb-3">Registration ID: {submitStatus.id}</p>
            )}
          </div>
          <div className="flex flex-col gap-3">
            <button
              onClick={() => {
                // Go to dashboard without PIN - user already authenticated
                sessionStorage.setItem('admin_authenticated', 'true');
                window.location.href = '/admin-dashboard';
              }}
              className="w-full bg-black text-white py-3 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
            >
              Go to Dashboard
            </button>
            {submitStatus.id && (
              <button
                onClick={() => {
                  // Go directly to edit the patient file
                  sessionStorage.setItem('admin_authenticated', 'true');
                  window.location.href = `/admin-edit/${submitStatus.id}`;
                }}
                className="w-full bg-black text-white py-3 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
              >
                Go to Patient File
              </button>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setSubmitStatus(null);
                  setFormData({
                    firstName: "",
                    lastName: "",
                    dob: "",
                    patientConsent: "verbal",
                    gender: "",
                    province: "Ontario",
                    disposition: "",
                    aka: "",
                    age: "",
                    regDate: new Date().toISOString().split('T')[0],
                    healthCard: "",
                    healthCardVersion: "",
                    referralSite: "",
                    address: "",
                    unitNumber: "",
                    city: "",
                    postalCode: "",
                    phone1: "",
                    phone2: "",
                    leaveMessage: false,
                    voicemail: false,
                    text: false,
                    preferredTime: "",
                    email: "",
                    language: "English",
                    specialAttention: "",
                    photo: null,
                    summaryTemplate: "", // Keep empty until user selects template
                    physician: "Dr. David Fletcher",
                    rnaAvailable: "No",
                    rnaSampleDate: "",
                    rnaResult: "Positive",
                    coverageType: "Select",
                    referralPerson: "",
                    testType: "Tests",
                    hivDate: new Date().toISOString().split('T')[0],
                    hivResult: "negative",
                    hivType: "",
                    hivTester: "CM"
                  });
                  setPhotoPreview(null);
                  setPhotoUploadStatus(null);
                }}
                className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
              >
                Register Another
              </button>
              <button
                onClick={goBack}
                className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Intake</h1>
          <div className="flex gap-2 mb-4">
            <button
              onClick={goBack}
              className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Admin Menu
            </button>
            <button
              onClick={() => navigate('/admin-dashboard')}
              className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Back to Dashboard
            </button>
            <button
              onClick={goBack}
              className="inline-flex items-center gap-1 px-3 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Home
            </button>
          </div>

          {submitStatus?.type === 'error' && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{submitStatus.message}</p>
            </div>
          )}

          {/* System Test Section */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <h3 className="text-lg font-medium text-blue-900 mb-2">🔧 System Verification</h3>
            <p className="text-blue-800 text-sm mb-3">
              Before filling out the registration form, you can test that photo upload and email functionality is working correctly.
            </p>
            <button
              type="button"
              onClick={testPhotoUploadSystem}
              disabled={systemTestStatus?.type === 'testing'}
              className="bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-sm"
            >
              {systemTestStatus?.type === 'testing' ? 'Testing System...' : 'Test Photo Upload System'}
            </button>
            
            {systemTestStatus && (
              <div className={`mt-3 p-3 rounded-md ${
                systemTestStatus.type === 'success' ? 'bg-green-50 border border-green-200' :
                systemTestStatus.type === 'error' ? 'bg-red-50 border border-red-200' :
                'bg-blue-50 border border-blue-200'
              }`}>
                <div className="flex items-center">
                  {systemTestStatus.type === 'success' && (
                    <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                  {systemTestStatus.type === 'error' && (
                    <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                  {systemTestStatus.type === 'testing' && (
                    <svg className="w-5 h-5 text-blue-600 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  )}
                  <p className={`text-sm ${
                    systemTestStatus.type === 'success' ? 'text-green-800' :
                    systemTestStatus.type === 'error' ? 'text-red-800' :
                    'text-blue-800'
                  }`}>
                    {systemTestStatus.message}
                  </p>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Photo Upload Section */}
            <div className="border-b border-gray-200 pb-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Client Photo</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Photo Options
                  </label>
                  
                  {/* Camera Option */}
                  <div className="mb-4">
                    <label htmlFor="photo-camera" className="block text-sm font-medium text-gray-600 mb-2">
                      📷 Take Photo with Camera
                    </label>
                    <input
                      type="file"
                      id="photo-camera"
                      accept="image/*"
                      capture="environment"
                      onChange={handlePhotoChange}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      Use your device's camera to take a new photo
                    </p>
                  </div>

                  {/* Upload Option */}
                  <div className="mb-4">
                    <label htmlFor="photo-upload" className="block text-sm font-medium text-gray-600 mb-2">
                      📁 Upload Existing Image
                    </label>
                    <input
                      type="file"
                      id="photo-upload"
                      accept="image/*"
                      onChange={handlePhotoChange}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      Choose an existing image from your device
                    </p>
                  </div>

                  <p className="mt-2 text-sm text-gray-500">
                    Photos are optimized to ~800KB while maintaining high quality. Supported formats: JPG, PNG, GIF.
                  </p>
                </div>
                
                {photoPreview && (
                  <div className="mt-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Photo Preview</h3>
                    <div className="w-48 h-48 border-2 border-gray-300 rounded-lg overflow-hidden">
                      <img
                        src={photoPreview}
                        alt="Client photo preview"
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={removePhoto}
                      className="mt-2 text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      Remove Photo
                    </button>
                  </div>
                )}

                {/* Photo Upload Status */}
                {photoUploadStatus && (
                  <div className={`mt-4 p-4 rounded-md ${
                    photoUploadStatus.type === 'success' ? 'bg-green-50 border border-green-200' :
                    photoUploadStatus.type === 'error' ? 'bg-red-50 border border-red-200' :
                    'bg-blue-50 border border-blue-200'
                  }`}>
                    <div className="flex items-center">
                      {photoUploadStatus.type === 'success' && (
                        <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                      {photoUploadStatus.type === 'error' && (
                        <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )}
                      {photoUploadStatus.type === 'testing' && (
                        <svg className="w-5 h-5 text-blue-600 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      )}
                      <p className={`text-sm ${
                        photoUploadStatus.type === 'success' ? 'text-green-800' :
                        photoUploadStatus.type === 'error' ? 'text-red-800' :
                        'text-blue-800'
                      }`}>
                        {photoUploadStatus.message}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Tabs Navigation */}
            <div className="border-b border-gray-200 mb-6 relative">
              <div className="flex space-x-1 overflow-x-auto scrollbar-hide">
                {getAllowedTabs().map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-2 text-sm font-medium whitespace-nowrap relative ${
                      activeTab === tab.id
                        ? 'border-b-2 border-white text-black bg-white -mb-0.5 z-10'
                        : 'border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {tab.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
              {activeTab === 'patient' && (
                <div className="space-y-6">
                  {/* Basic Information */}
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Registration Information</h2>

                    {/* Verbal Registration Input */}
                    <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-md">
                      <h3 className="text-sm font-medium text-gray-700 mb-3">
                        🎤 Verbal Registration: Record all details at once, then auto-populate fields
                      </h3>
                      
                      {/* Voice Text Area (Blank) */}
                      <div className="mb-3">
                        <textarea
                          value={voiceInputText}
                          onChange={(e) => setVoiceInputText(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
                          rows="4"
                          placeholder=""
                          style={{ whiteSpace: 'pre-wrap' }}
                        />
                      </div>
                      
                      {/* Auto-Fill/Clear Button */}
                      <div className="mb-3">
                        <button
                          type="button"
                          onClick={autoFillFromVoiceText}
                          disabled={!voiceInputText.trim() && !hasAutoFilledData}
                          className={`w-full px-4 py-2 rounded-md font-medium transition-colors ${
                            (!voiceInputText.trim() && !hasAutoFilledData)
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                              : hasAutoFilledData
                                ? 'bg-red-600 text-white hover:bg-red-700'
                                : 'bg-black text-white hover:bg-gray-800'
                          }`}
                        >
                          {hasAutoFilledData 
                            ? '🗑️ Clear Auto-Filled Data' 
                            : '✨ Auto-Fill Fields'
                          }
                        </button>
                      </div>

                      {/* Voice Status - Only show success messages, not detection messages */}
                      {voiceInputStatus && !voiceInputStatus.includes('Detected:') && (
                        <div className={`text-sm mt-2 p-2 rounded-md ${
                          voiceInputStatus.includes('❌') 
                            ? 'bg-red-50 text-red-700 border border-red-200' 
                            : voiceInputStatus.includes('✅') 
                              ? 'bg-green-50 text-green-700 border border-green-200'
                              : 'bg-blue-50 text-blue-700 border border-blue-200'
                        }`}>
                          {voiceInputStatus}
                        </div>
                      )}
                    </div>

                    {/* Registration Date Field */}
                    <div className="mb-6">
                      <label htmlFor="regDate" className="block text-sm font-medium text-gray-700 mb-2">
                        Registration Date
                      </label>
                      <div className="flex items-center space-x-2">
                        <div className="relative">
                          <input
                            type="text"
                            id="regDate"
                            name="regDate"
                            value={formData.regDate ? (() => {
                              // Create date in local timezone to avoid timezone conversion issues
                              const dateParts = formData.regDate.split('-');
                              const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
                              return date.toLocaleDateString('en-US', { 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                              });
                            })() : ''}
                            readOnly
                            onClick={() => document.getElementById('regDatePicker').showPicker()}
                            className="px-3 py-2 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-left font-medium cursor-pointer border border-gray-300"
                            style={{ 
                              width: '160px'  // Keep width for proper date display
                            }}
                            placeholder="Select date"
                          />
                          <input
                            type="date"
                            id="regDatePicker"
                            value={formData.regDate}
                            onChange={handleChange}
                            name="regDate"
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            style={{ width: '160px' }}
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => openVoiceDateInput('regDate')}
                          className="p-2 text-gray-600 hover:text-black transition-colors rounded-md hover:bg-gray-100 border border-black"
                          title="Voice input for date"
                        >
                          🎤
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                          First Name <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          id="firstName"
                          name="firstName"
                          value={formData.firstName}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Enter first name"
                          autoComplete="given-name"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                          Last Name <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          id="lastName"
                          name="lastName"
                          value={formData.lastName}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Enter last name"
                          autoComplete="family-name"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="dob" className="block text-sm font-medium text-gray-700 mb-2">
                          Date of Birth
                        </label>
                        <div className="flex items-center space-x-2">
                          <div className="relative">
                            <input
                              type="text"
                              id="dob"
                              name="dob"
                              value={formData.dob ? (() => {
                                // Create date in local timezone to avoid timezone conversion issues
                                const dateParts = formData.dob.split('-');
                                const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
                                return date.toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                });
                              })() : ''}
                              readOnly
                              onClick={() => document.getElementById('dobPicker').showPicker()}
                              className="px-3 py-2 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-left font-medium cursor-pointer border border-gray-300"
                              style={{ 
                                width: '160px'  // Keep width for proper date display
                              }}
                              placeholder="Select date"
                            />
                            <input
                              type="date"
                              id="dobPicker"
                              value={formData.dob}
                              onChange={handleChange}
                              name="dob"
                              className="absolute inset-0 opacity-0 cursor-pointer"
                              style={{ width: '160px' }}
                            />
                          </div>
                          <button
                            type="button"
                            onClick={() => openVoiceDateInput('dob')}
                            className="p-2 text-gray-600 hover:text-black transition-colors rounded-md hover:bg-gray-100 border border-black"
                            title="Voice input for date of birth"
                          >
                            🎤
                          </button>
                        </div>
                      </div>

                      <div>
                        <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-2">
                          Age (Calculated automatically)
                        </label>
                        <input
                          type="text"
                          id="age"
                          name="age"
                          value={formData.age}
                          readOnly
                          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed"
                          placeholder="Select date of birth to calculate age"
                        />
                      </div>

                      <div>
                        <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-2">
                          Gender
                        </label>
                        <select
                          id="gender"
                          name="gender"
                          value={formData.gender}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select Gender</option>
                          <option value="Male">Male</option>
                          <option value="Female">Female</option>
                        </select>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label htmlFor="disposition" className="block text-sm font-medium text-gray-700">
                            Disposition
                          </label>
                          <button
                            type="button"
                            onClick={() => setShowDispositionManager(true)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Manage Dispositions
                          </button>
                        </div>
                        <select
                          id="disposition"
                          name="disposition"
                          value={formData.disposition}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select Disposition</option>
                          {/* Most Frequently Used */}
                          {availableDispositions.filter(d => d.is_frequent).map(disposition => (
                            <option key={disposition.id} value={disposition.name}>
                              {disposition.name}
                            </option>
                          ))}
                          {/* Separator */}
                          {availableDispositions.filter(d => !d.is_frequent).length > 0 && (
                            <option disabled>-------</option>
                          )}
                          {/* All Others in Alphabetical Order */}
                          {availableDispositions
                            .filter(d => !d.is_frequent)
                            .sort((a, b) => a.name.localeCompare(b.name))
                            .map(disposition => (
                              <option key={disposition.id} value={disposition.name}>
                                {disposition.name}
                              </option>
                            ))}
                        </select>
                      </div>

                      <div>
                        <label htmlFor="aka" className="block text-sm font-medium text-gray-700 mb-2">
                          AKA (Also Known As)
                        </label>
                        <input
                          type="text"
                          id="aka"
                          name="aka"
                          value={formData.aka}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        />
                      </div>

                      <div className="flex gap-4">
                        <div className="flex-1">
                          <label htmlFor="healthCard" className="block text-sm font-medium text-gray-700 mb-2">
                            Health Card Number
                          </label>
                          <input
                            type="text"
                            id="healthCard"
                            name="healthCard"
                            value={formData.healthCard}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            maxLength="10"
                            placeholder="10 digits"
                          />
                        </div>
                        <div className="w-24">
                          <label htmlFor="healthCardVersion" className="block text-sm font-medium text-gray-700 mb-2">
                            Version Code
                          </label>
                          <input
                            type="text"
                            id="healthCardVersion"
                            name="healthCardVersion"
                            value={formData.healthCardVersion}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            placeholder="AB"
                            maxLength="2"
                          />
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label htmlFor="referralSite" className="block text-sm font-medium text-gray-700">
                            Referral Site
                          </label>
                          <button
                            type="button"
                            onClick={() => setShowReferralSiteManager(true)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Manage Referral Sites
                          </button>
                        </div>
                        <select
                          id="referralSite"
                          name="referralSite"
                          value={formData.referralSite}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select Referral Site</option>
                          {/* Most Frequently Used */}
                          {availableReferralSites.filter(s => s.is_frequent).map(site => (
                            <option key={site.id} value={site.name}>
                              {site.name}
                            </option>
                          ))}
                          {/* Separator */}
                          {availableReferralSites.filter(s => !s.is_frequent).length > 0 && (
                            <option disabled>-------</option>
                          )}
                          {/* All Others in Alphabetical Order */}
                          {availableReferralSites
                            .filter(s => !s.is_frequent)
                            .sort((a, b) => a.name.localeCompare(b.name))
                            .map(site => (
                              <option key={site.id} value={site.name}>
                                {site.name}
                              </option>
                            ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Address Information */}
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Address Information</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                          Address
                        </label>
                        <AddressAutocomplete
                          id="address"
                          name="address"
                          value={formData.address}
                          onChange={handleChange}
                          onPlaceSelected={handlePlaceSelected}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Start typing address..."
                        />
                      </div>

                      <div>
                        <label htmlFor="unitNumber" className="block text-sm font-medium text-gray-700 mb-2">
                          Unit #
                        </label>
                        <input
                          type="text"
                          id="unitNumber"
                          name="unitNumber"
                          value={formData.unitNumber}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        />
                      </div>

                      <div>
                        <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-2">
                          City
                        </label>
                        <input
                          type="text"
                          id="city"
                          name="city"
                          value={formData.city}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        />
                      </div>

                      <div>
                        <label htmlFor="province" className="block text-sm font-medium text-gray-700 mb-2">
                          Province
                        </label>
                        <select
                          id="province"
                          name="province"
                          value={formData.province}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select Province</option>
                          <option value="Ontario">Ontario</option>
                          <option value="Quebec">Quebec</option>
                          <option value="British Columbia">British Columbia</option>
                          <option value="Alberta">Alberta</option>
                          <option value="Manitoba">Manitoba</option>
                          <option value="Saskatchewan">Saskatchewan</option>
                          <option value="Nova Scotia">Nova Scotia</option>
                          <option value="New Brunswick">New Brunswick</option>
                          <option value="Newfoundland and Labrador">Newfoundland and Labrador</option>
                          <option value="Prince Edward Island">Prince Edward Island</option>
                          <option value="Northwest Territories">Northwest Territories</option>
                          <option value="Nunavut">Nunavut</option>
                          <option value="Yukon">Yukon</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="postalCode" className="block text-sm font-medium text-gray-700 mb-2">
                          Postal Code
                        </label>
                        <input
                          type="text"
                          id="postalCode"
                          name="postalCode"
                          value={formData.postalCode}
                          onChange={handleChange}
                          onBlur={(e) => {
                            // Format postal code when field loses focus (including after voice input)
                            const formatted = formatPostalCode(e.target.value);
                            if (formatted !== e.target.value) {
                              setFormData(prev => ({ ...prev, postalCode: formatted }));
                            }
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="e.g., A1A 1A1"
                          maxLength="7"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Contact Information */}
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Contact Information</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="phone1" className="block text-sm font-medium text-gray-700 mb-2">
                          Primary
                        </label>
                        <input
                          type="tel"
                          id="phone1"
                          name="phone1"
                          value={formData.phone1}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="(123) 456-7890"
                          maxLength="14"
                        />
                      </div>

                      <div>
                        <label htmlFor="phone2" className="block text-sm font-medium text-gray-700 mb-2">
                          Secondary
                        </label>
                        <input
                          type="tel"
                          id="phone2"
                          name="phone2"
                          value={formData.phone2}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="(123) 456-7890"
                          maxLength="14"
                        />
                      </div>

                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                          Email
                        </label>
                        <input
                          type="email"
                          id="email"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        />
                      </div>

                      <div>
                        <label htmlFor="preferredTime" className="block text-sm font-medium text-gray-700 mb-2">
                          Preferred Contact Time
                        </label>
                        <input
                          type="text"
                          id="preferredTime"
                          name="preferredTime"
                          value={formData.preferredTime}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="e.g., Morning, Afternoon, Evening"
                        />
                      </div>

                      <div>
                        <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-2">
                          Preferred Language
                        </label>
                        <select
                          id="language"
                          name="language"
                          value={formData.language}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="English">English</option>
                          <option value="French">French</option>
                        </select>
                      </div>

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Contact Preferences
                        </label>
                        <div className="space-y-2">
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              name="leaveMessage"
                              checked={formData.leaveMessage}
                              onChange={handleChange}
                              className="mr-2"
                            />
                            Leave Message
                          </label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              name="voicemail"
                              checked={formData.voicemail}
                              onChange={handleChange}
                              className="mr-2"
                            />
                            Voicemail
                          </label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              name="text"
                              checked={formData.text}
                              onChange={handleChange}
                              className="mr-2"
                            />
                            Text Messages
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Additional Information */}
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Additional Information</h2>
                    <div className="space-y-6">
                      <div>
                        <label htmlFor="specialAttention" className="block text-sm font-medium text-gray-700 mb-2">
                          Special Attention / Notes
                        </label>
                        <textarea
                          id="specialAttention"
                          name="specialAttention"
                          value={formData.specialAttention}
                          onChange={handleChange}
                          rows={4}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="Any special instructions or notes..."
                        />
                      </div>

                      <div>
                        <label htmlFor="instructions" className="block text-sm font-medium text-gray-700 mb-2">
                          Instructions
                        </label>
                        <textarea
                          id="instructions"
                          name="instructions"
                          value={formData.instructions}
                          onChange={handleChange}
                          rows={4}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="Any additional instructions..."
                        />
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label htmlFor="selectedTemplate" className="block text-sm font-medium text-gray-700">
                            Clinical Summary Template
                          </label>
                          <button
                            type="button"
                            onClick={() => setShowClinicalTemplateManager(true)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Manage Templates
                          </button>
                        </div>
                        <select
                          id="selectedTemplate"
                          value={selectedTemplate}
                          onChange={(e) => handleTemplateChange(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="Select">Select</option>
                          {availableClinicalTemplates.map((template) => (
                            <option key={template.id} value={template.name}>
                              {template.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      {selectedTemplate === 'Positive' && (
                        <>
                          <div>
                            <label htmlFor="rnaAvailable" className="block text-sm font-medium text-gray-700 mb-2">
                              RNA available?
                            </label>
                            <select
                              id="rnaAvailable"
                              name="rnaAvailable"
                              value={formData.rnaAvailable}
                              onChange={handleChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="No">No</option>
                              <option value="Yes">Yes</option>
                            </select>
                          </div>

                          {formData.rnaAvailable === "Yes" && (
                            <>
                              <div>
                                <label htmlFor="rnaSampleDate" className="block text-sm font-medium text-gray-700 mb-2">
                                  RNA Sample Date
                                </label>
                                <div className="flex items-center space-x-2">
                                  <div className="relative">
                                    <input
                                      type="text"
                                      id="rnaSampleDate"
                                      name="rnaSampleDate"
                                      value={formData.rnaSampleDate ? (() => {
                                        // Create date in local timezone to avoid timezone conversion issues
                                        const dateParts = formData.rnaSampleDate.split('-');
                                        const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
                                        return date.toLocaleDateString('en-US', { 
                                          year: 'numeric', 
                                          month: 'short', 
                                          day: 'numeric' 
                                        });
                                      })() : ''}
                                      readOnly
                                      onClick={() => document.getElementById('rnaSampleDatePicker').showPicker()}
                                      className="px-3 py-2 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-left font-medium cursor-pointer border border-gray-300"
                                      style={{ 
                                        width: '160px'  // Keep width for proper date display
                                      }}
                                      placeholder="Select date"
                                    />
                                    <input
                                      type="date"
                                      id="rnaSampleDatePicker"
                                      value={formData.rnaSampleDate}
                                      onChange={handleChange}
                                      name="rnaSampleDate"
                                      className="absolute inset-0 opacity-0 cursor-pointer"
                                      style={{ width: '160px' }}
                                    />
                                  </div>
                                  <button
                                    type="button"
                                    onClick={() => openVoiceDateInput('rnaSampleDate')}
                                    className="p-2 text-gray-600 hover:text-black transition-colors rounded-md hover:bg-gray-100 border border-black"
                                    title="Voice input for RNA sample date"
                                  >
                                    🎤
                                  </button>
                                </div>
                              </div>

                              <div>
                                <label htmlFor="rnaResult" className="block text-sm font-medium text-gray-700 mb-2">
                                  RNA Result
                                </label>
                                <select
                                  id="rnaResult"
                                  name="rnaResult"
                                  value={formData.rnaResult}
                                  onChange={handleChange}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                                >
                                  <option value="Positive">Positive</option>
                                  <option value="Negative">Negative</option>
                                </select>
                              </div>
                            </>
                          )}

                          <div>
                            <label htmlFor="coverageType" className="block text-sm font-medium text-gray-700 mb-2">
                              Coverage Type
                            </label>
                            <select
                              id="coverageType"
                              name="coverageType"
                              value={formData.coverageType}
                              onChange={handleChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="Select">Select</option>
                              <option value="OW">OW</option>
                              <option value="ODSP">ODSP</option>
                              <option value="No coverage">No coverage</option>
                            </select>
                          </div>

                          <div>
                            <label htmlFor="referralPerson" className="block text-sm font-medium text-gray-700 mb-2">
                              Referral Person
                            </label>
                            <input
                              type="text"
                              id="referralPerson"
                              name="referralPerson"
                              value={formData.referralPerson}
                              onChange={handleChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              placeholder="Name of person who referred this patient"
                            />
                          </div>
                        </>
                      )}

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label htmlFor="summaryTemplate" className="text-sm font-medium text-gray-700">
                            Clinical Summary Content
                          </label>
                          {selectedTemplate !== 'Positive' && selectedTemplate !== 'Select' && (
                            <div className="space-x-2">
                              {!isEditingTemplate ? (
                                <button
                                  type="button"
                                  onClick={() => setIsEditingTemplate(true)}
                                  className="text-blue-600 hover:text-blue-800 text-sm"
                                >
                                  Edit Template
                                </button>
                              ) : (
                                <>
                                  <button
                                    type="button"
                                    onClick={saveTemplate}
                                    className="text-green-600 hover:text-green-800 text-sm"
                                  >
                                    Save Template
                                  </button>
                                  <button
                                    type="button"
                                    onClick={cancelTemplateEdit}
                                    className="text-gray-600 hover:text-gray-800 text-sm"
                                  >
                                    Cancel
                                  </button>
                                </>
                              )}
                            </div>
                          )}
                        </div>
                        <textarea
                          id="summaryTemplate"
                          name="summaryTemplate"
                          value={formData.summaryTemplate}
                          onChange={handleChange}
                          rows={8}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-sm resize-vertical whitespace-pre-wrap"
                          style={{ 
                            wordWrap: 'break-word',
                            overflowWrap: 'break-word',
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.5'
                          }}
                          placeholder="Type your clinical summary here or select a template above to auto-populate..."
                          readOnly={false}
                        />
                        <p className="mt-1 text-sm text-gray-500">
                          You can type manually here or select a template above to auto-populate the content. Templates can be edited for individual patients.
                        </p>
                      </div>

                      <div>
                        <label htmlFor="physician" className="block text-sm font-medium text-gray-700 mb-2">
                          Physician
                        </label>
                        <select
                          id="physician"
                          name="physician"
                          value={formData.physician}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="Dr. David Fletcher">Dr. David Fletcher</option>
                          <option value="None">None</option>
                        </select>
                        <p className="mt-1 text-sm text-gray-500">
                          Automatically set to "None" when disposition is "POCT NEG"
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Patient Consent */}
                  <div className="border-t pt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Patient Consent Type <span className="text-red-500">*</span>
                    </label>
                    <div className="space-y-2">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="patientConsent"
                          value="verbal"
                          checked={formData.patientConsent === "verbal"}
                          onChange={handleChange}
                          className="mr-2"
                        />
                        Verbal Consent
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="patientConsent"
                          value="written"
                          checked={formData.patientConsent === "written"}
                          onChange={handleChange}
                          className="mr-2"
                        />
                        Written Consent
                      </label>
                    </div>
                  </div>

                  {/* Save Button - Only show in Patient tab */}
                  {activeTab === 'patient' && (
                    <div className="border-t pt-6 space-y-4">
                      {/* Labels Button */}
                      <button
                        type="button"
                        onClick={copyLabelsData}
                        className="w-full bg-black text-white py-3 px-6 rounded-md hover:bg-gray-800 transition-colors text-lg font-semibold"
                      >
                        Labels
                      </button>
                      {/* Copy Button */}
                      <button
                        type="button"
                        onClick={copyFormData}
                        className="w-full bg-black text-white py-3 px-6 rounded-md hover:bg-gray-800 transition-colors text-lg font-semibold"
                      >
                        Copy
                      </button>
                      {/* Submit Button */}
                      <button
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full bg-black text-white py-3 px-6 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-lg font-semibold"
                      >
                        {isSubmitting ? 'Saving...' : 'Save'}
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Template Management Modal */}
              {showTemplateManager && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                  <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
                    <div className="mt-3">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-medium text-gray-900">
                          Manage Notes Templates
                        </h3>
                        <button
                          type="button"
                          onClick={closeTemplateManager}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>

                      {/* Add New Template Section */}
                      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                        <h4 className="text-md font-medium text-gray-900 mb-3">Add New Template</h4>
                        <div className="grid grid-cols-1 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Template Name
                            </label>
                            <input
                              type="text"
                              value={newTemplateName}
                              onChange={(e) => setNewTemplateName(e.target.value)}
                              placeholder="Enter template name (e.g., Follow-up, Referral)"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Template Content
                            </label>
                            <textarea
                              value={newTemplateContent}
                              onChange={(e) => setNewTemplateContent(e.target.value)}
                              placeholder="Enter default content for this template (optional)"
                              rows="3"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            />
                          </div>
                          <div>
                            <button
                              type="button"
                              onClick={addNewTemplate}
                              disabled={!newTemplateName.trim()}
                              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                            >
                              Add Template
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Existing Templates List */}
                      <div>
                        <h4 className="text-md font-medium text-gray-900 mb-3">Existing Templates</h4>
                        <div className="space-y-3">
                          {availableNotesTemplates.length === 0 ? (
                            <div className="text-center py-8 text-gray-500">
                              <p>Loading templates...</p>
                            </div>
                          ) : (
                            availableNotesTemplates.map((template) => (
                              <div key={template.id} className="border border-gray-200 rounded-lg p-4 bg-white">
                                {editingTemplateId === template.id ? (
                                <div className="space-y-3">
                                  <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                      Template Name
                                    </label>
                                    <input
                                      type="text"
                                      defaultValue={template.name}
                                      id={`edit-name-${template.id}`}
                                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                                    />
                                  </div>
                                  <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                      Template Content
                                    </label>
                                    <textarea
                                      defaultValue={template.content}
                                      id={`edit-content-${template.id}`}
                                      rows="3"
                                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                                    />
                                  </div>
                                  <div className="flex gap-2">
                                    <button
                                      type="button"
                                      onClick={() => {
                                        const name = document.getElementById(`edit-name-${template.id}`).value;
                                        const content = document.getElementById(`edit-content-${template.id}`).value;
                                        updateTemplate(template.id, name, content);
                                      }}
                                      className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 text-sm"
                                    >
                                      Save
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => setEditingTemplateId(null)}
                                      className="bg-gray-300 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-400 text-sm"
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                <div className="flex justify-between items-start">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                      <span className="text-lg font-semibold text-gray-900">
                                        {template.name}
                                      </span>
                                      {template.is_default && (
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                          Default
                                        </span>
                                      )}
                                    </div>
                                    <div className="text-sm text-gray-700">
                                      <p className="break-words">
                                        {template.content || 'No default content'}
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex gap-2 ml-4">
                                    <button
                                      type="button"
                                      onClick={() => setEditingTemplateId(template.id)}
                                      className="text-blue-600 hover:text-blue-800 text-sm"
                                    >
                                      Edit
                                    </button>
                                    {!template.is_default && (
                                      <button
                                        type="button"
                                        onClick={() => deleteTemplate(template.id, template.name)}
                                        className="text-red-600 hover:text-red-800 text-sm"
                                      >
                                        Delete
                                      </button>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          ))
                          )}
                        </div>
                      </div>

                      {/* Close Button */}
                      <div className="mt-6 flex justify-end">
                        <button
                          type="button"
                          onClick={closeTemplateManager}
                          className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                        >
                          Close
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'tests' && (
                <div className="space-y-6">
                  {/* Registration ID Check */}
                  {!currentRegistrationId && (
                    <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-orange-800">
                            Patient Registration Required
                          </h3>
                          <div className="mt-2 text-sm text-orange-700">
                            <p>
                              Please complete and save the Patient tab form first before adding tests. 
                              This will create a registration record that tests can be associated with.
                            </p>
                          </div>
                          <div className="mt-4">
                            <button
                              type="button"
                              onClick={() => setActiveTab('patient')}
                              className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                            >
                              Go to Patient Tab
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Test Form */}
                  <div className={!currentRegistrationId ? 'opacity-50 pointer-events-none' : ''}>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">
                      {editingTestId ? 'Edit Test' : 'Add Test'}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="testType" className="block text-sm font-medium text-gray-700 mb-2">
                          Test Type
                        </label>
                        <select
                          id="testType"
                          name="test_type"
                          value={testFormData.test_type}
                          onChange={handleTestChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select Option</option>
                          <option value="HIV">HIV</option>
                          <option value="HCV">HCV</option>
                          <option value="Bloodwork">Bloodwork</option>
                        </select>
                      </div>
                    </div>

                    {/* HIV Test Fields */}
                    {testFormData.test_type === 'HIV' && (
                      <div className="mt-6">
                        <h3 className="text-md font-medium text-gray-900 mb-4">HIV Test Details</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label htmlFor="testDate" className="block text-sm font-medium text-gray-700 mb-2">
                              Test Date
                            </label>
                            <input
                              type="date"
                              id="testDate"
                              name="test_date"
                              value={testFormData.test_date}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              style={{ 
                                lineHeight: '1.5',
                                height: 'auto'
                              }}
                            />
                          </div>

                          <div>
                            <label htmlFor="hivResult" className="block text-sm font-medium text-gray-700 mb-2">
                              Test Result
                            </label>
                            <select
                              id="hivResult"
                              name="hiv_result"
                              value={testFormData.hiv_result}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="">Select Result</option>
                              <option value="negative">Negative</option>
                              <option value="positive">Positive</option>
                            </select>
                          </div>

                          {/* HIV Type - only show if result is positive */}
                          {testFormData.hiv_result === 'positive' && (
                            <div>
                              <label htmlFor="hivType" className="block text-sm font-medium text-gray-700 mb-2">
                                HIV Type
                              </label>
                              <select
                                id="hivType"
                                name="hiv_type"
                                value={testFormData.hiv_type}
                                onChange={handleTestChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              >
                                <option value="">Select Type</option>
                                <option value="Type 1">Type 1</option>
                                <option value="Type 2">Type 2</option>
                              </select>
                            </div>
                          )}

                          <div>
                            <label htmlFor="hivTester" className="block text-sm font-medium text-gray-700 mb-2">
                              Tester
                            </label>
                            <select
                              id="hivTester"
                              name="hiv_tester"
                              value={testFormData.hiv_tester}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="CM">CM</option>
                              <option value="JY">JY</option>
                            </select>
                          </div>
                        </div>

                        {/* Save Test Button */}
                        <div className="mt-6 flex gap-3">
                          <button
                            type="button"
                            onClick={saveTest}
                            className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                          >
                            {editingTestId ? 'Update Test' : 'Save Test'}
                          </button>
                          {editingTestId && (
                            <button
                              type="button"
                              onClick={cancelTestEdit}
                              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                            >
                              Cancel Edit
                            </button>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Bloodwork Test Fields */}
                    {testFormData.test_type === 'Bloodwork' && (
                      <div className="mt-6">
                        <h3 className="text-md font-medium text-gray-900 mb-4">Bloodwork Test Details</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label htmlFor="bloodworkTestDate" className="block text-sm font-medium text-gray-700 mb-2">
                              Test Date
                            </label>
                            <input
                              type="date"
                              id="bloodworkTestDate"
                              name="test_date"
                              value={testFormData.test_date}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              style={{ 
                                lineHeight: '1.5',
                                height: 'auto'
                              }}
                            />
                          </div>

                          <div>
                            <label htmlFor="bloodworkType" className="block text-sm font-medium text-gray-700 mb-2">
                              Type
                            </label>
                            <select
                              id="bloodworkType"
                              name="bloodwork_type"
                              value={testFormData.bloodwork_type}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="">Select Type</option>
                              <option value="DBS">DBS</option>
                              <option value="Serum">Serum</option>
                            </select>
                          </div>

                          {testFormData.bloodwork_type === 'DBS' && (
                            <div>
                              <label htmlFor="bloodworkCircles" className="block text-sm font-medium text-gray-700 mb-2">
                                Circles
                              </label>
                              <select
                                id="bloodworkCircles"
                                name="bloodwork_circles"
                                value={testFormData.bloodwork_circles}
                                onChange={handleTestChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              >
                                <option value="">Select Circles</option>
                                <option value="1">1</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                                <option value="4">4</option>
                                <option value="5">5</option>
                              </select>
                            </div>
                          )}

                          <div>
                            <label htmlFor="bloodworkResult" className="block text-sm font-medium text-gray-700 mb-2">
                              Results
                            </label>
                            <select
                              id="bloodworkResult"
                              name="bloodwork_result"
                              value={testFormData.bloodwork_result}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="Pending">Pending</option>
                              <option value="Submitted">Submitted</option>
                              <option value="Positive">Positive</option>
                              <option value="Negative">Negative</option>
                            </select>
                          </div>

                          <div>
                            <label htmlFor="bloodworkDateSubmitted" className="block text-sm font-medium text-gray-700 mb-2">
                              Date Submitted
                            </label>
                            <input
                              type="date"
                              id="bloodworkDateSubmitted"
                              name="bloodwork_date_submitted"
                              value={testFormData.bloodwork_date_submitted}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              style={{ 
                                lineHeight: '1.5',
                                height: 'auto'
                              }}
                            />
                          </div>

                          <div>
                            <label htmlFor="bloodworkTester" className="block text-sm font-medium text-gray-700 mb-2">
                              Tester
                            </label>
                            <select
                              id="bloodworkTester"
                              name="bloodwork_tester"
                              value={testFormData.bloodwork_tester}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="CM">CM</option>
                              <option value="JY">JY</option>
                            </select>
                          </div>
                        </div>

                        {/* Save Test Button */}
                        <div className="mt-6 flex gap-3">
                          <button
                            type="button"
                            onClick={saveTest}
                            className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                          >
                            {editingTestId ? 'Update Test' : 'Save Test'}
                          </button>
                          {editingTestId && (
                            <button
                              type="button"
                              onClick={cancelTestEdit}
                              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                            >
                              Cancel Edit
                            </button>
                          )}
                        </div>
                      </div>
                    )}

                    {/* HCV Test Fields */}
                    {testFormData.test_type === 'HCV' && (
                      <div className="mt-6">
                        <h3 className="text-md font-medium text-gray-900 mb-4">HCV Test Details</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label htmlFor="hcvTestDate" className="block text-sm font-medium text-gray-700 mb-2">
                              Test Date
                            </label>
                            <input
                              type="date"
                              id="hcvTestDate"
                              name="test_date"
                              value={testFormData.test_date}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              style={{ 
                                lineHeight: '1.5',
                                height: 'auto'
                              }}
                            />
                          </div>

                          <div>
                            <label htmlFor="hcvResult" className="block text-sm font-medium text-gray-700 mb-2">
                              Test Result
                            </label>
                            <select
                              id="hcvResult"
                              name="hcv_result"
                              value={testFormData.hcv_result}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="">Select Result</option>
                              <option value="negative">Negative</option>
                              <option value="positive">Positive</option>
                            </select>
                          </div>

                          <div>
                            <label htmlFor="hcvTester" className="block text-sm font-medium text-gray-700 mb-2">
                              Tester
                            </label>
                            <select
                              id="hcvTester"
                              name="hcv_tester"
                              value={testFormData.hcv_tester}
                              onChange={handleTestChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            >
                              <option value="CM">CM</option>
                              <option value="JY">JY</option>
                            </select>
                          </div>
                        </div>

                        {/* Save Test Button */}
                        <div className="mt-6 flex gap-3">
                          <button
                            type="button"
                            onClick={saveTest}
                            className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                          >
                            {editingTestId ? 'Update Test' : 'Save Test'}
                          </button>
                          {editingTestId && (
                            <button
                              type="button"
                              onClick={cancelTestEdit}
                              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                            >
                              Cancel Edit
                            </button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Saved Tests - Debug Info */}
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      Saved Tests Debug Info
                    </h3>
                    <div className="bg-gray-100 p-4 rounded mb-4 text-sm">
                      <p><strong>Current Registration ID:</strong> {currentRegistrationId || 'Not set'}</p>
                      <p><strong>Saved Tests Count:</strong> {savedTests.length}</p>
                      <p><strong>Test Form Data:</strong> {JSON.stringify(testFormData)}</p>
                      {savedTests.length > 0 && (
                        <div>
                          <p><strong>Saved Tests:</strong></p>
                          <pre>{JSON.stringify(savedTests, null, 2)}</pre>
                        </div>
                      )}
                      <div className="mt-2">
                        <button
                          type="button"
                          onClick={() => currentRegistrationId && loadTests(currentRegistrationId)}
                          className="bg-gray-500 text-white px-3 py-1 rounded text-sm"
                          disabled={!currentRegistrationId}
                        >
                          Manual Load Tests
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Saved Tests */}
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Saved Tests</h3>
                    
                    {savedTests.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>No tests have been saved yet.</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {savedTests.map((test) => (
                          <div key={test.id} className="border rounded-lg p-4 bg-gray-50">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center flex-wrap">
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-3">
                                    {test.test_type}
                                  </span>
                                  <span className="text-sm text-gray-500 mr-3">
                                    {new Date(test.test_date).toLocaleDateString()}
                                  </span>
                                  {test.created_at && (
                                    <span className="text-xs text-gray-400 whitespace-nowrap">
                                      Saved: {new Date(test.created_at).toLocaleTimeString('en-US', { 
                                        timeZone: 'America/New_York',
                                        hour12: true 
                                      })}
                                    </span>
                                  )}
                                </div>
                                {test.test_type === 'HIV' && (
                                  <div className="mt-2 text-sm text-gray-700">
                                    <p><strong>Result:</strong> {test.hiv_result || 'Not specified'}</p>
                                    {test.hiv_result === 'positive' && test.hiv_type && (
                                      <p><strong>Type:</strong> {test.hiv_type}</p>
                                    )}
                                    <p><strong>Tester:</strong> {test.hiv_tester || 'Not specified'}</p>
                                  </div>
                                )}
                                {test.test_type === 'HCV' && (
                                  <div className="mt-2 text-sm text-gray-700">
                                    <p><strong>Result:</strong> {test.hcv_result || 'Not specified'}</p>
                                    <p><strong>Tester:</strong> {test.hcv_tester || 'Not specified'}</p>
                                  </div>
                                )}
                                {test.test_type === 'Bloodwork' && (
                                  <div className="mt-2 text-sm text-gray-700">
                                    <p><strong>Type:</strong> {test.bloodwork_type || 'Not specified'}</p>
                                    {test.bloodwork_circles && <p><strong>Circles:</strong> {test.bloodwork_circles}</p>}
                                    <p><strong>Result:</strong> {test.bloodwork_result || 'Not specified'}</p>
                                    {test.bloodwork_date_submitted && <p><strong>Submitted:</strong> {test.bloodwork_date_submitted}</p>}
                                    <p><strong>Tester:</strong> {test.bloodwork_tester || 'Not specified'}</p>
                                  </div>
                                )}
                              </div>
                              <div className="flex gap-2">
                                <button
                                  type="button"
                                  onClick={() => editTest(test)}
                                  className="text-blue-600 hover:text-blue-800 text-sm"
                                  title="Edit test"
                                >
                                  Edit
                                </button>
                                <button
                                  type="button"
                                  onClick={() => deleteTest(test.id)}
                                  className="text-red-600 hover:text-red-800 text-sm"
                                  title="Delete test"
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'medication' && (
                <div className="space-y-6">
                  {/* Registration ID Check */}
                  {!currentRegistrationId && (
                    <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-orange-800">
                            Patient Registration Required
                          </h3>
                          <div className="mt-2 text-sm text-orange-700">
                            <p>
                              Please complete and save the Patient tab form first before adding medications. 
                              This will create a registration record that medications can be associated with.
                            </p>
                          </div>
                          <div className="mt-4">
                            <button
                              type="button"
                              onClick={() => setActiveTab('patient')}
                              className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                            >
                              Go to Patient Tab
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Medication Form */}
                  <div className={!currentRegistrationId ? 'opacity-50 pointer-events-none' : ''}>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">
                      {editingMedicationId ? 'Edit Medication' : 'Add Medication'}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="medication" className="block text-sm font-medium text-gray-700 mb-2">
                          Medication *
                        </label>
                        <select
                          id="medication"
                          name="medication"
                          value={medicationData.medication}
                          onChange={handleMedicationChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select</option>
                          <option value="Epclusa">Epclusa</option>
                          <option value="Maviret">Maviret</option>
                          <option value="Vosevi">Vosevi</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="outcome" className="block text-sm font-medium text-gray-700 mb-2">
                          Outcome *
                        </label>
                        <select
                          id="outcome"
                          name="outcome"
                          value={medicationData.outcome}
                          onChange={handleMedicationChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select</option>
                          <option value="Active">Active</option>
                          <option value="Completed">Completed</option>
                          <option value="Non Compliance">Non Compliance</option>
                          <option value="Side Effect">Side Effect</option>
                          <option value="Did not start">Did not start</option>
                          <option value="Death">Death</option>
                        </select>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-2">
                            Start Date
                          </label>
                          <input
                            type="date"
                            id="start_date"
                            name="start_date"
                            value={medicationData.start_date}
                            onChange={handleMedicationChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                        </div>

                        <div>
                          <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-2">
                            End Date
                          </label>
                          <input
                            type="date"
                            id="end_date"
                            name="end_date"
                            value={medicationData.end_date}
                            onChange={handleMedicationChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Form Actions */}
                    <div className="mt-6 grid grid-cols-2 gap-4">
                      <button
                        type="button"
                        onClick={saveMedication}
                        disabled={isSavingMedication}
                        className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                      >
                        {isSavingMedication ? 'Saving...' : editingMedicationId ? 'Update Medication' : 'Save Medication'}
                      </button>
                      
                      <button
                        type="button"
                        onClick={clearMedicationForm}
                        className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
                      >
                        Clear Form
                      </button>
                    </div>
                  </div>

                  {/* Saved Medications */}
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Saved Medications</h3>
                    
                    {savedMedications.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>No medications have been saved yet.</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {savedMedications.map((medication, index) => (
                          <div key={medication.id} className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-lg font-semibold text-gray-900">{medication.medication}</span>
                                  <span className={`text-xs px-2 py-1 rounded-full ${
                                    medication.outcome === 'Active' ? 'bg-blue-100 text-blue-700' :
                                    medication.outcome === 'Completed' ? 'bg-green-100 text-green-700' :
                                    medication.outcome === 'Non Compliance' ? 'bg-yellow-100 text-yellow-700' :
                                    medication.outcome === 'Side Effect' ? 'bg-red-100 text-red-700' :
                                    medication.outcome === 'Did not start' ? 'bg-gray-100 text-gray-700' :
                                    medication.outcome === 'Death' ? 'bg-black text-white' :
                                    'bg-gray-100 text-gray-700'
                                  }`}>
                                    {medication.outcome}
                                  </span>
                                </div>
                                <div className="text-sm text-gray-700 space-y-1">
                                  {medication.start_date && (
                                    <p><strong>Start Date:</strong> {new Date(medication.start_date).toLocaleDateString()}</p>
                                  )}
                                  {medication.end_date && (
                                    <p><strong>End Date:</strong> {new Date(medication.end_date).toLocaleDateString()}</p>
                                  )}
                                  {medication.start_date && medication.end_date && (
                                    <p><strong>Duration:</strong> {
                                      Math.ceil((new Date(medication.end_date) - new Date(medication.start_date)) / (1000 * 60 * 60 * 24))
                                    } days</p>
                                  )}
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <button
                                  onClick={() => editMedication(medication)}
                                  className="text-blue-600 hover:text-blue-800 text-sm"
                                  title="Edit medication"
                                >
                                  Edit
                                </button>
                                <button
                                  onClick={() => deleteMedication(medication.id)}
                                  className="text-red-600 hover:text-red-800 text-sm"
                                  title="Delete medication"
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'dispensing' && (
                <div className="space-y-6">
                  {/* Registration ID Check */}
                  {!currentRegistrationId && (
                    <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-orange-800">
                            Client Registration Required
                          </h3>
                          <div className="mt-2 text-sm text-orange-700">
                            <p>
                              Please complete and save the Client tab form first before adding dispensing records. 
                              This will create a registration record that dispensing can be associated with.
                            </p>
                          </div>
                          <div className="mt-4">
                            <button
                              type="button"
                              onClick={() => setActiveTab('patient')}
                              className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                            >
                              Go to Client Tab
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Dispensing Form */}
                  <div className={!currentRegistrationId ? 'opacity-50 pointer-events-none' : ''}>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">
                      {editingDispensingId ? 'Edit Dispensing' : 'Add Dispensing'}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="medication" className="block text-sm font-medium text-gray-700 mb-2">
                          Medication *
                        </label>
                        <select
                          id="medication"
                          name="medication"
                          value={dispensingData.medication}
                          onChange={handleDispensingChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select</option>
                          <option value="Epclusa">Epclusa</option>
                          <option value="Maviret">Maviret</option>
                          <option value="Vosevi">Vosevi</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="rx" className="block text-sm font-medium text-gray-700 mb-2">
                          Rx
                        </label>
                        <input
                          type="text"
                          id="rx"
                          name="rx"
                          value={dispensingData.rx}
                          onChange={handleDispensingChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="Enter Rx number"
                        />
                      </div>

                      <div>
                        <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-2">
                          Quantity
                        </label>
                        <select
                          id="quantity"
                          name="quantity"
                          value={dispensingData.quantity}
                          onChange={handleDispensingChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="28">28</option>
                          <option value="14">14</option>
                          <option value="56">56</option>
                          <option value="84">84</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="lot" className="block text-sm font-medium text-gray-700 mb-2">
                          Lot
                        </label>
                        <input
                          type="text"
                          id="lot"
                          name="lot"
                          value={dispensingData.lot}
                          onChange={handleDispensingChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          placeholder="Enter lot number"
                        />
                      </div>

                      <div>
                        <label htmlFor="product_type" className="block text-sm font-medium text-gray-700 mb-2">
                          Product Type
                        </label>
                        <select
                          id="product_type"
                          name="product_type"
                          value={dispensingData.product_type}
                          onChange={handleDispensingChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="Commercial">Commercial</option>
                          <option value="Compassionate">Compassionate</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="expiry_date" className="block text-sm font-medium text-gray-700 mb-2">
                          Expiry Date
                        </label>
                        <input
                          type="date"
                          id="expiry_date"
                          name="expiry_date"
                          value={dispensingData.expiry_date}
                          onChange={handleDispensingChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        />
                      </div>
                    </div>

                    {/* Form Actions */}
                    <div className="mt-6 grid grid-cols-2 gap-4">
                      <button
                        type="button"
                        onClick={saveDispensing}
                        disabled={isSavingDispensing}
                        className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                      >
                        {isSavingDispensing ? 'Saving...' : editingDispensingId ? 'Update Dispensing' : 'Save Dispensing'}
                      </button>
                      
                      <button
                        type="button"
                        onClick={clearDispensingForm}
                        className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
                      >
                        Clear Form
                      </button>
                    </div>
                  </div>

                  {/* Saved Dispensing Records */}
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Saved Dispensing Records</h3>
                    
                    {savedDispensing.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>No dispensing records have been saved yet.</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {savedDispensing.map((dispensing, index) => (
                          <div key={dispensing.id} className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-lg font-semibold text-gray-900">{dispensing.medication}</span>
                                  <span className={`text-xs px-2 py-1 rounded-full ${
                                    dispensing.product_type === 'Commercial' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                                  }`}>
                                    {dispensing.product_type}
                                  </span>
                                </div>
                                <div className="text-sm text-gray-700 space-y-1">
                                  {dispensing.rx && (
                                    <p><strong>Rx:</strong> {dispensing.rx}</p>
                                  )}
                                  <p><strong>Quantity:</strong> {dispensing.quantity}</p>
                                  {dispensing.lot && (
                                    <p><strong>Lot:</strong> {dispensing.lot}</p>
                                  )}
                                  {dispensing.expiry_date && (
                                    <p><strong>Expiry Date:</strong> {new Date(dispensing.expiry_date).toLocaleDateString()}</p>
                                  )}
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <button
                                  onClick={() => editDispensing(dispensing)}
                                  className="text-blue-600 hover:text-blue-800 text-sm"
                                  title="Edit dispensing record"
                                >
                                  Edit
                                </button>
                                <button
                                  onClick={() => deleteDispensing(dispensing.id)}
                                  className="text-red-600 hover:text-red-800 text-sm"
                                  title="Delete dispensing record"
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'notes' && (
                <div className="space-y-6">
                  {/* Notes Tab Warning */}
                  {!currentRegistrationId && (
                    <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-orange-800">
                            Patient Registration Required
                          </h3>
                          <div className="mt-2 text-sm text-orange-700">
                            <p>
                              Please complete and save the Patient tab form first before adding notes.
                            </p>
                          </div>
                          <div className="mt-4">
                            <button
                              type="button"
                              onClick={() => setActiveTab('patient')}
                              className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                            >
                              Go to Patient Tab
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className={!currentRegistrationId ? 'opacity-50 pointer-events-none' : ''}>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">
                      {editingNoteId ? 'Edit Note' : 'Add Note'}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="noteDate" className="block text-sm font-medium text-gray-700 mb-2">
                          Date
                        </label>
                          <input
                            type="date"
                            id="noteDate"
                            name="noteDate"
                            value={notesData.noteDate}
                            onChange={handleNotesChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                        </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label htmlFor="selectedNotesTemplate" className="block text-sm font-medium text-gray-700">
                            Notes Template
                          </label>
                          <button
                            type="button"
                            onClick={() => setShowTemplateManager(true)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Manage Templates
                          </button>
                        </div>
                        <select
                          id="selectedNotesTemplate"
                          value={selectedNotesTemplate}
                          onChange={(e) => handleNotesTemplateChange(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="Select">Select</option>
                          {availableNotesTemplates.map((template) => (
                            <option key={template.id} value={template.name}>
                              {template.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="md:col-span-2">
                        <label htmlFor="noteText" className="block text-sm font-medium text-gray-700 mb-2">
                          Note Text
                        </label>
                        <textarea
                          id="noteText"
                          name="noteText"
                          rows="6"
                          value={notesData.noteText}
                          onChange={handleNotesChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black resize-y"
                          placeholder={
                            editingNoteId 
                              ? "Edit your note content..."
                              : selectedNotesTemplate === 'Select'
                                ? "Please select a template above..."
                                : `Enter ${selectedNotesTemplate} note content...`
                          }
                          style={{ whiteSpace: 'pre-wrap' }}
                          autoComplete="off"
                          spellCheck="true"
                          readOnly={selectedNotesTemplate === 'Select'}
                        />
                      </div>
                    </div>

                    {/* Form Actions */}
                    <div className="mt-6 grid grid-cols-2 gap-4">
                      <button
                        type="button"
                        onClick={saveNote}
                        disabled={isSavingNotes || !notesData.noteText.trim() || !currentRegistrationId}
                        className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                      >
                        {isSavingNotes ? 'Saving...' : editingNoteId ? 'Update Note' : 'Save Note'}
                      </button>
                      
                      <button
                        type="button"
                        onClick={clearNotesForm}
                        className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
                      >
                        Clear Form
                      </button>
                    </div>
                  </div>

                  {/* Saved Notes */}
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Saved Notes</h3>
                      
                      {savedNotes.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          <p>No notes have been saved yet.</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {savedNotes.map((note, index) => (
                          <div key={note.id} className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="mb-2">
                                  <span className="text-lg font-semibold text-gray-900">
                                    {note.templateType || 'General Note'}
                                  </span>
                                </div>
                                <div className="text-sm text-gray-700 space-y-1">
                                  <p><strong>Date:</strong> {note.noteDate ? new Date(note.noteDate).toLocaleDateString() : 'No date'}</p>
                                  {note.created_at && (
                                    <p className="text-xs text-gray-400">
                                      Saved: {new Date(note.created_at).toLocaleTimeString('en-US', { 
                                        timeZone: 'America/New_York',
                                        hour12: true 
                                      })}
                                    </p>
                                  )}
                                  <div className="mt-2">
                                    <p style={{ whiteSpace: 'pre-wrap' }} className="break-words">
                                      {note.noteText}
                                    </p>
                                  </div>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <button
                                  onClick={() => editNote(note)}
                                  className="text-blue-600 hover:text-blue-800 text-sm"
                                  title="Edit note"
                                >
                                  Edit
                                </button>
                                <button
                                  onClick={() => deleteNote(note.id)}
                                  className="text-red-600 hover:text-red-800 text-sm"
                                  title="Delete note"
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'activities' && (
                <div className="space-y-6">
                  {/* Activities Tab Warning */}
                  {!currentRegistrationId && (
                    <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-orange-800">
                            Client Registration Required
                          </h3>
                          <div className="mt-2 text-sm text-orange-700">
                            <p>
                              Please complete and save the Client tab form first before adding activities.
                            </p>
                          </div>
                          <div className="mt-4">
                            <button
                              type="button"
                              onClick={() => setActiveTab('patient')}
                              className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                            >
                              Go to Client Tab
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className={!currentRegistrationId ? 'opacity-50 pointer-events-none' : ''}>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">
                      {editingActivityId ? 'Edit Activity' : 'Add Activity'}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="activityDescription" className="block text-sm font-medium text-gray-700 mb-2">
                          Description *
                        </label>
                          <input
                            type="date"
                            id="activityDate"
                            name="date"
                            value={activityData.date}
                            onChange={handleActivityChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                        </div>

                        <div>
                          <label htmlFor="activityTime" className="block text-sm font-medium text-gray-700 mb-2">
                            Time
                          </label>
                          <input
                            type="time"
                            id="activityTime"
                            name="time"
                            value={activityData.time}
                            onChange={handleActivityChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                        </div>

                        <div>
                          <label htmlFor="activityDescription" className="block text-sm font-medium text-gray-700 mb-2">
                            Description
                          </label>
                          <textarea
                            id="activityDescription"
                            name="description"
                            rows={4}
                            value={activityData.description}
                            onChange={handleActivityChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black resize-y"
                            placeholder="Enter activity description..."
                          />
                        </div>

                        {/* Save Buttons */}
                        <div className="flex gap-3">
                          <button
                            type="button"
                            onClick={saveActivity}
                            disabled={isSavingActivity || !activityData.description.trim() || !currentRegistrationId}
                            className="bg-black text-white px-6 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                          >
                            {isSavingActivity ? 'Saving...' : (editingActivityId ? 'Update Activity' : 'Save Activity')}
                          </button>
                          {editingActivityId && (
                            <button
                              type="button"
                              onClick={clearActivityForm}
                              className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400 transition-colors"
                            >
                              Cancel Edit
                            </button>
                          )}
                          <button
                            type="button"
                            onClick={clearActivityForm}
                            className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400 transition-colors"
                          >
                            Clear Form
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Activities List */}
                    <div className="border-t pt-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Saved Activities</h3>
                      
                      {savedActivities.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          <p>No activities have been saved yet.</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {savedActivities.map((activity, index) => (
                            <div key={activity.id} className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                              <div className="flex justify-between items-start mb-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="text-lg font-semibold text-gray-900">{activity.description}</span>
                                    {/* Recent indicator */}
                                    {(() => {
                                      const activityDateTime = new Date(activity.date + 'T' + (activity.time || '00:00'));
                                      const now = new Date();
                                      const diffHours = (now - activityDateTime) / (1000 * 60 * 60);
                                      if (diffHours < 24) {
                                        return <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Recent</span>;
                                      }
                                      return null;
                                    })()}
                                  </div>
                                  <div className="text-sm text-gray-700 space-y-1">
                                    {activity.date && (
                                      <p><strong>Date:</strong> {new Date(activity.date).toLocaleDateString()}</p>
                                    )}
                                    {activity.time && (
                                      <p><strong>Time:</strong> {activity.time}</p>
                                    )}
                                  </div>
                                </div>
                                <div className="flex gap-2">
                                  <button
                                    type="button"
                                    onClick={() => editActivity(activity)}
                                    className="text-blue-600 hover:text-blue-800 text-sm"
                                    title="Edit activity"
                                  >
                                    Edit
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => deleteActivity(activity.id)}
                                    className="text-red-600 hover:text-red-800 text-sm"
                                    title="Delete activity"
                                  >
                                    Delete
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
              )}

              {activeTab === 'interactions' && (
                <div className="space-y-6">
                  {/* Registration ID Check */}
                  {!currentRegistrationId && (
                    <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-orange-800">
                            Patient Registration Required
                          </h3>
                          <div className="mt-2 text-sm text-orange-700">
                            <p>
                              Please complete and save the Patient tab form first before adding interactions. 
                              This will create a registration record that interactions can be associated with.
                            </p>
                          </div>
                          <div className="mt-4">
                            <button
                              type="button"
                              onClick={() => setActiveTab('patient')}
                              className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                            >
                              Go to Patient Tab
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Interaction Form */}
                  <div className={!currentRegistrationId ? 'opacity-50 pointer-events-none' : ''} id="interactionForm">
                    <h2 className="text-lg font-medium text-gray-900 mb-4">
                      {editingInteractionId ? 'Edit Interaction' : 'Add Interaction'}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                          Date
                        </label>
                        <input
                          type="date"
                          id="date"
                          name="date"
                          value={interactionData.date}
                          onChange={handleInteractionChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        />
                      </div>

                      <div>
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                          Description *
                        </label>
                        <select
                          id="description"
                          name="description"
                          value={interactionData.description}
                          onChange={handleInteractionChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select</option>
                          <option value="Screening">Screening</option>
                          <option value="Adherence">Adherence</option>
                          <option value="Bloodwork">Bloodwork</option>
                          <option value="Discretionary">Discretionary</option>
                          <option value="Referral">Referral</option>
                          <option value="Consultation">Consultation</option>
                          <option value="Outreach">Outreach</option>
                          <option value="Repeat">Repeat</option>
                          <option value="Results">Results</option>
                          <option value="Safe Supply">Safe Supply</option>
                          <option value="Lab Req">Lab Req</option>
                          <option value="Telephone">Telephone</option>
                          <option value="Remittance">Remittance</option>
                          <option value="Update">Update</option>
                          <option value="Counselling">Counselling</option>
                          <option value="Trillium">Trillium</option>
                          <option value="Housing">Housing</option>
                          <option value="SOT">SOT</option>
                          <option value="EOT">EOT</option>
                          <option value="SVR">SVR</option>
                          <option value="Locate">Locate</option>
                          <option value="Staff">Staff</option>
                        </select>
                      </div>

                      {/* Conditional Referral ID field - only shows when Referral is selected */}
                      {interactionData.description === 'Referral' && (
                        <div>
                          <label htmlFor="referral_id" className="block text-sm font-medium text-gray-700 mb-2">
                            Referral ID
                          </label>
                          <input
                            type="text"
                            id="referral_id"
                            name="referral_id"
                            value={interactionData.referral_id}
                            onChange={handleInteractionChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            placeholder="Enter referral ID"
                          />
                        </div>
                      )}

                      <div>
                        <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                          Amount
                        </label>
                        <div className="relative">
                          <span className="absolute left-3 top-2 text-gray-500">$</span>
                          <input
                            type="number"
                            id="amount"
                            name="amount"
                            value={interactionData.amount}
                            onChange={handleInteractionChange}
                            className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                            placeholder="0.00"
                            step="0.01"
                          />
                        </div>
                      </div>

                      {/* Conditional Payment Type field - only shows when amount is entered */}
                      {interactionData.amount && interactionData.amount !== '' && (
                        <div>
                          <label htmlFor="payment_type" className="block text-sm font-medium text-gray-700 mb-2">
                            Payment Type
                          </label>
                          <select
                            id="payment_type"
                            name="payment_type"
                            value={interactionData.payment_type}
                            onChange={handleInteractionChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          >
                            <option value="">Select</option>
                            <option value="Cash">Cash</option>
                            <option value="EFT">EFT</option>
                          </select>
                        </div>
                      )}

                      <div>

                        <label htmlFor="issued" className="block text-sm font-medium text-gray-700 mb-2">
                          Issued
                        </label>
                        <select
                          id="issued"
                          name="issued"
                          value={interactionData.issued}
                          onChange={handleInteractionChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="Select">Select</option>
                          <option value="Yes">Yes</option>
                          <option value="No">No</option>
                        </select>
                      </div>
                    </div>

                    {/* Form Actions */}
                    <div className="mt-6 flex gap-4">
                      <button
                        type="button"
                        onClick={saveInteraction}
                        disabled={isSavingInteraction}
                        className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                      >
                        {isSavingInteraction ? 'Saving...' : editingInteractionId ? 'Update Interaction' : 'Save Interaction'}
                      </button>
                      
                      {editingInteractionId && (
                        <button
                          type="button"
                          onClick={clearInteractionForm}
                          className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
                        >
                          Cancel Edit
                        </button>
                      )}
                      
                      <button
                        type="button"
                        onClick={clearInteractionForm}
                        className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
                      >
                        Clear Form
                      </button>
                    </div>
                  </div>

                  {/* Interactions Management */}
                  <div className="space-y-4" id="interactions-section">
                    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                      <div className="flex flex-col gap-1">
                        <h3 className="text-lg font-medium text-gray-900">
                          Saved Interactions
                        </h3>
                        {savedInteractions.length !== getFilteredInteractions().length && (
                          <p className="text-sm text-gray-500">
                            Showing {getFilteredInteractions().length} of {savedInteractions.length} total interactions
                          </p>
                        )}
                      </div>
                      
                      {/* Enhanced Filter and Search Controls */}
                      <div className="flex flex-col sm:flex-row gap-3">
                        <select
                          value={interactionsFilter}
                          onChange={(e) => setInteractionsFilter(e.target.value)}
                          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-sm"
                        >
                          <option value="all">All Interactions</option>
                          <option value="today">Today</option>
                          <option value="week">Past Week</option>
                          <option value="month">Past Month</option>
                          <option value="recent">Most Recent (20)</option>
                        </select>
                        
                        <div className="relative">
                          <input
                            type="text"
                            placeholder="Search interactions..."
                            value={interactionsSearch}
                            onChange={(e) => setInteractionsSearch(e.target.value)}
                            className="px-3 py-2 pr-8 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-sm w-full sm:w-48"
                          />
                          {interactionsSearch && (
                            <button
                              onClick={() => setInteractionsSearch('')}
                              className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                              title="Clear search"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Performance Warning for Large Interaction Sets */}
                    {savedInteractions.length > 50 && interactionsFilter === 'all' && (
                      <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                        <div className="flex items-center gap-2">
                          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <p className="text-sm text-blue-700">
                            You have {savedInteractions.length} interactions. Consider using filters for better performance.
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Interactions List */}
                    {getFilteredInteractions().length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>{savedInteractions.length === 0 ? 'No interactions have been saved yet.' : 'No interactions match your search criteria.'}</p>
                        {interactionsSearch && (
                          <div className="mt-2">
                            <button
                              onClick={() => setInteractionsSearch('')}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              Clear search to see all interactions
                            </button>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {getFilteredInteractions()
                          .slice((interactionsPage - 1) * interactionsPerPage, interactionsPage * interactionsPerPage)
                          .map((interaction, index) => (
                            <div key={interaction.id} className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                              <div className="flex justify-between items-start mb-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="text-lg font-semibold text-gray-900">{interaction.description}</span>
                                    {interaction.issued && interaction.issued !== 'Select' && (
                                      <span className={`text-xs px-2 py-1 rounded-full ${
                                        interaction.issued === 'Yes' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                      }`}>
                                        {interaction.issued}
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-sm text-gray-700 space-y-1">
                                    {interaction.date && (
                                      <p><strong>Date:</strong> {new Date(interaction.date).toLocaleDateString()}</p>
                                    )}
                                    {interaction.referral_id && (
                                      <p><strong>Referral ID:</strong> {interaction.referral_id}</p>
                                    )}
                                    {interaction.amount && (
                                      <p><strong>Amount:</strong> ${interaction.amount}{interaction.payment_type && ` (${interaction.payment_type})`}</p>
                                    )}
                                  </div>
                                </div>
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => editInteraction(interaction)}
                                    className="text-blue-600 hover:text-blue-800 text-sm"
                                    title="Edit interaction"
                                  >
                                    Edit
                                  </button>
                                  <button
                                    onClick={() => deleteInteraction(interaction.id)}
                                    className="text-red-600 hover:text-red-800 text-sm"
                                    title="Delete interaction"
                                  >
                                    Delete
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))
                        }
                      </div>
                    )}

                    {/* Enhanced Pagination */}
                    {getFilteredInteractions().length > interactionsPerPage && (
                      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mt-6">
                        <div className="flex items-center gap-2">
                          <label className="text-sm text-gray-600">Show:</label>
                          <select
                            value={interactionsPerPage}
                            onChange={(e) => {
                              setInteractionsPerPage(parseInt(e.target.value));
                              setInteractionsPage(1);
                            }}
                            className="px-2 py-1 border border-gray-300 rounded text-sm"
                          >
                            <option value={10}>10</option>
                            <option value={20}>20</option>
                            <option value={50}>50</option>
                          </select>
                          <span className="text-sm text-gray-600">per page</span>
                        </div>
                        
                        <div className="flex justify-center items-center gap-4">
                          <button
                            onClick={() => setInteractionsPage(Math.max(1, interactionsPage - 1))}
                            disabled={interactionsPage === 1}
                            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Previous
                          </button>
                          <span className="text-sm text-gray-600">
                            Page {interactionsPage} of {Math.ceil(getFilteredInteractions().length / interactionsPerPage)}
                          </span>
                          <button
                            onClick={() => setInteractionsPage(Math.min(Math.ceil(getFilteredInteractions().length / interactionsPerPage), interactionsPage + 1))}
                            disabled={interactionsPage >= Math.ceil(getFilteredInteractions().length / interactionsPerPage)}
                            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Next
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'attachments' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Add New Document</h2>
                    
                    {/* Document Type Selection */}
                    <div className="mb-6">
                      <label htmlFor="documentType" className="block text-sm font-medium text-gray-700 mb-2">
                        Document Type
                      </label>
                      <select
                        id="documentType"
                        name="documentType"
                        value={documentType}
                        onChange={(e) => setDocumentType(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        style={{ maxHeight: '150px', overflowY: 'auto' }}
                        size="1"
                      >
                        <option value="">Select Document Type</option>
                        <option value="consultation-report">Consultation Report</option>
                        <option value="treatment-consent">Treatment Consent</option>
                        <option value="hcv-prescription">HCV Prescription</option>
                      </select>
                    </div>

                    {/* File Upload Options */}
                    <div className="mb-6">
                      <h3 className="text-md font-medium text-gray-900 mb-3">Upload Methods</h3>
                      
                      {/* URL Input */}
                      <div className="mb-4">
                        <label htmlFor="documentUrl" className="block text-sm font-medium text-gray-700 mb-2">
                          📎 Paste Document URL
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="url"
                            id="documentUrl"
                            name="documentUrl"
                            value={documentUrl}
                            onChange={(e) => setDocumentUrl(e.target.value)}
                            placeholder="https://example.com/document.pdf"
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                          <button
                            type="button"
                            onClick={handleLoadUrl}
                            disabled={isLoadingDocument}
                            className="px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                          >
                            {isLoadingDocument ? 'Loading...' : 'Load URL'}
                          </button>
                        </div>
                      </div>

                      {/* File Upload */}
                      <div className="mb-4">
                        <label htmlFor="documentFile" className="block text-sm font-medium text-gray-700 mb-2">
                          📁 Upload Document File
                        </label>
                        <input
                          type="file"
                          id="documentFile"
                          name="documentFile"
                          onChange={handleDocumentFileChange}
                          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                          Supported formats: PDF, DOC, DOCX, JPG, PNG (Max 10MB)
                        </p>
                      </div>
                    </div>

                    {/* Document Preview */}
                    <div className="mb-6">
                      <h3 className="text-md font-medium text-gray-900 mb-3">Document Preview</h3>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center min-h-96">
                        {documentPreview ? (
                          <div className="space-y-4">
                            {documentPreview.type === 'image' && (
                              <div 
                                className="cursor-pointer transition-transform hover:scale-105"
                                onClick={openFullScreenPreview}
                                key={documentPreview.filename + documentPreview.url?.substring(0, 20)} // Force re-render
                              >
                                <img
                                  src={documentPreview.url}
                                  alt="Document preview"
                                  className="w-full h-full object-contain border-2 border-gray-300 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                                  style={{ minHeight: '300px', maxHeight: '350px' }}
                                  key={documentPreview.url?.substring(0, 50)} // Force img re-render
                                />
                              </div>
                            )}
                            {documentPreview.type === 'pdf' && (
                              <div className="space-y-4">
                                {/* PDF Preview */}
                                <div className="border-2 border-gray-300 rounded-lg overflow-hidden shadow-md" style={{ height: '600px' }}>
                                  <iframe
                                    key={`pdf-preview-${currentPage}-${documentPreview.filename}`}
                                    src={`${documentPreview.url}#page=${currentPage}&view=FitV&zoom=85&toolbar=0`}
                                    className="w-full h-full"
                                    title="PDF Preview"
                                    style={{ border: 'none' }}
                                  />
                                </div>
                                
                                {/* Navigation Controls - Clean Layout */}
                                <div className="bg-gray-50 border rounded-lg p-4">
                                  <div className="flex items-center justify-between max-w-md mx-auto">
                                    <button
                                      onClick={prevPage}
                                      disabled={currentPage <= 1}
                                      className="px-4 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                                    >
                                      ← Prev
                                    </button>
                                    
                                    <div className="flex items-center space-x-2">
                                      <span className="text-sm text-gray-600">Page</span>
                                      <input
                                        type="number"
                                        value={currentPage}
                                        onChange={(e) => {
                                          const page = parseInt(e.target.value);
                                          if (page >= 1 && page <= totalPages) {
                                            setCurrentPage(page);
                                          }
                                        }}
                                        min="1"
                                        max={totalPages}
                                        className="w-16 px-2 py-1 border border-gray-300 rounded text-center text-sm"
                                      />
                                      <span className="text-sm text-gray-600">of {totalPages}</span>
                                    </div>
                                    
                                    <button
                                      onClick={nextPage}
                                      disabled={currentPage >= totalPages}
                                      className="px-4 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                                    >
                                      Next →
                                    </button>
                                  </div>
                                </div>
                                
                                {/* Full Screen Button */}
                                <div className="text-center mt-4">
                                  <button
                                    onClick={openFullScreenPreview}
                                    className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 text-sm"
                                  >
                                    📄 View Full Screen
                                  </button>
                                </div>
                              </div>
                            )}
                            {documentPreview.type === 'document' && (
                              <div className="text-gray-600">
                                <svg className="mx-auto h-12 w-12 mb-2" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                                </svg>
                                <p className="text-sm">Document ready for upload</p>
                              </div>
                            )}
                            {documentPreview.type === 'link' && (
                              <div className="text-blue-600">
                                <svg className="mx-auto h-12 w-12 mb-2" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
                                </svg>
                                <p className="text-sm">External link loaded</p>
                                <a 
                                  href={documentPreview.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:text-blue-800 underline"
                                >
                                  Open in new tab
                                </a>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-gray-400">
                            <svg className="mx-auto h-12 w-12 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            <p className="text-sm">No document loaded</p>
                            <p className="text-xs text-gray-500 mt-1">Upload a file or paste a URL to preview</p>
                          </div>
                        )}
                      </div>
                      {/* Click instruction text - positioned OUTSIDE the preview frame */}
                      {documentPreview && (
                        <p className="text-center text-xs text-gray-500 mt-3">Click image to see full screen</p>
                      )}
                    </div>

                    {/* Document Actions */}
                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={clearDocument}
                        className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
                      >
                        Clear Document
                      </button>
                      <button
                        type="button"
                        onClick={saveAttachment}
                        className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
                      >
                        Save Attachment
                      </button>
                    </div>

                    {/* Saved Attachments List */}
                    {savedAttachments.length > 0 && (
                      <div className="mt-8 border-t pt-6">
                        <h3 className="text-md font-medium text-gray-900 mb-4">Saved Attachments ({savedAttachments.length})</h3>
                        <div className="space-y-3">
                          {savedAttachments.map((attachment) => (
                            <div key={attachment.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                  {attachment.documentType === 'pdf' ? (
                                    <svg className="h-6 w-6 mr-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                                    </svg>
                                  ) : (
                                    <svg className="h-6 w-6 mr-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                                    </svg>
                                  )}
                                  <div>
                                    <p className="text-sm font-medium text-gray-900">{attachment.type}</p>
                                    <p className="text-xs text-gray-500">{attachment.filename}</p>
                                    <p className="text-xs text-gray-400">Saved: {attachment.savedAt}</p>
                                  </div>
                                </div>
                                <div className="flex gap-2">
                                  <button
                                    type="button"
                                    onClick={() => {
                                      // Clear current state first
                                      setDocumentFile(null);
                                      setDocumentUrl('');
                                      setDocumentPreview(null);
                                      setDocumentType(attachment.type);
                                      
                                      // Clear file input
                                      const fileInput = document.getElementById('documentFile');
                                      if (fileInput) fileInput.value = '';
                                      
                                      // Use a setTimeout to ensure state is cleared before setting new preview
                                      setTimeout(() => {
                                        // Ensure proper URL format for images
                                        let previewUrl = attachment.url;
                                        
                                        // For images, ensure they have the proper base64 data URI format
                                        if (attachment.documentType === 'image' && previewUrl && !previewUrl.startsWith('data:image/')) {
                                          // If it's a raw base64 string, add the proper prefix
                                          if (!previewUrl.startsWith('data:')) {
                                            previewUrl = `data:image/jpeg;base64,${previewUrl}`;
                                          }
                                        }
                                        
                                        // Set the document preview with the exact same structure as upload
                                        setDocumentPreview({
                                          type: attachment.documentType,
                                          url: previewUrl,
                                          filename: attachment.filename,
                                          isLocal: attachment.isLocal || false
                                        });
                                      }, 50);
                                    }}
                                    className="bg-black text-white px-3 py-1 rounded text-xs hover:bg-gray-800 transition-colors"
                                  >
                                    View
                                  </button>
                                  <button
                                    type="button"
                                    onClick={async () => {
                                      if (window.confirm(`Are you sure you want to remove "${attachment.type}" attachment? This action cannot be undone.`)) {
                                        try {
                                          // Delete from backend if we have a registration ID
                                          if (currentRegistrationId) {
                                            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/attachment/${attachment.id}`, {
                                              method: 'DELETE',
                                            });
                                            
                                            if (!response.ok) {
                                              throw new Error('Failed to delete from backend');
                                            }
                                          }
                                          
                                          // Remove from local state
                                          setSavedAttachments(prev => prev.filter(item => item.id !== attachment.id));
                                        } catch (error) {
                                          console.error('Error deleting attachment:', error);
                                          alert('Error deleting attachment. Please try again.');
                                        }
                                      }
                                    }}
                                    className="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700 transition-colors"
                                  >
                                    Remove
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

          </form>
        </div>
      </div>

      {/* Full Screen Document Preview Modal */}
      {isFullScreenPreview && documentPreview && (documentPreview.type === 'pdf' || documentPreview.type === 'image') && (
        <div className="fixed inset-0 z-50 bg-black overflow-hidden">
          {/* Top Control Bar - Fixed positioning with safe area */}
          <div className="absolute top-0 left-0 right-0 z-60 bg-black bg-opacity-50 p-4">
            <div className="flex justify-between items-center max-w-full">
              {/* Document Info */}
              <div className="bg-white px-3 py-2 rounded-md shadow-lg flex-shrink-0 mr-3">
                <div className="flex items-center text-black">
                  {documentPreview.type === 'pdf' ? (
                    <svg className="h-4 w-4 mr-2 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="h-4 w-4 mr-2 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                    </svg>
                  )}
                  <span className="text-xs font-medium truncate">{documentPreview.filename}</span>
                </div>
              </div>

              {/* Page Navigation for PDFs */}
              {documentPreview.type === 'pdf' && (
                <div className="bg-white px-3 py-2 rounded-md shadow-lg flex-shrink-0 mr-3">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={prevPage}
                      disabled={currentPage <= 1}
                      className="p-1 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                      </svg>
                    </button>
                    
                    <div className="flex items-center space-x-1">
                      <input
                        type="number"
                        value={currentPage}
                        onChange={(e) => goToPage(parseInt(e.target.value))}
                        min="1"
                        max={totalPages}
                        className="w-12 px-1 py-1 border border-gray-300 rounded text-center text-xs"
                      />
                      <span className="text-xs text-gray-600">/{totalPages}</span>
                    </div>
                    
                    <button
                      onClick={nextPage}
                      disabled={currentPage >= totalPages}
                      className="p-1 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>
                </div>
              )}

              {/* Control Buttons */}
              <div className="flex space-x-2 flex-shrink-0">
                {/* Share Button */}
                <button
                  onClick={copyShareLink}
                  disabled={isSharing}
                  className="bg-black text-white px-3 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors font-semibold shadow-lg flex items-center text-xs"
                >
                  {isSharing ? (
                    <>
                      <svg className="animate-spin h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating...
                    </>
                  ) : (
                    <>
                      <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                      </svg>
                      {shareUrl ? 'Copy Link' : 'Share'}
                    </>
                  )}
                </button>

                {/* Close Button */}
                <button
                  onClick={closeFullScreenPreview}
                  className="bg-white text-black px-3 py-2 rounded-md hover:bg-gray-100 transition-colors font-semibold shadow-lg text-xs"
                >
                  ✕ Close
                </button>
              </div>
            </div>
          </div>

          {/* Share Status Message */}
          {shareStatus && (
            <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-60">
              <div className="bg-green-600 text-white px-4 py-2 rounded-md shadow-lg text-sm">
                {shareStatus}
              </div>
            </div>
          )}

          {/* Document Viewer - Positioned below controls */}
          <div className="absolute top-16 left-0 right-0 bottom-0">
            {documentPreview.type === 'pdf' ? (
              <iframe
                src={`${documentPreview.url}#toolbar=1&navpanes=1&scrollbar=1&view=FitV&zoom=100`}
                className="w-full h-full"
                title="Full Screen PDF Preview"
                style={{ border: 'none' }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center p-4">
                <img
                  src={documentPreview.url}
                  alt={documentPreview.filename}
                  className="max-w-full max-h-full object-contain"
                />
              </div>
            )}
          </div>

          {/* Share URL Display - Bottom overlay */}
          {shareUrl && (
            <div className="absolute bottom-4 left-4 right-4 z-60">
              <div className="bg-white px-4 py-3 rounded-md shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex-1 mr-3">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Shareable Link:</label>
                    <input
                      type="text"
                      value={shareUrl}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-xs"
                    />
                  </div>
                  <button
                    onClick={copyShareLink}
                    className="bg-black text-white px-3 py-2 rounded-md hover:bg-gray-800 transition-colors text-xs font-medium flex-shrink-0"
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Clinical Summary Template Management Modal */}
      {showClinicalTemplateManager && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Manage Clinical Summary Templates
                </h3>
                <button
                  type="button"
                  onClick={closeClinicalTemplateManager}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Add New Template Section */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3">Add New Template</h4>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Template Name
                    </label>
                    <input
                      type="text"
                      value={newClinicalTemplateName}
                      onChange={(e) => setNewClinicalTemplateName(e.target.value)}
                      placeholder="Enter template name (e.g., Inconclusive, Follow-up)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Template Content
                    </label>
                    <textarea
                      value={newClinicalTemplateContent}
                      onChange={(e) => setNewClinicalTemplateContent(e.target.value)}
                      placeholder="Enter default content for this template"
                      rows="4"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    />
                  </div>
                  <div>
                    <button
                      type="button"
                      onClick={addNewClinicalTemplate}
                      disabled={!newClinicalTemplateName.trim()}
                      className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                    >
                      Add Template
                    </button>
                  </div>
                </div>
              </div>

              {/* Existing Templates List */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Existing Templates</h4>
                <div className="space-y-3">
                  {availableClinicalTemplates.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <p>Loading templates...</p>
                    </div>
                  ) : (
                    availableClinicalTemplates.map((template) => (
                      <div key={template.id} className="border border-gray-200 rounded-lg p-4 bg-white">
                        {editingClinicalTemplateId === template.id ? (
                          <div className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Template Name
                              </label>
                              <input
                                type="text"
                                defaultValue={template.name}
                                id={`edit-clinical-name-${template.id}`}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Template Content
                              </label>
                              <textarea
                                defaultValue={template.content}
                                id={`edit-clinical-content-${template.id}`}
                                rows="4"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                              />
                            </div>
                            <div className="flex gap-2">
                              <button
                                type="button"
                                onClick={() => {
                                  const name = document.getElementById(`edit-clinical-name-${template.id}`).value;
                                  const content = document.getElementById(`edit-clinical-content-${template.id}`).value;
                                  updateClinicalTemplate(template.id, name, content);
                                }}
                                className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 text-sm"
                              >
                                Save
                              </button>
                              <button
                                type="button"
                                onClick={() => setEditingClinicalTemplateId(null)}
                                className="bg-gray-300 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-400 text-sm"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg font-semibold text-gray-900">
                                  {template.name}
                                </span>
                                {template.is_default && (
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    Default
                                  </span>
                                )}
                              </div>
                              <div className="text-sm text-gray-700">
                                <p className="break-words">
                                  {template.content || 'No default content'}
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-2 ml-4">
                              <button
                                type="button"
                                onClick={() => setEditingClinicalTemplateId(template.id)}
                                className="text-blue-600 hover:text-blue-800 text-sm"
                              >
                                Edit
                              </button>
                              {!template.is_default && (
                                <button
                                  type="button"
                                  onClick={() => deleteClinicalTemplate(template.id, template.name)}
                                  className="text-red-600 hover:text-red-800 text-sm"
                                >
                                  Delete
                                </button>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Close Button */}
              <div className="mt-6 flex justify-end">
                <button
                  type="button"
                  onClick={closeClinicalTemplateManager}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Disposition Management Modal */}
      {showDispositionManager && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">Manage Dispositions</h2>
              <button
                onClick={closeDispositionManager}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Search Section */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Dispositions
              </label>
              <input
                type="text"
                value={dispositionSearch}
                onChange={(e) => setDispositionSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Search by disposition name..."
              />
            </div>

            {/* Add New Disposition Section */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Add New Disposition</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Disposition Name
                  </label>
                  <input
                    type="text"
                    value={newDispositionName}
                    onChange={(e) => setNewDispositionName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    placeholder="Enter disposition name (e.g., ACTIVE, PENDING)"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="newDispositionFrequent"
                    checked={newDispositionIsFrequent}
                    onChange={(e) => setNewDispositionIsFrequent(e.target.checked)}
                    className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
                  />
                  <label htmlFor="newDispositionFrequent" className="text-sm text-gray-700">
                    Add to "Most Frequently Used" list
                  </label>
                </div>
                <button
                  type="button"
                  onClick={addNewDisposition}
                  className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                >
                  Add Disposition
                </button>
              </div>
            </div>

            {/* Existing Dispositions List */}
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-3">
                Existing Dispositions
                <span className="text-sm font-normal text-gray-500 ml-2">
                  (Click to edit)
                </span>
              </h3>
              
              {/* Frequently Used Section */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-600 mb-2">Most Frequently Used</h4>
                <div className="grid grid-cols-3 gap-2">
                  {getFilteredDispositions()
                    .filter(d => d.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map(disposition => (
                      <div
                        key={disposition.id}
                        className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                        onClick={() => openEditDisposition(disposition)}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-gray-900 truncate">
                            {disposition.name}
                          </span>
                          {disposition.is_default && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              D
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
                {getFilteredDispositions().filter(d => d.is_frequent).length === 0 && (
                  <p className="text-sm text-gray-500 italic">
                    {dispositionSearch ? 'No frequently used dispositions match your search.' : 'No frequently used dispositions.'}
                  </p>
                )}
              </div>

              {/* All Others Section */}
              <div>
                <h4 className="text-sm font-medium text-gray-600 mb-2">All Others</h4>
                <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
                  {getFilteredDispositions()
                    .filter(d => !d.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map(disposition => (
                      <div
                        key={disposition.id}
                        className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => openEditDisposition(disposition)}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-gray-900 truncate">
                            {disposition.name}
                          </span>
                          {disposition.is_default && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              D
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
                {getFilteredDispositions().filter(d => !d.is_frequent).length === 0 && (
                  <p className="text-sm text-gray-500 italic">
                    {dispositionSearch ? 'No other dispositions match your search.' : 'No other dispositions.'}
                  </p>
                )}
              </div>
            </div>

            {/* Close Button */}
            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={closeDispositionManager}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Disposition Popup */}
      {showEditPopup && editingDisposition && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900">Edit Disposition</h3>
              <button
                onClick={() => setShowEditPopup(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Disposition Name
                </label>
                <input
                  type="text"
                  id="editDispositionName"
                  defaultValue={editingDisposition.name}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="editDispositionFrequent"
                  defaultChecked={editingDisposition.is_frequent}
                  className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
                />
                <label htmlFor="editDispositionFrequent" className="text-sm text-gray-700">
                  Add to "Most Frequently Used" list
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    if (editingDisposition.is_default) {
                      alert('Cannot delete default disposition');
                    } else {
                      deleteDisposition(editingDisposition.id, editingDisposition.name);
                    }
                  }}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    editingDisposition.is_default 
                      ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
                      : 'bg-black text-white hover:bg-gray-800'
                  }`}
                  disabled={editingDisposition.is_default}
                >
                  Delete
                </button>
                <button
                  type="button"
                  onClick={() => setShowEditPopup(false)}
                  className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const nameInput = document.getElementById('editDispositionName');
                    const frequentInput = document.getElementById('editDispositionFrequent');
                    updateDisposition(editingDisposition.id, nameInput.value, frequentInput.checked);
                  }}
                  className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Referral Site Management Modal */}
      {showReferralSiteManager && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">Manage Referral Sites</h2>
              <button
                onClick={closeReferralSiteManager}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Search Section */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Referral Sites
              </label>
              <input
                type="text"
                value={referralSiteSearch}
                onChange={(e) => setReferralSiteSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Search by referral site name..."
              />
            </div>

            {/* Add New Referral Site Section */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Add New Referral Site</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Referral Site Name
                  </label>
                  <input
                    type="text"
                    value={newReferralSiteName}
                    onChange={(e) => setNewReferralSiteName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    placeholder="Enter referral site name (e.g., Toronto - Outreach)"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="newReferralSiteFrequent"
                    checked={newReferralSiteIsFrequent}
                    onChange={(e) => setNewReferralSiteIsFrequent(e.target.checked)}
                    className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
                  />
                  <label htmlFor="newReferralSiteFrequent" className="text-sm text-gray-700">
                    Add to "Most Frequently Used" list
                  </label>
                </div>
                <button
                  type="button"
                  onClick={addNewReferralSite}
                  className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                >
                  Add Referral Site
                </button>
              </div>
            </div>

            {/* Existing Referral Sites List */}
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-3">
                Existing Referral Sites
                <span className="text-sm font-normal text-gray-500 ml-2">
                  (Click to edit)
                </span>
              </h3>
              
              {/* Frequently Used Section */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-600 mb-2">Most Frequently Used</h4>
                <div className="grid grid-cols-3 gap-2">
                  {getFilteredReferralSites()
                    .filter(s => s.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map(site => (
                      <div
                        key={site.id}
                        className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                        onClick={() => openEditReferralSite(site)}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-gray-900 truncate">
                            {site.name}
                          </span>
                          {site.is_default && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              D
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
                {getFilteredReferralSites().filter(s => s.is_frequent).length === 0 && (
                  <p className="text-sm text-gray-500 italic">
                    {referralSiteSearch ? 'No frequently used referral sites match your search.' : 'No frequently used referral sites.'}
                  </p>
                )}
              </div>

              {/* All Others Section */}
              <div>
                <h4 className="text-sm font-medium text-gray-600 mb-2">All Others</h4>
                <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
                  {getFilteredReferralSites()
                    .filter(s => !s.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map(site => (
                      <div
                        key={site.id}
                        className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => openEditReferralSite(site)}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-gray-900 truncate">
                            {site.name}
                          </span>
                          {site.is_default && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              D
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
                {getFilteredReferralSites().filter(s => !s.is_frequent).length === 0 && (
                  <p className="text-sm text-gray-500 italic">
                    {referralSiteSearch ? 'No other referral sites match your search.' : 'No other referral sites.'}
                  </p>
                )}
              </div>
            </div>

            {/* Close Button */}
            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={closeReferralSiteManager}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Referral Site Popup */}
      {showReferralSiteEditPopup && editingReferralSite && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900">Edit Referral Site</h3>
              <button
                onClick={() => setShowReferralSiteEditPopup(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Referral Site Name
                </label>
                <input
                  type="text"
                  id="editReferralSiteName"
                  defaultValue={editingReferralSite.name}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="editReferralSiteFrequent"
                  defaultChecked={editingReferralSite.is_frequent}
                  className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
                />
                <label htmlFor="editReferralSiteFrequent" className="text-sm text-gray-700">
                  Add to "Most Frequently Used" list
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    if (editingReferralSite.is_default) {
                      alert('Cannot delete default referral site');
                    } else {
                      deleteReferralSite(editingReferralSite.id, editingReferralSite.name);
                    }
                  }}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    editingReferralSite.is_default 
                      ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
                      : 'bg-black text-white hover:bg-gray-800'
                  }`}
                  disabled={editingReferralSite.is_default}
                >
                  Delete
                </button>
                <button
                  type="button"
                  onClick={() => setShowReferralSiteEditPopup(false)}
                  className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const nameInput = document.getElementById('editReferralSiteName');
                    const frequentInput = document.getElementById('editReferralSiteFrequent');
                    updateReferralSite(editingReferralSite.id, nameInput.value, frequentInput.checked);
                  }}
                  className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Voice Date Input Modal */}
      {showVoiceDateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">🎤 Voice Date Input</h3>
              <button
                type="button"
                onClick={() => setShowVoiceDateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Tap the text field below and use your phone's microphone to speak the date:
              </p>
              <input
                type="text"
                value={voiceDateInput}
                onChange={(e) => setVoiceDateInput(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Say: 'August third nineteen sixty five' or 'today'"
                autoFocus
              />
            </div>
            
            <div className="mb-4 text-xs text-gray-500">
              <strong>Examples:</strong>
              <br />• "August third nineteen sixty five"
              <br />• "January fifteenth twenty twenty four"
              <br />• "Today" or "Yesterday"
              <br />• "Fifteenth of January twenty twenty four"
            </div>
            
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handleVoiceDateSubmit}
                className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-medium"
              >
                Set Date
              </button>
              <button
                type="button"
                onClick={() => setShowVoiceDateModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminRegister;