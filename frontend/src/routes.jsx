import "./App.css";
import { Routes, Route, Navigate } from "react-router-dom";
import { Header as My420Header } from "./my420/components/Header";
import { Footer as My420Footer } from "./my420/components/Footer";
import ScrollToTop from "./scroll.jsx";
import CrmRoutes from "./crm/routes.jsx";
import My420Routes from "./my420/routes.jsx";
import Header from "./crm/components/Header.jsx";
import Footer from "./crm/components/Footer.jsx";
import { NotFound } from "./components/NotFound.jsx";

const isMy420 = import.meta.env.VITE_IS_MY420 === "true";

function AppRoutes() {
  return (
    <div className="App min-h-screen flex flex-col bg-gray-50">
      <ScrollToTop />
      {isMy420 ? <My420Header /> : <Header />}
      <main className="flex-grow flex flex-col">
        <Routes>
          {isMy420 && <Route path="/*" element={<My420Routes />} />}
          {!isMy420 && (
            <Route path="/" element={<Navigate to="/crm" replace />} />
          )}
          <Route path="/crm/*" element={<CrmRoutes />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      {isMy420 ? <My420Footer /> : <Footer />}
    </div>
  );
}

export default AppRoutes;
