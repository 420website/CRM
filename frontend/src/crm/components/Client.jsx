import { useState } from "react";
import AddressAutocomplete from "./AddressAutocomplete";
import {
  calculateAge,
  formatPhoneNumber,
  formatPostalCode,
} from "../../utils/formatData";
import DatePicker from "../ui/DatePicker";
import { useAuth } from "../../context/AuthContext";
import { PhoneCall } from "lucide-react";
import { useReferences } from "../../context/ReferenceContext";
import OptionManager from "../managers/OptionManager";
import TemplateManager from "../managers/TemplateManager";

// Map Google Places province codes to full province names
const getProvince = (code) => {
  const provinceMap = {
    ON: "Ontario",
    QC: "Quebec",
    BC: "British Columbia",
    AB: "Alberta",
    MB: "Manitoba",
    SK: "Saskatchewan",
    NS: "Nova Scotia",
    NB: "New Brunswick",
    NL: "Newfoundland and Labrador",
    PE: "Prince Edward Island",
    NT: "Northwest Territories",
    NU: "Nunavut",
    YT: "Yukon",
  };

  return provinceMap[code] || code;
};

export default function Client({
  formData,
  setFormData,
  selectedTemplate,
  setSelectedTemplate,
  openVoiceDateInput,
  openVoiceFillInput,
}) {
  const { userRole } = useAuth();
  const [error, setError] = useState("");
  const { setShowManager, showManager, options, templates } = useReferences();

  const defaultPositiveClinicalSummary = async (formData) => {
    const baseTemplate = "Dx 10+ years ago and treated. ";

    let rnaSection = "";
    if (formData.rna_available === "No") {
      rnaSection = "RNA - no labs available. ";
    } else if (formData.rna_available === "Yes") {
      const date = formData.rna_sample_date
        ? formData.rna_sample_date
        : "[date]";
      const result = formData.rna_result
        ? formData.rna_result.toLowerCase()
        : "positive";
      rnaSection = `RNA - ${date}, ${result}. `;
    }

    const middleTemplate =
      "However, has had ongoing risk factors with sharing pipes and straws. Counselled regarding risk factors. Point of care test was completed for HCV and tested positive at approximately two minutes with a dark line. HIV testing came back negative. Collected a DBS specimen and advised that it will take approximately 7 to 10 days for results. ";

    let coverageSection = "";
    if (formData.coverage_type && formData.coverage_type !== "Select") {
      coverageSection = `Coverage Type: ${formData.coverage_type}. `;
    } else {
      coverageSection = `Coverage Type: not selected. `;
    }

    let referralSection = "";
    if (formData.referral_person && formData.referral_person.trim() !== "") {
      referralSection = `Referral: ${formData.referral_person}. `;
    } else {
      referralSection = "Referral: none. ";
    }

    // Dynamic address/phone section based on client data
    const hasAddress = formData.address && formData.address.trim() !== "";
    const hasPhone = formData.phone1 && formData.phone1.trim() !== "";

    let endTemplate = "";
    if (hasAddress && hasPhone) {
      endTemplate =
        "Client does have a valid address and has also provided a phone number for results.";
    } else if (hasAddress && !hasPhone) {
      endTemplate =
        "Client does have a valid address but no phone number for results.";
    } else if (!hasAddress && hasPhone) {
      endTemplate =
        "Client does not have a valid address but has provided a phone number for results.";
    } else {
      endTemplate =
        "Client does not have a valid address or phone number for results.";
    }

    return (
      baseTemplate +
      rnaSection +
      middleTemplate +
      coverageSection +
      referralSection +
      endTemplate
    );
  };

  const updateClinicalSummary = async (formData) => {
    if (
      formData.selected_template === "Positive" &&
      formData.summary_template
    ) {
      let updatedSummary = formData.summary_template;

      // Update RNA section ONLY if it exists
      const rnaRegex = /RNA - ([^,]+), ([^.]+)\.|RNA - no labs available\./;
      if (rnaRegex.test(updatedSummary)) {
        if (formData.rna_available === "No") {
          updatedSummary = updatedSummary.replace(
            rnaRegex,
            "RNA - no labs available.",
          );
        } else if (formData.rna_available === "Yes") {
          const date = formData.rna_sample_date || "[date]";
          const result = formData.rna_result?.toLowerCase() || "positive";
          updatedSummary = updatedSummary.replace(
            rnaRegex,
            `RNA - ${date}, ${result}.`,
          );
        }
      }

      // Update coverage ONLY if it exists
      const coverageRegex = /Coverage Type: [^.]+\./;
      if (coverageRegex.test(updatedSummary)) {
        const newCoverage =
          formData.coverage_type && formData.coverage_type !== "Select"
            ? `Coverage Type: ${formData.coverage_type}.`
            : "Coverage Type: not selected.";
        updatedSummary = updatedSummary.replace(coverageRegex, newCoverage);
      }

      // Update referral ONLY if it exists
      const referralRegex = /Referral: [^.]+\./;
      if (referralRegex.test(updatedSummary)) {
        const newReferral = formData.referral_person?.trim()
          ? `Referral: ${formData.referral_person}.`
          : "Referral: none.";
        updatedSummary = updatedSummary.replace(referralRegex, newReferral);
      }

      // Update address/phone ONLY if it exists
      const addressPhoneRegex = /Client does.*?results\./;
      if (addressPhoneRegex.test(updatedSummary)) {
        const hasAddress = formData.address?.trim();
        const hasPhone = formData.phone1?.trim();
        let newEndTemplate = "";
        if (hasAddress && hasPhone) {
          newEndTemplate =
            "Client does have a valid address and has also provided a phone number for results.";
        } else if (hasAddress) {
          newEndTemplate =
            "Client does have a valid address but no phone number for results.";
        } else if (hasPhone) {
          newEndTemplate =
            "Client does not have a valid address but has provided a phone number for results.";
        } else {
          newEndTemplate =
            "Client does not have a valid address or phone number for results.";
        }
        updatedSummary = updatedSummary.replace(
          addressPhoneRegex,
          newEndTemplate,
        );
      }

      return updatedSummary;
    } else {
      return defaultPositiveClinicalSummary(formData);
    }
  };

  const handleTemplateChange = async (templateName) => {
    setSelectedTemplate(templateName);

    if (templateName === "Select") {
      setFormData((prev) => ({
        ...prev,
        summary_template: "",
        selected_template: "",
      }));
    } else if (templateName === "Positive") {
      const dynamicTemplate = await updateClinicalSummary(formData);

      setFormData((prev) => ({
        ...prev,
        summary_template: dynamicTemplate,
        selected_template: templateName,
      }));
    } else {
      const content =
        templates["clinical"].find((item) => item.name === templateName)
          ?.content || "";

      setFormData((prev) => ({
        ...prev,
        summary_template: content,
        selected_template: templateName,
      }));
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    let processedValue = type === "checkbox" ? checked : value;

    if (name === "phone1" || name === "phone2") {
      processedValue = formatPhoneNumber(value);
    }

    // Health card should only contain numeric characters
    if (name === "health_card") {
      processedValue = value.replace(/\D/g, "");
    }

    let newFormData = {
      ...formData,
      [name]: processedValue,
    };

    // Update clinical summary ONLY if user has explicitly selected Positive template
    if (
      selectedTemplate === "Positive" &&
      (name === "rna_available" ||
        name === "rna_sample_date" ||
        name === "rna_result" ||
        name === "coverage_type" ||
        name === "referral_person" ||
        name === "address" ||
        name === "phone1")
    ) {
      setFormData(newFormData);
      updateClinicalSummary(newFormData)
        .then((template) => {
          setFormData((prev) => ({
            ...prev,
            summary_template: template,
          }));
        })
        .catch((error) => {
          setError("Error updating clinical summary:", error);
        });
    } else {
      setFormData(newFormData);
    }

    // If DOB is changed, automatically calculate and update age
    if (name === "dob" && value) {
      const calculatedAge = calculateAge(value);
      newFormData.age = calculatedAge;
    }

    // If disposition is changed to POCT NEG, set physician to None
    if (name === "disposition" && value === "POCT NEG") {
      newFormData.physician = "None";
    }

    setFormData(newFormData);
  };

  const onPlaceSelected = (place) => {
    handleChange({
      target: {
        name: "address",
        value: place.displayName,
        type: "text",
        checked: false,
      },
    });

    setFormData((prev) => ({
      ...prev,
      address: place.displayName,
      city: place.city,
      postal_code: place.postal_code,
      province: getProvince(place.province),
    }));
  };

  return (
    <div>
      <div className="tab-content">
        <div className="space-y-6">
          {(showManager === "coverage" ||
            showManager === "physician" ||
            showManager === "disposition" ||
            showManager === "referral_site") && (
            <OptionManager type={showManager} />
          )}
          {showManager === "clinical" && <TemplateManager type={showManager} />}
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Registration Information
            </h2>

            {/* Voice to text icons
            <div>
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <p> Click to fill with audio </p>
                </div>
                <button
                  type="button"
                  onClick={() => openVoiceFillInput()}
                  className="p-2 text-gray-600 hover:text-black transition-colors rounded-md hover:bg-gray-100 border border-black"
                  title="Voice input for date of birth"
                >
                  🎤
                </button>
              </div>
            </div>
                */}

            {/* Registration Date Field */}
            <div id="regDate" className="mb-6 scroll-mt-[60px]">
              <label
                htmlFor="reg_date"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Registration Date
              </label>
              <div className="flex items-center space-x-2">
                <DatePicker
                  name="reg_date"
                  value={formData.reg_date}
                  onChange={handleChange}
                  className="px-3 py-2 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-left font-medium cursor-pointer border border-gray-300"
                  style={{
                    width: "160px",
                  }}
                />
                {/*
                <button
                  type="button"
                  onClick={() => openVoiceDateInput("reg_date")}
                  className="p-2 text-gray-600 hover:text-black transition-colors rounded-md hover:bg-gray-100 border border-black"
                  title="Voice input for date"
                >
                  🎤
                </button>
                */}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div id="firstName" className="scroll-mt-[60px]">
                <label
                  htmlFor="first_name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  First Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter first name"
                  autoComplete="given-name"
                  // required
                />
              </div>

              <div id="lastName" className="scroll-mt-[60px]">
                <label
                  htmlFor="last_name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Last Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter last name"
                  autoComplete="family-name"
                  // required
                />
              </div>

              <div id="dateOfBirth" className="scroll-mt-[60px]">
                <label
                  htmlFor="dob"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Date of Birth<span className="text-red-500">*</span>
                </label>
                <div className="flex items-center space-x-2">
                  <DatePicker
                    name="dob"
                    value={formData.dob}
                    onChange={handleChange}
                    className="px-3 py-2 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-left font-medium cursor-pointer border border-gray-300"
                    style={{
                      width: "160px",
                    }}
                  />
                  {/*
                  <button
                    type="button"
                    onClick={() => openVoiceDateInput("dob")}
                    className="p-2 text-gray-600 hover:text-black transition-colors rounded-md hover:bg-gray-100 border border-black"
                    title="Voice input for date of birth"
                  >
                    🎤
                  </button>
                  */}
                </div>
              </div>

              <div>
                <label
                  htmlFor="age"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Age (Calculated automatically)
                </label>
                <input
                  type="text"
                  id="age"
                  name="age"
                  value={formData.age}
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed"
                  placeholder="Select date of birth to calculate age"
                />
              </div>

              <div>
                <label
                  htmlFor="gender"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Gender
                </label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="disposition"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Disposition
                  </label>
                  {userRole == "admin" && (
                    <button
                      type="button"
                      onClick={() => setShowManager("disposition")}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Manage Dispositions
                    </button>
                  )}
                </div>
                <select
                  id="disposition"
                  name="disposition"
                  value={formData.disposition}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select Disposition</option>
                  {/* Most Frequently Used */}
                  {options["disposition"]
                    .filter((d) => d.is_frequent)
                    .map((disposition) => (
                      <option key={disposition.id} value={disposition.name}>
                        {disposition.name}
                      </option>
                    ))}
                  {/* Separator */}
                  {options["disposition"].filter((d) => !d.is_frequent).length >
                    0 && <option disabled>-------</option>}
                  {/* All Others in Alphabetical Order */}
                  {options["disposition"]
                    .filter((d) => !d.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map((disposition) => (
                      <option key={disposition.id} value={disposition.name}>
                        {disposition.name}
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="aka"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  AKA (Also Known As)
                </label>
                <input
                  type="text"
                  id="aka"
                  name="aka"
                  value={formData.aka}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div className="flex gap-4">
                <div id="healthcard" className="flex-1 scroll-mt-[60px]">
                  <label
                    htmlFor="health_card"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Health Card Number
                  </label>
                  <input
                    type="text"
                    id="health_card"
                    name="health_card"
                    value={formData.health_card}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    maxLength="10"
                    placeholder="10 digits"
                  />
                </div>
                <div className="w-24">
                  <label
                    htmlFor="health_card_version"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Version Code
                  </label>
                  <input
                    type="text"
                    id="health_card_version"
                    name="health_card_version"
                    // required
                    value={formData.health_card_version}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    placeholder="AB"
                    maxLength="2"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="referral_site"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Referral Site
                  </label>
                  {userRole == "admin" && (
                    <button
                      type="button"
                      onClick={() => setShowManager("referral_site")}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Manage Referral Sites
                    </button>
                  )}
                </div>
                <select
                  id="referral_site"
                  name="referral_site"
                  value={formData.referral_site}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select Referral Site</option>
                  {/* Most Frequently Used */}
                  {options["referral_site"]
                    .filter((s) => s.is_frequent)
                    .map((site) => (
                      <option key={site.id} value={site.name}>
                        {site.name}
                      </option>
                    ))}
                  {/* Separator */}
                  {options["referral_site"].filter((s) => !s.is_frequent)
                    .length > 0 && <option disabled>-------</option>}
                  {/* All Others in Alphabetical Order */}
                  {options["referral_site"]
                    .filter((s) => !s.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map((site) => (
                      <option key={site.id} value={site.name}>
                        {site.name}
                      </option>
                    ))}
                </select>
              </div>
            </div>
          </div>
          {/* Address Information */}
          <div>
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Address Information
            </h2>
            <AddressAutocomplete
              onPlaceSelected={onPlaceSelected}
              initialAddress={formData.address}
            />
            <div className="py-2 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label
                  htmlFor="address"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Address
                </label>
                <input
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  // placeholder="Start typing address..."
                />
              </div>

              <div>
                <label
                  htmlFor="unit_number"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Unit #
                </label>
                <input
                  type="text"
                  id="unit_number"
                  name="unit_number"
                  value={formData.unit_number}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label
                  htmlFor="city"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  City
                </label>
                <input
                  type="text"
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label
                  htmlFor="province"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Province
                </label>
                <select
                  id="province"
                  name="province"
                  value={formData.province}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select Province</option>
                  <option value="Ontario">Ontario</option>
                  <option value="Quebec">Quebec</option>
                  <option value="British Columbia">British Columbia</option>
                  <option value="Alberta">Alberta</option>
                  <option value="Manitoba">Manitoba</option>
                  <option value="Saskatchewan">Saskatchewan</option>
                  <option value="Nova Scotia">Nova Scotia</option>
                  <option value="New Brunswick">New Brunswick</option>
                  <option value="Newfoundland and Labrador">
                    Newfoundland and Labrador
                  </option>
                  <option value="Prince Edward Island">
                    Prince Edward Island
                  </option>
                  <option value="Northwest Territories">
                    Northwest Territories
                  </option>
                  <option value="Nunavut">Nunavut</option>
                  <option value="Yukon">Yukon</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="postal_code"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Postal Code
                </label>
                <input
                  type="text"
                  id="postal_code"
                  name="postal_code"
                  value={formData.postal_code}
                  onChange={handleChange}
                  onBlur={(e) => {
                    // Format postal code when field loses focus (including after voice input)
                    const formatted = formatPostalCode(e.target.value);
                    if (formatted !== e.target.value) {
                      setFormData((prev) => ({
                        ...prev,
                        postal_code: formatted,
                      }));
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="e.g., A1A 1A1"
                  maxLength="7"
                />
              </div>
            </div>
          </div>
          {/* Contact Information */}
          <div>
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Contact Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex justify-between items-center">
                  <label
                    htmlFor="phone1"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Primary
                  </label>

                  {/* Use an anchor tag instead of JS handler */}
                  <button
                    type="button"
                    onClick={() => {
                      const cleaned = formData.phone1.replace(/[^+\d]/g, "");
                      if (cleaned.length >= 10) {
                        window.location.href = `tel:${cleaned}`;
                      }
                    }}
                    className="pr-1"
                  >
                    <PhoneCall className="w-4 h-4 text-gray-700 mb-2" />
                  </button>
                </div>

                <input
                  type="tel"
                  id="phone1"
                  name="phone1"
                  value={formData.phone1}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="(123) 456-7890"
                  maxLength="14"
                />
              </div>

              <div>
                <div className="flex justify-between items-center">
                  <label
                    htmlFor="phone1"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Secondary
                  </label>

                  {/* Use an anchor tag instead of JS handler */}
                  <button
                    type="button"
                    onClick={() => {
                      const cleaned = formData.phone2.replace(/[^+\d]/g, "");
                      if (cleaned.length >= 10) {
                        window.location.href = `tel:${cleaned}`;
                      }
                    }}
                    className="pr-1"
                  >
                    <PhoneCall className="w-4 h-4 text-gray-700 mb-2" />
                  </button>
                </div>
                <input
                  type="tel"
                  id="phone2"
                  name="phone2"
                  value={formData.phone2}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="(123) 456-7890"
                  maxLength="14"
                />
              </div>

              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label
                  htmlFor="preferred_time"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Preferred Contact Time
                </label>
                <input
                  type="text"
                  id="preferred_time"
                  name="preferred_time"
                  value={formData.preferred_time}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="e.g., Morning, Afternoon, Evening"
                />
              </div>

              <div>
                <label
                  htmlFor="language"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Preferred Language
                </label>
                <select
                  id="language"
                  name="language"
                  value={formData.language}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="English">English</option>
                  <option value="French">French</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Preferences
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="leave_message"
                      checked={formData.leave_message}
                      onChange={handleChange}
                      className="mr-2"
                    />
                    Leave Message
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="voicemail"
                      checked={formData.voicemail}
                      onChange={handleChange}
                      className="mr-2"
                    />
                    Voicemail
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="text"
                      checked={formData.text}
                      onChange={handleChange}
                      className="mr-2"
                    />
                    Text Messages
                  </label>
                </div>
              </div>
            </div>
          </div>
          {/* Additional Information */}
          <div>
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Additional Information
            </h2>
            <div className="space-y-6">
              <div>
                <label
                  htmlFor="special_attention"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Special Attention / Notes
                </label>
                <textarea
                  id="special_attention"
                  name="special_attention"
                  value={formData.special_attention}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="Any special instructions or notes..."
                />
              </div>

              <div>
                <label
                  htmlFor="instructions"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Instructions
                </label>
                <textarea
                  id="instructions"
                  name="instructions"
                  value={formData.instructions}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="Any additional instructions..."
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="selectedTemplate"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Clinical Summary Template
                  </label>
                  {userRole == "admin" && (
                    <button
                      type="button"
                      onClick={() => setShowManager("clinical")}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Manage Templates
                    </button>
                  )}
                </div>
                <select
                  id="selected_template"
                  value={selectedTemplate}
                  onChange={(e) => handleTemplateChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="Select">Select</option>
                  {templates["clinical"].map((template) => (
                    <option key={template.id} value={template.name}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>

              {selectedTemplate === "Positive" && (
                <>
                  <div>
                    <label
                      htmlFor="rna_available"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      RNA available?
                    </label>
                    <select
                      id="rna_available"
                      name="rna_available"
                      value={formData.rna_available}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="No">No</option>
                      <option value="Yes">Yes</option>
                    </select>
                  </div>

                  {formData.rna_available === "Yes" && (
                    <>
                      <div>
                        <label
                          htmlFor="rna_sample_date"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          RNA Sample Date
                        </label>
                        <div className="flex items-center space-x-2">
                          <DatePicker
                            name="rna_sample_date"
                            value={formData.rna_sample_date}
                            onChange={handleChange}
                            className="px-3 py-2 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-left font-medium cursor-pointer border border-gray-300"
                            style={{
                              width: "160px",
                            }}
                          />
                          {/*
                          <button
                            type="button"
                            onClick={() =>
                              openVoiceDateInput("rna_sample_date")
                            }
                            className="p-2 text-gray-600 hover:text-black transition-colors rounded-md hover:bg-gray-100 border border-black"
                            title="Voice input for RNA sample date"
                          >
                            🎤
                          </button>
                          */}
                        </div>
                      </div>

                      <div>
                        <label
                          htmlFor="rna_result"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          RNA Result
                        </label>
                        <select
                          id="rna_result"
                          name="rna_result"
                          value={formData.rna_result}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="Positive">Positive</option>
                          <option value="Negative">Negative</option>
                        </select>
                      </div>
                    </>
                  )}

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label
                        htmlFor="coverage_type"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Coverage Type
                      </label>
                      {userRole == "admin" && (
                        <button
                          type="button"
                          onClick={() => setShowManager("coverage")}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Manage Coverage
                        </button>
                      )}
                    </div>
                    <select
                      id="coverage_type"
                      name="coverage_type"
                      value={formData.coverage_type}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="">Select</option>
                      {/* Most Frequently Used */}
                      {options["coverage"]
                        .filter((c) => c.is_frequent)
                        .map((c) => (
                          <option key={c.id} value={c.name}>
                            {c.name}
                          </option>
                        ))}
                      {/* Separator */}
                      {options["coverage"].filter((c) => !c.is_frequent)
                        .length > 0 && <option disabled>-------</option>}
                      {/* All Others in Alphabetical Order */}
                      {options["coverage"]
                        .filter((c) => !c.is_frequent)
                        .sort((a, b) => a.name.localeCompare(b.name))
                        .map((c) => (
                          <option key={c.id} value={c.name}>
                            {c.name}
                          </option>
                        ))}
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="referral_person"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Referral Person
                    </label>
                    <input
                      type="text"
                      id="referral_person"
                      name="referral_person"
                      value={formData.referral_person}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                      placeholder="Name of person who referred this patient"
                    />
                  </div>
                </>
              )}

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="summary_template"
                    className="text-sm font-medium text-gray-700"
                  >
                    Clinical Summary Content
                  </label>
                </div>
                <textarea
                  id="summary_template"
                  name="summary_template"
                  value={formData.summary_template}
                  onChange={handleChange}
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-sm resize-vertical whitespace-pre-wrap"
                  style={{
                    wordWrap: "break-word",
                    overflowWrap: "break-word",
                    whiteSpace: "pre-wrap",
                    lineHeight: "1.5",
                  }}
                  placeholder="Type your clinical summary here or select a template above to auto-populate..."
                  readOnly={false}
                />
                <p className="mt-1 text-sm text-gray-500">
                  You can type manually here or select a template above to
                  auto-populate the content. Templates can be edited for
                  individual patients.
                </p>
              </div>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="limited"
                    checked={formData.limited}
                    onChange={handleChange}
                    className="mr-2"
                  />
                  Limited
                </label>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="physician"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Physician
                  </label>
                  {userRole == "admin" && (
                    <button
                      type="button"
                      onClick={() => setShowManager("physician")}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Manage Physicians
                    </button>
                  )}
                </div>
                <select
                  id="physician"
                  name="physician"
                  value={formData.physician}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="None">None</option>
                  {/* Most Frequently Used */}
                  {options["physician"]
                    .filter((c) => c.is_frequent)
                    .map((c) => (
                      <option key={c.id} value={c.name}>
                        {c.name}
                      </option>
                    ))}
                  {/* Separator */}
                  {options["physician"].filter((c) => !c.is_frequent).length >
                    0 && <option disabled>-------</option>}
                  {/* All Others in Alphabetical Order */}
                  {options["physician"]
                    .filter((c) => !c.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map((c) => (
                      <option key={c.id} value={c.name}>
                        {c.name}
                      </option>
                    ))}
                </select>
                <p className="mt-1 text-sm text-gray-500">
                  Automatically set to "None" when disposition is "POCT NEG"
                </p>
              </div>
            </div>
          </div>
          {/* Patient Consent */}
          <div className="border-t pt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient Consent Type <span className="text-red-500">*</span>
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="patient_consent"
                  value="verbal"
                  checked={formData.patient_consent === "verbal"}
                  onChange={handleChange}
                  className="mr-2"
                />
                Verbal Consent
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="patient_consent"
                  value="written"
                  checked={formData.patient_consent === "written"}
                  onChange={handleChange}
                  className="mr-2"
                />
                Written Consent
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
