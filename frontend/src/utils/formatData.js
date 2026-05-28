export const normalizeFormData = (form) => {
  return Object.fromEntries(
    Object.entries(form).map(([key, value]) => [
      key,
      value === "" ? null : value,
    ]),
  );
};

// Uses local time to calculate
export const calculateAge = (birthDate) => {
  if (!birthDate) return "";

  const today = new Date();
  const [year, month, day] = birthDate.split("-").map(Number);
  const birth = new Date(year, month - 1, day);

  if (birth > today) return "";

  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();

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
