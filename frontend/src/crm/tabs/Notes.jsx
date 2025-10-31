import { useState, useEffect } from "react";
import { PatientServices } from "../../services/patientServices";
import NoteTemplateManager from "../managers/NotesTemplateManager";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import DatePicker from "../ui/DatePicker";
import toast from "react-hot-toast";
import { useAuth } from "../../context/AuthContext";

export default function Notes({ setActiveTab, currentRegistrationId }) {
  const { userRole } = useAuth();
  const {
    getNotes,
    notes,
    showNoteManager,
    setShowNoteManager,
    notesTemplates,
  } = useRegistration();

  const [loading, setLoading] = useState(false);
  const [notesFilter, setNotesFilter] = useState("all");
  const [notesSearch, setNotesSearch] = useState("");
  const [notesPage, setNotesPage] = useState(1);
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [selectedNotesTemplate, setSelectedNotesTemplate] = useState("Select");
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteNoteId, setDeleteNoteId] = useState(null);
  const [notesData, setNotesData] = useState({
    note_date: new Date().toISOString().split("T")[0],
    note_text: "",
  });

  function validateForm() {
    if (!currentRegistrationId) {
      alert("Please complete the Patient tab first to save notes.");
      setActiveTab("patient");
      return false;
    }

    if (!notesData.note_date || notesData.note_date === "") {
      toast.error("Please select a date");
      return false;
    }

    if (!notesData.note_text.trim() || notesData.note_text === "") {
      toast.error("Please add note text");
      return false;
    }

    return true;
  }

  const saveNote = async () => {
    if (!validateForm()) {
      return;
    }
    editingNoteId ? updateNote() : createNote();
  };

  const createNote = async () => {
    setLoading(true);
    setIsSavingNotes(true);

    // Include the template type with the note data
    const noteDataWithTemplate = {
      ...notesData,
      template_type:
        selectedNotesTemplate !== "Select"
          ? selectedNotesTemplate
          : "General Note",
    };

    const result = await PatientServices.create_note(
      currentRegistrationId,
      noteDataWithTemplate,
    );

    if (result.success) {
      getNotes(currentRegistrationId);
      clearNotesForm();
      toast.success("Created note successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error creating note.");
      } else {
        toast.error("Error creating note. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingNotes(false);
  };

  const updateNote = async () => {
    setLoading(true);
    setIsSavingNotes(true);

    // Include the template type with the note data
    const noteDataWithTemplate = {
      ...notesData,
      template_type:
        selectedNotesTemplate !== "Select"
          ? selectedNotesTemplate
          : "General Note",
    };

    const result = await PatientServices.update_note(
      currentRegistrationId,
      editingNoteId,
      noteDataWithTemplate,
    );

    if (result.success) {
      getNotes(currentRegistrationId);
      clearNotesForm();
      toast.success("Updated note successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating note.");
      } else {
        toast.error("Error updating note. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingNotes(false);
  };

  const deleteNote = async () => {
    setLoading(true);

    const result = await PatientServices.delete_note_by_id(
      currentRegistrationId,
      deleteNoteId,
    );

    if (result.success) {
      getNotes(currentRegistrationId);
      toast.success("Deleted note successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting note.");
      } else {
        toast.error("Error deleting note. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleDeleteNote = async (id) => {
    setDeleteNoteId(id);
    setShowDeleteConfirm(true);
  };

  const handleNotesTemplateChange = async (templateName) => {
    setSelectedNotesTemplate(templateName);
    const template = notesTemplates.find(
      (template) => template.name === templateName,
    );

    const content = template ? template.content : "";

    setNotesData((prev) => ({
      ...prev,
      note_text: content,
    }));
  };

  const handleNotesChange = (e) => {
    const { name, value } = e.target;
    setNotesData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const editNote = (note) => {
    setNotesData({
      note_date: note.note_date || new Date().toISOString().split("T")[0],
      note_text: note.note_text || "",
      template_type: note.template_type || "General Note",
    });
    setEditingNoteId(note.id);

    // Set template to 'Select' when editing individual notes to allow free editing
    setSelectedNotesTemplate(note.template_type || "Select");

    // Scroll to top of notes form
    document.querySelector("#tabs")?.scrollIntoView({ behavior: "smooth" });
  };

  const clearNotesForm = () => {
    setNotesData({
      note_date: new Date().toISOString().split("T")[0],
      note_text: "",
    });
    setEditingNoteId(null);
    setSelectedNotesTemplate("Select");
  };

  // Reset pagination when filter/search changes
  useEffect(() => {
    setNotesPage(1);
  }, [notesFilter, notesSearch]);

  // Auto-scroll to top when notes page changes
  useEffect(() => {
    if (notesPage > 1) {
      document
        .querySelector("#notes-section")
        ?.scrollIntoView({ behavior: "smooth" });
    }
  }, [notesPage]);

  return (
    <div>
      <div className="space-y-6">
        {/* Notes Tab Warning */}
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
            message={"Confirm delete note"}
            subMessage={"This action cannot be undone"}
            confirm={deleteNote}
            setShowConfirm={setShowDeleteConfirm}
          />
        )}
        <div
          className={
            !currentRegistrationId ? "opacity-50 pointer-events-none" : ""
          }
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            {editingNoteId ? "Edit Note" : "Add Note"}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label
                htmlFor="note_date"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Date
              </label>
              <DatePicker
                name="note_date"
                value={notesData.note_date}
                onChange={handleNotesChange}
                className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="mm/dd/yyyy"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="selectedNotesTemplate"
                  className="block text-sm font-medium text-gray-700"
                >
                  Notes Template
                </label>
                {userRole == "admin" && (
                  <button
                    type="button"
                    onClick={() => setShowNoteManager(true)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Manage Templates
                  </button>
                )}
              </div>
              <select
                id="selectedNotesTemplate"
                value={selectedNotesTemplate}
                onChange={(e) => handleNotesTemplateChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="Select">Select</option>
                {notesTemplates.map((template) => (
                  <option key={template.id} value={template.name}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label
                htmlFor="note_text"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Note Text
              </label>
              <textarea
                id="note_text"
                name="note_text"
                rows="6"
                value={notesData.note_text}
                onChange={handleNotesChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black resize-y"
                placeholder={
                  editingNoteId
                    ? "Edit your note content..."
                    : selectedNotesTemplate === "Select"
                      ? "Please select a template above..."
                      : `Enter ${selectedNotesTemplate} note content...`
                }
                style={{ whiteSpace: "pre-wrap" }}
                autoComplete="off"
                spellCheck="true"
                // readOnly={selectedNotesTemplate === "Select"}
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="mt-6 grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={saveNote}
              disabled={
                isSavingNotes ||
                !notesData.note_text.trim() ||
                !currentRegistrationId
              }
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              {isSavingNotes
                ? "Saving..."
                : editingNoteId
                  ? "Update Note"
                  : "Save Note"}
            </button>

            <button
              type="button"
              onClick={clearNotesForm}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
            >
              Clear Form
            </button>
          </div>
        </div>

        {/* Saved Notes */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Saved Notes
          </h3>

          {notes.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No notes have been saved yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {notes.map((note, index) => (
                <div
                  key={note.id}
                  className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="mb-2">
                        <span className="text-lg font-semibold text-gray-900">
                          {note.template_type || "General Note"}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700 space-y-1">
                        <p>
                          <strong>Date:</strong>{" "}
                          {note.note_date ? note.note_date : "No date"}
                        </p>
                        {note.created_at && (
                          <p className="text-xs text-gray-400">
                            Saved:{" "}
                            {new Date(note.created_at).toLocaleTimeString(
                              "en-US",
                              {
                                timeZone: "America/New_York",
                                hour12: true,
                              },
                            )}
                          </p>
                        )}
                        <div className="mt-2">
                          <p
                            style={{ whiteSpace: "pre-wrap" }}
                            className="break-words"
                          >
                            {note.note_text}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => editNote(note)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                        title="Edit note"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteNote(note.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                        title="Delete note"
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
      {showNoteManager && <NoteTemplateManager />}
    </div>
  );
}
