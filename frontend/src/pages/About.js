import React, { useEffect } from "react";
import { Link } from "react-router-dom";

const About = () => {
  // Force scroll to top on fresh navigation
  useEffect(() => {
    // Check if this is marked as fresh navigation from a button click
    const isFreshNavigation = sessionStorage.getItem('freshNavigation') === 'true';
    
    // Clear the fresh navigation flag immediately
    sessionStorage.removeItem('freshNavigation');
    
    if (isFreshNavigation) {
      // Force immediate scroll to top for button clicks
      window.scrollTo(0, 0);
      // Also force it after a short delay to ensure it sticks
      setTimeout(() => {
        window.scrollTo(0, 0);
      }, 10);
      return;
    }
    
    // For any other navigation that's not back/forward, also scroll to top
    const isBackForwardNavigation = () => {
      if (window.performance && window.performance.getEntriesByType) {
        const navEntries = window.performance.getEntriesByType('navigation');
        if (navEntries.length > 0 && navEntries[0].type === 'back_forward') {
          return true;
        }
      }
      if (window.performance && window.performance.navigation) {
        if (window.performance.navigation.type === 1) {
          return true;
        }
      }
      return false;
    };

    // If not back/forward navigation, scroll to top
    if (!isBackForwardNavigation()) {
      window.scrollTo(0, 0);
      setTimeout(() => {
        window.scrollTo(0, 0);
      }, 50);
    }
  }, []);

  // Additional effect to ensure scroll to top happens after page load
  useEffect(() => {
    const isFreshNavigation = sessionStorage.getItem('wasClicked') === 'true';
    if (isFreshNavigation) {
      sessionStorage.removeItem('wasClicked');
      const forceScroll = () => {
        window.scrollTo(0, 0);
      };
      
      // Force scroll multiple times to ensure it works
      forceScroll();
      setTimeout(forceScroll, 1);
      setTimeout(forceScroll, 10);
      setTimeout(forceScroll, 50);
      setTimeout(forceScroll, 100);
    }
  }, []);

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-black to-gray-800 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              About Our Program
            </h1>
            <p className="text-xl text-gray-200 max-w-3xl mx-auto">
              We provide accessible, confidential testing and treatment services for 
              individuals at risk of Hepatitis C<br />and HIV infection.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="pt-4 pb-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Our Mission
              </h2>
              <p className="text-lg text-gray-700 mb-4 leading-relaxed">
                We believe everyone in Ontario deserves access to quality healthcare, regardless of their 
                circumstances.
              </p>
              <p className="text-lg text-gray-700 mb-4 leading-relaxed">
                Our program specifically serves individuals who may face barriers 
                to accessing traditional healthcare services, including those with a history of substance use.
              </p>
              <p className="text-lg text-gray-700 mb-4 leading-relaxed">
                We provide testing, treatment, and support services across Ontario in a judgment-free environment 
                that prioritizes dignity, respect, and confidentiality.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  to="/register#registration-form"
                  className="bg-black text-white hover:bg-gray-800 px-6 py-3 rounded-lg font-semibold transition-colors duration-200 text-center"
                >
                  Get Started
                </Link>
                <Link
                  to="/services"
                  className="border-2 border-black text-black hover:bg-black hover:text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200 text-center"
                >
                  Our Services
                </Link>
              </div>
            </div>
            <div>
              <div className="bg-gray-100 rounded-2xl px-8 pb-8 pt-2 border border-gray-300">
                <h3 className="text-2xl font-bold text-black mb-4">
                  Our Values
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <span className="text-black text-xl">🤝</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Compassion</h4>
                      <p className="text-gray-600">Treating everyone with<br />dignity and respect</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-black text-xl">🔒</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Confidentiality</h4>
                      <p className="text-gray-600">Protecting your privacy<br />and personal information</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-black text-xl">🎯</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Accessibility</h4>
                      <p className="text-gray-600">Removing barriers to<br />essential healthcare</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-black text-xl">💪</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Empowerment</h4>
                      <p className="text-gray-600">Supporting informed<br />health decisions</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Video Testimonial Section */}
      <section className="py-4 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Patient Stories
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Hear from real people whose<br />lives have been changed through<br />our testing and support services.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-100 rounded-lg p-6 shadow-lg">
              <video 
                className="w-full h-auto rounded-lg"
                controls
                preload="metadata"
                playsInline
                disablePictureInPicture
                controlsList="nodownload nofullscreen noremoteplayback"
                poster="/testimonial-poster.jpg"
                style={{
                  aspectRatio: '3/4',
                  objectFit: 'cover',
                  maxWidth: '100%',
                  maxHeight: '400px'
                }}
              >
                <source src="/testimonial-video.mov" type="video/mp4" />
                <source src="/testimonial-video.mov" type="video/quicktime" />
                Your browser does not support the video tag.
              </video>
              <p className="text-center text-sm text-gray-600 mt-4">
                Patient sharing their program experience
              </p>
            </div>

            <div className="bg-gray-100 rounded-lg p-6 shadow-lg">
              <video 
                className="w-full h-auto rounded-lg"
                controls
                preload="metadata"
                playsInline
                disablePictureInPicture
                controlsList="nodownload nofullscreen noremoteplayback"
                poster="/testimonial-poster-2.jpg"
                style={{
                  aspectRatio: '3/4',
                  objectFit: 'cover',
                  maxWidth: '100%',
                  maxHeight: '400px'
                }}
              >
                <source src="/testimonial-video-2-final.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              <p className="text-center text-sm text-gray-600 mt-4">
                Patient's journey to better<br />health with our program
              </p>
            </div>
          </div>

          <div className="text-center">
            <Link
              to="/register#registration-form"
              className="bg-black text-white hover:bg-gray-800 px-8 py-3 rounded-lg font-semibold transition-colors duration-200 inline-block"
            >
              Start Your Journey Today
            </Link>
          </div>
        </div>
      </section>

      {/* Why Testing Matters */}
      <section className="pt-4 pb-4 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Testing Matters
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Early detection and treatment can dramatically improve health outcomes 
              and prevent transmission to others.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-2xl font-bold text-red-600 mb-4">
                🦠 Hepatitis C
              </h3>
              <div className="space-y-2 text-gray-700">
                <div>
                  <h4 className="font-semibold text-gray-900">The Silent Epidemic</h4>
                  <p>Often called the "silent killer" because most people don't know they have it.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Highly Treatable</h4>
                  <p>New medications can cure Hepatitis C<br />in 8-12 weeks with minimal side effects.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Prevention is Key</h4>
                  <p>Without treatment, it can lead to liver damage, cirrhosis, and liver cancer.</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-2xl font-bold text-purple-600 mb-4">
                🩸 HIV
              </h3>
              <div className="space-y-2 text-gray-700">
                <div>
                  <h4 className="font-semibold text-gray-900">Early Detection</h4>
                  <p>Early treatment leads to better<br />outcomes and normal life expectancy.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Manageable Condition</h4>
                  <p>Modern treatments can reduce<br />viral load to undetectable levels.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Prevention Strategies</h4>
                  <p>Undetectable = Untransmittable (U=U) - treatment prevents transmission.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Harm Reduction Approach */}
      <section className="pt-4 pb-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Our Harm Reduction Approach
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We meet people where they are, without judgment, and focus on reducing 
              risks and improving health outcomes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-green-600 text-2xl">🛡️</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Risk Reduction
              </h3>
              <p className="text-gray-600">
                Practical strategies to minimize health<br />risks while respecting personal choices.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 text-2xl">🏥</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Healthcare Access
              </h3>
              <p className="text-gray-600">
                Connecting people to essential healthcare services and ongoing support.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-600 text-2xl">🎓</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Education & Support
              </h3>
              <p className="text-gray-600">
                Providing information and resources<br />to make informed health decisions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="pt-4 pb-4 bg-white text-black">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Take<br />the First Step?
          </h2>
          <p className="text-xl mb-4 text-gray-700">
            Our team is here to support you<br />through every step of the process.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register#registration-form"
              className="bg-black text-white hover:bg-gray-800 px-8 py-4 rounded-lg font-bold text-lg transition-colors duration-200 text-center"
            >
              Register for Testing
            </Link>
            <Link
              to="/contact"
              className="border-2 border-black text-black hover:bg-black hover:text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors duration-200 text-center"
            >
              Contact Us
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;