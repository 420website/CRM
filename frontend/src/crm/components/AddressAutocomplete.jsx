import "./AddressAutocomplete.css";
import { useEffect, useRef } from "react";

// Needed b/c for postal code there are two spaces
// the second should not be split on
function splitFirstSpace(str) {
  const idx = str.indexOf(" ");
  if (idx === -1) return [str, ""];
  return [str.substring(0, idx), str.substring(idx + 1)];
}

const AddressAutocomplete = ({ onPlaceSelected }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    const initializeAutocomplete = async () => {
      if (!containerRef.current || !window.google) return;

      // Load Places library
      await google.maps.importLibrary("places");

      // Create the autocomplete element
      const placeAutocomplete =
        new google.maps.places.PlaceAutocompleteElement();
      placeAutocomplete.background;
      containerRef.current.appendChild(placeAutocomplete);

      // Listen for selection
      placeAutocomplete.addEventListener(
        "gmp-select",
        async ({ placePrediction }) => {
          const place = placePrediction.toPlace();
          await place.fetchFields({
            fields: ["formattedAddress"], // Could include "display"
          });

          if (onPlaceSelected) {
            let components = place.formattedAddress
              .split(",")
              .map((item) => item.trim());
            const [province, postal_code] = splitFirstSpace(components[2]);

            onPlaceSelected({
              formattedAddress: place.formattedAddress,
              displayName: components[0],
              city: components[1],
              province: province,
              postal_code: postal_code,
              country: components[3],
            });
          }
        },
      );
    };

    initializeAutocomplete();

    // Cleanup on unmount
    return () => {
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [onPlaceSelected]);

  return <div ref={containerRef} />;
};

export default AddressAutocomplete;
