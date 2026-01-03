import "../App.css";
import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import About from "./pages/About";
import Services from "./pages/Services";
import Register from "./pages/Register";
import Contact from "./pages/Contact";
import Resources from "./pages/Resources";
import HepatitisC from "./pages/HepatitisC";
import HepatitisCOntario from "./pages/HepatitisCOntario";

function My420Routes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="/services" element={<Services />} />
      <Route path="/register" element={<Register />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/resources" element={<Resources />} />
      <Route path="/hepatitis-c" element={<HepatitisC />} />
      <Route path="/hepatitis-c-ontario" element={<HepatitisCOntario />} />
    </Routes>
  );
}

export default My420Routes;
