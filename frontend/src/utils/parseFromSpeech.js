// Parse spoken date into YYYY-MM-DD format
export const parseDateFromSpeech = (spokenText) => {
  const text = spokenText.toLowerCase().trim();

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
          const date = new Date(Date.UTC(year, month - 1, day))
            .toISOString()
            .split("T")[0];

          return date;
        }
      } catch (error) {
        console.warn("Error parsing date:", error);
      }
    }
  }

  console.warn("❌ Could not parse date from:", text);
  return null;
};

function capitalize(word) {
  if (!word) return "";
  return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
}

const parseName = (text) => {
  const regex =
    /name\s+(?:is\s+)?([A-Za-zÀ-ÿ\u0100-\u017F]+)\s+([A-Za-zÀ-ÿ\u0100-\u017F]+)/i;

  const result = text.match(regex);
  return result;
};

// Match "born August 3 1990", "dob August 3 1990", or "date of birth August 3 1990"
const parseDob = (text) => {
  const regex =
    /(?:date of birth|dob|born)\s+([a-zA-Z]+\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4})/i;

  const match = text.match(regex);
  if (match) {
    return parseDateFromSpeech(match[1]);
  }

  return null;
};

const parseGender = (text) => {
  if (
    text.includes(" mail ") ||
    text.includes(" male ") ||
    text.includes("man ") ||
    text.includes(" mail") ||
    text.includes(" male")
  ) {
    return "Male";
  } else if (
    text.includes("female") ||
    text.includes("woman") ||
    text.includes("femail")
  ) {
    return "Female";
  }
};

const parseHealthCard = (text) => {
  // Match "health card" optionally followed by "number"
  // Capture digits/spaces/hyphens first, then optional trailing letters
  const regex = /health card(?: number)?\s+([\d\s-]+)\s*([a-zA-Z\s]*)$/i;

  const match = text.match(regex);
  if (!match) return { number: null, version: null };

  // Clean the number: remove spaces and hyphens
  const number = match[1].replace(/[\s-]/g, "");

  // Clean version: remove spaces, make uppercase
  const version = match[2]
    ? match[2].replace(/\s+/g, "").toUpperCase().slice(0, 2)
    : null;

  return { number, version };
};

// Process all fields from voice text
export const parseFields = (text) => {
  const updates = {};

  // Name
  const nameMatch = parseName(text);
  if (nameMatch) {
    updates.first_name = capitalize(nameMatch[1]);
    updates.last_name = capitalize(nameMatch[2]);
  }

  // Dob
  const dobMatch = parseDob(text);
  if (dobMatch) {
    updates.dob = dobMatch;
  }

  // Gender
  const gender = parseGender(text);
  if (gender) {
    updates.gender = gender;
  }

  const healthCard = parseHealthCard(text);
  if (healthCard.number) {
    updates.health_card = healthCard.number;
  }

  if (healthCard.version) {
    updates.health_card_version = healthCard.version;
  }

  // Extract disposition
  if (text.includes("pending")) {
    updates.disposition = "PENDING";
  } else if (text.includes("active")) {
    updates.disposition = "ACTIVE";
  } else if (text.includes("dispensing")) {
    updates.disposition = "DISPENSING";
  } else if (text.includes("delivery")) {
    updates.disposition = "DELIVERY";
  }
  return updates;
};
