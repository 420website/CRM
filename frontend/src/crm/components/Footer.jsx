import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-black text-white border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* About Section */}
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">my420.ca</h3>
            <p className="text-gray-400 text-sm">4 Steps in 20 Minutes</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
