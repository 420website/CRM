import React, { useState, useEffect, useRef } from "react";
import { GeneralServices } from "../../services/generalService";
import { PatientServices } from "../../services/patientServices";

function NoteTemplateManager({
  setShowTemplateManager,
  availableNotesTemplates,
  getNoteTemplates,
}) {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState("");
  const [newTemplateContent, setNewTemplateContent] = useState("");
  const [editingTemplateId, setEditingTemplateId] = useState(null);

  const createNoteTemplate = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newTemplateName.trim()) {
      alert("Please enter a template name");
      return;
    }

    const data = {
      name: newTemplateName.trim(),
      content: newTemplateContent.trim(),
      is_default: false,
    };

    const result = await GeneralServices.create_note_template(data);

    if (result.success) {
      setNewTemplateName("");
      setNewTemplateContent("");
      getNoteTemplates();
      setMessage("Created referral-site successfully.");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateNoteTemplate = async (templateId, name, content) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      content: content.trim(),
    };

    const result = await GeneralServices.update_note_template(templateId, data);

    if (result.success) {
      setEditingTemplateId(null);
      getNoteTemplates();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteNoteTemplate = async (templateId, templateName) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the "${templateName}" template?`,
      )
    ) {
      return;
    }
    setLoading(true);
    setError("");

    const result = await GeneralServices.delete_note_template_by_id(templateId);

    if (result.success) {
      setEditingTemplateId(null);
      getNoteTemplates();

      // Reset selection if deleted template was selected
      if (selectedTemplate === templateName) {
        setSelectedTemplate("Select");
      }
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const closeTemplateManager = () => {
    setShowTemplateManager(false);
    setNewTemplateName("");
    setNewTemplateContent("");
    setEditingTemplateId(null);
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Manage Notes Templates
            </h3>
            <button
              type="button"
              onClick={closeTemplateManager}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Add New Template Section */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="text-md font-medium text-gray-900 mb-3">
              Add New Template
            </h4>
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            {message && (
              <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
                {message}
              </div>
            )}
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template Name
                </label>
                <input
                  type="text"
                  value={newTemplateName}
                  onChange={(e) => setNewTemplateName(e.target.value)}
                  placeholder="Enter template name (e.g., Follow-up, Referral)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template Content
                </label>
                <textarea
                  value={newTemplateContent}
                  onChange={(e) => setNewTemplateContent(e.target.value)}
                  placeholder="Enter default content for this template (optional)"
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>
              <div>
                <button
                  type="button"
                  onClick={createNoteTemplate}
                  disabled={!newTemplateName.trim()}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                >
                  Add Template
                </button>
              </div>
            </div>
          </div>

          {/* Existing Templates List */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">
              Existing Templates
            </h4>
            <div className="space-y-3">
              {availableNotesTemplates.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>Loading templates...</p>
                </div>
              ) : (
                availableNotesTemplates.map((template) => (
                  <div
                    key={template.id}
                    className="border border-gray-200 rounded-lg p-4 bg-white"
                  >
                    {editingTemplateId === template.id ? (
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Template Name
                          </label>
                          <input
                            type="text"
                            defaultValue={template.name}
                            id={`edit-name-${template.id}`}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Template Content
                          </label>
                          <textarea
                            defaultValue={template.content}
                            id={`edit-content-${template.id}`}
                            rows="3"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              const name = document.getElementById(
                                `edit-name-${template.id}`,
                              ).value;
                              const content = document.getElementById(
                                `edit-content-${template.id}`,
                              ).value;
                              updateNoteTemplate(template.id, name, content);
                            }}
                            className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 text-sm"
                          >
                            Save
                          </button>
                          <button
                            type="button"
                            onClick={() => setEditingTemplateId(null)}
                            className="bg-gray-300 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-400 text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-lg font-semibold text-gray-900">
                              {template.name}
                            </span>
                            {template.is_default && (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                Default
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-700">
                            <p className="break-words">
                              {template.content || "No default content"}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <button
                            type="button"
                            onClick={() => setEditingTemplateId(template.id)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              deleteNoteTemplate(template.id, template.name)
                            }
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Close Button */}
          <div className="mt-6 flex justify-end">
            <button
              type="button"
              onClick={closeTemplateManager}
              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Notes({
  setActiveTab,
  currentRegistrationId,
  savedNotes,
  setSavedNotes,
  getNotes,
}) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [notesTemplates, setNotesTemplates] = useState({});
  const [notesFilter, setNotesFilter] = useState("all");
  const [notesSearch, setNotesSearch] = useState("");
  const [notesPage, setNotesPage] = useState(1);
  const [notesPerPage, setNotesPerPage] = useState(10);
  const [showTemplateManager, setShowTemplateManager] = useState(false);
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [selectedNotesTemplate, setSelectedNotesTemplate] = useState("Select");
  const [availableNotesTemplates, setAvailableNotesTemplates] = useState([]);
  const [newTemplateName, setNewTemplateName] = useState("");
  const [newTemplateContent, setNewTemplateContent] = useState("");
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState("Select");

  const [notesData, setNotesData] = useState({
    note_name: "General Note",
    note_date: new Date().toISOString().split("T")[0],
    note_text: "",
    template_type: "General Note",
  });

  // templates
  const getNoteTemplates = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_note_templates();

    if (result.success) {
      const templatesObject = {};
      // Convert array to object for easier access
      result.data.forEach((template) => {
        templatesObject[template.name] = template.content;
      });

      setNotesTemplates(templatesObject);
      setAvailableNotesTemplates(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  // registration
  const saveNote = async () => {
    editingNoteId ? updateNote() : createNote();
  };

  const createNote = async () => {
    setLoading(true);
    setError("");

    if (!currentRegistrationId) {
      alert("Please complete the Client tab first to save notes.");
      setActiveTab("client");
      return;
    }

    if (!notesData.note_text.trim()) {
      alert("Please enter a note before saving");
      return;
    }

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
      await getNotes(currentRegistrationId);
      clearNotesForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingNotes(false);
  };

  const updateNote = async () => {
    setLoading(true);
    setError("");

    if (!currentRegistrationId) {
      alert("Please complete the Client tab first to save notes.");
      setActiveTab("client");
      return;
    }

    if (!notesData.note_text.trim()) {
      alert("Please enter a note before saving");
      return;
    }

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
      await getNotes(currentRegistrationId);
      clearNotesForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
    setIsSavingNotes(false);
  };

  const deleteNote = async (noteId) => {
    if (!window.confirm("Are you sure you want to delete this note?")) {
      return;
    }

    setLoading(true);
    setError("");

    const result = await PatientServices.delete_note_by_id(
      currentRegistrationId,
      noteId,
    );

    if (result.success) {
      await getNotes(currentRegistrationId);
      // clearNotesForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleNotesTemplateChange = async (templateName) => {
    setSelectedNotesTemplate(templateName);

    if (templateName === "Select") {
      setNotesData((prev) => ({
        ...prev,
        note_text: "",
      }));
    }
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
      template_type: note.template_type || "Select",
    });
    setEditingNoteId(note.id);

    // Set template to 'Select' when editing individual notes to allow free editing
    setSelectedNotesTemplate(note.template_type || "Select");
    // Scroll to top of notes form
    document.querySelector("#noteText")?.scrollIntoView({ behavior: "smooth" });
  };

  const clearNotesForm = () => {
    setNotesData({
      note_date: new Date().toISOString().split("T")[0],
      note_text: "",
    });
    setEditingNoteId(null);
    setSelectedNotesTemplate("Select");
  };

  useEffect(() => {
    getNoteTemplates();
  }, []);

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
              <input
                type="date"
                id="note_date"
                name="note_date"
                value={notesData.note_date}
                onChange={handleNotesChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
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
                <button
                  type="button"
                  onClick={() => setShowTemplateManager(true)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  Manage Templates
                </button>
              </div>
              <select
                id="selectedNotesTemplate"
                value={selectedNotesTemplate}
                onChange={(e) => handleNotesTemplateChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="Select">Select</option>
                {availableNotesTemplates.map((template) => (
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
                readOnly={selectedNotesTemplate === "Select"}
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

          {savedNotes.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No notes have been saved yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {savedNotes.map((note, index) => (
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
                        onClick={() => deleteNote(note.id)}
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
      {showTemplateManager && (
        <NoteTemplateManager
          setShowTemplateManager={setShowTemplateManager}
          availableNotesTemplates={availableNotesTemplates}
          getNoteTemplates={getNoteTemplates}
        />
      )}
    </div>
  );
}
