import { useState } from "react";
import { PatientServices } from "../../services/patientServices";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import DatePicker from "../ui/DatePicker";
import toast from "react-hot-toast";
import { newlineChars } from "pdf-lib";
import { normalizeFormData } from "../../utils/formatData";

export default function Tests({ setActiveTab, currentRegistrationId }) {
  const { tests, getTests } = useRegistration();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteTestId, setDeleteTestId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editingTestId, setEditingTestId] = useState(null);
  const [testFormData, setTestFormData] = useState({
    test_type: "",
    test_date: new Date().toISOString().split("T")[0],
    hiv_result: "negative",
    hiv_type: "",
    hiv_tester: "CM",
    hcv_result: "negative",
    hcv_tester: "CM",
    bloodwork_type: "",
    bloodwork_circles: "",
    bloodwork_result: "Pending",
    bloodwork_date_submitted: new Date().toISOString().split("T")[0],
    bloodwork_tester: "CM",
  });

  function validateHIV() {
    if (!testFormData.hiv_result || testFormData.hiv_result === "") {
      toast.error("Please select test result");
      return false;
    }

    if (
      testFormData.hiv_result === "positive" &&
      testFormData.hiv_type === ""
    ) {
      toast.error("Please select HIV Type");
      return false;
    }

    if (!testFormData.hiv_tester || testFormData.hiv_tester === "") {
      toast.error("Please select a tester");
      return false;
    }

    testFormData.bloodwork_type = null;
    testFormData.bloodwork_result = null;
    testFormData.bloodwork_tester = null;
    testFormData.bloodwork_circles = null;
    testFormData.bloodwork_date_submitted = null;
    testFormData.hcv_result = null;
    testFormData.hcv_tester = null;
    testFormData.hcv_result = null;

    return true;
  }

  function validateHCV() {
    if (!testFormData.hcv_result || testFormData.hcv_result === "") {
      toast.error("Please select test result");
      return false;
    }

    if (!testFormData.hcv_tester || testFormData.hcv_tester === "") {
      toast.error("Please select a tester");
      return false;
    }

    testFormData.bloodwork_type = null;
    testFormData.bloodwork_result = null;
    testFormData.bloodwork_tester = null;
    testFormData.bloodwork_circles = null;
    testFormData.bloodwork_date_submitted = null;
    testFormData.hiv_result = null;
    testFormData.hiv_tester = null;
    testFormData.hiv_type = null;

    return true;
  }

  function validateBloodwork() {
    if (!testFormData.bloodwork_type || testFormData.bloodwork_type === "") {
      toast.error("Please select bloodwork type");
      return false;
    }

    if (
      !testFormData.bloodwork_tester ||
      testFormData.bloodwork_tester === ""
    ) {
      toast.error("Please select a tester");
      return false;
    }

    if (
      !testFormData.bloodwork_date_submitted ||
      testFormData.bloodwork_date_submitted === ""
    ) {
      toast.error("Please select date submitted");
      return false;
    }

    if (
      !testFormData.bloodwork_result ||
      testFormData.bloodwork_result === ""
    ) {
      toast.error("Please select test result");
      return false;
    }

    if (
      testFormData.bloodwork_type === "DBS" &&
      testFormData.bloodwork_circles === ""
    ) {
      toast.error("Please select bloodwork circles");
      return false;
    }
    testFormData.hiv_result = null;
    testFormData.hiv_tester = null;
    testFormData.hiv_type = null;
    testFormData.hcv_result = null;
    testFormData.hcv_tester = null;

    return true;
  }

  function validateForm() {
    if (!currentRegistrationId) {
      alert("Please complete the Patient tab first to save tests.");
      setActiveTab("patient");
      return false;
    }

    if (!testFormData.test_type || testFormData.test_type === "") {
      toast.error("Please select a test type");
      return false;
    }

    if (!testFormData.test_date || testFormData.test_date === "") {
      toast.error("Please select a test date");
      return false;
    }

    if (testFormData.test_type === "HIV") {
      return validateHIV();
    } else if (testFormData.test_type === "HCV") {
      return validateHCV();
    } else if (testFormData.test_type == "Bloodwork") {
      return validateBloodwork();
    }

    return true;
  }

  const saveTest = async () => {
    if (!validateForm()) {
      return;
    }
    editingTestId ? updateTests() : createTests();
  };

  const createTests = async () => {
    setLoading(true);

    const data = normalizeFormData(testFormData);
    const result = await PatientServices.create_test(
      currentRegistrationId,
      data,
    );

    if (result.success) {
      getTests(currentRegistrationId);

      // Reset form
      setTestFormData({
        test_type: "",
        test_date: new Date().toISOString().split("T")[0],
        hiv_result: "negative",
        hiv_type: "",
        hiv_tester: "CM",
        hcv_result: "negative",
        hcv_tester: "CM",
        bloodwork_type: "",
        bloodwork_circles: "",
        bloodwork_result: "Pending",
        bloodwork_date_submitted: new Date().toISOString().split("T")[0],
        bloodwork_tester: "CM",
      });
      setEditingTestId(null);
      toast.success("Test created successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error creating test.");
      } else {
        toast.error("Error creating test. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateTests = async () => {
    setLoading(true);

    const data = normalizeFormData(testFormData);
    const result = await PatientServices.update_test(
      currentRegistrationId,
      editingTestId,
      data,
    );

    if (result.success) {
      getTests(currentRegistrationId);

      // Reset form
      setTestFormData({
        test_type: "",
        test_date: new Date().toISOString().split("T")[0],
        hiv_result: "negative",
        hiv_type: "",
        hiv_tester: "CM",
        hcv_result: "negative",
        hcv_tester: "CM",
        bloodwork_type: "",
        bloodwork_circles: "",
        bloodwork_result: "Pending",
        bloodwork_date_submitted: new Date().toISOString().split("T")[0],
        bloodwork_tester: "CM",
      });
      setEditingTestId(null);
      toast.success("Test updated successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating test.");
      } else {
        toast.error("Error updating test. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteTest = async () => {
    setLoading(true);

    const result = await PatientServices.delete_test_by_id(
      currentRegistrationId,
      deleteTestId,
    );

    if (result.success) {
      getTests(currentRegistrationId);
      toast.success("Deleted test successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting test.");
      } else {
        toast.error("Error deleting test. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleDeleteTest = async (testId) => {
    setDeleteTestId(testId);
    setShowDeleteConfirm(true);
  };

  const editTest = (test) => {
    setTestFormData({
      test_type: test.test_type,
      test_date: test.test_date,
      hiv_result: test.hiv_result || "negative",
      hiv_type: test.hiv_type || "",
      hiv_tester: test.hiv_tester || "CM",
      hcv_result: test.hcv_result || "negative",
      hcv_tester: test.hcv_tester || "CM",
      bloodwork_type: test.bloodwork_type || "",
      bloodwork_circles: test.bloodwork_circles || "",
      bloodwork_result: test.bloodwork_result || "Pending",
      bloodwork_date_submitted:
        test.bloodwork_date_submitted || new Date().toISOString().split("T")[0],
      bloodwork_tester: test.bloodwork_tester || "CM",
    });
    setEditingTestId(test.id);
  };

  const cancelTestEdit = () => {
    setTestFormData({
      test_type: "",
      test_date: new Date().toISOString().split("T")[0],
      hiv_result: "negative",
      hiv_type: "",
      hiv_tester: "CM",
      hcv_result: "negative",
      hcv_tester: "CM",
      bloodwork_type: "",
      bloodwork_circles: "",
      bloodwork_result: "Pending",
      bloodwork_date_submitted: new Date().toISOString().split("T")[0],
      bloodwork_tester: "CM",
    });
    setEditingTestId(null);
  };

  const handleTestChange = (e) => {
    const { name, value } = e.target;

    let newTestData = {
      ...testFormData,
      [name]: value,
    };

    // Clear HIV type when result is not positive
    if (name === "hiv_result" && value !== "positive") {
      newTestData.hiv_type = "";
    }

    // Set defaults when switching to HIV
    if (name === "test_type" && value === "HIV") {
      newTestData.test_date = new Date().toISOString().split("T")[0];
      newTestData.hiv_result = "negative";
      newTestData.hiv_type = "";
      newTestData.hiv_tester = "CM";
    }

    // Set defaults when switching to HCV
    if (name === "test_type" && value === "HCV") {
      newTestData.test_date = new Date().toISOString().split("T")[0];
      newTestData.hcv_result = "negative";
      newTestData.hcv_tester = "CM";
    }

    if (
      value === "Cepheid" &&
      newTestData.bloodwork_result !== "Positive" &&
      newTestData.bloodwork_result !== "Negative"
    ) {
      newTestData.bloodwork_result = "Positive";
    }

    if (
      newTestData.bloodwork_type !== "DBS" &&
      newTestData.bloodwork_circles !== ""
    ) {
      newTestData.bloodwork_circles = "";
    }

    setTestFormData(newTestData);
  };

  return (
    <div>
      <div className="tab-content">
        <div className="space-y-6">
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
              message={"Confirm delete test"}
              subMessage={"This action cannot be undone"}
              confirm={deleteTest}
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
              {editingTestId ? "Edit Test" : "Add Test"}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label
                  htmlFor="testType"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Test Type
                </label>
                <select
                  id="testType"
                  name="test_type"
                  value={testFormData.test_type}
                  onChange={handleTestChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select Option</option>
                  <option value="HIV">HIV</option>
                  <option value="HCV">HCV</option>
                  <option value="Bloodwork">Bloodwork</option>
                </select>
              </div>
            </div>

            {/* HIV Test Fields */}
            {testFormData.test_type === "HIV" && (
              <div className="mt-6">
                <h3 className="text-md font-medium text-gray-900 mb-4">
                  HIV Test Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label
                      htmlFor="testDate"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Test Date
                    </label>
                    <DatePicker
                      name="test_date"
                      value={testFormData.test_date}
                      onChange={handleTestChange}
                      className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                      style={{
                        lineHeight: "1.5",
                        height: "auto",
                      }}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="hivResult"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Test Result
                    </label>
                    <select
                      id="hivResult"
                      name="hiv_result"
                      value={testFormData.hiv_result}
                      onChange={handleTestChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="">Select Result</option>
                      <option value="negative">Negative</option>
                      <option value="positive">Positive</option>
                    </select>
                  </div>

                  {/* HIV Type - only show if result is positive */}
                  {testFormData.hiv_result === "positive" && (
                    <div>
                      <label
                        htmlFor="hivType"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        HIV Type
                      </label>
                      <select
                        id="hivType"
                        name="hiv_type"
                        value={testFormData.hiv_type}
                        onChange={handleTestChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                      >
                        <option value="">Select Type</option>
                        <option value="Type 1">Type 1</option>
                        <option value="Type 2">Type 2</option>
                      </select>
                    </div>
                  )}

                  <div>
                    <label
                      htmlFor="hivTester"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Tester
                    </label>
                    <select
                      id="hivTester"
                      name="hiv_tester"
                      value={testFormData.hiv_tester}
                      onChange={handleTestChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="CM">CM</option>
                      <option value="JY">JY</option>
                    </select>
                  </div>
                </div>

                {/* Save Test Button */}
                <div className="mt-6 flex gap-3">
                  <button
                    type="button"
                    onClick={saveTest}
                    className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                  >
                    {editingTestId ? "Update Test" : "Save Test"}
                  </button>
                  {editingTestId && (
                    <button
                      type="button"
                      onClick={cancelTestEdit}
                      className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                    >
                      Cancel Edit
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Bloodwork Test Fields */}
            {testFormData.test_type === "Bloodwork" && (
              <div className="mt-6">
                <h3 className="text-md font-medium text-gray-900 mb-4">
                  Bloodwork Test Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label
                      htmlFor="bloodwork_test_date"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Test Date
                    </label>
                    <DatePicker
                      name="test_date"
                      value={testFormData.test_date}
                      onChange={handleTestChange}
                      className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                      style={{
                        lineHeight: "1.5",
                        height: "auto",
                      }}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="bloodwork_type"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Type
                    </label>
                    <select
                      id="bloodwork_type"
                      name="bloodwork_type"
                      value={testFormData.bloodwork_type}
                      onChange={handleTestChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="">Select Type</option>
                      <option value="DBS">DBS</option>
                      <option value="Serum">Serum</option>
                      <option value="Cepheid">Cepheid</option>
                    </select>
                  </div>

                  {testFormData.bloodwork_type === "DBS" && (
                    <div>
                      <label
                        htmlFor="bloodwork_circles"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Circles
                      </label>
                      <select
                        id="bloodwork_circles"
                        name="bloodwork_circles"
                        value={testFormData.bloodwork_circles}
                        onChange={handleTestChange}
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
                    <label
                      htmlFor="bloodwork_result"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Results
                    </label>
                    <select
                      id="bloodwork_result"
                      name="bloodwork_result"
                      value={testFormData.bloodwork_result}
                      onChange={handleTestChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      {testFormData.bloodwork_type !== "Cepheid" && (
                        <>
                          <option value="Pending">Pending</option>
                          <option value="Submitted">Submitted</option>
                        </>
                      )}
                      <option value="Positive">Positive</option>
                      <option value="Negative">Negative</option>
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="bloodwork_date_submitted"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Date Submitted
                    </label>
                    <DatePicker
                      name="bloodwork_date_submitted"
                      value={testFormData.bloodwork_date_submitted}
                      onChange={handleTestChange}
                      className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                      style={{
                        lineHeight: "1.5",
                        height: "auto",
                      }}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="bloodwork_tester"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Tester
                    </label>
                    <select
                      id="bloodwork_tester"
                      name="bloodwork_tester"
                      value={testFormData.bloodwork_tester}
                      onChange={handleTestChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="CM">CM</option>
                      <option value="JY">JY</option>
                    </select>
                  </div>
                </div>

                {/* Save Test Button */}
                <div className="mt-6 flex gap-3">
                  <button
                    type="button"
                    onClick={saveTest}
                    className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                  >
                    {editingTestId ? "Update Test" : "Save Test"}
                  </button>
                  {editingTestId && (
                    <button
                      type="button"
                      onClick={cancelTestEdit}
                      className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                    >
                      Cancel Edit
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* HCV Test Fields */}
            {testFormData.test_type === "HCV" && (
              <div className="mt-6">
                <h3 className="text-md font-medium text-gray-900 mb-4">
                  HCV Test Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label
                      htmlFor="hcvTestDate"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Test Date
                    </label>
                    <DatePicker
                      name="test_date"
                      value={testFormData.test_date}
                      onChange={handleTestChange}
                      className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                      style={{
                        lineHeight: "1.5",
                        height: "auto",
                      }}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="hcvResult"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Test Result
                    </label>
                    <select
                      id="hcvResult"
                      name="hcv_result"
                      value={testFormData.hcv_result}
                      onChange={handleTestChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="">Select Result</option>
                      <option value="negative">Negative</option>
                      <option value="positive">Positive</option>
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="hcvTester"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Tester
                    </label>
                    <select
                      id="hcvTester"
                      name="hcv_tester"
                      value={testFormData.hcv_tester}
                      onChange={handleTestChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                    >
                      <option value="CM">CM</option>
                      <option value="JY">JY</option>
                    </select>
                  </div>
                </div>

                {/* Save Test Button */}
                <div className="mt-6 flex gap-3">
                  <button
                    type="button"
                    onClick={saveTest}
                    className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
                  >
                    {editingTestId ? "Update Test" : "Save Test"}
                  </button>
                  {editingTestId && (
                    <button
                      type="button"
                      onClick={cancelTestEdit}
                      className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                    >
                      Cancel Edit
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Saved Tests */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Saved Tests
            </h3>

            {tests.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No tests have been saved yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {tests.map((test) => (
                  <div
                    key={test.id}
                    className="border rounded-lg p-4 bg-gray-50"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center flex-wrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-3">
                            {test.test_type}
                          </span>
                          <span className="text-sm text-gray-500 mr-3">
                            {test.test_date}
                          </span>
                          {test.updated_at && (
                            <span className="text-xs text-gray-400 whitespace-nowrap">
                              Saved:{" "}
                              {new Date(test.updated_at).toLocaleString(
                                "en-US",
                                {
                                  timeZone: "America/New_York",
                                  hour12: true,
                                  month: "short",
                                  day: "numeric",
                                  year: "numeric",
                                  hour: "2-digit",
                                  minute: "2-digit",
                                },
                              )}
                            </span>
                          )}
                        </div>
                        {test.test_type === "HIV" && (
                          <div className="mt-2 text-sm text-gray-700">
                            <p>
                              <strong>Result:</strong>{" "}
                              {test.hiv_result || "Not specified"}
                            </p>
                            {test.hiv_result === "positive" &&
                              test.hiv_type && (
                                <p>
                                  <strong>Type:</strong> {test.hiv_type}
                                </p>
                              )}
                            <p>
                              <strong>Tester:</strong>{" "}
                              {test.hiv_tester || "Not specified"}
                            </p>
                          </div>
                        )}
                        {test.test_type === "HCV" && (
                          <div className="mt-2 text-sm text-gray-700">
                            <p>
                              <strong>Result:</strong>{" "}
                              {test.hcv_result || "Not specified"}
                            </p>
                            <p>
                              <strong>Tester:</strong>{" "}
                              {test.hcv_tester || "Not specified"}
                            </p>
                          </div>
                        )}
                        {test.test_type === "Bloodwork" && (
                          <div className="mt-2 text-sm text-gray-700">
                            <p>
                              <strong>Type:</strong>{" "}
                              {test.bloodwork_type || "Not specified"}
                            </p>
                            {test.bloodwork_circles && (
                              <p>
                                <strong>Circles:</strong>{" "}
                                {test.bloodwork_circles}
                              </p>
                            )}
                            <p>
                              <strong>Result:</strong>{" "}
                              {test.bloodwork_result || "Not specified"}
                            </p>
                            {test.bloodwork_date_submitted && (
                              <p>
                                <strong>Submitted:</strong>{" "}
                                {test.bloodwork_date_submitted}
                              </p>
                            )}
                            <p>
                              <strong>Tester:</strong>{" "}
                              {test.bloodwork_tester || "Not specified"}
                            </p>
                          </div>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => editTest(test)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                          title="Edit test"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDeleteTest(test.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                          title="Delete test"
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
    </div>
  );
}
