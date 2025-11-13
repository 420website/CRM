import { useNavigate } from "react-router-dom";

export default function DuplicateModal({ userData, setShowConfirm }) {
  const navigate = useNavigate();
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg max-w-sm mx-4">
        <h3 className="font-bold mb-0 flex justify-center text-center ">
          Health Card Already Registered
        </h3>
        <p className="mb-4 flex justify-center text-center">
          {`Registered to: ${userData.firstName} ${userData.lastName}`}
        </p>
        <div className="flex gap-5 justify-center">
          <button
            onClick={() => {
              setShowConfirm(null);
              navigate(`/admin-edit/${userData.id}`);
            }}
            className="bg-black text-white px-4 py-2 rounded"
          >
            Go to Registration
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
