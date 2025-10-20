import { PatientServices } from "../services/patientServices";
import toast from "react-hot-toast";

export const copyLabelsData = async (formData) => {
  const labelsData = getFormattedLabelsData(formData);
  if (labelsData) {
    try {
      await navigator.clipboard.writeText(labelsData);
      toast.success("Label data copied to clipboard!");
    } catch (error) {
      toast.error("Error copying label data: " + error.message);
    }
  }
};

// ClipboardItem is required for safari to work with the async calls
export const copyFormData = async (currentRegistrationId, formData) => {
  try {
    const item = new ClipboardItem({
      "text/plain": new Promise(async (resolve) => {
        const data = await getFormattedCopyData(
          currentRegistrationId,
          formData,
        );
        resolve(new Blob([data], { type: "text/plain" }));
      }),
    });

    await navigator.clipboard.write([item]);
    toast.success("Client data copied to clipboard!");
  } catch (error) {
    toast.error("Failed to copy data to clipboard: " + error.message);
  }
};

// Format helper functions
const getFormattedLabelsData = (formData) => {
  try {
    // Format date of birth for labels (YYYY-MM-DD format)
    let formattedDOB = "";
    if (formData.dob) {
      // Create date in local timezone to avoid timezone conversion issues
      const dateParts = formData.dob.split("-");
      const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]); // year, month (0-indexed), day
      const month = (date.getMonth() + 1).toString().padStart(2, "0");
      const day = date.getDate().toString().padStart(2, "0");
      const year = date.getFullYear();
      formattedDOB = `${year}-${month}-${day}`;
    }

    // Get current date and time
    const now = new Date();
    const currentMonth = (now.getMonth() + 1).toString().padStart(2, "0");
    const currentDay = now.getDate().toString().padStart(2, "0");
    const currentYear = now.getFullYear();
    const currentDate = `${currentYear}-${currentMonth}-${currentDay}`;
    const currentTime = now.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });

    // Format labels data
    //NOTE: Cannot start with 'WORD:' becauyse it gets encoded liek http: and messes up text on past anywhere but browser
    const labelsData = `LABEL\nHCN: ${formData.health_card || ""} ${formData.health_card_version || ""} Sex: ${formData.gender === "Male" ? "M" : formData.gender === "Female" ? "F" : formData.gender || ""}\n${formData.last_name}, ${formData.first_name}\nDOB: ${formattedDOB}\n${formData.address ? `Address: ${formData.address}` : "Address not available"}\n${formData.city || ""}, ${formData.province?.toUpperCase().substring(0, 2) || ""} ${formData.postal_code || ""}\n${formData.phone1 ? `Phone: ${formData.phone1}` : "Phone number not available"}\n${currentDate} ${currentTime}`;

    return labelsData;
  } catch (error) {
    console.error("Error formatting labels data:", error);
    return "";
  }
};

// Copy form data function with test summary
const getFormattedCopyData = async (currentRegistrationId, formData) => {
  try {
    // Get fresh test data directly from API
    let currentTests = [];
    if (currentRegistrationId) {
      try {
        const result = await PatientServices.get_tests_by_patient(
          currentRegistrationId,
        );

        if (result.success) {
          currentTests = result.data || [];
        } else {
          if (result.status === 400 || result.status === 409) {
            console.log(result.message || "Error getting tests.");
          } else {
            console.log("Error getting tests. Please try again.");
          }
        }
      } catch (error) {
        console.warn(
          "⚠️ Error loading test data, proceeding without tests:",
          error,
        );
      }
    }

    // Format date of birth
    let formattedDOB = "";
    if (formData.dob) {
      // Create date in local timezone to avoid timezone conversion issues
      const dateParts = formData.dob.split("-");
      const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]); // year, month (0-indexed), day
      const months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ];
      formattedDOB = `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
    }

    // Format test summary using fresh data
    let testSummary = "";
    if (currentTests && currentTests.length > 0) {
      testSummary = "\n\nTEST SUMMARY:\n";
      currentTests.forEach((test, index) => {
        const testDate = test.test_date
          ? new Date(test.test_date).toLocaleDateString()
          : "No date";
        testSummary += `\nTest ${index + 1} (${testDate}):\n`;
        testSummary += `Type: ${test.test_type || "Not specified"}\n`;

        if (test.test_type === "HIV" || test.test_type === "Combined") {
          testSummary += `HIV Result: ${test.hiv_result || "Not specified"}`;
          if (test.hiv_result === "positive" && test.hiv_type) {
            testSummary += ` (${test.hiv_type})`;
          }
          testSummary += `\nHIV Tester: ${test.hiv_tester || "Not specified"}\n`;
        }

        if (test.test_type === "HCV" || test.test_type === "Combined") {
          testSummary += `HCV Result: ${test.hcv_result || "Not specified"}\n`;
          testSummary += `HCV Tester: ${test.hcv_tester || "Not specified"}\n`;
        }

        if (test.bloodwork_type) {
          testSummary += `Bloodwork Type: ${test.bloodwork_type}`;
          if (test.bloodwork_type === "DBS" && test.bloodwork_circles) {
            testSummary += ` (${test.bloodwork_circles} circles)`;
          }
          testSummary += "\n";
        }
      });
    }

    // Format data with actual form values and test summary
    const formattedData = `${formData.last_name}, ${formData.first_name}
${formattedDOB}
HCN # ${formData.health_card || ""} ${formData.health_card_version || ""}
Tel: ${formData.phone1 || ""}
${formData.address || ""}
${formData.city || ""}, ${formData.province?.toUpperCase().substring(0, 2) || ""}, ${formData.postal_code || ""}

MEDICAL INFORMATION:
${formData.summary_template || ""}${testSummary}`;

    return formattedData;
  } catch (error) {
    console.error("Error formatting labels data:", error);
    return "";
  }
};
