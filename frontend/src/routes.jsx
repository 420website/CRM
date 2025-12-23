import "./App.css";
import {
  Navigate,
  Routes,
  Route,
  useLocation,
  Outlet,
  useParams,
} from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./my420/pages/Home";
import About from "./my420/pages/About";
import Services from "./my420/pages/Services";
import Register from "./my420/pages/Register";
import Contact from "./my420/pages/Contact";
import Resources from "./my420/pages/Resources";
import HepatitisC from "./my420/pages/HepatitisC";
import HepatitisCOntario from "./my420/pages/HepatitisCOntario";
import AdminRegister from "./crm/pages/AdminRegister";
import AdminDashboard from "./crm/pages/AdminDashboard";
import AdminEdit from "./crm/pages/AdminEdit";
import AdminMenu from "./crm/pages/AdminMenu";
import AdminPIN from "./crm/pages/AdminPIN";
import AdminAnalytics from "./crm/pages/AdminAnalytics";
import UserManagement from "./crm/pages/UserManagement";
import { useAuth } from "./context/AuthContext";
import VerifyEmail from "./crm/pages/VerifyEmail";
import ShareViewer from "./crm/components/ShareViewer";
import ScrollToTop from "./scroll.jsx";
import { RegistrationProvider } from "./context/RegistrationContext.jsx";
import { UsersProvider } from "./context/UserContext.jsx";
import { DashboardProvider } from "./context/DashboardContext.jsx";
import { ReferenceProvider } from "./context/ReferenceContext.jsx";
import { ZoomProvider } from "./context/ZoomContext.jsx";
import VideoSession from "./crm/pages/VideoSession.jsx";
import GuestVideoAccess from "./crm/pages/GuestVideoAccess.jsx";
import VideoPreview from "./crm/pages/Preview.jsx";
import { useGuestAuth } from "./context/GuestAuthContext.jsx";
import GuestVideoSession from "./crm/pages/GuestVideoSession.jsx";

function AuthenticatedRoute() {
  const { isAuthenticated, isCheckingAuth } = useAuth();
  const location = useLocation();

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/admin-pin" state={{ from: location }} replace />;
  }

  return (
    <ReferenceProvider>
      <DashboardProvider>
        <RegistrationProvider>
          <ZoomProvider>
            <Outlet />
          </ZoomProvider>
        </RegistrationProvider>
      </DashboardProvider>
    </ReferenceProvider>
  );
}

function GuestAuthenticatedRoute() {
  const { isAuthenticated } = useGuestAuth();
  const { token } = useParams();
  const location = useLocation();

  if (!isAuthenticated) {
    // Redirect back to guest login with the token
    return (
      <Navigate
        to={`/guest-video/${token}`}
        state={{ from: location }}
        replace
      />
    );
  }

  // Wrap authenticated guest routes with ZoomProvider
  return (
    <ZoomProvider>
      <Outlet />
    </ZoomProvider>
  );
}

function GuestRoute() {
  const { userRole } = useAuth();
  const location = useLocation();

  if (!["guest", "admin"].includes(userRole)) {
    return <Navigate to="/admin-menu" state={{ from: location }} replace />;
  }
  return <Outlet />;
}

function LimitedRoute() {
  const { userRole } = useAuth();
  const location = useLocation();
  if (!["limited", "standard", "admin"].includes(userRole)) {
    return <Navigate to="/admin-menu" state={{ from: location }} replace />;
  }
  return <Outlet />;
}

function StandardRoute() {
  const { userRole } = useAuth();
  const location = useLocation();

  if (!["standard", "admin"].includes(userRole)) {
    return <Navigate to="/admin-menu" state={{ from: location }} replace />;
  }

  return <Outlet />;
}

function AdminRoute() {
  const { userRole } = useAuth();
  const location = useLocation();

  if (userRole !== "admin") {
    return <Navigate to="/admin-menu" state={{ from: location }} replace />;
  }

  return (
    <UsersProvider>
      <Outlet />
    </UsersProvider>
  );
}

function AppRoutes() {
  return (
    <div className="App min-h-screen flex flex-col bg-gray-50">
      <ScrollToTop />
      <Header />
      <main className="flex-grow flex flex-col">
        <Routes>
          {/* my420 website  */}
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/services" element={<Services />} />
          <Route path="/register" element={<Register />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/hepatitis-c" element={<HepatitisC />} />
          <Route path="/hepatitis-c-ontario" element={<HepatitisCOntario />} />

          {/* CRM */}
          <Route path="/admin-pin" element={<AdminPIN />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/share-links" element={<ShareViewer />} />

          {/* Guest Video */}
          <Route
            path="/guest-video/:patientId"
            element={<GuestVideoAccess />}
          />
          <Route element={<GuestAuthenticatedRoute />}>
            <Route
              path="/guest-preview/:patientId"
              element={<VideoPreview />}
            />
            <Route
              path="/guest-session/:patientId"
              element={<GuestVideoSession />}
            />
          </Route>

          {/* Authenticate Routes */}
          <Route element={<AuthenticatedRoute />}>
            <Route path="/admin-menu" element={<AdminMenu />} />

            {/* Authenticate Routes */}
            <Route element={<LimitedRoute />}>
              <Route path="/admin-dashboard" element={<AdminDashboard />} />
              <Route path="/admin-edit/:patientId" element={<AdminEdit />} />

              {/* Zoom Routes */}
              <Route path="/preview/:patientId" element={<VideoPreview />} />
              <Route path="/video/:patientId" element={<VideoSession />} />
            </Route>

            {/* Authenticate Routes */}
            <Route element={<GuestRoute />}>
              <Route path="/admin-analytics" element={<AdminAnalytics />} />
            </Route>

            {/* Authenticate Routes */}
            <Route element={<StandardRoute />}>
              <Route path="/admin-register" element={<AdminRegister />} />
            </Route>

            {/* Authenticate Routes */}
            <Route element={<AdminRoute />}>
              <Route path="/admin-users" element={<UserManagement />} />
            </Route>
          </Route>
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default AppRoutes;
