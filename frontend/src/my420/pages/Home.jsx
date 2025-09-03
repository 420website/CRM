import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { Helmet } from 'react-helmet-async';

// Counter animation component
const AnimatedCounter = ({ target, duration = 2500, suffix = "" }) => {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [isVisible]);

  useEffect(() => {
    if (isVisible) {
      let startTime;
      const animate = (currentTime) => {
        if (!startTime) startTime = currentTime;
        const progress = Math.min((currentTime - startTime) / duration, 1);
        
        setCount(Math.floor(progress * target));
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      
      requestAnimationFrame(animate);
    }
  }, [isVisible, target, duration]);

  return (
    <span ref={ref}>
      {count.toLocaleString()}{suffix}
    </span>
  );
};

const Home = () => {
  // No scroll manipulation - let the App-level ScrollToTop component handle everything
  const navigate = useNavigate();
  const [dashboardClickCount, setDashboardClickCount] = useState(0);

  // Handle stats clicks for dashboard access (3 clicks)
  const handleStatsClick = (e) => {
    e.stopPropagation(); // Prevent triggering any parent click handlers
    const newCount = dashboardClickCount + 1;
    setDashboardClickCount(newCount);
    
    if (newCount >= 3) {
      // Reset counter and navigate to admin PIN entry
      setDashboardClickCount(0);
      navigate('/admin-pin');
    }
  };

  return (
    <div className="bg-white">
      <Helmet>
        <title>Free Hepatitis C Testing | Hepatitis C Ontario Services | MY420.CA</title>
        <meta name="description" content="Leading Hepatitis C testing and Hepatitis C Ontario services. Free confidential testing, 2000+ screened, 98% linked to care, 97% treatment adherence. Professional Hepatitis C program." />
        <meta name="keywords" content="hepatitis C, hepatitis c ontario, free hepatitis C testing, hepatitis C testing ontario, confidential hepatitis C, rapid hepatitis C testing, hepatitis C treatment ontario, hepatitis C services" />
        <link rel="canonical" href="https://my420.ca/" />
        <meta property="og:title" content="Free Hepatitis C Testing | Hepatitis C Ontario Services" />
        <meta property="og:description" content="Leading Hepatitis C and Hepatitis C Ontario provider. 2000+ screened, 98% linked to care, 97% treatment adherence. Free 20-minute testing." />
        <meta property="og:url" content="https://my420.ca/" />
        <meta property="og:type" content="website" />
      </Helmet>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-4">
              Free & Confidential
              <span className="block text-gray-300">Testing in 20 Minutes</span>
            </h1>
            <p className="text-xl text-gray-200 mb-4 leading-relaxed max-w-3xl mx-auto">
              Get tested for Hepatitis C and HIV in just 4 simple steps, completed in 20 minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register#registration-form"
                className="bg-white text-black hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200 text-center"
                onClick={() => {
                  sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
                }}
              >
                Register for Testing
              </Link>
              <Link
                to="/services"
                className="border-2 border-white text-white hover:bg-white hover:text-black px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200 text-center"
                onClick={() => {
                  sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
                }}
              >
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="pt-5 pb-0 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-lg shadow-lg">
            <video 
              className="w-full h-auto rounded-lg"
              autoPlay 
              muted
              loop 
              playsInline
              preload="auto"
              style={{
                aspectRatio: '9/16',
                objectFit: 'cover'
              }}
            >
              <source src="/420-video.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
          
          <div className="text-center mt-4 mb-6">
            <p className="text-lg text-gray-700 mb-6">
              Ready to get started? Our process is quick, confidential, and focused on your needs.
            </p>
            <Link
              to="/register#registration-form"
              className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200"
              onClick={() => {
                sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
              }}
            >
              Register for Testing
            </Link>
          </div>
        </div>
      </section>

      {/* Impact Statistics Section */}
      <section className="pt-4 pb-4 bg-black text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-white mb-4">
              Our Impact
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Since our program began, we've<br />made a real difference in the<br />communities we service.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="text-center bg-gray-900 rounded-lg p-8 border border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors duration-200" onClick={handleStatsClick}>
              <div className="text-4xl font-bold text-white mb-2">
                <AnimatedCounter target={2000} suffix="+" />
              </div>
              <div className="text-gray-300 text-lg">Participants Screened</div>
              <div className="text-gray-400 text-sm mt-2">People who inject/share drug equipment</div>
            </div>
            
            <div className="text-center bg-gray-900 rounded-lg p-8 border border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors duration-200" onClick={handleStatsClick}>
              <div className="text-4xl font-bold text-white mb-2">
                <AnimatedCounter target={98} suffix="%" />
              </div>
              <div className="text-gray-300 text-lg">Linked to Care</div>
              <div className="text-gray-400 text-sm mt-2">Connected to Treatment</div>
            </div>
            
            <div className="text-center bg-gray-900 rounded-lg p-8 border border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors duration-200" onClick={handleStatsClick}>
              <div className="text-4xl font-bold text-white mb-2">
                <AnimatedCounter target={97} suffix="%" />
              </div>
              <div className="text-gray-300 text-lg">Treatment Adherence</div>
              <div className="text-gray-400 text-sm mt-2">Successfully Completing Treatment</div>
            </div>
            
            <div className="text-center bg-gray-900 rounded-lg p-8 border border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors duration-200" onClick={handleStatsClick}>
              <div className="text-4xl font-bold text-white mb-2">
                $<AnimatedCounter target={250000} suffix="+" />
              </div>
              <div className="text-gray-300 text-lg">Donated to People at Risk</div>
              <div className="text-gray-400 text-sm mt-2">Financial Support Provided</div>
            </div>
          </div>

          <div className="text-center mt-4 mb-4">
            <p className="text-lg text-gray-300 mb-6">
              <strong>Making a real difference in our community.</strong> Every test, every connection to care, 
              every dollar of support provided helps save lives and improve health outcomes.
            </p>
            <Link
              to="/about"
              className="bg-white text-black hover:bg-gray-100 px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200"
              onClick={() => {
                sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
                sessionStorage.setItem('freshNavigation', 'true');
                sessionStorage.setItem('wasClicked', 'true');
              }}
            >
              Learn More About Our Program
            </Link>
          </div>
        </div>
      </section>

      {/* Risk Factors Section */}
      <section className="pt-4 pb-4 bg-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-black mb-4">
              Important Facts You Should Know
            </h2>
            <p className="text-xl text-gray-700 max-w-3xl mx-auto">
              Understanding the risks helps<br />protect you and your community.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300 text-center">
              <div className="text-4xl font-bold text-black mb-3">2 in 3</div>
              <h3 className="text-lg font-semibold text-black mb-2">
                People We Screen
              </h3>
              <p className="text-gray-700 text-sm">
                Have been exposed to Hepatitis C,<br />showing how common exposure really is
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300 text-center">
              <div className="text-4xl font-bold text-black mb-3">1 in 3</div>
              <h3 className="text-lg font-semibold text-black mb-2">
                Remain Positive
              </h3>
              <p className="text-gray-700 text-sm">
                Of those exposed, continue to test<br />
                positive and need treatment
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300 text-center">
              <div className="text-4xl font-bold text-black mb-3">Most</div>
              <h3 className="text-lg font-semibold text-black mb-2">
                Don't Know
              </h3>
              <p className="text-gray-700 text-sm">
                People are unaware they can acquire<br />HCV and HIV from sharing pipes
              </p>
            </div>
          </div>

          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-black mb-4">
              Are You at Risk?
            </h2>
            <p className="text-xl text-gray-700 max-w-3xl mx-auto">
              Certain activities can increase your<br />risk of Hepatitis C and HIV. Testing<br />is recommended if you have any of<br />these risk factors.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300">
              <div className="text-black text-3xl mb-4">⚠️</div>
              <h3 className="text-lg font-semibold text-black mb-3">
                Sharing Equipment
              </h3>
              <p className="text-gray-700">
                Sharing needles, syringes, pipes, or<br />other drug equipment significantly<br />increases infection risk. Many don't<br />realize pipes transmit HCV and HIV.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300">
              <div className="text-black text-3xl mb-4">🩸</div>
              <h3 className="text-lg font-semibold text-black mb-3">
                Blood Exposure
              </h3>
              <p className="text-gray-700">
                Tattoos, piercings, or<br />medical procedures with unsterile<br />equipment can transmit infections.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300">
              <div className="text-black text-3xl mb-4">👥</div>
              <h3 className="text-lg font-semibold text-black mb-3">
                Unprotected Contact
              </h3>
              <p className="text-gray-700">
                Certain sexual activities or contact with infected blood 
                increases transmission risk.
              </p>
            </div>
          </div>

          <div className="text-center mt-4 mb-4">
            <p className="text-lg text-gray-800 mb-6">
              <strong>Remember:</strong> Many people with Hepatitis C<br />or HIV have no symptoms. Testing is the<br />only way to know your status.
            </p>
            <Link
              to="/register#registration-form"
              className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200"
              onClick={() => {
                sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
              }}
            >
              Get Tested Today
            </Link>
          </div>
        </div>
      </section>

      {/* Services Overview with Images */}
      <section className="pt-4 pb-4 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-black mb-4">
              Our Services
            </h2>
            <p className="text-xl text-gray-700">
              Comprehensive testing and support services designed with you in mind.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-8 border border-gray-300">
              <div className="mb-4">
                <img 
                  src="https://images.pexels.com/photos/8442105/pexels-photo-8442105.jpeg"
                  alt="Professional medical testing laboratory"
                  className="w-full h-48 object-cover rounded-lg"
                />
              </div>
              <h3 className="text-2xl font-bold text-black mb-4">
                🧪 Testing Services
              </h3>
              <ul className="space-y-3 text-gray-800">
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>Rapid HCV & HIV antibody testing (results in 20 minutes)</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>RNA testing for confirmation of virus</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>Pre and post-test counseling</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>Results explanation and next steps</span>
                </li>
              </ul>
            </div>

            <div className="bg-gray-50 rounded-lg p-8 border border-gray-300">
              <div className="mb-4">
                <img 
                  src="https://images.pexels.com/photos/4101143/pexels-photo-4101143.jpeg"
                  alt="Professional counseling and support for recovery"
                  className="w-full h-48 object-cover rounded-lg"
                />
              </div>
              <h3 className="text-2xl font-bold text-black mb-4">
                🤝 Support Services
              </h3>
              <ul className="space-y-3 text-gray-800">
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>Connection to treatment services</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>Harm reduction education</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>Addiction and mental health support</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-black">•</span>
                  <span>Ongoing case management</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Information Section */}
      <section className="pt-4 pb-2 bg-gray-100">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-black mb-4">
            Contact Us Today
          </h2>
          <p className="text-xl mb-6 text-gray-700">
            Ready to get tested? Have questions? Contact us for confidential support.
          </p>
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300 mb-6">
            <div className="text-black text-4xl mb-4">📞</div>
            <h3 className="text-2xl font-bold text-black mb-4">Phone, Text & Fax</h3>
            <a href="tel:1-833-420-3733" className="text-xl md:text-2xl font-bold text-black hover:text-gray-700 transition-colors">
              1-833-420-3733
            </a>
            <p className="text-gray-600 mt-2 mb-4">Same number for phone, text, and fax</p>
            <div className="bg-gray-100 rounded-lg p-4 border border-gray-300">
              <p className="text-black text-lg mb-4">
                <strong>Contact Information:</strong>
              </p>
              <p className="text-gray-700 mb-4">
                <strong>Email:</strong> support@my420.ca
              </p>
              <p className="text-gray-700">
                <strong>Hours:</strong> Available 24/7
              </p>
            </div>
          </div>
          <div className="text-center mt-4 mb-4">
            <p className="text-lg text-gray-700 mb-4">
              <strong>Get started today!</strong> Register for testing or send us a message for more information.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register#registration-form"
                className="bg-black text-white hover:bg-gray-800 px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200"
                onClick={() => {
                  sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
                }}
              >
                Register for Testing
              </Link>
              <Link
                to="/contact#contact-form"
                className="border-2 border-black text-black hover:bg-black hover:text-white px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200"
                onClick={() => {
                  sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
                }}
              >
                Send Message
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="pt-0 pb-4 bg-white text-black">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mt-4 mb-4">
            Ready to Take<br />Control of Your Health?
          </h2>
          <div className="text-center mt-4 mb-2">
            <p className="text-xl mb-6 text-gray-700">
              Registration is quick, confidential, and the first step toward getting support.
            </p>
            <Link
              to="/register#registration-form"
              className="bg-black text-white hover:bg-gray-800 px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200 inline-block"
              onClick={() => {
                sessionStorage.setItem('scrollPos/', window.pageYOffset.toString());
              }}
            >
              Register for Testing Now
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;