import { useState, useEffect } from "react";
import { PatientServices } from "../../services/patientServices";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import DatePicker from "../ui/DatePicker";
import toast from "react-hot-toast";

export default function Interactions({ setActiveTab, currentRegistrationId }) {
  const { interactions, getInteractions } = useRegistration();
  const [loading, setLoading] = useState(false);
  const [interactionsFilter, setInteractionsFilter] = useState("all");
  const [interactionsSearch, setInteractionsSearch] = useState("");
  const [editingInteractionId, setEditingInteractionId] = useState(null);
  const [isSavingInteraction, setIsSavingInteraction] = useState(false);
  const [interactionsPerPage, setInteractionsPerPage] = useState(10);
  const [interactionsPage, setInteractionsPage] = useState(1);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteInteractionId, setDeleteInteractionId] = useState(null);
  const [interactionData, setInteractionData] = useState({
    date: new Date().toISOString().split("T")[0],
    description: "",
    referral_id: "",
    amount: "",
    payment_type: "",
    issued: "Select",
  });

  function validateForm() {
    if (!currentRegistrationId) {
      alert("Please complete the Patient tab first to save dispensing.");
      setActiveTab("patient");
      return false;
    }

    if (!interactionData.date || interactionData.date === "") {
      toast.error("Please select a date");
      return false;
    }

    if (!interactionData.description || interactionData.description === "") {
      toast.error("Please select a description");
      return false;
    }

    if (interactionData.amount !== "" && interactionData.payment_type === "") {
      toast.error("Please select a payment type");
      return false;
    }

    if (
      interactionData.description === "Referral" &&
      interactionData.referral_id === ""
    ) {
      toast.error("Please set a referral id");
      return false;
    }

    return true;
  }

  const saveInteraction = async () => {
    if (!validateForm()) {
      return;
    }
    editingInteractionId ? updateInteraction() : createInteraction();
  };

  const createInteraction = async () => {
    setLoading(true);
    setIsSavingInteraction(true);

    let data = interactionData;

    if (!interactionData.amount) {
      data = { ...data, amount: 0 };
    }

    const result = await PatientServices.create_interaction(
      currentRegistrationId,
      data,
    );

    if (result.success) {
      getInteractions(currentRegistrationId);
      clearInteractionForm();
      toast.success("Interaction saved successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error creating interaction.");
      } else {
        toast.error("Error creating interaction. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingInteraction(false);
  };

  const updateInteraction = async () => {
    setLoading(true);
    setIsSavingInteraction(true);

    let data = interactionData;

    if (!interactionData.amount) {
      data = { ...data, amount: 0 };
    }

    const result = await PatientServices.update_interaction(
      currentRegistrationId,
      editingInteractionId,
      data,
    );

    if (result.success) {
      getInteractions(currentRegistrationId);
      clearInteractionForm();
      toast.success("Interaction updated successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating interaction.");
      } else {
        toast.error("Error updating interaction. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingInteraction(false);
  };

  const deleteInteraction = async () => {
    setLoading(true);

    const result = await PatientServices.delete_interaction_by_id(
      currentRegistrationId,
      deleteInteractionId,
    );

    if (result.success) {
      getInteractions(currentRegistrationId);
      toast.error("Interaction deleted successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting interaction.");
      } else {
        toast.error("Error deleting interaction. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleDeleteInteraction = async (id) => {
    setDeleteInteractionId(id);
    setShowDeleteConfirm(true);
  };

  // Interaction management functions
  const handleInteractionChange = (e) => {
    const { name, value } = e.target;
    setInteractionData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const editInteraction = (interaction) => {
    setInteractionData({
      date: interaction.date || new Date().toISOString().split("T")[0],
      description: interaction.description || "",
      referral_id: interaction.referral_id || "",
      amount: interaction.amount || "",
      payment_type: interaction.payment_type || "",
      issued: interaction.issued || "Select",
    });
    setEditingInteractionId(interaction.id);
    // Scroll to top of interaction form
    document.querySelector("#tabs")?.scrollIntoView({ behavior: "smooth" });
  };

  const clearInteractionForm = () => {
    setInteractionData({
      date: new Date().toISOString().split("T")[0], // Default to current date
      description: "",
      referral_id: "",
      amount: "",
      payment_type: "",
      location: "",
      issued: "Select",
    });
    setEditingInteractionId(null);
  };

  // Enhanced filter and search for interactions
  const getFilteredInteractions = () => {
    let filtered = [...interactions];

    // Apply date filter
    const today = new Date();
    const todayStr = today.toISOString().split("T")[0];
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0];
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0];

    switch (interactionsFilter) {
      case "today":
        filtered = filtered.filter(
          (interaction) => interaction.date === todayStr,
        );
        break;
      case "week":
        filtered = filtered.filter(
          (interaction) => interaction.date >= weekAgo,
        );
        break;
      case "month":
        filtered = filtered.filter(
          (interaction) => interaction.date >= monthAgo,
        );
        break;
      case "recent":
        // Show only last 20 interactions for performance
        filtered = filtered.slice(0, 20);
        break;
      default:
        break;
    }

    // Apply search filter with enhanced search
    if (interactionsSearch.trim()) {
      const searchTerm = interactionsSearch.toLowerCase();
      filtered = filtered.filter(
        (interaction) =>
          interaction.description.toLowerCase().includes(searchTerm) ||
          (interaction.date && interaction.date.includes(searchTerm)) ||
          (interaction.referral_id &&
            interaction.referral_id.toLowerCase().includes(searchTerm)) ||
          (interaction.amount &&
            interaction.amount.toLowerCase().includes(searchTerm)) ||
          (interaction.payment_type &&
            interaction.payment_type.toLowerCase().includes(searchTerm)) ||
          (interaction.issued &&
            interaction.issued.toLowerCase().includes(searchTerm)),
      );
    }

    // Sort by date and created_at (newest first) - ensure proper chronological order
    filtered.sort((a, b) => {
      // Use the interaction date first, fall back to created_at
      const dateA = new Date(a.date || a.created_at || "1970-01-01");
      const dateB = new Date(b.date || b.created_at || "1970-01-01");

      // Sort newest first (descending order)
      return dateB.getTime() - dateA.getTime();
    });

    return filtered;
  };

  // Reset pagination when filter/search changes
  useEffect(() => {
    setInteractionsPage(1);
  }, [interactionsFilter, interactionsSearch]);

  return (
    <div>
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
            message={"Confirm delete interaction"}
            subMessage={"This action cannot be undone"}
            confirm={deleteInteraction}
            setShowConfirm={setShowDeleteConfirm}
          />
        )}
        {/* Interaction Form */}
        <div
          className={
            !currentRegistrationId ? "opacity-50 pointer-events-none" : ""
          }
          id="interactionForm"
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            {editingInteractionId ? "Edit Interaction" : "Add Interaction"}
          </h2>
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
                value={interactionData.date}
                onChange={handleInteractionChange}
                className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="mm/dd/yyyy"
              />
            </div>

            <div>
              <label
                htmlFor="description"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Description *
              </label>
              <select
                id="description"
                name="description"
                value={interactionData.description}
                onChange={handleInteractionChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="">Select</option>
                <option value="Screening">Screening</option>
                <option value="Adherence">Adherence</option>
                <option value="Bloodwork">Bloodwork</option>
                <option value="Discretionary">Discretionary</option>
                <option value="Referral">Referral</option>
                <option value="Consultation">Consultation</option>
                <option value="Outreach">Outreach</option>
                <option value="Repeat">Repeat</option>
                <option value="Results">Results</option>
                <option value="Safe Supply">Safe Supply</option>
                <option value="Lab Req">Lab Req</option>
                <option value="Telephone">Telephone</option>
                <option value="Remittance">Remittance</option>
                <option value="Update">Update</option>
                <option value="Counselling">Counselling</option>
                <option value="Trillium">Trillium</option>
                <option value="Housing">Housing</option>
                <option value="SOT">SOT</option>
                <option value="EOT">EOT</option>
                <option value="SVR">SVR</option>
                <option value="Locate">Locate</option>
                <option value="Staff">Staff</option>
              </select>
            </div>

            {/* Conditional Referral ID field - only shows when Referral is selected */}
            {interactionData.description === "Referral" && (
              <div>
                <label
                  htmlFor="referral_id"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Referral ID
                </label>
                <input
                  type="text"
                  id="referral_id"
                  name="referral_id"
                  value={interactionData.referral_id}
                  onChange={handleInteractionChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="Enter referral ID"
                />
              </div>
            )}

            <div>
              <label
                htmlFor="amount"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Amount
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">$</span>
                <input
                  type="number"
                  id="amount"
                  name="amount"
                  value={interactionData.amount}
                  onChange={handleInteractionChange}
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="0.00"
                  step="0.01"
                />
              </div>
            </div>

            {/* Conditional Payment Type field - only shows when amount is entered */}
            {interactionData.amount && interactionData.amount !== "" && (
              <div>
                <label
                  htmlFor="payment_type"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Payment Type
                </label>
                <select
                  id="payment_type"
                  name="payment_type"
                  value={interactionData.payment_type}
                  onChange={handleInteractionChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">Select</option>
                  <option value="Cash">Cash</option>
                  <option value="EFT">EFT</option>
                </select>
              </div>
            )}

            <div>
              <label
                htmlFor="issued"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Issued
              </label>
              <select
                id="issued"
                name="issued"
                value={interactionData.issued}
                onChange={handleInteractionChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="Select">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          </div>

          {/* Form Actions */}
          <div className="mt-6 flex gap-4">
            <button
              type="button"
              onClick={saveInteraction}
              disabled={isSavingInteraction}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              {isSavingInteraction
                ? "Saving..."
                : editingInteractionId
                  ? "Update Interaction"
                  : "Save Interaction"}
            </button>

            {editingInteractionId && (
              <button
                type="button"
                onClick={clearInteractionForm}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel Edit
              </button>
            )}

            <button
              type="button"
              onClick={clearInteractionForm}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
            >
              Clear Form
            </button>
          </div>
        </div>

        {/* Interactions Management */}
        <div className="space-y-4" id="interactions-section">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-medium text-gray-900">
                Saved Interactions
              </h3>
              {interactions.length !== getFilteredInteractions().length && (
                <p className="text-sm text-gray-500">
                  Showing {getFilteredInteractions().length} of{" "}
                  {interactions.length} total interactions
                </p>
              )}
            </div>

            {/* Enhanced Filter and Search Controls */}
            <div className="flex flex-col sm:flex-row gap-3">
              <select
                value={interactionsFilter}
                onChange={(e) => setInteractionsFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-sm"
              >
                <option value="all">All Interactions</option>
                <option value="today">Today</option>
                <option value="week">Past Week</option>
                <option value="month">Past Month</option>
                <option value="recent">Most Recent (20)</option>
              </select>

              <div className="relative">
                <input
                  type="text"
                  placeholder="Search interactions..."
                  value={interactionsSearch}
                  onChange={(e) => setInteractionsSearch(e.target.value)}
                  className="px-3 py-2 pr-8 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black text-sm w-full sm:w-48"
                />
                {interactionsSearch && (
                  <button
                    onClick={() => setInteractionsSearch("")}
                    className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                    title="Clear search"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Performance Warning for Large Interaction Sets */}
          {interactions.length > 50 && interactionsFilter === "all" && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-sm text-blue-700">
                  You have {interactions.length} interactions. Consider using
                  filters for better performance.
                </p>
              </div>
            </div>
          )}

          {/* Interactions List */}
          {getFilteredInteractions().length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>
                {interactions.length === 0
                  ? "No interactions have been saved yet."
                  : "No interactions match your search criteria."}
              </p>
              {interactionsSearch && (
                <div className="mt-2">
                  <button
                    onClick={() => setInteractionsSearch("")}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Clear search to see all interactions
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {getFilteredInteractions()
                .slice(
                  (interactionsPage - 1) * interactionsPerPage,
                  interactionsPage * interactionsPerPage,
                )
                .map((interaction, index) => (
                  <div
                    key={interaction.id}
                    className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg font-semibold text-gray-900">
                            {interaction.description}
                          </span>
                          {interaction.issued &&
                            interaction.issued !== "Select" && (
                              <span
                                className={`text-xs px-2 py-1 rounded-full ${
                                  interaction.issued === "Yes"
                                    ? "bg-green-100 text-green-700"
                                    : "bg-red-100 text-red-700"
                                }`}
                              >
                                {interaction.issued}
                              </span>
                            )}
                        </div>
                        <div className="text-sm text-gray-700 space-y-1">
                          {interaction.date && (
                            <p>
                              <strong>Date:</strong> {interaction.date}
                            </p>
                          )}
                          {interaction.referral_id && (
                            <p>
                              <strong>Referral ID:</strong>{" "}
                              {interaction.referral_id}
                            </p>
                          )}
                          {interaction.amount && (
                            <p>
                              <strong>Amount:</strong> ${interaction.amount}
                              {interaction.payment_type &&
                                ` (${interaction.payment_type})`}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => editInteraction(interaction)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                          title="Edit interaction"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            handleDeleteInteraction(interaction.id)
                          }
                          className="text-red-600 hover:text-red-800 text-sm"
                          title="Delete interaction"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          )}

          {/* Enhanced Pagination */}
          {getFilteredInteractions().length > interactionsPerPage && (
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mt-6">
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Show:</label>
                <select
                  value={interactionsPerPage}
                  onChange={(e) => {
                    setInteractionsPerPage(parseInt(e.target.value));
                    setInteractionsPage(1);
                  }}
                  className="px-2 py-1 border border-gray-300 rounded text-sm"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                </select>
                <span className="text-sm text-gray-600">per page</span>
              </div>

              <div className="flex justify-center items-center gap-4">
                <button
                  onClick={() =>
                    setInteractionsPage(Math.max(1, interactionsPage - 1))
                  }
                  disabled={interactionsPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {interactionsPage} of{" "}
                  {Math.ceil(
                    getFilteredInteractions().length / interactionsPerPage,
                  )}
                </span>
                <button
                  onClick={() =>
                    setInteractionsPage(
                      Math.min(
                        Math.ceil(
                          getFilteredInteractions().length /
                            interactionsPerPage,
                        ),
                        interactionsPage + 1,
                      ),
                    )
                  }
                  disabled={
                    interactionsPage >=
                    Math.ceil(
                      getFilteredInteractions().length / interactionsPerPage,
                    )
                  }
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
