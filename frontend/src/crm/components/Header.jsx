import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="bg-black text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <img
                src="/logo-white.svg"
                alt="420 Logo"
                className="h-12 w-auto"
              />
              <div className="text-white">
                <h1 className="text-lg font-bold text-white">my420.ca</h1>
                <p className="text-gray-300 text-xs font-medium whitespace-nowrap">
                  4 Steps in 20 Minutes
                </p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
