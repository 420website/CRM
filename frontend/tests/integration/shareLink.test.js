import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { PatientServices } from "../../src/services/patientServices";
import { ShareLinkServices } from "../../src/services/shareLinkService";
import { AuthServices } from "../../src/services/authService";

describe("ShareLinkServices", () => {
  let createdPatientId;
  let createdAttachmentId;

  const email = "test_share_links@example.com";
  const password = "password123";

  const patientForm = {
    first_name: "Eveyy",
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

  const attachmentFormData = {
    type: "PDF",
    filename: "test_document.pdf",
    url: "data:application/pdf;base64,JVBERi0xLjQKJcfs...", // base64 string
    document_type: "Medical Report",
    is_local: true,
    original_url: "data:application/pdf;base64,JVBERi0xLjQKJcfs...",
  };

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

    // Attachment
    const attachmentRes = await PatientServices.create_attachment(
      createdPatientId,
      attachmentFormData,
    );
    createdAttachmentId = attachmentRes.data?.id;
  });

  afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should get share link with a token", async () => {
    const response =
      await ShareLinkServices.get_share_link(createdAttachmentId);

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
    const response =
      await ShareLinkServices.get_share_link(createdAttachmentId);

    const url = response.data?.share_url;
    const token = url.split("token=")[1];

    // test
    const result = await ShareLinkServices.access_link(token);

    // validate
    expect(result.success).toBe(true);
    expect(result.data?.type, attachmentFormData.type);
    expect(result.data?.filename, attachmentFormData.filename);
    expect(result.data?.document_type, attachmentFormData.document_type);
    expect(result.data?.original_url, attachmentFormData.original_url);
    expect(result.data?.url, attachmentFormData.url);
  });

  it("should access share-link invalid successfully", async () => {
    await ShareLinkServices.get_share_link(createdAttachmentId);

    // test
    const result = await ShareLinkServices.access_link("invalid_token");

    // validate
    expect(result.success).toBe(false);
    expect(result.status).toBe(401);
    expect(result.message).toBe("Url has expired.");
  });
});
