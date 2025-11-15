export default function DuplicateModal({
  title,
  handleGoTo,
  userData,
  handleContinue,
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg max-w-sm mx-4">
        <h3 className="font-bold mb-0 flex justify-center text-center ">
          {`${title}`}
        </h3>
        <p className="mb-4 flex justify-center text-center">
          {`Registered to: ${userData.firstName} ${userData.lastName}`}
        </p>
        <div className="flex gap-5 justify-center">
          <button
            onClick={() => handleGoTo(userData.id)}
            className="bg-black text-white px-4 py-2 rounded"
          >
            Go to Registration
          </button>
          <button
            onClick={() => handleContinue()}
            className="bg-gray-300 px-4 py-2 rounded"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
