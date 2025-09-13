import "./App.css";
import { useEffect, useState } from "react";
import { Navigate, Routes, Route, useLocation, Outlet } from "react-router-dom";
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
import MobileOnlyWrapper from "./mobileOnlyWrapper.jsx";

function AuthenticatedRoute() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/admin-pin" state={{ from: location }} replace />;
  }

  return <Outlet />;
}

function AdminRoute() {
  const { userRole } = useAuth();
  const location = useLocation();

  if (userRole !== "admin") {
    return <Navigate to="/admin-menu" state={{ from: location }} replace />;
  }

  return <Outlet />;
}

function StandardRoute() {
  const { userRole } = useAuth();
  const location = useLocation();

  if (userRole === "guest") {
    return <Navigate to="/admin-menu" state={{ from: location }} replace />;
  }

  return <Outlet />;
}

function AppRoutes() {
  return (
    // <MobileOnlyWrapper>
    <div className="App min-h-screen bg-gray-50">
      <ScrollToTop />
      <Header />
      <main>
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
          <Route path="/share-link" element={<ShareViewer />} />

          <Route element={<AuthenticatedRoute />}>
            <Route path="/admin-menu" element={<AdminMenu />} />
            <Route path="/admin-analytics" element={<AdminAnalytics />} />
            <Route element={<StandardRoute />}>
              <Route path="/admin-register" element={<AdminRegister />} />
              <Route path="/admin-dashboard" element={<AdminDashboard />} />
              <Route
                path="/admin-edit/:registrationId"
                element={<AdminEdit />}
              />
              <Route element={<AdminRoute />}>
                <Route path="/admin-users" element={<UserManagement />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </main>
      <Footer />
    </div>
    // </MobileOnlyWrapper>
  );
}

export default AppRoutes;
