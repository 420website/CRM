import "../App.css";
import {
  Navigate,
  Routes,
  Route,
  useLocation,
  Outlet,
  useParams,
} from "react-router-dom";
import AdminRegister from "./pages/AdminRegister";
import AdminDashboard from "./pages/AdminDashboard";
import AdminEdit from "./pages/AdminEdit";
import AdminMenu from "./pages/AdminMenu";
import AdminPIN from "./pages/AdminPIN";
import AdminAnalytics from "./pages/AdminAnalytics";
import UserManagement from "./pages/UserManagement";
import { useAuth } from "../context/AuthContext";
import VerifyEmail from "./pages/VerifyEmail";
import ShareViewer from "./components/ShareViewer";
import { RegistrationProvider } from "../context/RegistrationContext.jsx";
import { UsersProvider } from "../context/UserContext.jsx";
import { DashboardProvider } from "../context/DashboardContext.jsx";
import { ReferenceProvider } from "../context/ReferenceContext.jsx";
import { ZoomProvider } from "../context/ZoomContext.jsx";
import VideoSession from "./pages/VideoSession.jsx";
import GuestVideoAccess from "./pages/GuestVideoAccess.jsx";
import VideoPreview from "./pages/Preview.jsx";
import { useGuestAuth } from "../context/GuestAuthContext.jsx";
import GuestVideoSession from "./pages/GuestVideoSession.jsx";

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
    return <Navigate to="/crm/login" state={{ from: location }} replace />;
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
        to={`/crm/guest-video/${token}`}
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
    return <Navigate to="/crm/menu" state={{ from: location }} replace />;
  }
  return <Outlet />;
}

function LimitedRoute() {
  const { userRole } = useAuth();
  const location = useLocation();
  if (!["limited", "standard", "admin"].includes(userRole)) {
    return <Navigate to="/crm/menu" state={{ from: location }} replace />;
  }
  return <Outlet />;
}

function StandardRoute() {
  const { userRole } = useAuth();
  const location = useLocation();

  if (!["standard", "admin"].includes(userRole)) {
    return <Navigate to="/crm/menu" state={{ from: location }} replace />;
  }

  return <Outlet />;
}

function AdminRoute() {
  const { userRole } = useAuth();
  const location = useLocation();

  if (userRole !== "admin") {
    return <Navigate to="/crm/menu" state={{ from: location }} replace />;
  }

  return (
    <UsersProvider>
      <Outlet />
    </UsersProvider>
  );
}

function CrmRoutes() {
  return (
    <Routes>
      {/* CRM */}
      <Route path="/" element={<Navigate to="/crm/login" replace />} />
      <Route path="/login" element={<AdminPIN />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route path="/share-links" element={<ShareViewer />} />

      {/* Guest Video */}
      <Route path="/guest-video/:patientId" element={<GuestVideoAccess />} />
      <Route element={<GuestAuthenticatedRoute />}>
        <Route path="/guest-preview/:patientId" element={<VideoPreview />} />
        <Route
          path="/guest-session/:patientId"
          element={<GuestVideoSession />}
        />
      </Route>

      {/* Authenticate Routes */}
      <Route element={<AuthenticatedRoute />}>
        <Route path="/menu" element={<AdminMenu />} />

        {/* Authenticate Routes */}
        <Route element={<LimitedRoute />}>
          <Route path="/dashboard" element={<AdminDashboard />} />
          <Route path="/file/:patientId" element={<AdminEdit />} />

          {/* Zoom Routes */}
          <Route path="/preview/:patientId" element={<VideoPreview />} />
          <Route path="/video/:patientId" element={<VideoSession />} />
        </Route>

        {/* Authenticate Routes */}
        <Route element={<GuestRoute />}>
          <Route path="/analytics" element={<AdminAnalytics />} />
        </Route>

        {/* Authenticate Routes */}
        <Route element={<StandardRoute />}>
          <Route path="/register" element={<AdminRegister />} />
        </Route>

        {/* Authenticate Routes */}
        <Route element={<AdminRoute />}>
          <Route path="/users" element={<UserManagement />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default CrmRoutes;
