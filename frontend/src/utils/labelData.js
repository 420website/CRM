import { PatientServices } from "../services/patientServices";

// Format labels data helper function
export const getFormattedLabelsData = (formData) => {
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
    const labelsData = `HCN: ${formData.health_card || ""} ${formData.health_card_version || ""}  Sex: ${formData.gender === "Male" ? "M" : formData.gender === "Female" ? "F" : formData.gender || ""}
${formData.last_name}, ${formData.first_name}
DOB: ${formattedDOB}
${formData.address ? `Address: ${formData.address}` : "Address not available"}
${formData.city || ""}, ${formData.province?.toUpperCase().substring(0, 2) || ""} ${formData.postal_code || ""}
${formData.phone1 ? `Phone: ${formData.phone1}` : "Phone number not available"}
${currentDate} ${currentTime}`;

    return labelsData;
  } catch (error) {
    console.error("Error formatting labels data:", error);
    return "";
  }
};

// Copy form data function with test summary
export const getFormattedCopyData = async (currentRegistrationId, formData) => {
  try {
    // Get fresh test data directly from API
    let currentTests = [];
    console.log(currentRegistrationId);
    if (currentRegistrationId) {
      console.log("tring to get tests");
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

// Copy labels function - Copy to clipboard only
export const copyLabelsData = (formData) => {
  try {
    const labelsData = getFormattedLabelsData(formData);
    if (labelsData) {
      navigator.clipboard.writeText(labelsData);
      alert("✅ Label data copied to clipboard!");
    }
  } catch (error) {
    alert("❌ Error copying label data: " + error.message);
    console.error("Labels copy failed:", error);
  }
};

// Copy form data function with test summary
export const copyFormData = async (currentRegistrationId, formData) => {
  console.log(currentRegistrationId);
  const data = await getFormattedCopyData(currentRegistrationId, formData);
  console.log(data);

  try {
    await navigator.clipboard.writeText(data);
    alert("✅ Client data copied to clipboard!");
    console.log("✅ Copy successful");
  } catch {
    try {
      const textarea = document.createElement("textarea");
      textarea.value = data;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      console.log("✅ Copy fallback succeeded");
    } catch (error) {
      console.error("Copy failed:", error);
      alert("❌ Failed to copy data to clipboard: " + error.message);
    }
  }
};

// // Copy form data function with test summary
// export const copyFormData = async (currentRegistrationId, formData) => {
//   console.log(currentRegistrationId, formData);
//
//   try {
//     // Get fresh test data directly from API
//     let currentTests = [];
//
//     if (currentRegistrationId) {
//       try {
//         const result = await PatientServices.get_tests_by_patient(
//           currentRegistrationId,
//         );
//
//         if (result.success) {
//           currentTests = result.data || [];
//         } else {
//           if (result.status === 400 || result.status === 409) {
//             console.log(result.message || "Error getting tests.");
//           } else {
//             console.log("Error getting tests. Please try again.");
//           }
//         }
//       } catch (error) {
//         console.warn(
//           "⚠️ Error loading test data, proceeding without tests:",
//           error,
//         );
//       }
//     }
//     console.log(currentTests);
//
//     // Format date of birth
//     let formattedDOB = "";
//     if (formData.dob) {
//       // Create date in local timezone to avoid timezone conversion issues
//       const dateParts = formData.dob.split("-");
//       const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]); // year, month (0-indexed), day
//       const months = [
//         "Jan",
//         "Feb",
//         "Mar",
//         "Apr",
//         "May",
//         "Jun",
//         "Jul",
//         "Aug",
//         "Sep",
//         "Oct",
//         "Nov",
//         "Dec",
//       ];
//       formattedDOB = `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
//     }
//     console.log(formattedDOB);
//
//     // Format test summary using fresh data
//     let testSummary = "";
//     if (currentTests && currentTests.length > 0) {
//       testSummary = "\n\nTEST SUMMARY:\n";
//       currentTests.forEach((test, index) => {
//         const testDate = test.test_date
//           ? new Date(test.test_date).toLocaleDateString()
//           : "No date";
//         testSummary += `\nTest ${index + 1} (${testDate}):\n`;
//         testSummary += `Type: ${test.test_type || "Not specified"}\n`;
//
//         if (test.test_type === "HIV" || test.test_type === "Combined") {
//           testSummary += `HIV Result: ${test.hiv_result || "Not specified"}`;
//           if (test.hiv_result === "positive" && test.hiv_type) {
//             testSummary += ` (${test.hiv_type})`;
//           }
//           testSummary += `\nHIV Tester: ${test.hiv_tester || "Not specified"}\n`;
//         }
//
//         if (test.test_type === "HCV" || test.test_type === "Combined") {
//           testSummary += `HCV Result: ${test.hcv_result || "Not specified"}\n`;
//           testSummary += `HCV Tester: ${test.hcv_tester || "Not specified"}\n`;
//         }
//
//         if (test.bloodwork_type) {
//           testSummary += `Bloodwork Type: ${test.bloodwork_type}`;
//           if (test.bloodwork_type === "DBS" && test.bloodwork_circles) {
//             testSummary += ` (${test.bloodwork_circles} circles)`;
//           }
//           testSummary += "\n";
//         }
//       });
//     }
//     console.log(testSummary);
//
//     // Format data with actual form values and test summary
//     const formattedData = `${formData.last_name}, ${formData.first_name}
// ${formattedDOB}
// HCN # ${formData.health_card || ""} ${formData.health_card_version || ""}
// Tel: ${formData.phone1 || ""}
// ${formData.address || ""}
// ${formData.city || ""}, ${formData.province?.toUpperCase().substring(0, 2) || ""}, ${formData.postal_code || ""}
//
// MEDICAL INFORMATION:
// ${formData.summary_template || ""}${testSummary}`;
//
//     console.log(formattedData);
//
//     // Try modern clipboard API first, fallback to legacy method
//     let copySuccess = false;
//
//     // For iOS Safari, we need to use the more compatible approach
//     if (navigator.clipboard && navigator.clipboard.writeText) {
//       try {
//         await navigator.clipboard.writeText(formattedData);
//         copySuccess = true;
//         console.log("✅ Copy successful using modern clipboard API");
//       } catch (error) {
//         console.warn(
//           "⚠️ Modern clipboard API failed, trying fallback method:",
//           error,
//         );
//       }
//     }
//
//     // Enhanced fallback method with better mobile support
//     if (!copySuccess) {
//       try {
//         const textArea = document.createElement("textarea");
//         textArea.value = formattedData;
//         textArea.style.position = "fixed";
//         textArea.style.left = "-999999px";
//         textArea.style.top = "-999999px";
//         textArea.style.opacity = "0";
//         textArea.setAttribute("readonly", "");
//         textArea.setAttribute("contenteditable", "true");
//         document.body.appendChild(textArea);
//
//         // For iOS, we need to handle selection differently
//         if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
//           textArea.contentEditable = true;
//           textArea.readOnly = false;
//           const range = document.createRange();
//           range.selectNodeContents(textArea);
//           const selection = window.getSelection();
//           selection.removeAllRanges();
//           selection.addRange(range);
//           textArea.setSelectionRange(0, 999999);
//         } else {
//           textArea.focus();
//           textArea.select();
//         }
//
//         const successful = document.execCommand("copy");
//         document.body.removeChild(textArea);
//
//         if (successful) {
//           copySuccess = true;
//           console.log("✅ Copy successful using enhanced fallback method");
//         } else {
//           console.error("❌ Enhanced fallback copy method failed");
//         }
//       } catch (error) {
//         console.error("❌ Enhanced fallback copy method error:", error);
//       }
//     }
//
//     if (copySuccess) {
//       alert("✅ Client data copied to clipboard!");
//       console.log("✅ Copy successful:", formattedData);
//     } else {
//       alert(
//         "❌ Failed to copy data to clipboard. Please try again or copy manually.",
//       );
//       console.error("❌ All copy methods failed");
//     }
//   } catch (error) {
//     console.error("Copy failed:", error);
//     alert("❌ Failed to copy data to clipboard: " + error.message);
//   }
// };
