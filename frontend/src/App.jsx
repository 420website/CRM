import "./App.css";
import { HelmetProvider } from "react-helmet-async";
import AppRoutes from "./routes";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "react-hot-toast";

function App() {
  // useEffect(() => {
  //   // Load eruda dynamically only when needed
  //   if (window.innerWidth < 768 || process.env.NODE_ENV === "development") {
  //     const script = document.createElement("script");
  //     script.src = "https://cdn.jsdelivr.net/npm/eruda";
  //     script.onload = () => {
  //       window.eruda.init();
  //     };
  //     document.body.appendChild(script);
  //   }
  // }, []);

  return (
    <HelmetProvider>
      <AuthProvider>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 2500,
            style: {
              background: "#333",
              color: "#fff",
            },
          }}
        />
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
