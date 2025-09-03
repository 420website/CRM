import React from "react";
import { Link } from "react-router-dom";
import { Helmet } from 'react-helmet-async';

const HepatitisCOntario = () => {
  return (
    <div className="bg-white">
      <Helmet>
        <title>Hepatitis C Ontario | #1 Free HCV Testing & Treatment Services Ontario | MY420.CA</title>
        <meta name="description" content="Ontario's leading Hepatitis C testing provider. Free confidential Hepatitis C Ontario services across all Ontario communities. 2000+ screened, 98% linked to care, 97% treatment success rate. Expert Hepatitis C Ontario care since 2020." />
        <meta name="keywords" content="hepatitis C ontario, hepatitis c ontario, Hepatitis C Ontario testing, hepatitis C ontario treatment, hepatitis C ontario services, ontario hepatitis C, hepatitis C toronto, hepatitis C ottawa, hepatitis C hamilton, hepatitis C london ontario, free hepatitis C testing ontario" />
        <link rel="canonical" href="https://my420.ca/hepatitis-c-ontario" />
        <meta property="og:title" content="Hepatitis C Ontario | #1 Free Testing & Treatment Services" />
        <meta property="og:description" content="Ontario's premier Hepatitis C provider. Free testing, treatment connections, and support across all Ontario communities. 2000+ screened with proven results." />
        <meta property="og:url" content="https://my420.ca/hepatitis-c-ontario" />
        <meta property="og:type" content="website" />
        <meta property="og:image" content="https://my420.ca/logo-original.svg" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Hepatitis C Ontario | Free Confidential Testing" />
        <meta name="twitter:description" content="Leading Hepatitis C Ontario provider. Free confidential testing across all Ontario communities." />
        <meta name="robots" content="index, follow" />
        <meta name="author" content="MY420.CA - Hepatitis C Ontario Specialists" />
        <meta name="geo.region" content="CA-ON" />
        <meta name="geo.placename" content="Ontario, Canada" />
        <meta name="language" content="en-CA" />
        <script type="application/ld+json">
          {`
            {
              "@context": "https://schema.org",
              "@type": "MedicalOrganization",
              "name": "MY420.CA Hepatitis C Ontario Services",
              "url": "https://my420.ca/hepatitis-c-ontario",
              "logo": "https://my420.ca/logo-original.svg",
              "description": "Ontario's leading Hepatitis C testing and treatment connection service",
              "telephone": "1-833-420-3733",
              "email": "support@my420.ca",
              "address": {
                "@type": "PostalAddress",
                "addressRegion": "ON",
                "addressCountry": "CA"
              },
              "serviceType": "Hepatitis C Testing and Treatment Services",
              "medicalSpecialty": "Infectious Disease",
              "areaServed": {
                "@type": "State",
                "name": "Ontario",
                "containedInPlace": {
                  "@type": "Country",
                  "name": "Canada"
                }
              },
              "availableService": [
                {
                  "@type": "MedicalTest",
                  "name": "Hepatitis C Ontario Testing",
                  "description": "Free confidential Hepatitis C screening across Ontario"
                },
                {
                  "@type": "MedicalService", 
                  "name": "Hepatitis C Ontario Treatment Connection",
                  "description": "Connection to Hepatitis C treatment providers across Ontario"
                }
              ]
            }
          `}
        </script>
      </Helmet>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-red-600 to-red-800 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">
              Hepatitis C Ontario
            </h1>
            <h2 className="text-3xl font-semibold mb-4">
              #1 Hepatitis C Testing & Treatment Services Across Ontario
            </h2>
            <p className="text-xl mb-8 max-w-4xl mx-auto">
              Ontario's premier Hepatitis C testing and treatment connection service. 
              Free, confidential, and accessible Hepatitis C Ontario services across all Ontario communities. 
              2000+ people screened with 98% linked to care and 97% treatment success rate.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register#registration-form"
                className="bg-white text-red-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200"
              >
                Get Free Hepatitis C Testing Ontario
              </Link>
              <Link
                to="/contact"
                className="border-2 border-white text-white hover:bg-white hover:text-red-600 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200"
              >
                Learn About Hepatitis C Ontario
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Ontario Coverage Map */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Hepatitis C Ontario: Serving All Communities
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We provide Hepatitis C Ontario services across all regions, from major cities to rural communities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">🏙️</div>
              <h3 className="text-xl font-semibold mb-3">Greater Toronto Area</h3>
              <p className="text-gray-600 mb-4">
                Comprehensive Hepatitis C Ontario services throughout the GTA including Toronto, 
                Mississauga, Brampton, Markham, and surrounding areas.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Hepatitis C Toronto testing</li>
                <li>• Same-day results available</li>
                <li>• Multiple access points</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">🏛️</div>
              <h3 className="text-xl font-semibold mb-3">Ottawa & Eastern Ontario</h3>
              <p className="text-gray-600 mb-4">
                Hepatitis C Ontario services in Ottawa, Kingston, Cornwall, and throughout Eastern Ontario 
                with bilingual support available.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Hepatitis C Ottawa testing</li>
                <li>• French/English services</li>
                <li>• Rapid treatment connections</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">🏭</div>
              <h3 className="text-xl font-semibold mb-3">Southwestern Ontario</h3>
              <p className="text-gray-600 mb-4">
                Hepatitis C Ontario coverage in London, Windsor, Sarnia, Chatham, and surrounding 
                Southwestern Ontario communities.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Hepatitis C London Ontario testing</li>
                <li>• Border community access</li>
                <li>• Agricultural worker programs</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">⚓</div>
              <h3 className="text-xl font-semibold mb-3">Hamilton & Niagara</h3>
              <p className="text-gray-600 mb-4">
                Hepatitis C Ontario services in Hamilton, St. Catharines, Niagara Falls, 
                and throughout the Greater Hamilton Area.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Hepatitis C Hamilton testing</li>
                <li>• Industrial worker outreach</li>
                <li>• Cross-border coordination</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">🌲</div>
              <h3 className="text-xl font-semibold mb-3">Northern Ontario</h3>
              <p className="text-gray-600 mb-4">
                Hepatitis C Ontario services extending to Sudbury, Thunder Bay, Sault Ste. Marie, 
                and remote Northern Ontario communities.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Remote community access</li>
                <li>• Mobile testing units</li>
                <li>• Indigenous community support</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-4xl mb-4">🌾</div>
              <h3 className="text-xl font-semibold mb-3">Central Ontario</h3>
              <p className="text-gray-600 mb-4">
                Hepatitis C Ontario coverage in Barrie, Orillia, Peterborough, and throughout 
                Central Ontario including cottage country.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Rural community outreach</li>
                <li>• Seasonal population support</li>
                <li>• Mobile clinic services</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Hepatitis C Ontario Statistics */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Hepatitis C Ontario: By the Numbers
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our proven track record of Hepatitis C Ontario care demonstrates our commitment 
              to eliminating Hepatitis C across Ontario.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center bg-red-50 rounded-lg p-8">
              <div className="text-4xl font-bold text-red-600 mb-2">44,000+</div>
              <div className="text-lg font-semibold mb-2">Ontarians with Hepatitis C</div>
              <div className="text-gray-600">Estimated current cases in Ontario</div>
            </div>
            <div className="text-center bg-red-50 rounded-lg p-8">
              <div className="text-4xl font-bold text-red-600 mb-2">2000+</div>
              <div className="text-lg font-semibold mb-2">Tested by MY420.CA</div>
              <div className="text-gray-600">Ontarians screened for Hepatitis C</div>
            </div>
            <div className="text-center bg-red-50 rounded-lg p-8">
              <div className="text-4xl font-bold text-red-600 mb-2">98%</div>
              <div className="text-lg font-semibold mb-2">Linked to Care</div>
              <div className="text-gray-600">Successfully connected to treatment</div>
            </div>
            <div className="text-center bg-red-50 rounded-lg p-8">
              <div className="text-4xl font-bold text-red-600 mb-2">97%</div>
              <div className="text-lg font-semibold mb-2">Treatment Success</div>
              <div className="text-gray-600">Hepatitis C cure rate in Ontario</div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Hepatitis C Ontario Testing Matters */}
      <section className="py-16 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              Why Hepatitis C Ontario Testing is Critical
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Ontario has specific Hepatitis C challenges that make testing and treatment crucial 
              for public health and individual wellbeing.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-gray-800 rounded-lg p-8">
              <h3 className="text-2xl font-semibold mb-4 text-red-400">Ontario Hepatitis C Risk Factors</h3>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Large urban populations with injection drug use
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Historical blood transfusion cases (pre-1992)
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Immigration from high-prevalence countries
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Correctional facility populations
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Unregulated tattoo and piercing practices
                </li>
              </ul>
            </div>

            <div className="bg-gray-800 rounded-lg p-8">
              <h3 className="text-2xl font-semibold mb-4 text-red-400">Hepatitis C Ontario Treatment Benefits</h3>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  95%+ cure rate with modern medications
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  OHIP coverage for treatment medications
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Prevents liver cirrhosis and cancer
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Reduces transmission to others
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  Improves quality of life dramatically
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-red-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Get Free Hepatitis C Ontario Testing Today
          </h2>
          <p className="text-xl mb-8">
            Join thousands of Ontarians who have taken control of their health with our free, 
            confidential Hepatitis C Ontario testing services. Results in 20 minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register#registration-form"
              className="bg-white text-red-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200"
            >
              Schedule Hepatitis C Ontario Test
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

export default HepatitisCOntario;