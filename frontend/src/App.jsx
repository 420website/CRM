import "./App.css";
import { HelmetProvider } from "react-helmet-async";
import AppRoutes from "./routes";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "react-hot-toast";
import MobileOnlyWrapper from "./mobileOnlyWrapper";

function App() {
  return (
    <HelmetProvider>
      <AuthProvider>
        <MobileOnlyWrapper>
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
        </MobileOnlyWrapper>
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
