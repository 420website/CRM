import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { WebpageServices } from "../../src/services/webpageService";
import { TestServices } from "../setup";

////////////////
// WebpageServices
///////////////
describe("WebpageServices", () => {
  let createdRegisterId;
  let createdContactId;

  const registerForm = {
    first_name: "Alice",
    last_name: "Johnson",
    dob: "1990-04-15",
    health_card_number: "1234567890AB",
    phone_number: "416-555-1234",
    email: "alice.johnson@example.com",
    consent_given: true,
  };

  const contactForm = {
    first_name: "Bob",
    last_name: "Smith",
    email: "bob.smith@example.com",
    subject: "General Inquiry",
    message: "I have a question about services.",
  };

  beforeEach(async () => {
    if (createdRegisterId) {
      await WebpageServices.delete_register_message(createdRegisterId);
      createdRegisterId = null;
    }

    if (createdContactId) {
      await WebpageServices.delete_contact_message(createdContactId);
      createdContactId = null;
    }
  });

  // -------------------
  // Register tests
  // -------------------
  it("should create a registration successfully", async () => {
    const result = await TestServices.send_register_message(registerForm);

    expect(result.success).toBe(true);

    createdRegisterId = result.data?.registration_id;

    // Clean up
    if (createdRegisterId) {
      await WebpageServices.delete_register_message(createdRegisterId);

      createdRegisterId = null;
    }
  });

  // -------------------
  // Contact tests
  // -------------------
  it("should create a contact message successfully", async () => {
    const result = await TestServices.send_contact_message(contactForm);

    expect(result.success).toBe(true);

    createdContactId = result.data?.contact_id;

    // Clean up
    if (createdContactId) {
      await WebpageServices.delete_contact_message(createdContactId);
      createdContactId = null;
    }
  });
});
