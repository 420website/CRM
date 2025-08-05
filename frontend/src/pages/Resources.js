import React from "react";
import { Link } from "react-router-dom";

const Resources = () => {
  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-black to-gray-800 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Resources & Education
            </h1>
            <p className="text-xl text-gray-200 max-w-3xl mx-auto">
              Knowledge is power. Learn about prevention, testing, treatment, and living well 
              with Hepatitis C and HIV for people who have been exposed.
            </p>
          </div>
        </div>
      </section>

      {/* Harm Reduction Resources */}
      <section className="pt-4 pb-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              🛡️ Harm Reduction
            </h2>
            <p className="text-xl text-gray-600">
              Practical strategies to reduce health risks and stay safer.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-red-50 rounded-lg p-6 text-center">
              <div className="text-red-600 text-3xl mb-4">💉</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Safe Injection Practices
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm text-center">
                <li>Use new, sterile needles every time</li>
                <li>Never share injection equipment</li>
                <li>Clean injection sites with alcohol</li>
                <li>Rotate injection sites</li>
                <li>Dispose of equipment safely</li>
              </ul>
            </div>

            <div className="bg-blue-50 rounded-lg p-6 text-center">
              <div className="text-blue-600 text-3xl mb-4">🧼</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Hygiene & Prevention
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm text-center">
                <li>Wash hands before and after use</li>
                <li>Use sterile water for mixing</li>
                <li>Don't share personal items</li>
                <li>Clean surfaces and equipment</li>
                <li>Use condoms during activity</li>
              </ul>
            </div>

            <div className="bg-green-50 rounded-lg p-6 text-center">
              <div className="text-green-600 text-3xl mb-4">📦</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Safer Supply Services
              </h3>
              <ul className="text-gray-700 space-y-2 text-sm text-center">
                <li>Needle and syringe programs</li>
                <li>Safe disposal containers</li>
                <li>Alcohol swabs and sterile water</li>
                <li>Condoms and dental dams</li>
                <li>Naloxone kits and training</li>
              </ul>
            </div>
          </div>

          <div className="mt-4 text-center">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-4xl mx-auto">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">
                🚨 Overdose Prevention
              </h3>
              <p className="text-yellow-700 mb-4">
                Overdoses can happen to anyone. Know the signs and how to respond.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-yellow-700">
                <div>
                  <h4 className="font-semibold">Signs of Overdose:</h4>
                  <ul className="space-y-1">
                    <li>Slow or no breathing</li>
                    <li>Blue lips or fingernails</li>
                    <li>Cold, clammy skin</li>
                    <li>Unconsciousness</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold">What to Do:</h4>
                  <ul className="space-y-1">
                    <li>Call 911 immediately</li>
                    <li>Give naloxone if available</li>
                    <li>Do rescue breathing</li>
                    <li>Stay until help arrives</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Disease Information */}
      <section className="pt-4 pb-4 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              📚 Understanding the Diseases
            </h2>
            <p className="text-xl text-gray-600">
              Learn about Hepatitis C and HIV - knowledge helps reduce stigma and fear.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Hepatitis C */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-2xl font-bold text-red-600 mb-4">
                🦠 Hepatitis C (HCV)
              </h3>
              
              <div className="space-y-3">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">What is it?</h4>
                  <p className="text-gray-700">
                    A viral infection that affects the liver. It's often called the "silent epidemic" 
                    because many people don't know they have it.
                  </p>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">How is it spread?</h4>
                  <ul className="text-gray-700 space-y-1 text-sm">
                    <li>• Blood-to-blood contact</li>
                    <li>• Sharing injection equipment</li>
                    <li>• Unsterile tattoos or piercings</li>
                    <li>• Sharing personal items (razors, toothbrushes)</li>
                    <li>• Less commonly through sexual contact</li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Symptoms</h4>
                  <p className="text-gray-700 text-sm">
                    Often no symptoms for years. When symptoms do occur: fatigue, nausea, 
                    abdominal pain, dark urine, jaundice (yellowing of eyes/skin).
                  </p>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Treatment</h4>
                  <p className="text-gray-700 text-sm">
                    Highly curable with new direct-acting antiviral (DAA) medications. 
                    Treatment is usually 8-12 weeks with cure rates over 95%.
                  </p>
                </div>
              </div>
            </div>

            {/* HIV */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-2xl font-bold text-purple-600 mb-4">
                🩸 HIV (Human Immunodeficiency Virus)
              </h3>
              
              <div className="space-y-3">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">What is it?</h4>
                  <p className="text-gray-700">
                    A virus that attacks the immune system. Without treatment, it can lead to AIDS, 
                    but with treatment, people with HIV can live normal lifespans.
                  </p>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">How is it spread?</h4>
                  <ul className="text-gray-700 space-y-1 text-sm">
                    <li>• Unprotected sexual contact</li>
                    <li>• Sharing injection equipment</li>
                    <li>• From mother to child during pregnancy/birth/breastfeeding</li>
                    <li>• Blood transfusions (very rare in Canada)</li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Symptoms</h4>
                  <p className="text-gray-700 text-sm">
                    Early symptoms may include flu-like illness. Many people have no symptoms 
                    for years. Regular testing is the only way to know.
                  </p>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Treatment</h4>
                  <p className="text-gray-700 text-sm">
                    Antiretroviral therapy (ART) can reduce viral load to undetectable levels. 
                    Undetectable = Untransmittable (U=U). People can live normal, healthy lives.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testing Information */}
      <section className="pt-4 pb-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              🧪 About Testing
            </h2>
            <p className="text-xl text-gray-600">
              Understanding what to expect when you get tested.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  When to Get Tested
                </h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>If you've shared injection equipment</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>After unprotected sexual contact</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>If you have symptoms of infection</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>As part of regular health maintenance</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>If a partner tests positive</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  What Happens During Testing
                </h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>Brief pre-test discussion</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>Quick blood test (finger prick or small blood draw)</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>Some results available immediately</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>Results explained by trained staff</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-teal-600">•</span>
                    <span>Next steps discussed if needed</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Support Resources */}
      <section className="pt-4 pb-4 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              🤝 Support & Mental Health
            </h2>
            <p className="text-xl text-gray-600">
              You don't have to face this alone. Support is available.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-black text-3xl mb-4">📞</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Contact Support
              </h3>
              <p className="text-gray-600 mb-4 text-sm">
                Call us for information, support, and to schedule testing appointments.
              </p>
              <div className="space-y-2 text-sm">
                <p><strong>Phone, Text & Fax:</strong> 1-833-420-3733</p>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-black text-3xl mb-4">👥</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Peer Support Groups
              </h3>
              <p className="text-gray-600 mb-4 text-sm">
                Connect with others who understand what you're going through.
              </p>
              <div className="space-y-1 text-sm text-gray-700">
                <p>• HIV+ support groups</p>
                <p>• Hepatitis C support networks</p>
                <p>• Recovery support groups</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* External Resources */}
      <section className="pt-4 pb-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              🔗 Additional Resources
            </h2>
            <p className="text-xl text-gray-600">
              Trusted organizations with more information and support.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                CATIE (Canadian AIDS Treatment Information Exchange)
              </h3>
              <p className="text-gray-600 mb-4 text-sm">
                Canada's source for HIV and Hepatitis C information and treatment.
              </p>
              <a href="https://www.catie.ca" 
                className="text-teal-600 hover:text-teal-800 text-sm font-medium"
                target="_blank" rel="noopener noreferrer">
                Visit CATIE.ca →
              </a>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Ontario HIV Treatment Network
              </h3>
              <p className="text-gray-600 mb-4 text-sm">
                Research and knowledge exchange for HIV care in Ontario.
              </p>
              <a href="https://www.ohtn.on.ca" 
                className="text-teal-600 hover:text-teal-800 text-sm font-medium"
                target="_blank" rel="noopener noreferrer">
                Visit OHTN →
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="pt-4 pb-4 bg-white text-black">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Knowledge + Action = Better Health
          </h2>
          <p className="text-xl mb-4 text-gray-700">
            Now that you have information, take the next step toward protecting your health.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register#registration-form"
              className="bg-black text-white hover:bg-gray-800 px-8 py-4 rounded-lg font-bold text-lg transition-colors duration-200 text-center"
            >
              Get Tested
            </Link>
            <Link
              to="/contact"
              className="border-2 border-black text-black hover:bg-black hover:text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors duration-200 text-center"
            >
              Ask Questions
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Resources;