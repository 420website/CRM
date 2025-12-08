import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AuthServices } from "../../src/services/authService";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { PatientServices } from "../../src/services/patientServices";

////////////////
// Patients
///////////////
describe("PatientServices.patients", () => {
  let createdId;
  const email = "test99@example.com";
  const password = "password123";

  let patientForm = {
    first_name: "Johnathon",
    last_name: "Doe",
    dob: "1990-05-15",
    patient_consent: "verbal",
    gender: "Male",
    province: "Ontario",
    disposition: "New Referral",
    aka: "JD",
    age: 33,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234567890",
    health_card_version: "AB",
    referral_site: "Central Clinic",
    address: "123 Main Street",
    unit_number: "101",
    city: "Toronto",
    postal_code: "M1A 2B3",
    phone1: "416-555-1234",
    phone2: "416-555-5678",
    leave_message: true,
    voicemail: true,
    text: false,
    preferred_time: "Morning",
    email: `john.doe@example.com`,
    language: "English",
    special_attention: "Requires translator",
    instructions: "Patient prefers morning appointments",
    photo: null,
    summary_template: "General Summary",
    physician: "Dr. David Fletcher",
    rna_available: "No",
    rna_sample_date: new Date().toISOString().split("T")[0],
    rna_result: "Positive",
    coverage_type: "Private",
    referral_person: "Dr. Smith",
  };

  beforeEach(async () => {
    // Register
    const result = await TestServices.createVerifiedUser(email, password);
    await AuthServices.verify_email(result.data?.token);

    // Login
    const login_result = await AuthServices.login(email, password);
    tokenManager.setAccessToken(login_result.data?.access_token);

    // MFA
    const mfa_email = await TestServices.send_email_mfa(email);
    const mfa_result = await AuthServices.verify_email_mfa(
      mfa_email.data?.code,
    );
    tokenManager.setAccessToken(mfa_result.data?.access_token);
  });

  afterEach(async () => {
    await TestServices.deleteUser(email, password);
  });

  it("should create a patient successfully", async () => {
    const result = await PatientServices.create_patient(patientForm);

    expect(result.success).toBe(true);
    expect(result.data?.patient_id).toBeGreaterThan(0);

    createdId = result.data?.patient_id;
    // Clean up
    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should fetch patients and include created one", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const listRes = await PatientServices.get_patients();
    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((p) => p.id == createdId);
    expect(found).toBeDefined();

    // Clean up
    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should fetch patients by location", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const listRes = await PatientServices.get_patients_by_location(["Ontario"]);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((p) => p.id == createdId);
    expect(found).toBeDefined();

    // Clean up
    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should update a patient successfully", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const updateData = { instructions: "Updated instructions" };
    const updateRes = await PatientServices.update_patient(
      createdId,
      updateData,
    );
    expect(updateRes.success).toBe(true);

    const listRes = await PatientServices.get_patients();
    const updated = listRes.data.find((p) => p.id === createdId);
    expect(updated.instructions).toBe("Updated instructions");

    // Clean up
    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should delete a patient by ID", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const deleteRes = await PatientServices.delete_patient_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    const listRes = await PatientServices.get_patients();
    const stillThere = listRes.data.find((p) => p.id === createdId);
    expect(stillThere).toBeUndefined();
  });

  it("should delete a patient by name", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const deleteRes = await PatientServices.delete_patient_by_name(
      patientForm.first_name,
      patientForm.last_name,
    );
    expect(deleteRes.success).toBe(true);

    const listRes = await PatientServices.get_patients();
    const stillThere = listRes.data.find((p) => p.id === createdId);
    expect(stillThere).toBeUndefined();
  });

  it("should get a true that identity exists", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const data = {
      first_name: "Johnathon",
      last_name: "Doe",
      dob: "1990-05-15",
    };

    const result = await PatientServices.check_identity_exists(data);
    expect(result.success).toBe(true);
    expect(result.data?.exists).toBe(true);

    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should get a false that identity exists because same id", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const data = {
      first_name: "Johnathon",
      last_name: "Doe",
      dob: "1990-05-15",
      id: createdId,
    };

    const result = await PatientServices.check_identity_exists(data);
    expect(result.success).toBe(true);
    expect(result.data?.exists).toBe(false);

    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should get a false that identity exists", async () => {
    const data = {
      first_name: "Johnathon",
      last_name: "Doe",
      dob: "1990-05-15",
    };
    const result = await PatientServices.check_identity_exists(data);
    expect(result.success).toBe(true);
    expect(result.data?.exists).toBe(false);
  });

  it("should get user that already has healthcard", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const data = {
      health_card: "1234567890",
    };

    const result = await PatientServices.check_healthcard_exists(data);
    expect(result.success).toBe(true);
    expect(result.data?.exists).toBe(true);
    expect(result.data?.user?.id).toBe(createdId);
    expect(result.data?.user?.first_name).toBe(patientForm.first_name);
    expect(result.data?.user?.last_name).toBe(patientForm.last_name);

    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should get false that healthcard already in use because for current user", async () => {
    const createRes = await PatientServices.create_patient(patientForm);
    createdId = createRes.data?.patient_id;

    const data = {
      health_card: "1234567890",
      id: createdId,
    };

    const result = await PatientServices.check_healthcard_exists(data);
    expect(result.success).toBe(true);
    expect(result.data?.exists).toBe(false);

    await PatientServices.delete_patient_by_id(createdId);
  });

  it("should get a false that healthcard exists in database", async () => {
    const data = {
      health_card: "1234567890",
    };
    const result = await PatientServices.check_healthcard_exists(data);
    expect(result.success).toBe(true);
    expect(result.data?.exists).toBe(false);
  });
});

////////////////
// Tests
///////////////
describe("PatientServices.patient assessments", () => {
  let createdPatientId;
  let createdTestId;
  const email = "test99@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "John",
    last_name: "Doe",
    dob: "1990-05-15",
    patient_consent: "verbal",
    gender: "Male",
    province: "Ontario",
    disposition: "New Referral",
    aka: "JD",
    age: 33,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234567890",
    health_card_version: "AB",
    referral_site: "Central Clinic",
    address: "123 Main Street",
    city: "Toronto",
    postal_code: "M1A 2B3",
    phone1: "416-555-1234",
    leave_message: true,
    voicemail: true,
    text: false,
    preferred_time: "Morning",
    email: "john.doe@example.com",
    language: "English",
  };

  const hivFormData = {
    type: "HIV",
    date: new Date().toISOString().split("T")[0],
    result: "negative",
    tester: "CM",
    data: { hiv_type: "Type 1" },
  };

  const hcvFormData = {
    type: "HCV",
    date: new Date().toISOString().split("T")[0],
    result: "negative",
    hiv_tester: "CM",
    data: null,
  };

  const bloodworkFormData = {
    type: "Bloodwork",
    date: new Date().toISOString().split("T")[0],
    result: "negative",
    tester: "CM",
    data: {
      bloodwork_type: "CBC",
      bloodwork_circles: "3",
      bloodwork_date_submitted: new Date().toISOString().split("T")[0],
    },
  };

  beforeEach(async () => {
    // Register + login + MFA
    const result = await TestServices.createVerifiedUser(email, password);
    await AuthServices.verify_email(result.data?.token);

    const login_result = await AuthServices.login(email, password);
    tokenManager.setAccessToken(login_result.data?.access_token);

    const mfa_email = await TestServices.send_email_mfa(email);
    const mfa_result = await AuthServices.verify_email_mfa(
      mfa_email.data?.code,
    );
    tokenManager.setAccessToken(mfa_result.data?.access_token);

    // Create patient
    const patientRes = await PatientServices.create_patient(patientForm);
    createdPatientId = patientRes.data?.patient_id;
  });

  afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should create a patient HIV assessment", async () => {
    const result = await PatientServices.create_assessment(
      createdPatientId,
      hivFormData,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Assessment created successfully.");
  });

  it("should fetch all assessments for a patient", async () => {
    await PatientServices.create_assessment(createdPatientId, hivFormData);
    await PatientServices.create_assessment(createdPatientId, hcvFormData);
    await PatientServices.create_assessment(
      createdPatientId,
      bloodworkFormData,
    );

    const listRes =
      await PatientServices.get_assessments_by_patient(createdPatientId);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((t) => t.patient_id === createdPatientId);
    expect(found).toBeDefined();
  });

  it("should fetch a assessment by ID", async () => {
    await PatientServices.create_assessment(createdPatientId, hivFormData);

    const listRes =
      await PatientServices.get_assessments_by_patient(createdPatientId);

    const found = listRes.data.find((t) => t.patient_id === createdPatientId);
    const createdId = found.id;

    const getRes = await PatientServices.get_assessment_by_id(
      createdPatientId,
      createdId,
    );

    expect(getRes.success).toBe(true);
    expect(getRes.data?.id).toBe(createdId);
    expect(getRes.data?.type).toBe("HIV");
  });

  it("should update a assessment successfully", async () => {
    await PatientServices.create_assessment(
      createdPatientId,
      bloodworkFormData,
    );
    const listRes =
      await PatientServices.get_assessments_by_patient(createdPatientId);

    const found = listRes.data.find((t) => t.patient_id === createdPatientId);
    const createdId = found.id;

    const updateRes = await PatientServices.update_assessment(
      createdPatientId,
      createdId,
      {
        data: { bloodwork_result: "Completed" },
      },
    );
    expect(updateRes.success).toBe(true);

    const getRes = await PatientServices.get_assessment_by_id(
      createdPatientId,
      createdId,
    );
    expect(getRes.data?.data).toStrictEqual({ bloodwork_result: "Completed" });
  });

  it("should delete a assessment successfully", async () => {
    await PatientServices.create_assessment(createdPatientId, hivFormData);
    const listRes =
      await PatientServices.get_assessments_by_patient(createdPatientId);

    const found = listRes.data.find((t) => t.patient_id === createdPatientId);
    const createdId = found.id;

    const deleteRes = await PatientServices.delete_assessment_by_id(
      createdPatientId,
      createdId,
    );

    expect(deleteRes.success).toBe(true);

    const listRes2 =
      await PatientServices.get_assessments_by_patient(createdPatientId);

    const stillThere = listRes2.data.find((t) => t.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

////////////////
// Notes
///////////////
describe("PatientServices.patient notes", () => {
  let createdPatientId;
  let createdNoteId;
  const email = "test_notes@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "Jane",
    last_name: "Smith",
    dob: "1992-08-20",
    patient_consent: "verbal",
    gender: "Female",
    province: "Ontario",
    disposition: "New Referral",
    age: 31,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234567890",
    health_card_version: "AB",
    referral_site: "Downtown Clinic",
    address: "456 Queen Street",
    city: "Toronto",
    postal_code: "M2B 3C4",
    phone1: "416-555-6789",
    email: "jane.smith@example.com",
    language: "English",
  };

  const noteFormData = {
    note_name: "General Note",
    note_date: new Date().toISOString().split("T")[0],
    note_text: "Initial consultation note.",
    template_type: "General Note",
  };

  beforeEach(async () => {
    // Register + login + MFA
    const result = await TestServices.createVerifiedUser(email, password);
    await AuthServices.verify_email(result.data?.token);

    const login_result = await AuthServices.login(email, password);
    tokenManager.setAccessToken(login_result.data?.access_token);

    const mfa_email = await TestServices.send_email_mfa(email);
    const mfa_result = await AuthServices.verify_email_mfa(
      mfa_email.data?.code,
    );
    tokenManager.setAccessToken(mfa_result.data?.access_token);

    // Create patient
    const patientRes = await PatientServices.create_patient(patientForm);
    createdPatientId = patientRes.data?.patient_id;
  });

  afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should create a patient note", async () => {
    const result = await PatientServices.create_note(
      createdPatientId,
      noteFormData,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Note created successfully.");
  });

  it("should fetch all notes for a patient", async () => {
    await PatientServices.create_note(createdPatientId, noteFormData);

    const listRes =
      await PatientServices.get_notes_by_patient(createdPatientId);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((n) => n.patient_id === createdPatientId);
    expect(found).toBeDefined();
    createdNoteId = found.id;
  });

  it("should fetch a note by ID", async () => {
    await PatientServices.create_note(createdPatientId, noteFormData);
    const listRes =
      await PatientServices.get_notes_by_patient(createdPatientId);
    const found = listRes.data.find((n) => n.patient_id === createdPatientId);
    createdNoteId = found.id;

    const getRes = await PatientServices.get_note_by_id(
      createdPatientId,
      createdNoteId,
    );

    expect(getRes.success).toBe(true);
    expect(getRes.data?.id).toBe(createdNoteId);
    expect(getRes.data?.template_type).toBe("General Note");
  });

  it("should update a note successfully", async () => {
    await PatientServices.create_note(createdPatientId, noteFormData);
    const listRes =
      await PatientServices.get_notes_by_patient(createdPatientId);
    const found = listRes.data.find((n) => n.patient_id === createdPatientId);
    createdNoteId = found.id;

    const updateRes = await PatientServices.update_note(
      createdPatientId,
      createdNoteId,
      {
        note_text: "Updated consultation details.",
      },
    );
    expect(updateRes.success).toBe(true);

    const getRes = await PatientServices.get_note_by_id(
      createdPatientId,
      createdNoteId,
    );
    expect(getRes.data?.note_text).toBe("Updated consultation details.");
  });

  it("should delete a note successfully", async () => {
    await PatientServices.create_note(createdPatientId, noteFormData);
    const listRes =
      await PatientServices.get_notes_by_patient(createdPatientId);
    const found = listRes.data.find((n) => n.patient_id === createdPatientId);
    createdNoteId = found.id;

    const deleteRes = await PatientServices.delete_note_by_id(
      createdPatientId,
      createdNoteId,
    );
    expect(deleteRes.success).toBe(true);

    const listRes2 =
      await PatientServices.get_notes_by_patient(createdPatientId);
    const stillThere = listRes2.data.find((n) => n.id === createdNoteId);
    expect(stillThere).toBeUndefined();
  });
});

////////////////
// Activities
///////////////
describe("PatientServices.patient activities", () => {
  let createdPatientId;
  let createdActivityId;
  const email = "test_activities@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "Alice",
    last_name: "Walker",
    dob: "1988-04-12",
    patient_consent: "verbal",
    gender: "Female",
    province: "Ontario",
    disposition: "New Referral",
    age: 35,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234567890",
    health_card_version: "AB",
    referral_site: "West Clinic",
    address: "789 King Street",
    city: "Toronto",
    postal_code: "M3C 4D5",
    phone1: "416-555-9999",
    email: "alice.walker@example.com",
    language: "English",
  };

  const activityFormData = {
    date: new Date().toISOString().split("T")[0],
    time: "10:00",
    name: "Delivery",
    description: "Initial intake appointment",
  };

  beforeEach(async () => {
    // Register + login + MFA
    const result = await TestServices.createVerifiedUser(email, password);
    await AuthServices.verify_email(result.data?.token);

    const login_result = await AuthServices.login(email, password);
    tokenManager.setAccessToken(login_result.data?.access_token);

    const mfa_email = await TestServices.send_email_mfa(email);
    const mfa_result = await AuthServices.verify_email_mfa(
      mfa_email.data?.code,
    );
    tokenManager.setAccessToken(mfa_result.data?.access_token);

    // Create patient
    const patientRes = await PatientServices.create_patient(patientForm);
    createdPatientId = patientRes.data?.patient_id;
  });

  afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should create a patient activity", async () => {
    const result = await PatientServices.create_activity(
      createdPatientId,
      activityFormData,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Activity created successfully.");
  });

  it("should fetch all activities for a patient", async () => {
    await PatientServices.create_activity(createdPatientId, activityFormData);

    const listRes =
      await PatientServices.get_activities_by_patient(createdPatientId);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((a) => a.patient_id === createdPatientId);
    expect(found).toBeDefined();
  });

  it("should fetch a patient activity by ID", async () => {
    await PatientServices.create_activity(createdPatientId, activityFormData);
    const listRes =
      await PatientServices.get_activities_by_patient(createdPatientId);
    const found = listRes.data.find((a) => a.patient_id === createdPatientId);
    createdActivityId = found.id;

    const getRes = await PatientServices.get_activity_by_id(
      createdPatientId,
      createdActivityId,
    );

    expect(getRes.success).toBe(true);
    expect(getRes.data?.id).toBe(createdActivityId);
    expect(getRes.data?.description).toBe("Initial intake appointment");
  });

  it("should update an activity successfully", async () => {
    await PatientServices.create_activity(createdPatientId, activityFormData);
    const listRes =
      await PatientServices.get_activities_by_patient(createdPatientId);
    const found = listRes.data.find((a) => a.patient_id === createdPatientId);
    createdActivityId = found.id;

    const updateRes = await PatientServices.update_activity(
      createdPatientId,
      createdActivityId,
      {
        description: "Updated appointment details",
      },
    );
    expect(updateRes.success).toBe(true);

    const getRes = await PatientServices.get_activity_by_id(
      createdPatientId,
      createdActivityId,
    );
    expect(getRes.data?.description).toBe("Updated appointment details");
  });

  it("should delete an activity successfully", async () => {
    await PatientServices.create_activity(createdPatientId, activityFormData);
    const listRes =
      await PatientServices.get_activities_by_patient(createdPatientId);
    const found = listRes.data.find((a) => a.patient_id === createdPatientId);
    createdActivityId = found.id;

    const deleteRes = await PatientServices.delete_activity_by_id(
      createdPatientId,
      createdActivityId,
    );
    expect(deleteRes.success).toBe(true);

    const listRes2 =
      await PatientServices.get_activities_by_patient(createdPatientId);
    const stillThere = listRes2.data.find((a) => a.id === createdActivityId);
    expect(stillThere).toBeUndefined();
  });
});

////////////////
// Dispensings
///////////////
describe("PatientServices.patient dispensings", () => {
  let createdPatientId;
  let createdDispensingId;
  const email = "test_dispensings@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "Bob",
    last_name: "Taylor",
    dob: "1985-02-15",
    patient_consent: "verbal",
    gender: "Male",
    province: "Ontario",
    disposition: "New Referral",
    age: 38,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234567890",
    health_card_version: "AB",
    referral_site: "North Clinic",
    address: "321 Bloor Street",
    city: "Toronto",
    postal_code: "M4C 1E5",
    phone1: "416-555-2222",
    email: "bob.taylor@example.com",
    language: "English",
  };

  const medicationFormData = {
    medication: "Amoxicillin",
    start_date: new Date().toISOString().split("T")[0],
    end_date: "2025-12-31",
    outcome: "Ongoing",
  };

  const medicationFormData2 = {
    medication: "Tylenol",
    start_date: new Date().toISOString().split("T")[0],
    end_date: "2025-12-31",
    outcome: "Ongoing",
  };

  const dispensingFormData = {
    medication: "Amoxicillin",
    rx: "RX12345",
    quantity: "28",
    lot: "LOT2025",
    product_type: "Commercial",
    expiry_date: "2026-01-01",
  };

  beforeEach(async () => {
    // Register + login + MFA
    const result = await TestServices.createVerifiedUser(email, password);
    await AuthServices.verify_email(result.data?.token);

    const login_result = await AuthServices.login(email, password);
    tokenManager.setAccessToken(login_result.data?.access_token);

    const mfa_email = await TestServices.send_email_mfa(email);
    const mfa_result = await AuthServices.verify_email_mfa(
      mfa_email.data?.code,
    );
    tokenManager.setAccessToken(mfa_result.data?.access_token);

    // Create patient
    const patientRes = await PatientServices.create_patient(patientForm);
    createdPatientId = patientRes.data?.patient_id;

    // Create Medication
    await PatientServices.create_medication(
      createdPatientId,
      medicationFormData,
    );

    await PatientServices.create_medication(
      createdPatientId,
      medicationFormData2,
    );
  });

  afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should create a patient dispensing", async () => {
    const result = await PatientServices.create_dispensing(
      createdPatientId,
      dispensingFormData,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Dispensing created successfully.");
  });

  it("should fetch all dispensings for a patient", async () => {
    await PatientServices.create_dispensing(
      createdPatientId,
      dispensingFormData,
    );

    const listRes =
      await PatientServices.get_dispensings_by_patient(createdPatientId);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((d) => d.patient_id === createdPatientId);
    expect(found).toBeDefined();
    createdDispensingId = found.id;
  });

  it("should fetch a patient dispensing by ID", async () => {
    await PatientServices.create_dispensing(
      createdPatientId,
      dispensingFormData,
    );
    const listRes =
      await PatientServices.get_dispensings_by_patient(createdPatientId);
    const found = listRes.data.find((d) => d.patient_id === createdPatientId);
    createdDispensingId = found.id;

    const getRes = await PatientServices.get_dispensing_by_id(
      createdPatientId,
      createdDispensingId,
    );

    expect(getRes.success).toBe(true);
    expect(getRes.data?.id).toBe(createdDispensingId);
    expect(getRes.data?.medication).toBe("Amoxicillin");
  });

  it("should update a dispensing successfully", async () => {
    await PatientServices.create_dispensing(
      createdPatientId,
      dispensingFormData,
    );
    const listRes =
      await PatientServices.get_dispensings_by_patient(createdPatientId);
    const found = listRes.data.find((d) => d.patient_id === createdPatientId);
    createdDispensingId = found.id;

    const updateRes = await PatientServices.update_dispensing(
      createdPatientId,
      createdDispensingId,
      {
        medication: "Tylenol",
        quantity: "30",
      },
    );
    expect(updateRes.success).toBe(true);

    const getRes = await PatientServices.get_dispensing_by_id(
      createdPatientId,
      createdDispensingId,
    );
    expect(getRes.data?.quantity).toBe(30);
  });

  it("should delete a dispensing successfully", async () => {
    await PatientServices.create_dispensing(
      createdPatientId,
      dispensingFormData,
    );
    const listRes =
      await PatientServices.get_dispensings_by_patient(createdPatientId);
    const found = listRes.data.find((d) => d.patient_id === createdPatientId);
    createdDispensingId = found.id;

    const deleteRes = await PatientServices.delete_dispensing_by_id(
      createdPatientId,
      createdDispensingId,
    );
    expect(deleteRes.success).toBe(true);

    const listRes2 =
      await PatientServices.get_dispensings_by_patient(createdPatientId);
    const stillThere = listRes2.data.find((d) => d.id === createdDispensingId);
    expect(stillThere).toBeUndefined();
  });
});

////////////////
// Medications
///////////////
describe("PatientServices.patient medications", () => {
  let createdPatientId;
  let createdMedicationId;
  const email = "test_medications@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "Carol",
    last_name: "Johnson",
    dob: "1990-06-20",
    patient_consent: "verbal",
    gender: "Female",
    province: "Ontario",
    disposition: "New Referral",
    age: 33,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234567890",
    health_card_version: "AB",
    referral_site: "East Clinic",
    address: "654 Queen Street",
    city: "Toronto",
    postal_code: "M5V 2Y9",
    phone1: "416-555-7777",
    email: "carol.johnson@example.com",
    language: "English",
  };

  const medicationFormData = {
    medication: "Ibuprofen",
    start_date: new Date().toISOString().split("T")[0],
    end_date: "2025-12-31",
    outcome: "Ongoing",
  };

  beforeEach(async () => {
    // Register + login + MFA
    const result = await TestServices.createVerifiedUser(email, password);
    await AuthServices.verify_email(result.data?.token);

    const login_result = await AuthServices.login(email, password);
    tokenManager.setAccessToken(login_result.data?.access_token);

    const mfa_email = await TestServices.send_email_mfa(email);
    const mfa_result = await AuthServices.verify_email_mfa(
      mfa_email.data?.code,
    );
    tokenManager.setAccessToken(mfa_result.data?.access_token);

    // Create patient
    const patientRes = await PatientServices.create_patient(patientForm);
    createdPatientId = patientRes.data?.patient_id;
  });

  afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should create a patient medication", async () => {
    const result = await PatientServices.create_medication(
      createdPatientId,
      medicationFormData,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Medication created successfully.");
  });

  it("should fetch all medications for a patient", async () => {
    await PatientServices.create_medication(
      createdPatientId,
      medicationFormData,
    );

    const listRes =
      await PatientServices.get_medications_by_patient(createdPatientId);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((m) => m.patient_id === createdPatientId);
    expect(found).toBeDefined();
    createdMedicationId = found.id;
  });

  it("should fetch a patient medication by ID", async () => {
    await PatientServices.create_medication(
      createdPatientId,
      medicationFormData,
    );
    const listRes =
      await PatientServices.get_medications_by_patient(createdPatientId);
    const found = listRes.data.find((m) => m.patient_id === createdPatientId);
    createdMedicationId = found.id;

    const getRes = await PatientServices.get_medication_by_id(
      createdPatientId,
      createdMedicationId,
    );

    expect(getRes.success).toBe(true);
    expect(getRes.data?.id).toBe(createdMedicationId);
    expect(getRes.data?.medication).toBe("Ibuprofen");
  });

  it("should update a medication successfully", async () => {
    await PatientServices.create_medication(
      createdPatientId,
      medicationFormData,
    );
    const listRes =
      await PatientServices.get_medications_by_patient(createdPatientId);
    const found = listRes.data.find((m) => m.patient_id === createdPatientId);
    createdMedicationId = found.id;

    const updateRes = await PatientServices.update_medication(
      createdPatientId,
      createdMedicationId,
      {
        outcome: "Completed",
      },
    );
    expect(updateRes.success).toBe(true);

    const getRes = await PatientServices.get_medication_by_id(
      createdPatientId,
      createdMedicationId,
    );
    expect(getRes.data?.outcome).toBe("Completed");
  });

  it("should delete a medication successfully", async () => {
    await PatientServices.create_medication(
      createdPatientId,
      medicationFormData,
    );
    const listRes =
      await PatientServices.get_medications_by_patient(createdPatientId);
    const found = listRes.data.find((m) => m.patient_id === createdPatientId);
    createdMedicationId = found.id;

    const deleteRes = await PatientServices.delete_medication_by_id(
      createdPatientId,
      createdMedicationId,
    );
    expect(deleteRes.success).toBe(true);

    const listRes2 =
      await PatientServices.get_medications_by_patient(createdPatientId);
    const stillThere = listRes2.data.find((m) => m.id === createdMedicationId);
    expect(stillThere).toBeUndefined();
  });
});

////////////////
// Interactions
///////////////
describe("PatientServices.patient interactions", () => {
  let createdPatientId;
  let createdInteractionId;
  const email = "test_interactions@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "David",
    last_name: "Miller",
    dob: "1982-11-10",
    patient_consent: "verbal",
    gender: "Male",
    province: "Ontario",
    disposition: "New Referral",
    age: 41,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234567890",
    health_card_version: "AB",
    referral_site: "Central Clinic",
    address: "123 King Street",
    city: "Toronto",
    postal_code: "M1B 2C3",
    phone1: "416-555-1111",
    email: "david.miller@example.com",
    language: "English",
  };

  const interactionFormData = {
    date: new Date().toISOString().split("T")[0],
    description: "Initial phone consultation",
    referral_id: "REF123",
    amount: "150",
    payment_type: "Credit Card",
    issued: "Yes",
  };

  beforeEach(async () => {
    // Register + login + MFA
    const result = await TestServices.createVerifiedUser(email, password);
    await AuthServices.verify_email(result.data?.token);

    const login_result = await AuthServices.login(email, password);
    tokenManager.setAccessToken(login_result.data?.access_token);

    const mfa_email = await TestServices.send_email_mfa(email);
    const mfa_result = await AuthServices.verify_email_mfa(
      mfa_email.data?.code,
    );
    tokenManager.setAccessToken(mfa_result.data?.access_token);

    // Create patient
    const patientRes = await PatientServices.create_patient(patientForm);
    createdPatientId = patientRes.data?.patient_id;
  });

  afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should create a patient interaction", async () => {
    const result = await PatientServices.create_interaction(
      createdPatientId,
      interactionFormData,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Interaction created successfully.");
  });

  it("should fetch all interactions for a patient", async () => {
    await PatientServices.create_interaction(
      createdPatientId,
      interactionFormData,
    );

    const listRes =
      await PatientServices.get_interactions_by_patient(createdPatientId);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((i) => i.patient_id === createdPatientId);
    expect(found).toBeDefined();
    createdInteractionId = found.id;
  });

  it("should fetch a patient interaction by ID", async () => {
    await PatientServices.create_interaction(
      createdPatientId,
      interactionFormData,
    );

    const listRes =
      await PatientServices.get_interactions_by_patient(createdPatientId);
    const found = listRes.data.find((i) => i.patient_id === createdPatientId);
    createdInteractionId = found.id;

    const getRes = await PatientServices.get_interaction_by_id(
      createdPatientId,
      createdInteractionId,
    );

    expect(getRes.success).toBe(true);
    expect(getRes.data?.id).toBe(createdInteractionId);
    expect(getRes.data?.description).toBe("Initial phone consultation");
  });

  it("should update an interaction successfully", async () => {
    await PatientServices.create_interaction(
      createdPatientId,
      interactionFormData,
    );

    const listRes =
      await PatientServices.get_interactions_by_patient(createdPatientId);
    const found = listRes.data.find((i) => i.patient_id === createdPatientId);
    createdInteractionId = found.id;

    const updateRes = await PatientServices.update_interaction(
      createdPatientId,
      createdInteractionId,
      {
        amount: "200",
      },
    );
    expect(updateRes.success).toBe(true);

    const getRes = await PatientServices.get_interaction_by_id(
      createdPatientId,
      createdInteractionId,
    );
    expect(getRes.data?.amount).toBe("200.00");
  });

  it("should delete an interaction successfully", async () => {
    await PatientServices.create_interaction(
      createdPatientId,
      interactionFormData,
    );

    const listRes =
      await PatientServices.get_interactions_by_patient(createdPatientId);
    const found = listRes.data.find((i) => i.patient_id === createdPatientId);
    createdInteractionId = found.id;

    const deleteRes = await PatientServices.delete_interaction_by_id(
      createdPatientId,
      createdInteractionId,
    );
    expect(deleteRes.success).toBe(true);

    const listRes2 =
      await PatientServices.get_interactions_by_patient(createdPatientId);
    const stillThere = listRes2.data.find((i) => i.id === createdInteractionId);
    expect(stillThere).toBeUndefined();
  });
});
