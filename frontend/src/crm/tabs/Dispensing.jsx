import { useState, useEffect } from "react";
import { PatientServices } from "../../services/patientServices";
import ConfirmModal from "../components/ConfirmModal";

export default function Dispensing({ setActiveTab, currentRegistrationId }) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [editingDispensingId, setEditingDispensingId] = useState(null);
  const [isSavingDispensing, setIsSavingDispensing] = useState(false);
  const [savedDispensing, setSavedDispensing] = useState([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteDispensingId, setDeleteDispensingId] = useState(null);
  const [dispensingData, setDispensingData] = useState({
    medication: "",
    rx: "",
    quantity: "28",
    lot: "",
    product_type: "Commercial",
    expiry_date: "",
  });

  const getDispensing = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_dispensings_by_patient(registrationId);
    if (result.success) {
      setSavedDispensing(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispensing.");
      } else {
        setError("Error getting dispensing. Please try again.");
      }
    }
    setLoading(false);
  };

  const saveDispensing = async () => {
    editingDispensingId ? updateDispensing() : createDispensing();
  };

  const createDispensing = async () => {
    setLoading(true);
    setError("");

    if (!currentRegistrationId) {
      alert("Please complete the Client tab first to save dispensing records.");
      setActiveTab("client");
      return;
    }

    if (!dispensingData.medication || dispensingData.medication === "") {
      alert("Please select a medication");
      return;
    }

    setIsSavingDispensing(true);

    const result = await PatientServices.create_dispensing(
      currentRegistrationId,
      dispensingData,
    );

    if (result.success) {
      await getDispensing(currentRegistrationId);
      clearDispensingForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error creating dispensing.");
      } else {
        setError("Error getting dispensing. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingDispensing(false);
  };

  const updateDispensing = async () => {
    setLoading(true);
    setError("");

    if (!currentRegistrationId) {
      alert("Please complete the Client tab first to save dispensing records.");
      setActiveTab("client");
      return;
    }

    if (!dispensingData.medication || dispensingData.medication === "") {
      alert("Please select a medication");
      return;
    }

    setIsSavingDispensing(true);

    const result = await PatientServices.update_dispensing(
      currentRegistrationId,
      editingDispensingId,
      dispensingData,
    );

    if (result.success) {
      await getDispensing(currentRegistrationId);
      clearDispensingForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error update dispensing.");
      } else {
        setError("Error update dispensing. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingDispensing(false);
  };

  const deleteDispensing = async () => {
    setLoading(true);
    setError("");

    const result = await PatientServices.delete_dispensing_by_id(
      currentRegistrationId,
      deleteDispensingId,
    );

    if (result.success) {
      await getDispensing(currentRegistrationId);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error deleting dispensing.");
      } else {
        setError("Error getting dispensing. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleDeleteDispensing = async (id) => {
    setDeleteDispensingId(id);
    setShowDeleteConfirm(true);
  };

  // Dispensing management functions
  const handleDispensingChange = (e) => {
    const { name, value } = e.target;
    setDispensingData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const editDispensing = (dispensing) => {
    setDispensingData({
      medication: dispensing.medication || "",
      rx: dispensing.rx || "",
      quantity: dispensing.quantity || "28",
      lot: dispensing.lot || "",
      product_type: dispensing.product_type || "Commercial",
      expiry_date: dispensing.expiry_date || "",
    });
    setEditingDispensingId(dispensing.id);
    // Scroll to top of dispensing form
    document
      .querySelector("#dispensingForm")
      ?.scrollIntoView({ behavior: "smooth" });
  };

  const clearDispensingForm = () => {
    setDispensingData({
      medication: "",
      rx: "",
      quantity: "28",
      lot: "",
      product_type: "Commercial",
      expiry_date: "",
    });
    setEditingDispensingId(null);
  };

  // Load dispensing when registration ID changes
  useEffect(() => {
    if (currentRegistrationId) {
      getDispensing(currentRegistrationId);
    }
  }, [currentRegistrationId]);

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
              message={"Confirm you would like to delete dispensing"}
              subMessage={"This action cannot be undone"}
              confirm={deleteDispensing}
              setShowConfirm={setShowDeleteConfirm}
            />
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded text-sm text-center">
              {error}
            </div>
          )}

          {/* Dispensing Form */}
          <div
            className={
              !currentRegistrationId ? "opacity-50 pointer-events-none" : ""
            }
          >
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              {editingDispensingId ? "Edit Dispensing" : "Add Dispensing"}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label
                  htmlFor="medication"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Medication *
                </label>
                <select
                  id="medication"
                  name="medication"
                  value={dispensingData.medication}
                  onChange={handleDispensingChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select</option>
                  <option value="Epclusa">Epclusa</option>
                  <option value="Maviret">Maviret</option>
                  <option value="Vosevi">Vosevi</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="rx"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Rx
                </label>
                <input
                  type="text"
                  id="rx"
                  name="rx"
                  value={dispensingData.rx}
                  onChange={handleDispensingChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="Enter Rx number"
                />
              </div>

              <div>
                <label
                  htmlFor="quantity"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Quantity
                </label>
                <select
                  id="quantity"
                  name="quantity"
                  value={dispensingData.quantity}
                  onChange={handleDispensingChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="28">28</option>
                  <option value="14">14</option>
                  <option value="56">56</option>
                  <option value="84">84</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="lot"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Lot
                </label>
                <input
                  type="text"
                  id="lot"
                  name="lot"
                  value={dispensingData.lot}
                  onChange={handleDispensingChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="Enter lot number"
                />
              </div>

              <div>
                <label
                  htmlFor="product_type"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Product Type
                </label>
                <select
                  id="product_type"
                  name="product_type"
                  value={dispensingData.product_type}
                  onChange={handleDispensingChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="Commercial">Commercial</option>
                  <option value="Compassionate">Compassionate</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="expiry_date"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Expiry Date
                </label>
                <input
                  type="date"
                  id="expiry_date"
                  name="expiry_date"
                  value={dispensingData.expiry_date}
                  onChange={handleDispensingChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>
            </div>

            {/* Form Actions */}
            <div className="mt-6 grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={saveDispensing}
                disabled={isSavingDispensing}
                className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
              >
                {isSavingDispensing
                  ? "Saving..."
                  : editingDispensingId
                    ? "Update Dispensing"
                    : "Save Dispensing"}
              </button>

              <button
                type="button"
                onClick={clearDispensingForm}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
              >
                Clear Form
              </button>
            </div>
          </div>

          {/* Saved Dispensing Records */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Saved Dispensing Records
            </h3>

            {savedDispensing.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No dispensing records have been saved yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {savedDispensing.map((dispensing, index) => (
                  <div
                    key={dispensing.id}
                    className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg font-semibold text-gray-900">
                            {dispensing.medication}
                          </span>
                          <span
                            className={`text-xs px-2 py-1 rounded-full ${
                              dispensing.product_type === "Commercial"
                                ? "bg-blue-100 text-blue-700"
                                : "bg-green-100 text-green-700"
                            }`}
                          >
                            {dispensing.product_type}
                          </span>
                        </div>
                        <div className="text-sm text-gray-700 space-y-1">
                          {dispensing.rx && (
                            <p>
                              <strong>Rx:</strong> {dispensing.rx}
                            </p>
                          )}
                          <p>
                            <strong>Quantity:</strong> {dispensing.quantity}
                          </p>
                          {dispensing.lot && (
                            <p>
                              <strong>Lot:</strong> {dispensing.lot}
                            </p>
                          )}
                          {dispensing.expiry_date && (
                            <p>
                              <strong>Expiry Date:</strong>{" "}
                              {dispensing.expiry_date}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => editDispensing(dispensing)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                          title="Edit dispensing record"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDeleteDispensing(dispensing.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                          title="Delete dispensing record"
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
