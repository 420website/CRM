import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AuthServices } from "../../src/services/authService";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { PatientServices } from "../../src/services/patientServices";
import { VideoServices } from "../../src/services/videoService";

const createUser = async (email, password) => {
  const result = await TestServices.createVerifiedUser(email, password);
  await AuthServices.verify_email(result.data?.token);

  const login_result = await AuthServices.login(email, password);
  tokenManager.setAccessToken(login_result.data?.access_token);

  const mfa_email = await TestServices.send_email_mfa(email);
  const mfa_result = await AuthServices.verify_email_mfa(mfa_email.data?.code);

  return mfa_result.data?.access_token;
};

describe("VideoServices.tests", () => {
  let createdPatientId;
  let token1;
  let token2;

  const password = "password123";
  const email = "test_video@example.com";
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

  beforeEach(async () => {
    token1 = await createUser(email, password);
    token2 = await createUser(email2, password);

    tokenManager.setAccessToken(token1);

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
    await TestServices.deleteUser(email2, password);
  });

  // Internal Join Tests
  it("should create session and join as host", async () => {
    const result = await VideoServices.internalJoinVideo(createdPatientId);
    const data = result.data;

    expect(data).toBeDefined();
    expect(data.access_token).toBeDefined();
    expect(data.expires_at).toBeDefined();
    expect(data.sessionName).toBeDefined();
    expect(data.sessionPasscode).toBeDefined();
    expect(data.sessionName).toContain(createdPatientId.toString());
  });

  it("should join existing session (not as host)", async () => {
    // User 1 creates session
    const result1 = await VideoServices.internalJoinVideo(createdPatientId);
    const user1_data = result1.data;

    // User 2 joins existing session
    tokenManager.setAccessToken(token2);
    const result2 = await VideoServices.internalJoinVideo(createdPatientId);
    const user2_data = result2.data;

    expect(user1_data.sessionName).toBe(user2_data.sessionName);
    expect(user1_data.sessionPasscode).toBe(user2_data.sessionPasscode);
  });

  it("should fail to join locked session as non-host", async () => {
    // User 1 creates and locks session
    await VideoServices.internalJoinVideo(createdPatientId);
    await VideoServices.lockSession(createdPatientId);

    // User 2 tries to join
    tokenManager.setAccessToken(token2);
    const result = await VideoServices.internalJoinVideo(createdPatientId);

    expect(result.success).toBe(false);
    expect(result.message).toContain("locked");
  });

  // External Join Tests
  it("should join session with valid passcode", async () => {
    // Create session first
    const createResult =
      await VideoServices.internalJoinVideo(createdPatientId);
    const passcode = createResult.data.sessionPasscode;

    // Join as external user
    const result = await VideoServices.externalJoinVideo(
      createdPatientId,
      "guest123",
      passcode,
    );

    expect(result.success).toBe(true);
    expect(result.data.access_token).toBeDefined();
    expect(result.data.sessionName).toBeDefined();
    expect(result.data.sessionPasscode).toBe(passcode);
  });

  it("should fail to join with invalid passcode", async () => {
    // Create session first
    await VideoServices.internalJoinVideo(createdPatientId);

    // Try to join with invalid passcode
    const result = await VideoServices.externalJoinVideo(
      createdPatientId,
      "guest123",
      "invalid_passcode",
    );

    expect(result.success).toBe(false);
    expect(result.message).toContain("passcode");
  });

  it("should fail to join locked session", async () => {
    // Create and lock session
    const createResult =
      await VideoServices.internalJoinVideo(createdPatientId);
    const passcode = createResult.data.sessionPasscode;
    await VideoServices.lockSession(createdPatientId);

    // Try to join as external user
    const result = await VideoServices.externalJoinVideo(
      createdPatientId,
      "guest123",
      passcode,
    );

    expect(result.success).toBe(false);
    expect(result.message).toContain("locked");
  });

  it("should fail to join deleted session", async () => {
    // Create session, get passcode, then delete
    const createResult =
      await VideoServices.internalJoinVideo(createdPatientId);
    const passcode = createResult.data.sessionPasscode;
    await VideoServices.deleteSession(createdPatientId);

    // Try to join deleted session
    const result = await VideoServices.externalJoinVideo(
      createdPatientId,
      "guest123",
      passcode,
    );

    expect(result.success).toBe(false);
    expect(result.message).toContain("passcode");
  });

  // Delete Session Tests
  it("should successfully delete session as host", async () => {
    // Create session
    await VideoServices.internalJoinVideo(createdPatientId);

    // Delete session
    const result = await VideoServices.deleteSession(createdPatientId);

    expect(result.success).toBe(true);
    expect(result.data.message).toContain("no longer exists");
  });

  it("should fail to delete session as non-host", async () => {
    // User 1 creates session
    await VideoServices.internalJoinVideo(createdPatientId);

    // User 2 tries to delete
    tokenManager.setAccessToken(token2);
    const result = await VideoServices.deleteSession(createdPatientId);

    expect(result.success).toBe(false);
    expect(result.message).toContain("not the session host");
  });

  it("should fail to delete non-existent session", async () => {
    const result = await VideoServices.deleteSession(createdPatientId);

    expect(result.success).toBe(false);
    expect(result.message).toContain("not found");
  });

  // Lock Session Tests
  it("should successfully lock session as host", async () => {
    // Create session
    await VideoServices.internalJoinVideo(createdPatientId);

    // Lock session
    const result = await VideoServices.lockSession(createdPatientId);

    expect(result.success).toBe(true);
    expect(result.data.message).toContain("locked");
  });

  it("should fail to lock session as non-host", async () => {
    // User 1 creates session
    await VideoServices.internalJoinVideo(createdPatientId);

    // User 2 tries to lock
    tokenManager.setAccessToken(token2);
    const result = await VideoServices.lockSession(createdPatientId);

    expect(result.success).toBe(false);
    expect(result.message).toContain("not the session host");
  });

  it("should fail to lock non-existent session", async () => {
    const result = await VideoServices.lockSession(createdPatientId);

    expect(result.success).toBe(false);
    expect(result.message).toContain("not found");
  });

  // Unlock Session Tests
  it("should successfully unlock session as host", async () => {
    // Create and lock session
    await VideoServices.internalJoinVideo(createdPatientId);
    await VideoServices.lockSession(createdPatientId);

    // Unlock session
    const result = await VideoServices.unlockSession(createdPatientId);

    expect(result.success).toBe(true);
    expect(result.data.message).toContain("unlocked");
  });

  it("should fail to unlock session as non-host", async () => {
    // User 1 creates and locks session
    await VideoServices.internalJoinVideo(createdPatientId);
    await VideoServices.lockSession(createdPatientId);

    // User 2 tries to unlock
    tokenManager.setAccessToken(token2);
    const result = await VideoServices.unlockSession(createdPatientId);

    expect(result.success).toBe(false);
    expect(result.message).toContain("not the session host");
  });

  it("should fail to unlock non-existent session", async () => {
    const result = await VideoServices.unlockSession(createdPatientId);

    expect(result.success).toBe(false);
    expect(result.message).toContain("not found");
  });

  // Integration Tests
  it("should handle full session lifecycle", async () => {
    // Create session
    const createResult =
      await VideoServices.internalJoinVideo(createdPatientId);
    expect(createResult.success).toBe(true);

    // Lock session
    const lockResult = await VideoServices.lockSession(createdPatientId);
    expect(lockResult.success).toBe(true);

    // Unlock session
    const unlockResult = await VideoServices.unlockSession(createdPatientId);
    expect(unlockResult.success).toBe(true);

    // Delete session
    const deleteResult = await VideoServices.deleteSession(createdPatientId);
    expect(deleteResult.success).toBe(true);
  });

  it("should prevent external join after session is locked", async () => {
    // Host creates session
    const createResult =
      await VideoServices.internalJoinVideo(createdPatientId);
    const passcode = createResult.data.sessionPasscode;

    // Lock session
    await VideoServices.lockSession(createdPatientId);

    // External user tries to join
    const joinResult = await VideoServices.externalJoinVideo(
      createdPatientId,
      "guest123",
      passcode,
    );
    expect(joinResult.success).toBe(false);
    expect(joinResult.message).toContain("locked");
  });

  // it("should allow external user to join and sync participants", async () => {
  //   // Host creates session
  //   const createResult =
  //     await VideoServices.internalJoinVideo(createdPatientId);
  //   const passcode = createResult.data.sessionPasscode;
  //
  //   // External user joins
  //   const joinResult = await VideoServices.externalJoinVideo(
  //     createdPatientId,
  //     "guest123",
  //     passcode,
  //   );
  //   expect(joinResult.success).toBe(true);
  //
  //   // Sync participants
  //   const participants = [{ userId: "guest123", userName: "Guest User" }];
  //   const syncResult = await VideoServices.syncParticipants(
  //     createdPatientId,
  //     passcode,
  //     participants,
  //   );
  //   expect(syncResult.success).toBe(true);
  // });
  //
  // // Sync Participants Tests
  //   it("should successfully sync participants with valid session key", async () => {
  //     // Create session
  //     const createResult =
  //       await VideoServices.internalJoinVideo(createdPatientId);
  //     const passcode = createResult.data.sessionPasscode;
  //
  //     // Sync participants
  //     const participants = [
  //       { userId: "user1", userName: "Test User 1" },
  //       { userId: "user2", userName: "Test User 2" },
  //     ];
  //
  //     const result = await VideoServices.syncParticipants(
  //       createdPatientId,
  //       passcode,
  //       participants,
  //     );
  //
  //     expect(result.success).toBe(true);
  //   });
  //
  //   it("should fail to sync with invalid session key", async () => {
  //     // Create session
  //     await VideoServices.internalJoinVideo(createdPatientId);
  //
  //     // Try to sync with invalid key
  //     const participants = [{ userId: "user1", userName: "Test User 1" }];
  //
  //     const result = await VideoServices.syncParticipants(
  //       createdPatientId,
  //       "invalid_key",
  //       participants,
  //     );
  //
  //     expect(result.success).toBe(false);
  //     expect(result.error).toContain("session key");
  //   });
  //
  //   it("should fail to sync for non-existent session", async () => {
  //     const participants = [{ userId: "user1", userName: "Test User 1" }];
  //
  //     const result = await VideoServices.syncParticipants(
  //       createdPatientId,
  //       "any_key",
  //       participants,
  //     );
  //
  //     expect(result.success).toBe(false);
  //     expect(result.error).toContain("not found");
  //   });
});
