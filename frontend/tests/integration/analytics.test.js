import axios from "axios";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AuthServices } from "../../src/services/authService";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { PatientServices } from "../../src/services/patientServices";
import { ObjectServices } from "../../src/services/objectService";
import { readFileSync } from "fs";
import AdminAnalytics from "../../src/crm/pages/AdminAnalytics";
import { AnalyticsServices } from "../../src/services/analyticsService";

const currentTimestamp = () => {
  const now = new Date();

  // Get timezone offset
  const timezoneOffsetMinutes = now.getTimezoneOffset();
  const offsetSign = timezoneOffsetMinutes > 0 ? "-" : "+";
  const offsetHours = Math.floor(Math.abs(timezoneOffsetMinutes) / 60);
  const offsetMinutes = Math.abs(timezoneOffsetMinutes) % 60;
  const formattedOffset = `${offsetSign}${String(offsetHours).padStart(2, "0")}:${String(offsetMinutes).padStart(2, "0")}`;

  // Format local time as ISO string
  const localISO = now
    .toLocaleString("sv-SE", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      // fractionalSecondDigits: 3,
      hour12: false,
    })
    .replace(" ", "T");

  return `${localISO}${formattedOffset}`;
};

////////////////
// Photos
///////////////
describe.skip("AnalyticsServices", () => {
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

  it("should prompt claude successfully", async () => {
    const request = {
      legacy_data: false,
      message: "How many patients registered today?",
      datetime: currentTimestamp(),
    };

    console.log(request);

    // const response = await AnalyticsServices.prompt_claude(request);
    // console.log(response);
  }, 20000);
});
