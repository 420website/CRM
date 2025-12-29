import "./App.css";
import { HelmetProvider } from "react-helmet-async";
import AppRoutes from "./routes";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "react-hot-toast";
import MobileOnlyWrapper from "./mobileOnlyWrapper";
import { GuestAuthProvider } from "./context/GuestAuthContext";

function App() {
  return (
    <HelmetProvider>
      <AuthProvider>
        <MobileOnlyWrapper>
          <GuestAuthProvider>
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
          </GuestAuthProvider>
        </MobileOnlyWrapper>
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
