export default function LoadingScreen() {
  return (
    <div className="h-[75vh]  bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        {/* Spinning wheel */}
        <div className="relative w-16 h-16 mx-auto mb-4">
          <div className="absolute inset-0 border-4 border-gray-500 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-black rounded-full border-t-transparent animate-spin"></div>
        </div>

        {/* Loading text */}
        <p className="text-black text-lg font-medium">Loading...</p>
      </div>
    </div>
  );
}
