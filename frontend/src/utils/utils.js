export const calculateAge = (birthDate) => {
  if (!birthDate) return "";

  const today = new Date();
  const birth = new Date(birthDate);

  // Check if birth date is in the future
  if (birth > today) return "";

  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();

  // Adjust age if birthday hasn't occurred yet this year
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }

  return age.toString();
};

export const formatPhoneNumber = (value) => {
  // Remove all non-digits
  const phoneNumber = value.replace(/\D/g, "");

  // Limit to 10 digits
  const limitedPhoneNumber = phoneNumber.substring(0, 10);

  // Format based on length
  if (limitedPhoneNumber.length === 0) {
    return "";
  } else if (limitedPhoneNumber.length <= 3) {
    return `(${limitedPhoneNumber}`;
  } else if (limitedPhoneNumber.length <= 6) {
    return `(${limitedPhoneNumber.substring(0, 3)}) ${limitedPhoneNumber.substring(3)}`;
  } else {
    return `(${limitedPhoneNumber.substring(0, 3)}) ${limitedPhoneNumber.substring(3, 6)}-${limitedPhoneNumber.substring(6)}`;
  }
};

// Postal code formatting function (Canadian format: A1A 1A1)
// Format postal code to Canadian format (A1A 1A1)
export const formatPostalCode = (postalCode) => {
  if (!postalCode) return "";

  // Remove all non-alphanumeric characters and convert to uppercase
  const cleaned = postalCode.replace(/[^A-Za-z0-9]/g, "").toUpperCase();

  // Limit to 6 characters
  const limitedPostalCode = cleaned.substring(0, 6);

  // Format based on length
  if (limitedPostalCode.length === 0) {
    return "";
  } else if (limitedPostalCode.length <= 3) {
    return limitedPostalCode;
  } else {
    return `${limitedPostalCode.substring(0, 3)} ${limitedPostalCode.substring(3)}`;
  }
};

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

// Parse spoken date into YYYY-MM-DD format
export const parseDateFromSpeech = (spokenText) => {
  const text = spokenText.toLowerCase().trim();
  console.log("🎤 Parsing spoken date:", text);

  // Common date patterns people might say
  const patterns = [
    // "January 15th 2024", "January 15 2024"
    /(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})/,
    // "15th of January 2024", "15 of January 2024"
    /(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(\w+)\s+(\d{4})/,
    // "1/15/2024", "01/15/2024"
    /(\d{1,2})\/(\d{1,2})\/(\d{4})/,
    // "2024-01-15"
    /(\d{4})-(\d{1,2})-(\d{1,2})/,
    // "January 2024" (assume 1st)
    /(\w+)\s+(\d{4})/,
    // "today", "yesterday", "tomorrow"
    /(today|yesterday|tomorrow)/,
    // "15th" (assume current month/year)
    /(\d{1,2})(?:st|nd|rd|th)?$/,
  ];

  const months = {
    january: "01",
    jan: "01",
    february: "02",
    feb: "02",
    march: "03",
    mar: "03",
    april: "04",
    apr: "04",
    may: "05",
    june: "06",
    jun: "06",
    july: "07",
    jul: "07",
    august: "08",
    aug: "08",
    september: "09",
    sep: "09",
    october: "10",
    oct: "10",
    november: "11",
    nov: "11",
    december: "12",
    dec: "12",
  };

  const today = new Date();

  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      try {
        let year, month, day;

        // Pattern 1: "January 15th 2024"
        if (pattern === patterns[0]) {
          const monthName = match[1].toLowerCase();
          month = months[monthName];
          day = match[2].padStart(2, "0");
          year = match[3];
        }
        // Pattern 2: "15th of January 2024"
        else if (pattern === patterns[1]) {
          day = match[1].padStart(2, "0");
          const monthName = match[2].toLowerCase();
          month = months[monthName];
          year = match[3];
        }
        // Pattern 3: "1/15/2024" (MM/DD/YYYY)
        else if (pattern === patterns[2]) {
          month = match[1].padStart(2, "0");
          day = match[2].padStart(2, "0");
          year = match[3];
        }
        // Pattern 4: "2024-01-15" (already in correct format)
        else if (pattern === patterns[3]) {
          year = match[1];
          month = match[2].padStart(2, "0");
          day = match[3].padStart(2, "0");
        }
        // Pattern 5: "January 2024" (assume 1st)
        else if (pattern === patterns[4]) {
          const monthName = match[1].toLowerCase();
          month = months[monthName];
          day = "01";
          year = match[2];
        }
        // Pattern 6: "today", "yesterday", "tomorrow"
        else if (pattern === patterns[5]) {
          const relativeDate = new Date();
          if (match[1] === "yesterday") {
            relativeDate.setDate(today.getDate() - 1);
          } else if (match[1] === "tomorrow") {
            relativeDate.setDate(today.getDate() + 1);
          }
          year = relativeDate.getFullYear().toString();
          month = (relativeDate.getMonth() + 1).toString().padStart(2, "0");
          day = relativeDate.getDate().toString().padStart(2, "0");
        }
        // Pattern 7: "15th" (current month/year)
        else if (pattern === patterns[6]) {
          day = match[1].padStart(2, "0");
          month = (today.getMonth() + 1).toString().padStart(2, "0");
          year = today.getFullYear().toString();
        }

        if (year && month && day) {
          const parsedDate = `${year}-${month}-${day}`;
          console.log("✅ Parsed date:", parsedDate);

          // Validate the date
          const dateObj = new Date(parsedDate);
          if (
            !isNaN(dateObj.getTime()) &&
            dateObj.getFullYear() == year &&
            dateObj.getMonth() + 1 == parseInt(month) &&
            dateObj.getDate() == parseInt(day)
          ) {
            return parsedDate;
          }
        }
      } catch (error) {
        console.warn("Error parsing date:", error);
      }
    }
  }

  console.warn("❌ Could not parse date from:", text);
  return null;
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
  try {
    // Debug information
    console.log("🔄 Copy button clicked");
    console.log("📋 Current Registration ID:", currentRegistrationId);

    // Get fresh test data directly from API
    let currentTests = [];
    if (currentRegistrationId) {
      console.log("🔄 Fetching fresh test data...");
      try {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/admin-registration/${currentRegistrationId}/tests`,
        );
        if (response.ok) {
          const data = await response.json();
          currentTests = data.tests || [];
          console.log("✅ Fresh test data loaded:", currentTests);
        } else {
          console.warn("⚠️ Failed to load test data, proceeding without tests");
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
      console.log("✅ Including test summary in copy");
      testSummary = "\n\nTEST SUMMARY:\n";
      currentTests.forEach((test, index) => {
        console.log(`📝 Processing test ${index + 1}:`, test);
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
    } else {
      console.log("⚠️ No test data available for copy");
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

    // Try modern clipboard API first, fallback to legacy method
    let copySuccess = false;

    // For iOS Safari, we need to use the more compatible approach
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(formattedData);
        copySuccess = true;
        console.log("✅ Copy successful using modern clipboard API");
      } catch (error) {
        console.warn(
          "⚠️ Modern clipboard API failed, trying fallback method:",
          error,
        );
      }
    }

    // Enhanced fallback method with better mobile support
    if (!copySuccess) {
      try {
        const textArea = document.createElement("textarea");
        textArea.value = formattedData;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        textArea.style.opacity = "0";
        textArea.setAttribute("readonly", "");
        textArea.setAttribute("contenteditable", "true");
        document.body.appendChild(textArea);

        // For iOS, we need to handle selection differently
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
          textArea.contentEditable = true;
          textArea.readOnly = false;
          const range = document.createRange();
          range.selectNodeContents(textArea);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          textArea.setSelectionRange(0, 999999);
        } else {
          textArea.focus();
          textArea.select();
        }

        const successful = document.execCommand("copy");
        document.body.removeChild(textArea);

        if (successful) {
          copySuccess = true;
          console.log("✅ Copy successful using enhanced fallback method");
        } else {
          console.error("❌ Enhanced fallback copy method failed");
        }
      } catch (error) {
        console.error("❌ Enhanced fallback copy method error:", error);
      }
    }

    if (copySuccess) {
      alert("✅ Client data copied to clipboard!");
      console.log("✅ Copy successful:", formattedData);
    } else {
      alert(
        "❌ Failed to copy data to clipboard. Please try again or copy manually.",
      );
      console.error("❌ All copy methods failed");
    }
  } catch (error) {
    console.error("Copy failed:", error);
    alert("❌ Failed to copy data to clipboard: " + error.message);
  }
};

export const compressImage = (file, maxSizeKB = 800) => {
  return new Promise((resolve) => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      // Calculate new dimensions (increased max resolution for better quality)
      let { width, height } = img;
      const maxWidth = 1200; // Increased from 800
      const maxHeight = 1600; // Increased from 600

      // Only resize if image is larger than max dimensions
      if (width > maxWidth || height > maxHeight) {
        if (width > height) {
          if (width > maxWidth) {
            height = height * (maxWidth / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = width * (maxHeight / height);
            height = maxHeight;
          }
        }
      }

      canvas.width = width;
      canvas.height = height;

      // Draw and compress with higher quality settings
      ctx.drawImage(img, 0, 0, width, height);

      // Start with higher quality and reduce if needed
      let quality = 0.92; // Increased from 0.8 for better quality
      let compressedDataUrl;

      do {
        compressedDataUrl = canvas.toDataURL("image/jpeg", quality);
        quality -= 0.05; // Smaller steps for more gradual quality reduction
      } while (
        compressedDataUrl.length > maxSizeKB * 1024 * 1.37 &&
        quality > 0.3
      ); // Reduced minimum quality from 0.1 to 0.3

      resolve(compressedDataUrl);
    };

    img.src = URL.createObjectURL(file);
  });
};
