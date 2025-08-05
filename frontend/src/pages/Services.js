import React, { useEffect } from "react";
import { Link } from "react-router-dom";

const Services = () => {
  // Only scroll to top on fresh navigation, not browser back/forward
  useEffect(() => {
    if (window.performance && window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {
      // User came here via back/forward button, don't scroll to top
      return;
    }
    // Fresh navigation, scroll to top
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-black to-gray-800 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Testing Services
            </h1>
            <p className="text-xl text-gray-200 max-w-3xl mx-auto">
              Comprehensive, confidential testing and support services designed 
              for individuals with risk factors for Hepatitis C and HIV across Ontario.
            </p>
          </div>
        </div>
      </section>

      {/* Testing Services */}
      <section className="pt-4 pb-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                🧪 Available Tests
              </h2>
              
              <div className="space-y-4">
                <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-r-lg">
                  <h3 className="text-xl font-bold text-red-800 mb-3">
                    Hepatitis C Testing
                  </h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600">•</span>
                      <span><strong>Antibody Test:</strong> Shows if you've ever been exposed to Hepatitis C</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600">•</span>
                      <span><strong>RNA Test:</strong> Confirms current infection and viral load</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600">•</span>
                      <span><strong>Genotype Testing:</strong> Determines the best treatment approach</span>
                    </li>
                  </ul>
                </div>

                <div className="bg-purple-50 border-l-4 border-purple-500 p-6 rounded-r-lg">
                  <h3 className="text-xl font-bold text-purple-800 mb-3">
                    HIV Testing
                  </h3>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-start space-x-2">
                      <span className="text-purple-600">•</span>
                      <span><strong>Antibody Test:</strong> Shows if you've ever been exposed to HIV</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-purple-600">•</span>
                      <span><strong>Laboratory Test:</strong> Confirmatory testing if needed</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                📋 The 420 Process
                <span className="block text-2xl font-medium text-gray-700 mt-2">4 Steps in 20 Minutes</span>
              </h2>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="bg-black text-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg flex-shrink-0">
                    1
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Obtaining Consent</h3>
                    <p className="text-gray-600">Review and provide informed consent regarding testing procedures, privacy practices and next steps.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-black text-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg flex-shrink-0">
                    2
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Testing</h3>
                    <p className="text-gray-600">Quick and minimally invasive testing procedures performed by trained healthcare professionals.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-black text-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg flex-shrink-0">
                    3
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Education</h3>
                    <p className="text-gray-600">Receive comprehensive information about prevention strategies, risk reduction, and available treatment options.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-black text-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg flex-shrink-0">
                    4
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Results</h3>
                    <p className="text-gray-600">Receive your test results with clear explanations and connections to appropriate next steps if needed.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Support Services */}
      <section className="pt-4 pb-4 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              🤝 Support Services
            </h2>
            <p className="text-xl text-gray-600">
              We provide comprehensive support beyond just testing.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-green-600 text-3xl mb-4">🩺</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Treatment Connections
              </h3>
              <p className="text-gray-600">
                Direct referrals to specialists and treatment programs for positive results.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-3xl mb-4">📚</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Education & Resources
              </h3>
              <p className="text-gray-600">
                Information about prevention, treatment options, and living with HIV/Hepatitis C.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-purple-600 text-3xl mb-4">🧠</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Mental Health Support
              </h3>
              <p className="text-gray-600">
                Counseling and mental health resources to support overall well-being.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-orange-600 text-3xl mb-4">🏠</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Case Management
              </h3>
              <p className="text-gray-600">
                Help navigating healthcare systems and connecting to community resources.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-red-600 text-3xl mb-4">💊</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Harm Reduction
              </h3>
              <p className="text-gray-600">
                Practical strategies and supplies to reduce health risks and prevent transmission.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-teal-600 text-3xl mb-4">👥</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Peer Support
              </h3>
              <p className="text-gray-600">
                Connection with others who have similar experiences and challenges.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Locations & Hours */}
      <section className="pt-4 pb-4 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              📍 Mobile Testing
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-100 rounded-lg p-8 border border-gray-300">
              <img 
                src="/vehicle-mockup.jpg"
                alt="420 Mobile testing unit"
                className="w-full h-48 object-cover rounded-lg mb-4"
              />
              <h3 className="text-2xl font-bold text-black mb-4">
                Schedule & Locations
              </h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-900">Schedule</h4>
                  <p className="text-gray-700">Visits high-risk communities on rotating basis across Ontario</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Locations</h4>
                  <ul className="text-gray-700 space-y-1">
                    <li>• Community centers</li>
                    <li>• Harm reduction sites</li>
                    <li>• Shelters and drop-in centers</li>
                    <li>• Outreach events</li>
                    <li>• Safe consumption sites</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Contact</h4>
                  <p className="text-gray-700">Call for current schedule and locations</p>
                </div>
              </div>
            </div>

            <div className="bg-gray-200 rounded-lg p-8 border border-gray-400">
              <img 
                src="https://thelegaledgeteam.com/wp-content/uploads/2020/04/GetMedia-3-1.jpg"
                alt="Professional medical clinic interior"
                className="w-full h-48 object-cover rounded-lg mb-4"
              />
              <h3 className="text-2xl font-bold text-black mb-4">
                Head Office
              </h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-900">Address</h4>
                  <p className="text-gray-700">380 Pelissier St, Unit 204<br />Windsor, ON N9A 6V7</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Hours</h4>
                  <p className="text-gray-700">By appointment only</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Appointment</h4>
                  <p className="text-gray-700">Register online or call to schedule</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="pt-4 pb-4 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-4">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Is testing really free?
              </h3>
              <p className="text-gray-700">
                Yes, all testing services are completely 
                free. We believe financial barriers should 
                never prevent someone from knowing 
                their health status.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                How confidential is my information?
              </h3>
              <p className="text-gray-700">
                Your information is strictly confidential and 
                protected by privacy laws. We never share 
                your information without your explicit 
                consent.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                What if I test positive?
              </h3>
              <p className="text-gray-700">
                We provide immediate support, counseling, and 
                connect you with treatment services.
                <br /><br />
                Both Hepatitis C and HIV are treatable 
                with modern medications.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Can I get tested without a health card?
              </h3>
              <p className="text-gray-700">
                While we ask for health card information 
                during registration, we can provide testing 
                services if you don't have your card or 
                it's expired, as long as you are an Ontario resident.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="pt-4 pb-4 bg-black text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Get Tested?
          </h2>
          <p className="text-xl mb-4 text-gray-300">
            Take the first step toward better health. Registration is quick, easy, and confidential.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register#registration-form"
              className="bg-white text-black hover:bg-gray-100 px-8 py-4 rounded-lg font-bold text-lg transition-colors duration-200 text-center"
            >
              Register Now
            </Link>
            <Link
              to="/contact"
              className="border-2 border-white text-white hover:bg-white hover:text-black px-8 py-4 rounded-lg font-bold text-lg transition-colors duration-200 text-center"
            >
              Ask Questions
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Services;