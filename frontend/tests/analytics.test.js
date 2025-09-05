import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { AnalyticsServices } from "../../src/services/analyticsService";
import fs from "fs";
import FormData from "form-data";

// describe("AnalyticsServices.upload-legacy-data", () => {
//   it("register_successful", async () => {
//     const formData = new FormData();
//     formData.append("file", fs.createReadStream("tests/test_data.csv")); // "test_data.csv");
//
//     // Test
//     const result = await AnalyticsServices.upload_legacy_data(formData);
//
//     expect(result.success).toBe(true);
//     expect(result.status).toBe(200);
//   });
//
//   // it("register_unsuccessful (bad file)", async () => {
//   //   const formData = new FormData();
//   //   formData.append("file", Buffer.from("not a csv"), "bad.txt");
//   //
//   //   const result = await AnalyticsServices.upload_legacy_data(formData);
//   //
//   //   expect(result.success).toBe(false);
//   //   expect([400, 422]).toContain(result.status);
//   // });
// });
