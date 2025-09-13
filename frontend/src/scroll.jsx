import { useEffect } from "react";
import { useLocation } from "react-router-dom";

// Scroll restoration component
export default function ScrollToTop() {
  const location = useLocation();

  useEffect(() => {
    const currentPath = location.pathname;

    // Check if we have a saved scroll position for this path
    const savedPosition = sessionStorage.getItem(`scrollPos${currentPath}`);

    if (savedPosition) {
      // Restore scroll position after a short delay
      setTimeout(() => {
        window.scrollTo(0, parseInt(savedPosition));
        // Clear the saved position after using it
        sessionStorage.removeItem(`scrollPos${currentPath}`);
      }, 100);
    } else {
      // Fresh navigation - scroll behavior depends on page
      if (currentPath === "/about") {
        window.scrollTo(0, 0);
      } else if (
        currentPath === "/register" &&
        location.hash === "#registration-form"
      ) {
        // Let register page handle its own scrolling
        return;
      } else if (currentPath !== "/") {
        // For other pages, scroll to top
        window.scrollTo(0, 0);
      }
      // For home page, don't force scroll - let natural behavior happen
    }
  }, [location]);

  return null;
}
