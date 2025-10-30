export const DEFAULT_FORM = {
  first_name: "",
  last_name: "",
  dob: "",
  patient_consent: "verbal", // Default to verbal
  gender: "",
  province: "Ontario", // Default to Ontario
  disposition: "",
  aka: "",
  age: "",
  reg_date: new Date().toISOString().split("T")[0], // Default to current date
  health_card: "",
  health_card_version: "", // Add health card version code
  referral_site: "",
  address: "",
  unit_number: "",
  city: "",
  postal_code: "",
  phone1: "",
  phone2: "",
  leave_message: false,
  voicemail: false,
  text: false,
  preferred_time: "",
  email: "",
  language: "English", // Default to English
  special_attention: "",
  instructions: "", // Add instructions field
  photo: "", // Add photo field
  selected_template: "",
  summary_template: "", // Will be populated from template selection
  physician: "Dr. David Fletcher", // Add physician field with default
  rna_available: "No", // Add RNA available field
  rna_sample_date: new Date().toISOString().split("T")[0], // Add RNA sample date field
  rna_result: "Positive", // Add RNA result field
  coverage_type: "Select", // Add coverage type field
  referral_person: "", // Add referral person field
};
