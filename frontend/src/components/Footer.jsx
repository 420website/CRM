import React from "react";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-black text-white border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* About Section */}
          <div className="col-span-1 md:col-span-2">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-white">my420.ca</h3>
              <p className="text-gray-400 text-sm">4 Steps in 20 Minutes</p>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed mb-4">
              Providing confidential and accessible Hepatitis C and HIV testing services 
              for people in Ontario who have been exposed. Our team includes clinicians, phlebotomists, 
              and peers with lived experience offering testing in 4 simple steps, completed in just 20 minutes.
            </p>
            <div className="text-gray-300 text-sm">
              <p><strong>Confidential</strong> • <strong>Professional</strong> • <strong>Judgment-Free</strong></p>
            </div>
            <div className="mt-4 text-gray-400 text-sm space-y-1">
              <p><strong>Our Milestones:</strong></p>
              <p>• 2,000+ at-risk people screened</p>
              <p>• 98% linked to care</p>
              <p>• 97% treatment adherence</p>
              <p>• $250,000+ donated to people at risk</p>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link 
                  to="/register#registration-form" 
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                  onClick={() => {
                    sessionStorage.setItem(`scroll-${window.location.pathname}`, window.pageYOffset.toString());
                  }}
                >
                  Register for Testing
                </Link>
              </li>
              <li>
                <Link 
                  to="/services" 
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                  onClick={() => {
                    sessionStorage.setItem(`scroll-${window.location.pathname}`, window.pageYOffset.toString());
                  }}
                >
                  Our Services
                </Link>
              </li>
              <li>
                <Link 
                  to="/resources" 
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                  onClick={() => {
                    sessionStorage.setItem(`scroll-${window.location.pathname}`, window.pageYOffset.toString());
                  }}
                >
                  Resources & Education
                </Link>
              </li>
              <li>
                <Link 
                  to="/about" 
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                  onClick={() => {
                    sessionStorage.setItem(`scroll-${window.location.pathname}`, window.pageYOffset.toString());
                  }}
                >
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Contact</h4>
            <div className="text-gray-400 text-sm space-y-2">
              <p><strong>Phone, Text & Fax:</strong> 1-833-420-3733</p>
              <p><strong>Email:</strong> support@my420.ca</p>
              <p><strong>Hours:</strong> 24/7</p>
              <p className="mt-4">
                <Link 
                  to="/contact" 
                  className="text-gray-300 hover:text-white transition-colors"
                  onClick={() => {
                    sessionStorage.setItem(`scroll-${window.location.pathname}`, window.pageYOffset.toString());
                  }}
                >
                  Send us a message →
                </Link>
              </p>
            </div>
            
            {/* Copyright */}
            <div className="mt-6 pt-4">
              <p className="text-gray-500 text-sm">© 2025 my420.ca | All rights reserved.</p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;