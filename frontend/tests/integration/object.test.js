import axios from "axios";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AuthServices } from "../../src/services/authService";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { PatientServices } from "../../src/services/patientServices";
import { ObjectServices } from "../../src/services/objectService";
import { readFileSync } from "fs";

////////////////
// Photos
///////////////
describe("PatientServices.patient photos", () => {
  let createdPatientId;

  const email = "test_attachments@example.com";
  const password = "password123";
  const patientForm = {
    first_name: "Timothy",
    last_name: "Williams",
    dob: "1991-09-05",
    patient_consent: "verbal",
    gender: "Female",
    province: "Ontario",
    disposition: "New Referral",
    age: 32,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "4577898988",
    health_card_version: "AB",
    referral_site: "South Clinic",
    address: "987 Queen Street",
    city: "Toronto",
    postal_code: "M6C 3D4",
    phone1: "416-555-3333",
    email: "eve.williams@example.com",
    language: "English",
  };

  // Read the file from your test fixtures
  const fileName = "test-img.jpeg";
  const filePath = "tests/integration/docs/test-img.jpeg";
  const fileBuffer = readFileSync(filePath);

  // Create a File object (or Blob)
  const file = new File([fileBuffer], fileName, {
    type: "image/jpeg",
  });

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
      await ObjectServices.delete_photo(createdPatientId);
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should upload a patient photo", async () => {
    const result = await ObjectServices.upload_photo(
      createdPatientId,
      fileName,
      file,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Successfully uploaded file.");
  });

  it("should fetch photo in base64 form for a patient", async () => {
    await ObjectServices.upload_photo(createdPatientId, fileName, file);

    const result = await ObjectServices.get_photo_base64(createdPatientId);

    // Compare
    expect(result.success).toBeTruthy();
    expect(result.data?.file.length > 0).toBeTruthy();
    expect(result.data?.type).toBe("JPEG");
    expect(result.data?.name).toBe("test-img.jpeg");
  });

  it("should fetch photo in raw form for a patient", async () => {
    await ObjectServices.upload_photo(createdPatientId, fileName, file);

    const result = await ObjectServices.get_photo_raw(createdPatientId);

    // Convert to buffer
    const downloadedBuffer = Buffer.from(
      result.data,
      result.data instanceof ArrayBuffer ? undefined : "binary",
    );

    // Compare
    expect(result.success).toBeTruthy();
    expect(downloadedBuffer.length).toBe(fileBuffer.length);
    expect(Buffer.compare(downloadedBuffer, fileBuffer)).toBe(0);
  });

  it("fetch photo with no photo", async () => {
    const result = await ObjectServices.get_photo_raw(createdPatientId);

    // Compare
    expect(result.success).toBeFalsy();
    expect(result.status).toBe(404);
    expect(result.message).toBe("Fetching patient photo failed.");
  });

  it("should delete an attachment successfully", async () => {
    await ObjectServices.upload_photo(createdPatientId, fileName, file);

    const deleteRes = await ObjectServices.delete_photo(createdPatientId);
    expect(deleteRes.success).toBe(true);

    const getRes = await ObjectServices.get_photo_raw(createdPatientId);
    expect(getRes.success).toBeFalsy();
    expect(getRes.status).toBe(404);
  });
});

////////////////
// Attachments
///////////////
describe("PatientServices.patient attachments", () => {
  let createdPatientId;

  const email = "test_attachments@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "Billy",
    last_name: "Williams",
    dob: "1991-09-05",
    patient_consent: "verbal",
    gender: "Female",
    province: "Ontario",
    disposition: "New Referral",
    age: 32,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "1234565464",
    health_card_version: "AB",
    referral_site: "South Clinic",
    address: "987 Queen Street",
    city: "Toronto",
    postal_code: "M6C 3D4",
    phone1: "416-555-3333",
    email: "eve.williams@example.com",
    language: "English",
  };

  // Read the file from your test fixtures
  const fileName = "sample.pdf";
  const filePath = "tests/integration/docs/sample.pdf";
  const fileBuffer = readFileSync(filePath);

  // Create a File object (or Blob)
  const file = new File([fileBuffer], fileName, {
    type: "application/pdf",
  });

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
      await ObjectServices.delete_attachment(createdPatientId, fileName);
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should uploadattachment", async () => {
    const result = await ObjectServices.upload_attachment(
      createdPatientId,
      file,
      "Lab Report",
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Attachment uploaded successfully.");
  });

  it("should fetch all attachments for a patient", async () => {
    await ObjectServices.upload_attachment(
      createdPatientId,
      file,
      "Consultation Report",
    );

    // Read the file from your test fixtures
    const newFileName = "test-pdf.pdf";
    const newFilePath = "tests/integration/docs/test-pdf.pdf";
    const newFileBuffer = readFileSync(newFilePath);

    // Create a File object (or Blob)
    const newFile = new File([newFileBuffer], newFileName, {
      type: "application/pdf",
    });

    await ObjectServices.upload_attachment(
      createdPatientId,
      newFile,
      "Lab Report",
    );

    const listRes =
      await ObjectServices.get_attachments_by_patient(createdPatientId);

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);
    expect(listRes.data?.length).toBe(2);

    // cleanup
    await ObjectServices.delete_attachment(createdPatientId, newFileName);
  });

  it("should fetch attachment in raw form", async () => {
    await ObjectServices.upload_attachment(
      createdPatientId,
      file,
      "Consultation Report",
    );

    const result = await ObjectServices.get_attachment_raw(
      createdPatientId,
      fileName,
    );

    // Convert to buffer
    const downloadedBuffer = Buffer.from(
      result.data,
      result.data instanceof ArrayBuffer ? undefined : "binary",
    );

    // Compare
    expect(result.success).toBeTruthy();
    expect(downloadedBuffer.length).toBe(fileBuffer.length);
    expect(Buffer.compare(downloadedBuffer, fileBuffer)).toBe(0);
  });

  it("should delete an attachment successfully", async () => {
    await ObjectServices.upload_attachment(
      createdPatientId,
      file,
      "Consultation Report",
    );

    const deleteRes = await ObjectServices.delete_attachment(
      createdPatientId,
      fileName,
    );
    expect(deleteRes.success).toBe(true);

    const getRes =
      await ObjectServices.get_attachments_by_patient(createdPatientId);
    expect(getRes.success).toBe(true);
    expect(getRes.data?.length).toBe(0);
  });
});
