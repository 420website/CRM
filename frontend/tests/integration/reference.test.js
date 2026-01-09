import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AuthServices } from "../../src/services/authService";
import { TestServices } from "../setup";
import { tokenManager } from "../../src/tokenManager";
import { ReferenceServices } from "../../src/services/referenceService";

describe("ReferenceServices.option", () => {
  let createdId;
  const email = "test798@example.com"; // unique user for this suite
  const password = "password123";
  const general = {
    name: "test_general",
    is_frequent: true,
    custom_fields: {},
  };

  const cleanData = async () => {
    const interaction = await ReferenceServices.get_options("interaction");
    const coverage = await ReferenceServices.get_options("coverage");

    const allOptions = [...(interaction.data || []), ...(coverage.data || [])];

    for (const item of allOptions) {
      if (item.name === general.name) {
        await ReferenceServices.delete_option_by_id("all", item.id);
      }
    }
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

    // Clear old
    await cleanData();
  });

  afterEach(async () => {
    // cleanup
    await cleanData();

    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a option successfully", async () => {
    const result = await ReferenceServices.create_option(
      "interaction",
      general,
    );

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Option created successfully.");
  });

  it("should fetch option and include created one", async () => {
    await ReferenceServices.create_option("interaction", general);
    const result = await ReferenceServices.get_options("interaction");

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((g) => g.name === general.name);
    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a options successfully", async () => {
    await ReferenceServices.create_option("coverage", general);
    const listRes = await ReferenceServices.get_options("coverage");
    const found = listRes.data.find((g) => g.name === general.name);
    createdId = found.id;

    const updateData = { is_frequent: false };
    const updateRes = await ReferenceServices.update_option(
      "coverage",
      createdId,
      updateData,
    );
    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await ReferenceServices.get_options("coverage");
    const updated = refreshed.data.find((g) => g.id === createdId);
    expect(updated.is_frequent).toBe(false);
  });

  it("should delete a option by id", async () => {
    await ReferenceServices.create_option("coverage", general);
    const listRes = await ReferenceServices.get_options("coverage");
    const found = listRes.data.find((g) => g.name === general.name);
    createdId = found.id;

    const deleteRes = await ReferenceServices.delete_option_by_id(
      "dispositions",
      createdId,
    );

    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await ReferenceServices.get_options("coverage");
    const stillThere = refreshed.data.find((g) => g.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});

describe("ReferenceServices.templates", () => {
  let createdId;
  const email = "test798@example.com"; // unique user for this suite
  const password = "password123";

  let general = {
    name: "test_template",
    content: "This is the content",
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
    await ReferenceServices.delete_template_by_name("note", general.name);
    await ReferenceServices.delete_template_by_name("clinical", general.name);

    await TestServices.deleteUser(email, password);
    createdId = null;
  });

  it("should create a template successfully", async () => {
    const result = await ReferenceServices.create_template("note", general);

    expect(result.success).toBe(true);
    expect(result.data?.message).toBe("Template created successfully.");
  });

  it("should fetch template and include created one", async () => {
    await ReferenceServices.create_template("clinical", general);
    const result = await ReferenceServices.get_templates("clinical");

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);

    const found = result.data.find((g) => g.name === general.name);
    expect(found).toBeDefined();
    createdId = found.id;
  });

  it("should update a template successfully", async () => {
    await ReferenceServices.create_template("clinical", general);
    const listRes = await ReferenceServices.get_templates("clinical");
    const found = listRes.data.find((g) => g.name === general.name);
    createdId = found.id;

    const updateData = { content: "new content" };
    const updateRes = await ReferenceServices.update_template(
      "clinical",
      createdId,
      updateData,
    );
    expect(updateRes.success).toBe(true);

    // verify change
    const refreshed = await ReferenceServices.get_templates("clinical");
    const updated = refreshed.data.find((g) => g.id === createdId);

    expect(updated.content).toBe("new content");
  });

  it("should delete an template by name", async () => {
    await ReferenceServices.create_template("note", general);
    const deleteRes = await ReferenceServices.delete_template_by_name(
      "note",
      general.name,
    );
    expect(deleteRes.success).toBe(true);

    // verify removal
    const listRes = await ReferenceServices.get_templates("note");
    const stillThere = listRes.data.find((g) => g.name === general.name);
    expect(stillThere).toBeUndefined();
  });

  it("should delete a template by id", async () => {
    await ReferenceServices.create_template("clinical", general);
    const listRes = await ReferenceServices.get_templates("clinical");
    const found = listRes.data.find((g) => g.name === general.name);
    createdId = found.id;

    const deleteRes = await ReferenceServices.delete_template_by_id(
      "clinical",
      createdId,
    );
    expect(deleteRes.success).toBe(true);

    // verify removal
    const refreshed = await ReferenceServices.get_templates("clinical");
    const stillThere = refreshed.data.find((g) => g.id === createdId);
    expect(stillThere).toBeUndefined();
  });
});
