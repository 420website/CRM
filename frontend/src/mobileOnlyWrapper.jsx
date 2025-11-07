// import "./App.css";
// import { useEffect, useState } from "react";
// import { Navigate, Routes, Route, useLocation, Outlet } from "react-router-dom";
//
// // Mobile-only restriction component - PROPERLY IMPLEMENTED
// export default function MobileOnlyWrapper({ children }) {
//   const [isMobile, setIsMobile] = useState(false);
//   const [isAdmin, setIsAdmin] = useState(false);
//   const [showAdminBypass, setShowAdminBypass] = useState(false);
//   const [isLoading, setIsLoading] = useState(true);
//
//   useEffect(() => {
//     const checkAccess = () => {
//       // Check if user is authenticated as admin
//       const adminAuthenticated = sessionStorage.getItem("admin_authenticated");
//       const currentUser = sessionStorage.getItem("current_user");
//
//       // Check if accessing admin routes directly by looking at current URL
//       const isAdminRoute = window.location.pathname.startsWith("/admin");
//
//       // Admin users can access from any device
//       if (
//         adminAuthenticated === "true" ||
//         currentUser !== null ||
//         isAdminRoute
//       ) {
//         setIsAdmin(true);
//         setIsLoading(false);
//         return;
//       }
//
//       // Check if device is mobile - force small screens to be mobile
//       const windowWidth = window.innerWidth;
//       const userAgent = navigator.userAgent || navigator.vendor || window.opera;
//       const isMobileDevice =
//         /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
//           userAgent.toLowerCase(),
//         );
//
//       // Force mobile detection for small screens (375px is definitely mobile)
//       const isSmallScreen = windowWidth <= 768;
//       const isMobile = isMobileDevice || isSmallScreen;
//
//       // console.log("Mobile detection debug:", {
//       //   windowWidth: windowWidth,
//       //   userAgent: userAgent.substring(0, 50),
//       //   isMobileDevice: isMobileDevice,
//       //   isSmallScreen: isSmallScreen,
//       //   finalDecision: isMobile,
//       // });
//
//       setIsMobile(isMobile);
//       setIsLoading(false);
//     };
//
//     checkAccess();
//
//     // Listen for window resize to handle screen size changes
//     const handleResize = () => {
//       if (!isAdmin) {
//         const isSmallScreen = window.innerWidth <= 768;
//         const userAgent =
//           navigator.userAgent || navigator.vendor || window.opera;
//         const isMobileDevice =
//           /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
//             userAgent.toLowerCase(),
//           );
//
//         // More permissive - small screen = mobile
//         setIsMobile(isMobileDevice || isSmallScreen);
//       }
//     };
//
//     window.addEventListener("resize", handleResize);
//     return () => window.removeEventListener("resize", handleResize);
//   }, [isAdmin]);
//
//   // Handle admin bypass
//   const handleAdminBypass = () => {
//     setIsAdmin(true);
//     // Navigate to admin PIN page for authentication
//     window.location.href = "/admin-pin";
//   };
//
//   // Show loading state briefly
//   if (isLoading) {
//     return (
//       <div className="min-h-screen bg-gray-50 flex items-center justify-center">
//         <div className="text-center">
//           <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
//           <p className="text-gray-600">Loading...</p>
//         </div>
//       </div>
//     );
//   }
//
//   // Admin users can access from any device
//   if (isAdmin) {
//     return children;
//   }
//
//   // Non-admin users must use mobile devices
//   if (!isMobile) {
//     return (
//       <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
//         <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
//           <div className="text-6xl mb-6">📱</div>
//           <h1 className="text-2xl font-bold text-gray-800 mb-4">
//             Mobile Access Required
//           </h1>
//           <p className="text-gray-600 mb-6">
//             For security and privacy reasons, this healthcare application is
//             only accessible on mobile devices.
//           </p>
//           <p className="text-gray-600 mb-6">
//             Please visit this site using your smartphone.
//           </p>
//
//           {showAdminBypass && (
//             <div className="mb-6">
//               <p className="text-sm text-gray-600 mb-3">
//                 Administrative access from desktop requires authentication.
//               </p>
//               <button
//                 onClick={handleAdminBypass}
//                 className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
//               >
//                 Admin Login
//               </button>
//             </div>
//           )}
//
//           <div className="text-sm text-gray-500 bg-gray-100 p-4 rounded-md">
//             <p className="font-medium mb-2">Why Mobile Only?</p>
//             <ul className="text-left space-y-1">
//               <li>• Enhanced security for sensitive health information</li>
//               <li>• Optimized user experience for healthcare workflows</li>
//               <li>• Compliance with privacy regulations</li>
//             </ul>
//           </div>
//         </div>
//       </div>
//     );
//   }
//
//   return children;
// }
