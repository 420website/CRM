import "./App.css";
import { HelmetProvider } from "react-helmet-async";
import AppRoutes from "./routes";
import { AuthProvider } from "./context/AuthContext";
// import { useEffect } from "react";
// import eruda from "eruda";

function App() {
  // Only show on mobile or when debugging
  // useEffect(() => {
  //   if (window.innerWidth < 768 || process.env.NODE_ENV === "development") {
  //     import("vconsole").then((module) => {
  //       const VConsole = module.default;
  //       new VConsole();
  //     });
  //   }
  // }, []);
  // if (window.innerWidth < 768 || process.env.NODE_ENV === "development") {
  //   eruda.init();
  // }

  return (
    <HelmetProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
