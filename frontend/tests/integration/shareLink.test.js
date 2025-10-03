import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { PatientServices } from "../../src/services/patientServices";
import { ShareLinkServices } from "../../src/services/shareLinkService";
import { AuthServices } from "../../src/services/authService";
import { ObjectServices } from "../../src/services/objectService";
import { readFileSync } from "fs";

describe("ShareLinkServices", () => {
  let createdPatientId;
  const fileName = "sample.pdf";
  const filePath = "tests/integration/docs/sample.pdf";
  const email = "test_share_links@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "Atom",
    last_name: "Williams",
    dob: "1991-09-05",
    patient_consent: "verbal",
    gender: "Female",
    province: "Ontario",
    disposition: "New Referral",
    age: 32,
    reg_date: new Date().toISOString().split("T")[0],
    health_card: "0000000000",
    health_card_version: "AB",
    referral_site: "South Clinic",
    address: "987 Queen Street",
    city: "Toronto",
    postal_code: "M6C 3D4",
    phone1: "416-555-3333",
    email: "eve.williams@example.com",
    language: "English",
  };

  // Create a File object (or Blob)
  const fileBuffer = readFileSync(filePath);
  const file = new File([fileBuffer], fileName, {
    type: "application/pdf",
  });

  beforeEach(async () => {
    // Register + login + MFA
    await TestServices.createVerifiedUser(email, password);
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

    await ObjectServices.upload_attachment(
      createdPatientId,
      file,
      "Lab Report",
    );
  });

  afterEach(async () => {
    if (createdPatientId) {
      await ObjectServices.delete_attachment(createdPatientId, fileName);
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should get share link with a token", async () => {
    const attachments =
      await ObjectServices.get_attachments_by_patient(createdPatientId);

    const attachment = attachments.data[0];
    const attachmentId = attachment.id;

    // Test
    const response = await ShareLinkServices.get_share_link(attachmentId);

    expect(response.success).toBe(true);
    expect(response.data?.share_url).toBeTruthy();
  });

  it("should get attachment non-existant error", async () => {
    const response = await ShareLinkServices.get_share_link(-1);

    expect(response.success).toBe(false);
    expect(response.status).toBe(404);
    expect(response.message).toBe("Attachment not found.");
  });

  it("should access share-link successfully", async () => {
    const attachments =
      await ObjectServices.get_attachments_by_patient(createdPatientId);

    const attachment = attachments.data[0];
    const attachmentId = attachment.id;

    const response = await ShareLinkServices.get_share_link(attachmentId);

    const url = response.data?.share_url;
    const token = url.split("token=")[1];

    // test
    const result = await ShareLinkServices.access_link(token);

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

  it("should access share-link invalid successfully", async () => {
    const attachments =
      await ObjectServices.get_attachments_by_patient(createdPatientId);

    const attachment = attachments.data[0];
    const attachmentId = attachment.id;
    await ShareLinkServices.get_share_link(attachmentId);

    // test
    const result = await ShareLinkServices.access_link("invalid_token");

    // validate
    expect(result.success).toBe(false);
    expect(result.status).toBe(401);
  });
});
