import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Validation functions
const validateField = (name, value, formData) => {
  switch (name) {
    case 'email':
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    case 'phone_number':
      // Phone number must be exactly 10 digits (check raw digits, not formatted)
      const cleanPhone = value.replace(/\D/g, '');
      return cleanPhone.length === 10;
    case 'health_card_number':
      // Health card validation - if provided, must be 10 digits
      if (!value.trim()) return true; // Optional field
      const cleanHealthCard = value.replace(/[\s-]/g, '');
      return /^\d{10}$/.test(cleanHealthCard);
    case 'full_name':
      // Name should only contain letters and spaces, minimum 2 characters
      return value.trim().length >= 2 && /^[a-zA-Z\s]+$/.test(value.trim());
    case 'date_of_birth':
      return value && new Date(value) < new Date();
    default:
      return value.trim().length > 0;
  }
};

// Phone number formatting function (same as client intake form)
const formatPhoneNumber = (value) => {
  // Remove all non-digits
  const phoneNumber = value.replace(/\D/g, '');
  
  // Limit to 10 digits
  const limitedPhoneNumber = phoneNumber.substring(0, 10);
  
  // Format based on length
  if (limitedPhoneNumber.length === 0) {
    return '';
  } else if (limitedPhoneNumber.length <= 3) {
    return `(${limitedPhoneNumber}`;
  } else if (limitedPhoneNumber.length <= 6) {
    return `(${limitedPhoneNumber.substring(0, 3)}) ${limitedPhoneNumber.substring(3)}`;
  } else {
    return `(${limitedPhoneNumber.substring(0, 3)}) ${limitedPhoneNumber.substring(3, 6)}-${limitedPhoneNumber.substring(6)}`;
  }
};

// Postal code formatting function (Canadian format: A1A 1A1)
const formatPostalCode = (value) => {
  // Remove all non-alphanumeric characters and convert to uppercase
  const postalCode = value.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  
  // Limit to 6 characters
  const limitedPostalCode = postalCode.substring(0, 6);
  
  // Format based on length
  if (limitedPostalCode.length === 0) {
    return '';
  } else if (limitedPostalCode.length <= 3) {
    return limitedPostalCode;
  } else {
    return `${limitedPostalCode.substring(0, 3)} ${limitedPostalCode.substring(3)}`;
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

// Counter animation component
const AnimatedCounter = ({ target, duration = 2000, suffix = "" }) => {
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

const Register = () => {
  const [formData, setFormData] = useState({
    full_name: "",
    date_of_birth: "",
    health_card_number: "",
    phone_number: "",
    email: "",
    consent_given: false,
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [fieldValidation, setFieldValidation] = useState({});

  // Scroll to registration form when component mounts
  useEffect(() => {
    // More robust check for back/forward navigation
    const isBackForwardNavigation = () => {
      // Check multiple methods to detect back/forward navigation
      if (window.performance) {
        if (window.performance.navigation && window.performance.navigation.type === 1) {
          return true; // TYPE_BACK_FORWARD = 1
        }
        if (window.performance.getEntriesByType) {
          const navEntries = window.performance.getEntriesByType('navigation');
          if (navEntries.length > 0 && navEntries[0].type === 'back_forward') {
            return true;
          }
        }
      }
      
      // Fallback: Check if this is a page reload or fresh navigation
      const referrer = document.referrer;
      const currentHost = window.location.host;
      
      // If referrer is from same host and we have history, likely back navigation
      if (referrer && referrer.includes(currentHost) && window.history.length > 1) {
        // Additional check: see if we have state in session storage
        const navigationTimestamp = sessionStorage.getItem('lastNavigation');
        const now = Date.now();
        if (navigationTimestamp && (now - parseInt(navigationTimestamp)) < 100) {
          return false; // Recent programmatic navigation
        }
        return true; // Likely back button
      }
      
      return false;
    };
    
    // Don't scroll if user came via back/forward button (preserve their position)
    if (isBackForwardNavigation()) {
      return;
    }
    
    // Mark this as a fresh navigation
    sessionStorage.setItem('lastNavigation', Date.now().toString());
    
    // Check if there's a hash in the URL
    if (window.location.hash === '#registration-form') {
      const element = document.getElementById('registration-form');
      if (element) {
        // Move down slightly to hide the section above
        const elementRect = element.getBoundingClientRect();
        const absoluteElementTop = elementRect.top + window.pageYOffset;
        const offset = 15; // Smaller offset to move down and hide section above
        window.scrollTo({
          top: absoluteElementTop - offset,
          behavior: 'smooth'
        });
      }
    } else {
      // Default behavior - scroll to form section with slight offset
      setTimeout(() => {
        const element = document.getElementById('registration-form');
        if (element) {
          // Move down slightly to hide the section above
          const elementRect = element.getBoundingClientRect();
          const absoluteElementTop = elementRect.top + window.pageYOffset;
          const offset = 15; // Smaller offset to move down and hide section above
          window.scrollTo({
            top: absoluteElementTop - offset,
            behavior: 'smooth'
          });
        }
      }, 100);
    }
  }, []);

  // Auto-scroll to top when success message is shown
  useEffect(() => {
    if (submitStatus?.type === 'success') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [submitStatus]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    let newValue = type === 'checkbox' ? checked : value;
    
    // Format phone number as user types (same as client intake form)
    if (name === 'phone_number') {
      newValue = formatPhoneNumber(value);
    }
    
    // Format postal code as user types (Canadian format: A1A 1A1)
    if (name === 'postal_code') {
      newValue = formatPostalCode(value);
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: newValue
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ""
      }));
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    const isValid = validateField(name, value, formData);
    const hasValue = value.trim().length > 0;
    
    setFieldValidation(prev => ({
      ...prev,
      [name]: { isValid, hasValue }
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.full_name.trim()) {
      newErrors.full_name = "Full name is required";
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = "Full name must be at least 2 characters";
    } else if (!/^[a-zA-Z\s]+$/.test(formData.full_name.trim())) {
      newErrors.full_name = "Full name can only contain letters and spaces";
    }

    if (!formData.date_of_birth) {
      newErrors.date_of_birth = "Date of birth is required";
    } else {
      // Create date in local timezone to avoid timezone conversion issues
      const dateParts = formData.date_of_birth.split('-');
      const birthDate = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 16 || age > 120) {
        newErrors.date_of_birth = "Please enter a valid date of birth";
      }
    }

    // Health card is now optional, but validate format if provided
    if (formData.health_card_number.trim()) {
      const cleanHealthCard = formData.health_card_number.replace(/[\s-]/g, '');
      if (!/^\d{10}$/.test(cleanHealthCard)) {
        newErrors.health_card_number = "Health card must be 10 digits";
      }
    }

    // Require either phone OR email (or both)
    const hasPhone = formData.phone_number.trim();
    const hasEmail = formData.email.trim();
    
    if (!hasPhone && !hasEmail) {
      newErrors.contact_required = "Please provide either a phone number or email address";
    }

    // Validate phone if provided - MUST be exactly 10 digits
    if (hasPhone) {
      const cleanPhone = formData.phone_number.replace(/[^\d]/g, '');
      if (cleanPhone.length !== 10) {
        newErrors.phone_number = "Phone number must be exactly 10 digits";
      }
    }

    // Validate email if provided
    if (hasEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.consent_given) {
      newErrors.consent_given = "You must give consent to proceed";
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formErrors = validateForm();
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const response = await axios.post(`${API}/register`, formData);
      
      setSubmitStatus({
        type: 'success',
        message: 'Registration successful! We will contact you soon to schedule your testing appointment.',
        registrationId: response.data.registration_id
      });
      
      // Simple scroll to top
      setTimeout(() => {
        window.scrollTo(0, 0);
      }, 100);
      
      // Reset form
      setFormData({
        full_name: "",
        date_of_birth: "",
        health_card_number: "",
        phone_number: "",
        email: "",
        consent_given: false,
      });

    } catch (error) {
      console.error('Registration error:', error);
      console.error('Error response:', error.response?.data);
      
      let errorMessage = "Registration failed. Please try again.";
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map(err => err.msg || err).join(', ');
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

  // Handle scroll to top when success status changes
  React.useEffect(() => {
    if (submitStatus?.type === 'success') {
      window.scrollTo(0, 0);
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    }
  }, [submitStatus]);

  if (submitStatus?.type === 'success') {
    return (
      <div className="min-h-screen bg-gray-100 pt-8 pb-6">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-md p-8 text-center border border-gray-300">
            <div className="text-black text-6xl mb-6">✓</div>
            <h2 className="text-3xl font-bold text-black mb-4">
              Registration Successful!
            </h2>
            <p className="text-lg text-gray-800 mb-6">
              Thank you for registering! We will contact you soon to schedule your testing appointment.
            </p>
            <div className="bg-gray-100 border border-gray-300 rounded-lg p-4 mb-6">
              <p className="text-sm text-black">
                <strong>Registration ID:</strong> {submitStatus.registrationId || 'Pending'}
              </p>
              <p className="text-sm text-gray-700 mt-2">
                Please save this ID for your records.
              </p>
            </div>
            <button
              onClick={() => {
                setSubmitStatus(null);
              }}
              className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200"
            >
              Register Another Person
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Hero Banner */}
      <section className="bg-gradient-to-r from-black to-gray-800 text-white py-8 lg:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">
              Are you at risk?
            </h1>
            <p className="text-xl text-gray-200">
              If you share drug equipment you are at high risk and should be tested
            </p>
          </div>
        </div>
      </section>
      
      <div className="py-6">
        <div className="max-w-4xl lg:max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-12">
          
          {/* Left Column - Hero Image and Stats */}
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow-md px-8 pb-8 pt-4 border border-gray-300">
              <img 
                src="https://images.pexels.com/photos/7578808/pexels-photo-7578808.jpeg"
                alt="Professional healthcare consultation"
                className="w-full h-64 object-cover rounded-lg mb-6"
              />
              <h2 className="text-2xl font-bold text-black mb-4">
                Join 2,000+ At-Risk People in Ontario We've Helped
              </h2>
              <p className="text-gray-700 mb-6">
                Our program has successfully screened thousands of at-risk people across Ontario and connected 
                them to treatment and support services.
              </p>
              
              <div className="bg-black text-white rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Our Impact</h3>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold">
                      <AnimatedCounter target={2000} suffix="+" />
                    </div>
                    <div className="text-sm text-gray-300">At-Risk People in Ontario</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      <AnimatedCounter target={94} suffix="%" />
                    </div>
                    <div className="text-sm text-gray-300">Connected to Care</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Registration Form */}
          <div id="registration-form" className="bg-white rounded-lg shadow-md p-8 border border-gray-300">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-black mb-4">
                Register for Testing
              </h1>
              <p className="text-lg text-gray-700">
                Complete this form to register for free and confidential Hepatitis C and HIV testing and treatment.
              </p>
            </div>

            {submitStatus?.type === 'error' && (
              <div className="bg-red-50 border border-red-300 rounded-lg p-4 mb-6">
                <p className="text-red-800">{submitStatus.message}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Full Name */}
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-black mb-1">
                  Full Name *
                  <ValidationIcon 
                    isValid={fieldValidation.full_name?.isValid} 
                    hasValue={fieldValidation.full_name?.hasValue} 
                  />
                </label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                    errors.full_name ? 'border-red-500' : 
                    fieldValidation.full_name?.hasValue ? 
                      (fieldValidation.full_name?.isValid ? 'border-green-500' : 'border-red-500') : 
                      'border-gray-400'
                  }`}
                  placeholder="Enter your full name (letters and spaces only)"
                />
                {errors.full_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.full_name}</p>
                )}
              </div>

              {/* Date of Birth */}
              <div>
                <label htmlFor="date_of_birth" className="block text-sm font-medium text-black mb-1">
                  Date of Birth *
                  <ValidationIcon 
                    isValid={fieldValidation.date_of_birth?.isValid} 
                    hasValue={fieldValidation.date_of_birth?.hasValue} 
                  />
                </label>
                <input
                  type="date"
                  id="date_of_birth"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                    errors.date_of_birth ? 'border-red-500' : 
                    fieldValidation.date_of_birth?.hasValue ? 
                      (fieldValidation.date_of_birth?.isValid ? 'border-green-500' : 'border-red-500') : 
                      'border-gray-400'
                  }`}
                />
                {errors.date_of_birth && (
                  <p className="mt-1 text-sm text-red-600">{errors.date_of_birth}</p>
                )}
              </div>

              {/* Health Card Number */}
              <div>
                <label htmlFor="health_card_number" className="block text-sm font-medium text-black mb-1">
                  Health Card Number (Optional)
                  <ValidationIcon 
                    isValid={fieldValidation.health_card_number?.isValid} 
                    hasValue={fieldValidation.health_card_number?.hasValue} 
                  />
                </label>
                <input
                  type="text"
                  id="health_card_number"
                  name="health_card_number"
                  value={formData.health_card_number}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                    errors.health_card_number ? 'border-red-500' : 
                    fieldValidation.health_card_number?.hasValue ? 
                      (fieldValidation.health_card_number?.isValid ? 'border-green-500' : 'border-red-500') : 
                      'border-gray-400'
                  }`}
                  placeholder="Enter your health card number (if available)"
                />
                {errors.health_card_number && (
                  <p className="mt-1 text-sm text-red-600">{errors.health_card_number}</p>
                )}
                <p className="mt-1 text-sm text-gray-600">
                  10 digits (spaces and dashes will be removed).
                </p>
              </div>

              {/* Contact Information Notice */}
              {errors.contact_required && (
                <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4">
                  <p className="text-yellow-800">{errors.contact_required}</p>
                </div>
              )}

              {/* Phone Number */}
              <div>
                <label htmlFor="phone_number" className="block text-sm font-medium text-black mb-1">
                  Phone Number
                  <ValidationIcon 
                    isValid={fieldValidation.phone_number?.isValid} 
                    hasValue={fieldValidation.phone_number?.hasValue} 
                  />
                </label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                    errors.phone_number ? 'border-red-500' : 
                    fieldValidation.phone_number?.hasValue ? 
                      (fieldValidation.phone_number?.isValid ? 'border-green-500' : 'border-red-500') : 
                      'border-gray-400'
                  }`}
                  placeholder="(123) 456-7890"
                  maxLength="14"
                />
                {errors.phone_number && (
                  <p className="mt-1 text-sm text-red-600">{errors.phone_number}</p>
                )}
                <p className="mt-1 text-sm text-gray-600">
                  Optional if email provided. Must be exactly 10 digits.
                </p>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-black mb-1">
                  Email Address
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
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black ${
                    errors.email ? 'border-red-500' : 
                    fieldValidation.email?.hasValue ? 
                      (fieldValidation.email?.isValid ? 'border-green-500' : 'border-red-500') : 
                      'border-gray-400'
                  }`}
                  placeholder="your.email@example.com"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                )}
                <p className="mt-1 text-sm text-gray-600">
                  Optional if phone number provided.
                </p>
              </div>

              {/* Consent */}
              <div className="bg-gray-100 rounded-lg p-6 border border-gray-400">
                <h3 className="text-lg font-semibold text-black mb-4">
                  Consent and Privacy Statement
                </h3>
                <div className="text-sm text-gray-800 space-y-2 mb-4">
                  <p>By registering for our screening services, you consent to:</p>
                  
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li><strong>Testing Services:</strong> Undergo Hepatitis C and HIV testing and/or allow us to review your medical records to determine next steps in your care</li>
                    <li><strong>Communication:</strong> Be contacted by our team regarding your testing and follow-up care</li>
                    <li><strong>Information Sharing:</strong> Have your registration details shared with our support team for scheduling and providing services</li>
                    <li><strong>Confidentiality:</strong> All personal information will be kept confidential and used only to facilitate your healthcare services</li>
                    <li><strong>Data Retention:</strong> Your information will be retained only as long as necessary, then securely disposed of</li>
                    <li><strong>Your Rights:</strong> Access and correct your information, and withdraw consent at any time</li>
                  </ul>
                </div>
                
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    id="consent_given"
                    name="consent_given"
                    checked={formData.consent_given}
                    onChange={handleChange}
                    className={`mt-1 h-4 w-4 text-black border-2 rounded focus:ring-black ${
                      errors.consent_given ? 'border-red-500' : 'border-gray-400'
                    }`}
                  />
                  <label htmlFor="consent_given" className="text-sm text-gray-800">
                    <strong>I understand and agree</strong> to the testing and privacy practices described above. *
                  </label>
                </div>
                {errors.consent_given && (
                  <p className="mt-2 text-sm text-red-600">{errors.consent_given}</p>
                )}
              </div>

              {/* Submit Button */}
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
                  {isSubmitting ? 'Submitting...' : 'Register for Testing'}
                </button>
              </div>
            </form>

            <div className="mt-3 p-4 bg-gray-100 rounded-lg border border-gray-400">
              <p className="text-sm text-black">
                <strong>Need help or have questions?</strong> Call us at 
                <strong> 1-833-420-3733</strong> or <a 
                  href="/contact" 
                  className="underline"
                  onClick={() => {
                    sessionStorage.setItem(`scroll-${window.location.pathname}`, window.pageYOffset.toString());
                  }}
                >contact us</a>.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
};

export default Register;