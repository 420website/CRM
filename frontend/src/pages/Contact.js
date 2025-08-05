import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Validation functions for contact form
const validateContactField = (name, value) => {
  switch (name) {
    case 'email':
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    case 'name':
      // Name should only contain letters and spaces, minimum 2 characters
      return value.trim().length >= 2 && /^[a-zA-Z\s]+$/.test(value.trim());
    case 'subject':
      return value.trim().length >= 2;
    case 'message':
      return value.trim().length >= 10;
    default:
      return value.trim().length > 0;
  }
};

// Validation icon component
const ValidationIcon = ({ isValid, hasValue }) => {
  if (!hasValue) return null;
  
  return (
    <span className={`ml-2 text-lg font-bold ${isValid ? 'text-green-600' : 'text-red-600'}`}>
      {isValid ? '✓' : '✗'}
    </span>
  );
};

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [fieldValidation, setFieldValidation] = useState({});

  // Only scroll to top on fresh navigation, not browser back/forward (unless there's a hash)
  useEffect(() => {
    if (window.location.hash) {
      // Don't interfere if there's a hash
      return;
    }
    if (window.performance && window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {
      // User came here via back/forward button, don't scroll to top
      return;
    }
    // Fresh navigation, scroll to top
    window.scrollTo(0, 0);
  }, []);

  // Auto-scroll to contact form if URL has hash
  useEffect(() => {
    if (window.location.hash === '#contact-form') {
      const element = document.getElementById('contact-form');
      if (element) {
        setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    }
  }, []);

  // Handle scroll to top when success status changes (same pattern as client registration)
  useEffect(() => {
    if (submitStatus?.type === 'success') {
      window.scrollTo(0, 0);
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    }
  }, [submitStatus]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    const isValid = validateContactField(name, value);
    const hasValue = value.trim().length > 0;
    
    setFieldValidation(prev => ({
      ...prev,
      [name]: { isValid, hasValue }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form before submission
    const formErrors = {};
    
    if (!formData.name.trim()) {
      formErrors.name = "Name is required";
    } else if (formData.name.trim().length < 2) {
      formErrors.name = "Name must be at least 2 characters";
    } else if (!/^[a-zA-Z\s]+$/.test(formData.name.trim())) {
      formErrors.name = "Name can only contain letters and spaces";
    }
    
    if (!formData.email.trim()) {
      formErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      formErrors.email = "Please enter a valid email address";
    }
    
    if (!formData.subject.trim()) {
      formErrors.subject = "Subject is required";
    } else if (formData.subject.trim().length < 2) {
      formErrors.subject = "Subject must be at least 2 characters";
    }
    
    if (!formData.message.trim()) {
      formErrors.message = "Message is required";
    } else if (formData.message.trim().length < 10) {
      formErrors.message = "Message must be at least 10 characters";
    }
    
    if (Object.keys(formErrors).length > 0) {
      setSubmitStatus({
        type: 'error',
        message: Object.values(formErrors).join(', ')
      });
      return;
    }
    
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const response = await axios.post(`${API}/contact`, formData);
      setSubmitStatus({
        type: 'success',
        message: 'Thank you for your message! We will get back to you soon.',
        messageId: response.data.message_id
      });
      setFormData({ name: "", email: "", subject: "", message: "" });
    } catch (error) {
      console.error('Contact form error:', error);
      console.error('Error response:', error.response?.data);
      
      let errorMessage = 'Sorry, there was an error sending your message. Please try again or call us directly.';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Handle validation errors (array of error objects)
          errorMessage = detail.map(err => {
            const field = err.loc?.[err.loc.length - 1] || 'field';
            const message = err.msg || 'Invalid input';
            return `${field}: ${message}`;
          }).join(', ');
        } else {
          errorMessage = JSON.stringify(detail);
        }
      }
      
      setSubmitStatus({
        type: 'error',
        message: errorMessage
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitStatus?.type === 'success') {
    return (
      <div className="min-h-screen bg-gray-100 pt-8 pb-6">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-md p-8 text-center border border-gray-300">
            <div className="text-black text-6xl mb-6">✓</div>
            <h2 className="text-3xl font-bold text-black mb-4">
              Message Sent Successfully!
            </h2>
            <p className="text-lg text-gray-800 mb-6">
              {submitStatus.message}
            </p>
            <div className="bg-gray-100 border border-gray-300 rounded-lg p-4 mb-6">
              <p className="text-sm text-black">
                <strong>Message ID:</strong> {submitStatus.messageId}
              </p>
              <p className="text-sm text-gray-700 mt-2">
                Please save this ID for your records.
              </p>
            </div>
            <button
              onClick={() => {
                setSubmitStatus(null);
                // Scroll to contact form after a brief delay to allow render
                setTimeout(() => {
                  const element = document.getElementById('contact-form');
                  if (element) {
                    // Calculate offset to show the title as well
                    const elementRect = element.getBoundingClientRect();
                    const absoluteElementTop = elementRect.top + window.pageYOffset;
                    const offset = 100; // Offset to show title above the form
                    window.scrollTo({
                      top: absoluteElementTop - offset,
                      behavior: 'smooth'
                    });
                  }
                }, 100);
              }}
              className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200"
            >
              Send Another Message
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-black to-gray-800 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Contact Us
            </h1>
            <p className="text-xl text-gray-200 max-w-3xl mx-auto">
              Have questions? Need support? We're here to help. Reach out to us anytime 
              for confidential assistance and information about our testing services.
            </p>
          </div>
        </div>
      </section>

      {/* Quick Contact Info */}
      <section className="pt-4 pb-4 bg-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-black mb-4">
              Get in Touch
            </h2>
            <p className="text-xl text-gray-700 max-w-3xl mx-auto">
              Multiple ways to reach us for support, questions, or to schedule testing.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8 border border-gray-300 text-center">
            <div className="text-black text-4xl mb-4">📞</div>
            <h3 className="text-2xl font-bold text-black mb-4">Phone, Text & Fax</h3>
            <a href="tel:1-833-420-3733" className="text-xl md:text-2xl font-bold text-black hover:text-gray-700 transition-colors">
              1-833-420-3733
            </a>
            <p className="text-gray-600 mt-2">Same number for phone, text, and fax</p>
            
            <div className="bg-gray-100 rounded-lg p-6 border border-gray-300 mt-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <h4 className="font-semibold text-black">Phone</h4>
                  <p className="text-gray-700">Call for immediate assistance</p>
                </div>
                <div>
                  <h4 className="font-semibold text-black">Text</h4>
                  <p className="text-gray-700">Text for quick questions</p>
                </div>
                <div>
                  <h4 className="font-semibold text-black">Email</h4>
                  <p className="text-gray-700">support@my420.ca</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Form and Resources */}
      <section className="pt-4 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            
            {/* Contact Form */}
            <div id="contact-form" className="bg-white rounded-lg shadow-md p-8 border border-gray-300 mb-8">
              <h2 className="text-2xl font-bold text-black mb-4">
                Send Us a Message
              </h2>
              <p className="text-gray-700 mb-4">
                Fill out the form below and we'll get back to you as soon as possible.
              </p>

              {submitStatus && (
                <div className={`p-4 rounded-lg mb-4 ${
                  submitStatus.type === 'success' 
                    ? 'bg-green-50 border border-green-300 text-green-800' 
                    : 'bg-red-50 border border-red-300 text-red-800'
                }`}>
                  {submitStatus.message}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-black mb-1">
                    Name *
                    <ValidationIcon 
                      isValid={fieldValidation.name?.isValid} 
                      hasValue={fieldValidation.name?.hasValue} 
                    />
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    required
                    className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                      fieldValidation.name?.hasValue ? 
                        (fieldValidation.name?.isValid ? 'border-green-500' : 'border-red-500') : 
                        'border-gray-400'
                    }`}
                    placeholder="Your full name (letters and spaces only)"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-black mb-1">
                    Email *
                    <ValidationIcon 
                      isValid={fieldValidation.email?.isValid} 
                      hasValue={fieldValidation.email?.hasValue} 
                    />
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    required
                    className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                      fieldValidation.email?.hasValue ? 
                        (fieldValidation.email?.isValid ? 'border-green-500' : 'border-red-500') : 
                        'border-gray-400'
                    }`}
                    placeholder="your.email@example.com"
                  />
                </div>

                <div>
                  <label htmlFor="subject" className="block text-sm font-medium text-black mb-1">
                    Subject *
                    <ValidationIcon 
                      isValid={fieldValidation.subject?.isValid} 
                      hasValue={fieldValidation.subject?.hasValue} 
                    />
                  </label>
                  <input
                    type="text"
                    id="subject"
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    required
                    className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                      fieldValidation.subject?.hasValue ? 
                        (fieldValidation.subject?.isValid ? 'border-green-500' : 'border-red-500') : 
                        'border-gray-400'
                    }`}
                    placeholder="What is your message about?"
                  />
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-black mb-1">
                    Message *
                    <ValidationIcon 
                      isValid={fieldValidation.message?.isValid} 
                      hasValue={fieldValidation.message?.hasValue} 
                    />
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    required
                    minLength={10}
                    rows={5}
                    className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                      fieldValidation.message?.hasValue ? 
                        (fieldValidation.message?.isValid ? 'border-green-500' : 'border-red-500') : 
                        'border-gray-400'
                    }`}
                    placeholder="Please provide details about your question or concern (minimum 10 characters)..."
                  />
                  <p className="mt-1 text-sm text-gray-600">
                    Minimum 10 characters required.
                  </p>
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className={`w-full py-3 px-4 rounded-md font-semibold text-white transition-colors duration-200 ${
                      isSubmitting
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black'
                    }`}
                  >
                    {isSubmitting ? 'Sending...' : 'Send Message'}
                  </button>
                </div>
              </form>
            </div>

            {/* Resources */}
            <div className="space-y-4">
              <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300">
                <div className="text-black text-3xl mb-4">📋</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Treatment Information
                </h3>
                <p className="text-gray-600 mb-4 text-sm">
                  Learn about available treatments and what to expect during the process.
                </p>
                <div className="space-y-1 text-sm text-gray-700">
                  <p>• Hepatitis C treatment options</p>
                  <p>• HIV management and care</p>
                  <p>• Treatment effectiveness and timelines</p>
                  <p>• Support during treatment</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Emergency Contact */}
      <section className="pt-4 pb-12 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-black mb-4">
            Need Immediate Help?
          </h2>
          <p className="text-xl text-gray-700 mb-4">
            If you're experiencing a medical emergency, please call 911 immediately.
          </p>
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-300">
            <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-1 gap-4 max-w-md mx-auto">
              <div className="text-center">
                <div className="text-black text-3xl mb-3">🚨</div>
                <h3 className="text-lg font-semibold text-black mb-2">Crisis Support</h3>
                <p className="text-gray-700 text-sm mb-3">
                  24/7 crisis and mental health support available
                </p>
                <p className="text-black font-semibold">
                  Crisis Line: 1-833-420-3733
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="pt-4 pb-4 bg-white text-black">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-4 text-gray-700">
            Take the first step toward better health with our confidential testing services.
          </p>
          <Link
            to="/register#registration-form"
            className="bg-black text-white hover:bg-gray-800 px-8 py-4 rounded-lg font-bold text-lg transition-colors duration-200 inline-block"
          >
            Register for Testing
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Contact;