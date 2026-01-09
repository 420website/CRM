export default function EditModal({
  type,
  editingTemplate,
  setShowTemplateEditPopup,
  handleUpdate,
  updateTemplate,
  deleteTemplate,
}) {
  return (
    <div>
      <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-[60]">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-gray-900">{`Edit Option`}</h3>
            <button
              onClick={() => setShowTemplateEditPopup(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg
                className="w-5 h-5"
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
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {`Option Name`}
              </label>
              <input
                type="text"
                id="editTemplateName"
                defaultValue={editingTemplate.name}
                onChange={(e) => handleUpdate("name", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>

            {type === "referral_site" && (
              <div id="province" className="scroll-mt-[60px]">
                <select
                  id="province"
                  name="province"
                  value={editingTemplate.custom_fields.province}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  readOnly
                >
                  <option value="">
                    {editingTemplate.custom_fields.province}
                  </option>
                </select>
              </div>
            )}

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="editTemplateFrequent"
                defaultChecked={editingTemplate.is_frequent}
                onChange={(e) => handleUpdate("is_frequent", e.target.checked)}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="editTemplateFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() =>
                  deleteTemplate(editingTemplate.id, editingTemplate.name)
                }
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors bg-black text-white hover:bg-gray-800`}
              >
                Delete
              </button>
              <button
                type="button"
                onClick={() => setShowTemplateEditPopup(false)}
                className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  updateTemplate(editingTemplate.id);
                }}
                className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
