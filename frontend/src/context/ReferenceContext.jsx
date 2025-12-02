import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";
import { ReferenceServices } from "../services/referenceService";
import { PROVINCES } from "../constants";

const ReferenceContext = createContext();

export const useReferences = () => useContext(ReferenceContext);

export function ReferenceProvider({ children }) {
  const { userRole, userLocationPermissions } = useAuth();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  // const [userProvinces] = useState(
  //   userLocationPermissions.includes("All")
  //     ? PROVINCES
  //     : userLocationPermissions,
  // );

  const userProvinces = useMemo(() => {
    return userLocationPermissions.includes("All")
      ? PROVINCES
      : userLocationPermissions;
  }, [userLocationPermissions]);

  // Updated
  const [showManager, setShowManager] = useState("");
  const [templates, setTemplates] = useState({
    note: [],
    clinical: [],
    activity: [],
  });
  const [options, setOptions] = useState({
    disposition: [],
    referral_site: [],
    medication: [],
    medication_outcome: [],
    interaction: [],
    coverage: [],
    physician: [],
    document_type: [],
    dispensing_type: [],
    dispensing_quantity: [],
    assessment_type: [],
    assessment_result: [],
    assessment_tester: [],
  });

  // -- Options
  const getOption = async (type) => {
    setLoading(true);
    setError("");

    const result = await ReferenceServices.get_options(type);

    if (result.success) {
      let data = result.data;
      if (type === "referral_site") {
        data = data.filter((item) =>
          userProvinces.includes(item?.custom_fields?.province),
        );
      }

      setOptions((prev) => ({ ...prev, [type]: data }));
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || `Error getting ${type} options.`);
      } else {
        setError(
          result.message || `Error getting ${type} options. Please try again.`,
        );
      }
    }
    setLoading(false);
  };

  // -- templates
  const getTemplate = async (type) => {
    setLoading(true);
    setError("");

    const result = await ReferenceServices.get_templates(type);

    if (result.success) {
      setTemplates((prev) => ({ ...prev, [type]: result.data }));
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || `Error getting ${type} templates.`);
      } else {
        setError(
          result.message ||
            `Error getting ${type} templates. Please try again.`,
        );
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    const getInitialData = async () => {
      // Load all options in parallel
      await Promise.all([
        getOption("disposition"),
        getOption("document_type"),
        getOption("referral_site"),
        getOption("medication_outcome"),
        getOption("medication"),
        getOption("interaction"),
        getOption("coverage"),
        getOption("physician"),
        getOption("dispensing_type"),
        getOption("dispensing_quantity"),
        getOption("assessment_type"),
        getOption("assessment_result"),
        getOption("assessment_tester"),
        getTemplate("note"),
        getTemplate("clinical"),
        getTemplate("activity"),
      ]);
    };
    getInitialData();
  }, []);

  return (
    <ReferenceContext.Provider
      value={{
        options,
        templates,
        setShowManager,
        showManager,
        getTemplate,
        getOption,
      }}
    >
      {children}
    </ReferenceContext.Provider>
  );
}
