import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AuthServices } from "../../src/services/authService";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { UserServices } from "../../src/services/userServices";

////////////////
// Users
///////////////
describe("UserServices.users", () => {
  let createdUserId;
  const email = "test_user89@example.com";
  const password = "password123";

  const userForm = {
    first_name: "Jane",
    last_name: "Doe",
    email: "doe.jane@gmail.com",
    phone_number: "416-555-9999",
    password: "password",
    role: "standard",
    permissions: [],
  };

  beforeEach(async () => {
    // Register & verify (if needed) - optional depending on backend
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
    if (createdUserId) {
      await UserServices.delete_user(createdUserId);
      createdUserId = null;
    }
    await TestServices.deleteUser(email, password);
  });

  it("should create a user successfully", async () => {
    const result = await TestServices.create_user(userForm);
    createdUserId = result.data?.id;

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe(
      "Registration successful. Check your email to verify.",
    );

    // Clean up
    await UserServices.delete_user(result.data?.id);
  });

  it("should fetch users and include created one", async () => {
    const result = await TestServices.create_user(userForm);
    createdUserId = result.data?.id;

    const listRes = await UserServices.get_users();

    expect(listRes.success).toBe(true);
    expect(Array.isArray(listRes.data)).toBe(true);

    const found = listRes.data.find((u) => u.id === createdUserId);
    expect(found).toBeDefined();

    // Clean up
    await UserServices.delete_user(createdUserId);
    createdUserId = null;
  });

  it("should update a user successfully", async () => {
    const result = await TestServices.create_user(userForm);
    createdUserId = result.data?.id;

    const updateData = { phone_number: "416-555-0000" };
    const updateRes = await UserServices.update_user(createdUserId, updateData);
    expect(updateRes.success).toBe(true);

    const listRes = await UserServices.get_users();
    const updated = listRes.data.find((u) => u.id === createdUserId);
    expect(updated.phone_number).toBe("416-555-0000");

    // Clean up
    await UserServices.delete_user(createdUserId);
    createdUserId = null;
  });

  it("should delete a user by ID", async () => {
    const result = await TestServices.create_user(userForm);
    createdUserId = result.data?.id;

    const deleteRes = await UserServices.delete_user(createdUserId);
    expect(deleteRes.success).toBe(true);

    const listRes = await UserServices.get_users();
    const stillThere = listRes.data.find((u) => u.id === createdUserId);
    expect(stillThere).toBeUndefined();

    createdUserId = null;
  });
});
