import { useState } from "react";
import { PatientServices } from "../../services/patientServices";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import DatePicker from "../ui/DatePicker";
import toast from "react-hot-toast";
import { normalizeFormData } from "../../utils/formatData";
import { useReferences } from "../../context/ReferenceContext";
import { useAuth } from "../../context/AuthContext";
import OptionManager from "../managers/OptionManager";

export default function Assessments({ setActiveTab, currentRegistrationId }) {
  const { userRole } = useAuth();
  const { assessments, getClientAssessments } = useRegistration();
  const { showManager, setShowManager, options } = useReferences();

  const [loading, setLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    type: "",
    date: new Date().toLocaleDateString("en-CA"),
    result: "",
    tester: "",
    data: null,
  });

  function resetForm() {
    setFormData({
      type: "",
      date: new Date().toLocaleDateString("en-CA"),
      result: "",
      tester: "",
      data: {},
    });
  }

  function validateForm() {
    if (!currentRegistrationId) {
      alert("Please complete the Patient tab first to save assessments.");
      setActiveTab("patient");
      return false;
    }

    if (
      !formData.type ||
      formData.type === "" ||
      !options["assessment_type"].some((d) => d.name === formData.type)
    ) {
      toast.error("Please select a valid type");
      return false;
    }

    if (!formData.date || formData.date === "") {
      toast.error("Please select a date");
      return false;
    }

    if (formData.type === "HIV") {
      if (formData.result === "Positive" && !formData.data.hiv_type) {
        toast.error("Please select HIV Type");
        return false;
      }
    } else if (formData.type == "Bloodwork") {
      if (
        !formData.data.bloodwork_type ||
        formData.data.bloodwork_type === ""
      ) {
        toast.error("Please select type");
        return false;
      }
      if (
        formData.data.bloodwork_type === "DBS" &&
        !formData.data.bloodwork_circles
      ) {
        toast.error("Please select bloodwork circles");
        return false;
      }
    }

    if (
      !formData.result ||
      formData.result === "" ||
      !options["assessment_result"].some((d) => d.name === formData.result)
    ) {
      toast.error("Please select a valid result");
      return false;
    }

    if (
      !formData.tester ||
      formData.tester === "" ||
      !options["assessment_tester"].some((d) => d.name === formData.tester)
    ) {
      toast.error("Please select a valid tester");
      return false;
    }

    return true;
  }

  const saveAssessment = async () => {
    if (!validateForm()) {
      return;
    }
    editingId ? updateAssessment() : createAssessment();
  };

  const createAssessment = async () => {
    setLoading(true);

    const data = normalizeFormData(formData);
    const result = await PatientServices.create_assessment(
      currentRegistrationId,
      data,
    );

    if (result.success) {
      getClientAssessments(currentRegistrationId);
      resetForm();
      setEditingId(null);
      toast.success("Assessment created successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error creating assessment.");
      } else {
        toast.error("Error creating assessment. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateAssessment = async () => {
    setLoading(true);

    const data = normalizeFormData(formData);
    const result = await PatientServices.update_assessment(
      currentRegistrationId,
      editingId,
      data,
    );

    if (result.success) {
      getClientAssessments(currentRegistrationId);
      resetForm();
      setEditingId(null);
      toast.success("Assessment updated successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating assessment.");
      } else {
        toast.error("Error updating assessment. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteAssessment = async () => {
    setLoading(true);

    const result = await PatientServices.delete_assessment_by_id(
      currentRegistrationId,
      deleteId,
    );

    if (result.success) {
      getClientAssessments(currentRegistrationId);
      setDeleteId(null);
      toast.success("Deleted assessment successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting assessment.");
      } else {
        toast.error("Error deleting assessment. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleDelete = async (testId) => {
    setDeleteId(testId);
    setShowDeleteConfirm(true);
  };

  const handleEdit = (item) => {
    const form = {
      type: item.type,
      date: item.date,
      result: item.result,
      tester: item.tester,
      data: item.data || null,
    };

    setFormData(form);
    setEditingId(item.id);
    document.querySelector("#tests")?.scrollIntoView({ behavior: "smooth" });
  };

  const cancelEdit = () => {
    resetForm();
    setEditingId(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    let newData;
    if (name.startsWith("data.")) {
      const key = name.split(".")[1];

      if (!value || value === "") {
        const { [key]: removed, ...restData } = formData.data;
        newData = {
          ...formData,
          data: restData,
        };
      } else {
        const updated = { ...formData.data, [key]: value };

        newData = {
          ...formData,
          data: updated,
        };
      }
    } else {
      newData = {
        ...formData,
        [name]: value,
      };
    }

    if (name === "type" && value !== formData.type) {
      newData.data = {};
    }

    if (newData.type === "HIV" && newData.result !== "Positive") {
      newData.data = {};
    }

    if (
      newData.data?.bloodwork_type !== "DBS" &&
      newData.data?.bloodwork_circles
    ) {
      delete newData.data.bloodwork_circles;
    }

    setFormData(newData);
  };

  return (
    <div id="tests" className="scroll-mt-[20px]">
      <div className="tab-content">
        <div className="space-y-6">
          {(showManager === "assessment_type" ||
            showManager === "assessment_result" ||
            showManager === "assessment_tester") && (
            <OptionManager type={showManager} />
          )}
          {/* Registration ID Check */}
          {!currentRegistrationId && (
            <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-orange-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-orange-800">
                    Client Registration Required
                  </h3>
                  <div className="mt-2 text-sm text-orange-700">
                    <p>
                      Please complete and save the Client tab form first before
                      adding tests. This will create a registration record that
                      tests can be associated with.
                    </p>
                  </div>
                  <div className="mt-4">
                    <button
                      type="button"
                      onClick={() => setActiveTab("client")}
                      className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                    >
                      Go to Client Tab
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          {showDeleteConfirm && (
            <ConfirmModal
              message={"Confirm delete assessment"}
              subMessage={"This action cannot be undone"}
              confirm={deleteAssessment}
              setShowConfirm={setShowDeleteConfirm}
            />
          )}

          {/* Test Form */}
          <div
            className={
              !currentRegistrationId ? "opacity-50 pointer-events-none" : ""
            }
          >
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              {editingId ? "Edit Assessment" : "Add Assessment"}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="type"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Type
                  </label>
                  {userRole == "admin" && (
                    <button
                      type="button"
                      onClick={() => setShowManager("assessment_type")}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Manage
                    </button>
                  )}
                </div>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select Option</option>
                  {/* Show legacy value if it doesn't exist in current options */}
                  {formData.type &&
                    !options["assessment_type"].some(
                      (d) => d.name === formData.type,
                    ) && (
                      <option
                        value={formData.type}
                        disabled
                        className="text-red-600"
                      >
                        {formData.type} (No longer available)
                      </option>
                    )}

                  {/* Most Frequently Used */}
                  {options["assessment_type"]
                    .filter((d) => d.is_frequent)
                    .map((disposition) => (
                      <option key={disposition.id} value={disposition.name}>
                        {disposition.name}
                      </option>
                    ))}
                  {/* Separator */}
                  {options["assessment_type"].filter((d) => !d.is_frequent)
                    .length > 0 && <option disabled>-------</option>}
                  {/* All Others in Alphabetical Order */}
                  {options["assessment_type"]
                    .filter((d) => !d.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map((disposition) => (
                      <option key={disposition.id} value={disposition.name}>
                        {disposition.name}
                      </option>
                    ))}
                </select>
                {formData.type &&
                  !options["assessment_type"].some(
                    (d) => d.name === formData.type,
                  ) && (
                    <div className="mt-1 text-sm text-red-600">
                      ⚠️ This option is no longer available. Please select a new
                      option before saving.
                    </div>
                  )}
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-md font-medium text-gray-900 mb-4">
                {`Details`}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label
                    htmlFor="date"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Date
                  </label>
                  <DatePicker
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    style={{
                      lineHeight: "1.5",
                      height: "auto",
                    }}
                  />
                </div>

                {formData.type !== "Bloodwork" && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label
                        htmlFor="result"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Result
                      </label>
                      {userRole == "admin" && (
                        <button
                          type="button"
                          onClick={() => setShowManager("assessment_result")}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Manage
                        </button>
                      )}
                    </div>
                    <select
                      id="result"
                      name="result"
                      value={formData.result}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="">Select</option>
                      {formData.result &&
                        !options["assessment_result"].some(
                          (d) => d.name === formData.result,
                        ) && (
                          <option
                            value={formData.result}
                            disabled
                            className="text-red-600"
                          >
                            {formData.result} (No longer available)
                          </option>
                        )}
                      {/* Most Frequently Used */}
                      {options["assessment_result"]
                        .filter((d) => d.is_frequent)
                        .map((disposition) => (
                          <option key={disposition.id} value={disposition.name}>
                            {disposition.name}
                          </option>
                        ))}
                      {/* Separator */}
                      {options["assessment_result"].filter(
                        (d) => !d.is_frequent,
                      ).length > 0 && <option disabled>-------</option>}
                      {/* All Others in Alphabetical Order */}
                      {options["assessment_result"]
                        .filter((d) => !d.is_frequent)
                        .sort((a, b) => a.name.localeCompare(b.name))
                        .map((disposition) => (
                          <option key={disposition.id} value={disposition.name}>
                            {disposition.name}
                          </option>
                        ))}
                    </select>
                    {formData.result &&
                      !options["assessment_result"].some(
                        (d) => d.name === formData.result,
                      ) && (
                        <div className="mt-1 text-sm text-red-600">
                          ⚠️ This option is no longer available. Please select a
                          new option before saving.
                        </div>
                      )}
                  </div>
                )}
                {/* HIV Type - only show if result is positive */}
                {formData.type === "HIV" && formData.result === "Positive" && (
                  <div>
                    <label
                      htmlFor="hivType"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      HIV Type
                    </label>
                    <select
                      id="data.hivType"
                      name="data.hiv_type"
                      value={formData.data?.hiv_type}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="">Select Type</option>
                      <option value="Type 1">Type 1</option>
                      <option value="Type 2">Type 2</option>
                    </select>
                  </div>
                )}

                {/* Bloodwork Fields */}
                {formData.type === "Bloodwork" && (
                  <>
                    <div>
                      <label
                        htmlFor="bloodwork_type"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Type
                      </label>
                      <select
                        id="data.bloodwork_type"
                        name="data.bloodwork_type"
                        value={formData.data?.bloodwork_type}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                      >
                        <option value="">Select Type</option>
                        <option value="DBS">DBS</option>
                        <option value="Serum">Serum</option>
                        <option value="Cepheid">Cepheid</option>
                      </select>
                    </div>

                    {formData.data?.bloodwork_type === "DBS" && (
                      <div>
                        <label
                          htmlFor="bloodwork_circles"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          Circles
                        </label>
                        <select
                          id="data.bloodwork_circles"
                          name="data.bloodwork_circles"
                          value={formData.data?.bloodwork_circles}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select Circles</option>
                          <option value="1">1</option>
                          <option value="2">2</option>
                          <option value="3">3</option>
                          <option value="4">4</option>
                          <option value="5">5</option>
                        </select>
                      </div>
                    )}

                    <div>
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label
                            htmlFor="result"
                            className="block text-sm font-medium text-gray-700 mb-2"
                          >
                            Result
                          </label>
                          {userRole == "admin" && (
                            <button
                              type="button"
                              onClick={() =>
                                setShowManager("assessment_result")
                              }
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              Manage
                            </button>
                          )}
                        </div>
                        <select
                          id="result"
                          name="result"
                          value={formData.result}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        >
                          <option value="">Select</option>
                          {formData.result &&
                            !options["assessment_result"].some(
                              (d) => d.name === formData.result,
                            ) && (
                              <option
                                value={formData.result}
                                disabled
                                className="text-red-600"
                              >
                                {formData.result} (No longer available)
                              </option>
                            )}

                          {/* Most Frequently Used */}
                          {options["assessment_result"]
                            .filter((d) => d.is_frequent)
                            .map((disposition) => (
                              <option
                                key={disposition.id}
                                value={disposition.name}
                              >
                                {disposition.name}
                              </option>
                            ))}
                          {/* Separator */}
                          {options["assessment_result"].filter(
                            (d) => !d.is_frequent,
                          ).length > 0 && <option disabled>-------</option>}
                          {/* All Others in Alphabetical Order */}
                          {options["assessment_result"]
                            .filter((d) => !d.is_frequent)
                            .sort((a, b) => a.name.localeCompare(b.name))
                            .map((disposition) => (
                              <option
                                key={disposition.id}
                                value={disposition.name}
                              >
                                {disposition.name}
                              </option>
                            ))}
                        </select>
                        {formData.result &&
                          !options["assessment_result"].some(
                            (d) => d.name === formData.result,
                          ) && (
                            <div className="mt-1 text-sm text-red-600">
                              ⚠️ This option is no longer available. Please
                              select a new option before saving.
                            </div>
                          )}
                      </div>
                    </div>

                    <div>
                      <label
                        htmlFor="bloodwork_date_submitted"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Date Submitted
                      </label>
                      <DatePicker
                        name="data.bloodwork_date_submitted"
                        value={formData.data?.bloodwork_date_submitted}
                        onChange={handleChange}
                        className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                        style={{
                          lineHeight: "1.5",
                          height: "auto",
                        }}
                      />
                    </div>
                  </>
                )}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label
                      htmlFor="tester"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Tester
                    </label>
                    {userRole == "admin" && (
                      <button
                        type="button"
                        onClick={() => setShowManager("assessment_tester")}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Manage
                      </button>
                    )}
                  </div>
                  <select
                    id="tester"
                    name="tester"
                    value={formData.tester}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  >
                    <option value="">Select</option>
                    {/* Show legacy value if it doesn't exist in current options */}
                    {formData.tester &&
                      !options["assessment_tester"].some(
                        (d) => d.name === formData.tester,
                      ) && (
                        <option
                          value={formData.tester}
                          disabled
                          className="text-red-600"
                        >
                          {formData.tester} (No longer available)
                        </option>
                      )}
                    {/* Most Frequently Used */}
                    {options["assessment_tester"]
                      .filter((d) => d.is_frequent)
                      .map((disposition) => (
                        <option key={disposition.id} value={disposition.name}>
                          {disposition.name}
                        </option>
                      ))}
                    {/* Separator */}
                    {options["assessment_tester"].filter((d) => !d.is_frequent)
                      .length > 0 && <option disabled>-------</option>}
                    {/* All Others in Alphabetical Order */}
                    {options["assessment_tester"]
                      .filter((d) => !d.is_frequent)
                      .sort((a, b) => a.name.localeCompare(b.name))
                      .map((disposition) => (
                        <option key={disposition.id} value={disposition.name}>
                          {disposition.name}
                        </option>
                      ))}
                  </select>
                  {formData.tester &&
                    !options["assessment_tester"].some(
                      (d) => d.name === formData.tester,
                    ) && (
                      <div className="mt-1 text-sm text-red-600">
                        ⚠️ This option is no longer available. Please select a
                        new option before saving.
                      </div>
                    )}
                </div>
              </div>
            </div>
          </div>

          {/* Save Test Button */}
          <div className="mt-6 mb-6 flex gap-3">
            <button
              type="button"
              onClick={saveAssessment}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              {editingId ? "Update Assessment" : "Save Assessment"}
            </button>
            {editingId && (
              <button
                type="button"
                onClick={cancelEdit}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
              >
                Cancel Edit
              </button>
            )}
          </div>
        </div>

        {/* Saved Tests */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Saved Assessments
          </h3>

          {assessments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No assessments have been saved yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {assessments.map((a) => (
                <div key={a.id} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center flex-wrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-3">
                          {a.type}
                        </span>
                        <span className="text-sm text-gray-500 mr-3">
                          {a.date}
                        </span>
                        {a.updated_at && (
                          <span className="text-xs text-gray-400 whitespace-nowrap">
                            Saved:{" "}
                            {new Date(a.updated_at).toLocaleString("en-US", {
                              timeZone: "America/New_York",
                              hour12: true,
                              month: "short",
                              day: "numeric",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        )}
                      </div>
                      <div className="mt-2 text-sm text-gray-700">
                        {a.type !== "Bloodwork" && (
                          <>
                            <p>
                              <strong>Result:</strong>{" "}
                              {a.result || "Not specified"}
                            </p>
                            {a.data?.hiv_type && (
                              <p>
                                <strong>Type:</strong> {a.data?.hiv_type}
                              </p>
                            )}
                          </>
                        )}
                        {a.type === "Bloodwork" && (
                          <>
                            <p>
                              <strong>Type:</strong>{" "}
                              {a.data?.bloodwork_type || "Not specified"}
                            </p>
                            {a.data?.bloodwork_circles && (
                              <p>
                                <strong>Circles:</strong>{" "}
                                {a.data?.bloodwork_circles}
                              </p>
                            )}
                            <p>
                              <strong>Result:</strong>{" "}
                              {a.result || "Not specified"}
                            </p>
                            {a.data?.bloodwork_date_submitted && (
                              <p>
                                <strong>Submitted:</strong>{" "}
                                {a.data?.bloodwork_date_submitted}
                              </p>
                            )}
                          </>
                        )}
                        <p>
                          <strong>Tester:</strong> {a.tester || "Not specified"}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => handleEdit(a)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                        title="Edit Assessment"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(a.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                        title="Delete Assessment"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
