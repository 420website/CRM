import { useState } from "react";
import { GeneralServices } from "../../services/generalService";

export default function NoteTemplateManager({
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
        setError(result.message || "Error creating note template.");
      } else {
        setError("Error creating note template. Please try again.");
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
        setError(result.message || "Error update note template.");
      } else {
        setError("Error delete note template. Please try again.");
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
        setError(result.message || "Error deleting note templates.");
      } else {
        setError("Error deleting note templates. Please try again.");
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
