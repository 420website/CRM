import React, { useEffect, useRef, useState } from "react";
import { Loader } from "@googlemaps/js-api-loader";

const API_KEY =
  typeof import.meta !== "undefined" && import.meta.env
    ? import.meta.env?.VITE_APP_GOOGLE_PLACES_API_KEY
    : process.env.VITE_APP_GOOGLE_PLACES_API_KEY;

const AddressAutocomplete = ({
  value,
  onChange,
  onPlaceSelected,
  placeholder = "Enter address...",
  className = "",
  disabled = false,
  name = "address",
  id = "address",
}) => {
  const inputRef = useRef(null);
  const autocompleteRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const initializeAutocomplete = async () => {
      try {
        setIsLoading(true);
        setHasError(false);

        if (!API_KEY) {
          setIsLoading(false);
          return;
        }

        const loader = new Loader({
          apiKey: API_KEY,
          version: "weekly",
          libraries: ["places"],
        });

        // Simplified loading without Promise.race
        const { Autocomplete } = await loader.importLibrary("places");

        if (inputRef.current && !autocompleteRef.current) {
          autocompleteRef.current = new Autocomplete(inputRef.current, {
            types: ["address"],
            componentRestrictions: { country: ["ca", "us"] }, // Restrict to Canada and US
            fields: ["formatted_address", "address_components", "geometry"],
          });

          // Listen for place selection
          autocompleteRef.current.addListener("place_changed", () => {
            const place = autocompleteRef.current.getPlace();

            if (place.formatted_address) {
              const addressComponents = place.address_components || [];

              // Extract address components
              const addressData = {
                formatted_address: place.formatted_address,
                street_number: "",
                street_name: "",
                city: "",
                province: "",
                postal_code: "",
                country: "",
              };

              addressComponents.forEach((component) => {
                const types = component.types;

                if (types.includes("street_number")) {
                  addressData.street_number = component.long_name;
                } else if (types.includes("route")) {
                  addressData.street_name = component.long_name;
                } else if (types.includes("locality")) {
                  addressData.city = component.long_name;
                } else if (types.includes("administrative_area_level_1")) {
                  addressData.province = component.short_name;
                } else if (types.includes("postal_code")) {
                  addressData.postal_code = component.long_name;
                } else if (types.includes("country")) {
                  addressData.country = component.long_name;
                }
              });

              // Construct clean address (street number + street name)
              const cleanAddress =
                `${addressData.street_number} ${addressData.street_name}`.trim();

              // Call the callback with extracted data
              if (onPlaceSelected) {
                onPlaceSelected({
                  address: cleanAddress || place.formatted_address,
                  city: addressData.city,
                  province: addressData.province,
                  postal_code: addressData.postal_code,
                  country: addressData.country,
                  formatted_address: place.formatted_address,
                });
              } else {
                console.warn("⚠️ onPlaceSelected callback not provided");
              }
            } else {
              console.warn("⚠️ No formatted_address found in place object");
            }
          });
        }

        setIsLoading(false);
        console.log("✅ Google Places initialization complete");
      } catch (error) {
        console.error(
          "❌ Error initializing Google Places Autocomplete:",
          error,
        );
        console.log("🔄 Falling back to regular input field");
        setHasError(true);
        setIsLoading(false);

        // Show user-friendly message if API fails
        if (error.message && error.message.includes("API key")) {
          console.warn(
            "🗝️ API key issue detected - check Google Cloud Console restrictions",
          );
        }
      }
    };

    if (!disabled) {
      initializeAutocomplete();
    }

    // Cleanup
    return () => {
      if (autocompleteRef.current) {
        // Google Maps API doesn't provide a direct cleanup method for Autocomplete
        // The listener will be automatically removed when the component unmounts
        autocompleteRef.current = null;
      }
    };
  }, [disabled]); // Removed onPlaceSelected from dependencies

  const handleInputChange = (e) => {
    if (onChange) {
      onChange(e);
    }
  };

  return (
    <input
      ref={inputRef}
      type="text"
      name={name}
      id={id}
      value={value}
      onChange={handleInputChange}
      placeholder={
        hasError
          ? "Enter address (autocomplete unavailable)"
          : isLoading
            ? "Loading autocomplete..."
            : placeholder
      }
      className={className}
      disabled={disabled}
      autoComplete="off"
    />
  );
};

export default AddressAutocomplete;
