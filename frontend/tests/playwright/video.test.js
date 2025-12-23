import { chromium, test, expect } from "@playwright/test";
import { VideoServices } from "../../src/services/videoService";
import { PatientServices } from "../../src/services/patientServices";
import jwt from "jsonwebtoken";
import { TestServices } from "../setup";
import { AuthServices } from "../../src/services/authService";
import { tokenManager } from "../../src/tokenManager";

const password = "password123";
const email1 = "test_video@example.com";
const email2 = "test_video2@example.com";

const patientForm = {
  first_name: "David",
  last_name: "Mup",
  dob: "1982-11-10",
  patient_consent: "verbal",
  gender: "Male",
  province: "Ontario",
  disposition: "New Referral",
  age: 41,
  reg_date: new Date().toISOString().split("T")[0],
  health_card: "0000000000",
  health_card_version: "AB",
  referral_site: "Central Clinic",
  address: "123 King Street",
  city: "Toronto",
  postal_code: "M1B 2C3",
  phone1: "416-555-1111",
  email: "david.miller@example.com",
  language: "English",
};

async function initZoomClient(page) {
  await page.waitForSelector("#initButton");
  await page.click("#initButton");
  await page.waitForFunction(() => window.__zoomClient !== undefined, {
    timeout: 10000,
  });
}

async function joinZoomSession(page, sessionName, sessionKey, accessToken) {
  await page.fill("#sessionName", sessionName);
  await page.fill("#sessionKey", sessionKey);
  await page.fill("#accessToken", accessToken);
  await page.click("#joinButton");
  await page.waitForFunction(() => window.__zoomJoined !== undefined, {
    timeout: 10000,
  });
}

function generateZoomJWT(apiKey, apiSecret, expiresInSeconds = 60) {
  const payload = {
    iss: apiKey,
    exp: Math.floor(Date.now() / 1000) + expiresInSeconds,
  };

  return jwt.sign(payload, apiSecret);
}

async function listSessions() {
  // Call Zoom REST API directly from Node
  const apiKey = process.env.ZOOM_API_KEY;
  const apiSecret = process.env.ZOOM_API_SECRET;

  // Use JWT or OAuth token
  const token = generateZoomJWT(apiKey, apiSecret); // Implement JWT generation

  const res = await fetch(
    "https://api.zoom.us/v2/videosdk/sessions", // or list sessions endpoint
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  const data = await res.json();
  return data;
}

const createUser = async (email, password) => {
  const result = await TestServices.createVerifiedUser(email, password);
  await AuthServices.verify_email(result.data?.token);

  const login_result = await AuthServices.login(email, password);
  tokenManager.setAccessToken(login_result.data?.access_token);

  const mfa_email = await TestServices.send_email_mfa(email);
  const mfa_result = await AuthServices.verify_email_mfa(mfa_email.data?.code);

  return mfa_result.data?.access_token;
};

// --- Full Playwright test for Zoom SDK (headless-friendly) ---
test.describe("Zoom SDK initializes (headless-safe)", () => {
  let createdPatientId;
  let token1;
  let token2;
  let browser;
  let page;
  const zoom_ui = process.env.ZOOM_CLIENT_URL;

  test.beforeEach(async () => {
    token1 = await createUser(email1, password);
    token2 = await createUser(email2, password);
    tokenManager.setAccessToken(token1);

    const patientRes = await PatientServices.create_patient(patientForm);
    createdPatientId = patientRes.data?.patient_id;

    browser = await chromium.launch({ headless: true });
    page = await browser.newPage();

    // Capture all console logs from the page
    page.on("console", (msg) => {
      console.log(`[BROWSER ${msg.type()}]:`, msg.text());
    });

    // Capture page errors
    page.on("pageerror", (error) => {
      console.log("[BROWSER ERROR]:", error.message);
    });

    await page.goto(zoom_ui);
  });

  test.afterEach(async () => {
    if (createdPatientId) {
      await PatientServices.delete_patient_by_id(createdPatientId);
      createdPatientId = null;
    }

    await browser.close();
  });

  test("should fill Zoom session fields and join", async () => {
    const result = await VideoServices.internalJoinVideo(createdPatientId);
    console.log(result.data);
    const sessionName = result.data.sessionName;

    await initZoomClient(page);
    await joinZoomSession(
      page,
      result.data.sessionName,
      result.data.sessionPasscode,
      result.data.access_token,
    );

    await page.waitForFunction(() => window.__userAdded !== undefined, {
      timeout: 10000,
    });

    const result2 = await VideoServices.internalJoinVideo(createdPatientId);
    console.log(result2.data);

    const sessions_result = await listSessions();
    console.log(sessions_result);

    expect(result.data.access_token).toBeDefined();
    expect(result.data.sessionName).toContain(createdPatientId.toString());
  });
});
