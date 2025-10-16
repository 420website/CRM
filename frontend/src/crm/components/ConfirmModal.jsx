export default function ConfirmModal({
  message,
  subMessage,
  confirm,
  setShowConfirm,
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg max-w-sm mx-4">
        <h3 className="font-bold mb-0 flex justify-center">{message}</h3>
        <p className="mb-4 flex justify-center">{subMessage}</p>
        <div className="flex gap-5 justify-center">
          <button
            onClick={() => {
              confirm();
              setShowConfirm(null);
            }}
            className="bg-black text-white px-4 py-2 rounded"
          >
            Confirm
          </button>
          <button
            onClick={() => setShowConfirm(null)}
            className="bg-gray-300 px-4 py-2 rounded"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
