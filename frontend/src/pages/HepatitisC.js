import React from "react";
import { Link } from "react-router-dom";
import { Helmet } from 'react-helmet-async';

const HepatitisC = () => {
  return (
    <div className="bg-white">
      <Helmet>
        <title>Hepatitis C Testing Canada | #1 Free Confidential HCV Testing Services | MY420.CA</title>
        <meta name="description" content="Canada's leading Hepatitis C testing provider. Free confidential Hepatitis C screening, rapid results, treatment connections. 2000+ screened, 98% linked to care, 97% treatment adherence since 2020." />
        <meta name="keywords" content="hepatitis C, hepatitis C testing, hepatitis C treatment, hepatitis C screening, free hepatitis C testing, confidential hepatitis C, hepatitis C clinic, hepatitis C services, hepatitis C canada, hcv testing, hepatitis c virus, rapid hepatitis c test" />
        <link rel="canonical" href="https://my420.ca/hepatitis-c" />
        <meta property="og:title" content="Hepatitis C Testing Canada | #1 Free Confidential HCV Services" />
        <meta property="og:description" content="Canada's premier Hepatitis C testing and treatment connections. Free, confidential, expert care with proven results. 2000+ people screened." />
        <meta property="og:url" content="https://my420.ca/hepatitis-c" />
        <meta property="og:type" content="website" />
        <meta property="og:image" content="https://my420.ca/logo-original.svg" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Hepatitis C Testing Canada | Free Confidential Services" />
        <meta name="twitter:description" content="Leading Hepatitis C testing provider in Canada. Free confidential screening with rapid results." />
        <meta name="robots" content="index, follow" />
        <meta name="author" content="MY420.CA - Hepatitis C Testing Specialists" />
        <meta name="geo.region" content="CA" />
        <meta name="geo.placename" content="Canada" />
        <meta name="language" content="en-CA" />
        <script type="application/ld+json">
          {`
            {
              "@context": "https://schema.org",
              "@type": "MedicalOrganization",
              "name": "MY420.CA Hepatitis C Testing",
              "url": "https://my420.ca/hepatitis-c",
              "logo": "https://my420.ca/logo-original.svg",
              "description": "Canada's leading Hepatitis C testing and treatment connection service",
              "telephone": "1-833-420-3733",
              "email": "support@my420.ca",
              "address": {
                "@type": "PostalAddress",
                "addressCountry": "CA"
              },
              "serviceType": "Hepatitis C Testing and Treatment Services",
              "medicalSpecialty": "Infectious Disease",
              "availableService": [
                {
                  "@type": "MedicalTest",
                  "name": "Hepatitis C Testing",
                  "description": "Free confidential Hepatitis C screening and rapid testing"
                },
                {
                  "@type": "MedicalService", 
                  "name": "Hepatitis C Treatment Connection",
                  "description": "Connection to Hepatitis C treatment providers"
                }
              ]
            }
          `}
        </script>
      </Helmet>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-orange-600 to-red-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">
              Hepatitis C Testing Canada
            </h1>
            <h2 className="text-3xl font-semibold mb-4">
              #1 Free Confidential Hepatitis C Testing Services
            </h2>
            <p className="text-xl mb-8 max-w-4xl mx-auto">
              Canada's premier Hepatitis C testing provider. Expert Hepatitis C screening, rapid results, 
              and immediate treatment connections. Free, confidential, and professional Hepatitis C care 
              with proven outcomes: 2000+ people screened, 98% linked to care.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register#registration-form"
                className="bg-white text-red-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200"
              >
                Get Free Hepatitis C Testing
              </Link>
              <Link
                to="/contact"
                className="border-2 border-white text-white hover:bg-white hover:text-red-600 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200"
              >
                Learn About Hepatitis C
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Hepatitis C Facts Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Hepatitis C: What You Need to Know
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Hepatitis C is a viral infection that affects the liver. Early detection and treatment 
              are crucial for preventing serious health complications.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">🦠</div>
              <h3 className="text-xl font-semibold mb-3">What is Hepatitis C?</h3>
              <p className="text-gray-600">
                Hepatitis C (HCV) is a viral infection that causes liver inflammation. 
                It can lead to serious liver damage if left untreated, but is highly curable with modern treatment.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-3">Hepatitis C Statistics</h3>
              <ul className="text-gray-600 space-y-2">
                <li>• 250,000+ Canadians have Hepatitis C</li>
                <li>• 95% cure rate with treatment</li>
                <li>• Many people don't know they have it</li>
                <li>• Leading cause of liver transplants</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">💉</div>
              <h3 className="text-xl font-semibold mb-3">How is Hepatitis C Transmitted?</h3>
              <ul className="text-gray-600 space-y-2">
                <li>• Sharing needles or drug equipment</li>
                <li>• Unsterile tattoo/piercing equipment</li>
                <li>• Blood transfusions before 1992</li>
                <li>• Sharing personal care items</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Our Hepatitis C Services */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Comprehensive Hepatitis C Testing Services
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We provide complete Hepatitis C testing and support services across Canada, 
              from initial screening to treatment connections.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-red-50 rounded-lg p-8">
              <h3 className="text-2xl font-semibold mb-4 text-red-700">Free Hepatitis C Testing</h3>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="text-red-600 mr-2">✓</span>
                  Rapid Hepatitis C antibody screening
                </li>
                <li className="flex items-start">
                  <span className="text-red-600 mr-2">✓</span>
                  Hepatitis C RNA confirmatory testing
                </li>
                <li className="flex items-start">
                  <span className="text-red-600 mr-2">✓</span>
                  Results in 20 minutes or less
                </li>
                <li className="flex items-start">
                  <span className="text-red-600 mr-2">✓</span>
                  100% confidential Hepatitis C screening
                </li>
                <li className="flex items-start">
                  <span className="text-red-600 mr-2">✓</span>
                  No appointment needed
                </li>
              </ul>
            </div>

            <div className="bg-orange-50 rounded-lg p-8">
              <h3 className="text-2xl font-semibold mb-4 text-orange-700">Hepatitis C Support Services</h3>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="text-orange-600 mr-2">✓</span>
                  Direct connection to Hepatitis C treatment
                </li>
                <li className="flex items-start">
                  <span className="text-orange-600 mr-2">✓</span>
                  Hepatitis C education and counseling
                </li>
                <li className="flex items-start">
                  <span className="text-orange-600 mr-2">✓</span>
                  Navigation support for care
                </li>
                <li className="flex items-start">
                  <span className="text-orange-600 mr-2">✓</span>
                  Peer support from lived experience
                </li>
                <li className="flex items-start">
                  <span className="text-orange-600 mr-2">✓</span>
                  Follow-up care coordination
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="py-16 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              Why Choose MY420.CA for Hepatitis C Testing?
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              We're Canada's most trusted Hepatitis C testing provider with proven results and expert care.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-red-400 mb-2">2000+</div>
              <div className="text-lg font-semibold mb-2">People Screened</div>
              <div className="text-gray-400">For Hepatitis C across Canada</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-red-400 mb-2">98%</div>
              <div className="text-lg font-semibold mb-2">Linked to Care</div>
              <div className="text-gray-400">Successful treatment connections</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-red-400 mb-2">97%</div>
              <div className="text-lg font-semibold mb-2">Treatment Success</div>
              <div className="text-gray-400">Adherence to Hepatitis C treatment</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-red-400 mb-2">24/7</div>
              <div className="text-lg font-semibold mb-2">Support Available</div>
              <div className="text-gray-400">Hepatitis C questions answered</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-red-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Get Free Hepatitis C Testing Today
          </h2>
          <p className="text-xl mb-8">
            Don't wait - early detection of Hepatitis C can save your life. 
            Our free, confidential testing takes just 20 minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register#registration-form"
              className="bg-white text-red-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200"
            >
              Schedule Hepatitis C Test
            </Link>
            <a
              href="tel:1-833-420-3733"
              className="border-2 border-white text-white hover:bg-white hover:text-red-600 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200"
            >
              Call: 1-833-420-3733
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HepatitisC;