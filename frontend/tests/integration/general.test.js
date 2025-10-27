import axios from "axios";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AuthServices } from "../../src/services/authService";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { GeneralServices } from "../../src/services/generalService";

describe("GeneralServices.notes-template", () => {
  let createdId;
  const email = "test1@example.com";
  const password = "password123";

  let notes_template = {
    name: "test_template",
    content: "This is the content",
    is_default: true,
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
    await GeneralServices.delete_note_template_by_name("test_template");
    await TestServices.deleteUser(email, password);
  });

  it("should create a note template successfully", async () => {
    const result = await GeneralServices.create_note_template(notes_template);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Notes template created successfully.");
  });

  it("should fetch note templates and include created one", async () => {
    await GeneralServices.create_note_template(notes_template);

    const result = await GeneralServices.get_note_templates();

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((t) => t.name === notes_template.name);
    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a note template successfully", async () => {
    const createRes =
      await GeneralServices.create_note_template(notes_template);
    expect(createRes.success).toBe(true);

    // grab id
    const listRes = await GeneralServices.get_note_templates();
    const found = listRes.data.find((t) => t.name === notes_template.name);
    createdId = found.id;

    const updateData = { content: "Updated content" };
    const updateRes = await GeneralServices.update_note_template(
      createdId,
      updateData,
    );

    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await GeneralServices.get_note_templates();
    const updated = refreshed.data.find((t) => t.id === createdId);
    expect(updated.content).toBe("Updated content");
  });

  it("should delete a note template by name", async () => {
    await GeneralServices.create_note_template(notes_template);

    const deleteRes = await GeneralServices.delete_note_template_by_name(
      notes_template.name,
    );

    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await GeneralServices.get_note_templates();
    const stillThere = listRes.data.find((t) => t.name === notes_template.name);
    expect(stillThere).toBeUndefined();
  });

  it("should delete a note template by id", async () => {
    await GeneralServices.create_note_template(notes_template);

    const listRes = await GeneralServices.get_note_templates();
    const found = listRes.data.find((t) => t.name === notes_template.name);
    createdId = found.id;

    const deleteRes =
      await GeneralServices.delete_note_template_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await GeneralServices.get_note_templates();
    const stillThere = refreshed.data.find((t) => t.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

describe("GeneralServices.clinical-templates", () => {
  let createdId;
  const email = "test2@example.com"; // use a different user from notes test
  const password = "password123";

  const clinical_template = {
    name: "test_clinical_template",
    content: "This is the clinical content",
    is_default: true,
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
    // clean up
    await GeneralServices.delete_clinical_template_by_name(
      clinical_template.name,
    );
    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a clinical template successfully", async () => {
    const result =
      await GeneralServices.create_clinical_template(clinical_template);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe(
      "Clinical template created successfully.",
    );
  });

  it("should fetch clinical templates and include created one", async () => {
    await GeneralServices.create_clinical_template(clinical_template);

    const result = await GeneralServices.get_clinical_templates();

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((t) => t.name === clinical_template.name);
    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a clinical template successfully", async () => {
    const createRes =
      await GeneralServices.create_clinical_template(clinical_template);
    expect(createRes.success).toBe(true);

    // grab id
    const listRes = await GeneralServices.get_clinical_templates();
    const found = listRes.data.find((t) => t.name === clinical_template.name);
    createdId = found.id;

    const updateData = { content: "Updated clinical content" };
    const updateRes = await GeneralServices.update_clinical_template(
      createdId,
      updateData,
    );

    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await GeneralServices.get_clinical_templates();
    const updated = refreshed.data.find((t) => t.id === createdId);
    expect(updated.content).toBe("Updated clinical content");
  });

  it("should delete a clinical template by name", async () => {
    await GeneralServices.create_clinical_template(clinical_template);

    const deleteRes = await GeneralServices.delete_clinical_template_by_name(
      clinical_template.name,
    );

    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await GeneralServices.get_clinical_templates();
    const stillThere = listRes.data.find(
      (t) => t.name === clinical_template.name,
    );
    expect(stillThere).toBeUndefined();
  });

  it("should delete a clinical template by id", async () => {
    await GeneralServices.create_clinical_template(clinical_template);

    const listRes = await GeneralServices.get_clinical_templates();
    const found = listRes.data.find((t) => t.name === clinical_template.name);
    createdId = found.id;

    const deleteRes =
      await GeneralServices.delete_clinical_template_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await GeneralServices.get_clinical_templates();
    const stillThere = refreshed.data.find((t) => t.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

describe("GeneralServices.dispositions", () => {
  let createdId;
  const email = "test3@example.com"; // use a unique user
  const password = "password123";

  const disposition = {
    name: "test_disposition",
    is_frequent: true,
    is_default: true,
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
    // cleanup
    await GeneralServices.delete_disposition_by_name(disposition.name);
    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a disposition successfully", async () => {
    const result = await GeneralServices.create_disposition(disposition);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Disposition created successfully.");
  });

  it("should fetch dispositions and include created one", async () => {
    await GeneralServices.create_disposition(disposition);

    const result = await GeneralServices.get_dispositions();

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((d) => d.name === disposition.name);
    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a disposition successfully", async () => {
    await GeneralServices.create_disposition(disposition);

    const listRes = await GeneralServices.get_dispositions();
    const found = listRes.data.find((d) => d.name === disposition.name);
    createdId = found.id;

    const updateData = { is_frequent: false };
    const updateRes = await GeneralServices.update_disposition(
      createdId,
      updateData,
    );

    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await GeneralServices.get_dispositions();
    const updated = refreshed.data.find((d) => d.id === createdId);
    expect(updated.is_frequent).toBe(false);
  });

  it("should delete a disposition by name", async () => {
    await GeneralServices.create_disposition(disposition);

    const deleteRes = await GeneralServices.delete_disposition_by_name(
      disposition.name,
    );
    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await GeneralServices.get_dispositions();
    const stillThere = listRes.data.find((d) => d.name === disposition.name);
    expect(stillThere).toBeUndefined();
  });

  it("should delete a disposition by id", async () => {
    await GeneralServices.create_disposition(disposition);

    const listRes = await GeneralServices.get_dispositions();
    const found = listRes.data.find((d) => d.name === disposition.name);
    createdId = found.id;

    const deleteRes = await GeneralServices.delete_disposition_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await GeneralServices.get_dispositions();
    const stillThere = refreshed.data.find((d) => d.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

describe("GeneralServices.document-type", () => {
  let createdId;
  const email = "test3@example.com"; // use a unique user
  const password = "password123";

  const document_type = {
    name: "HCV Prescription",
    is_frequent: false,
    is_default: true,
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
    // cleanup
    await GeneralServices.delete_document_type_by_name(document_type.name);
    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a document type successfully", async () => {
    const result = await GeneralServices.create_document_type(document_type);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Document type created successfully.");
  });

  it("should fetch document type and include created one", async () => {
    await GeneralServices.create_document_type(document_type);

    const result = await GeneralServices.get_document_types();

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((d) => d.name === document_type.name);
    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a document type successfully", async () => {
    await GeneralServices.create_document_type(document_type);

    const listRes = await GeneralServices.get_document_types();
    const found = listRes.data.find((d) => d.name === document_type.name);
    createdId = found.id;

    const updateData = { is_default: false };
    const updateRes = await GeneralServices.update_document_type(
      createdId,
      updateData,
    );

    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await GeneralServices.get_document_types();
    const updated = refreshed.data.find((d) => d.id === createdId);
    expect(updated.is_default).toBe(false);
  });

  it("should delete a document type by name", async () => {
    await GeneralServices.create_document_type(document_type);

    const deleteRes = await GeneralServices.delete_document_type_by_name(
      document_type.name,
    );
    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await GeneralServices.get_document_types();
    const stillThere = listRes.data.find((d) => d.name === document_type.name);
    expect(stillThere).toBeUndefined();
  });

  it("should delete a document type by id", async () => {
    await GeneralServices.create_document_type(document_type);

    const listRes = await GeneralServices.get_document_types();
    const found = listRes.data.find((d) => d.name === document_type.name);
    createdId = found.id;

    const deleteRes =
      await GeneralServices.delete_document_type_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await GeneralServices.get_document_types();
    const stillThere = refreshed.data.find((d) => d.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

describe("GeneralServices.referral-sites", () => {
  let createdId;
  const email = "test4@example.com"; // unique user for this suite
  const password = "password123";

  const referral_site = {
    name: "test_referral_site",
    is_frequent: true,
    is_default: true,
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
    // cleanup
    await GeneralServices.delete_referral_site_by_name(referral_site.name);
    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a referral site successfully", async () => {
    const result = await GeneralServices.create_referral_site(referral_site);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Referral site created successfully.");
  });

  it("should fetch referral sites and include created one", async () => {
    await GeneralServices.create_referral_site(referral_site);

    const result = await GeneralServices.get_referral_sites();

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((r) => r.name === referral_site.name);
    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a referral site successfully", async () => {
    await GeneralServices.create_referral_site(referral_site);

    const listRes = await GeneralServices.get_referral_sites();
    const found = listRes.data.find((r) => r.name === referral_site.name);
    createdId = found.id;

    const updateData = { is_frequent: false };
    const updateRes = await GeneralServices.update_referral_site(
      createdId,
      updateData,
    );

    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await GeneralServices.get_referral_sites();
    const updated = refreshed.data.find((r) => r.id === createdId);
    expect(updated.is_frequent).toBe(false);
  });

  it("should delete a referral site by name", async () => {
    await GeneralServices.create_referral_site(referral_site);

    const deleteRes = await GeneralServices.delete_referral_site_by_name(
      referral_site.name,
    );
    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await GeneralServices.get_referral_sites();
    const stillThere = listRes.data.find((r) => r.name === referral_site.name);
    expect(stillThere).toBeUndefined();
  });

  it("should delete a referral site by id", async () => {
    await GeneralServices.create_referral_site(referral_site);

    const listRes = await GeneralServices.get_referral_sites();
    const found = listRes.data.find((r) => r.name === referral_site.name);
    createdId = found.id;

    const deleteRes =
      await GeneralServices.delete_referral_site_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await GeneralServices.get_referral_sites();
    const stillThere = refreshed.data.find((r) => r.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

describe("GeneralServices.medication-templates", () => {
  let createdId;

  const email = "test4@example.com"; // unique user for this suite
  const password = "password123";

  const medication = {
    name: "test_medication",
    is_frequent: true,
    is_default: true,
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
    // cleanup
    await GeneralServices.delete_medication_template_by_name(medication.name);
    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a medication template successfully", async () => {
    const result = await GeneralServices.create_medication_template(medication);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Medication created successfully.");
  });

  it("should fetch medications and include created one", async () => {
    await GeneralServices.create_medication_template(medication);
    const result = await GeneralServices.get_medication_template();

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((m) => m.name === medication.name);

    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a medication successfully", async () => {
    await GeneralServices.create_medication_template(medication);
    const listRes = await GeneralServices.get_medication_template();

    const found = listRes.data.find((m) => m.name === medication.name);

    createdId = found.id;
    const updateData = { is_frequent: false };
    const updateRes = await GeneralServices.update_medication_template(
      createdId,
      updateData,
    );
    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await GeneralServices.get_medication_template();
    const updated = refreshed.data.find((m) => m.id === createdId);
    expect(updated.is_frequent).toBe(false);
  });

  it("should delete a medication by name", async () => {
    await GeneralServices.create_medication_template(medication);
    const deleteRes = await GeneralServices.delete_medication_template_by_name(
      medication.name,
    );
    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await GeneralServices.get_medication_template();
    const stillThere = listRes.data.find((m) => m.name === medication.name);
    expect(stillThere).toBeUndefined();
  });

  it("should delete a medication by id", async () => {
    await GeneralServices.create_medication_template(medication);
    const listRes = await GeneralServices.get_medication_template();
    const found = listRes.data.find((m) => m.name === medication.name);
    createdId = found.id;

    const deleteRes =
      await GeneralServices.delete_medication_template_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await GeneralServices.get_medication_template();
    const stillThere = refreshed.data.find((m) => m.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

describe("GeneralServices.medication-outcomes", () => {
  let createdId;

  const email = "test4@example.com";
  const password = "password123";

  const medicationOutcome = {
    name: "test_outcome",
    is_frequent: true,
    is_default: true,
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
    // cleanup
    await GeneralServices.delete_medication_outcome_by_name(
      medicationOutcome.name,
    );
    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a medication outcome successfully", async () => {
    const result =
      await GeneralServices.create_medication_outcome(medicationOutcome);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe(
      "Medication outcome created successfully.",
    );
  });

  it("should fetch medication outcomes and include created one", async () => {
    await GeneralServices.create_medication_outcome(medicationOutcome);
    const result = await GeneralServices.get_medication_outcomes();

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((m) => m.name === medicationOutcome.name);

    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a medication outcome successfully", async () => {
    await GeneralServices.create_medication_outcome(medicationOutcome);
    const listRes = await GeneralServices.get_medication_outcomes();

    const found = listRes.data.find((m) => m.name === medicationOutcome.name);

    createdId = found.id;
    const updateData = { is_frequent: false };
    const updateRes = await GeneralServices.update_medication_outcome(
      createdId,
      updateData,
    );
    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await GeneralServices.get_medication_outcomes();
    const updated = refreshed.data.find((m) => m.id === createdId);
    expect(updated.is_frequent).toBe(false);
  });

  it("should delete a medication outcome by name", async () => {
    await GeneralServices.create_medication_outcome(medicationOutcome);
    const deleteRes = await GeneralServices.delete_medication_outcome_by_name(
      medicationOutcome.name,
    );
    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await GeneralServices.get_medication_outcomes();
    const stillThere = listRes.data.find(
      (m) => m.name === medicationOutcome.name,
    );
    expect(stillThere).toBeUndefined();
  });

  it("should delete a medication outcome by id", async () => {
    await GeneralServices.create_medication_outcome(medicationOutcome);
    const listRes = await GeneralServices.get_medication_outcomes();
    const found = listRes.data.find((m) => m.name === medicationOutcome.name);
    createdId = found.id;

    const deleteRes =
      await GeneralServices.delete_medication_outcome_by_id(createdId);
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await GeneralServices.get_medication_outcomes();
    const stillThere = refreshed.data.find((m) => m.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});
