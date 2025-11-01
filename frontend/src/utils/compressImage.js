export const compressImageToBlob = (file, maxSizeKB = 800) => {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      let { width, height } = img;
      const maxWidth = 1200;
      const maxHeight = 1600;

      if (width > maxWidth || height > maxHeight) {
        if (width > height) {
          height = height * (maxWidth / width);
          width = maxWidth;
        } else {
          width = width * (maxHeight / height);
          height = maxHeight;
        }
      }

      canvas.width = width;
      canvas.height = height;
      ctx.drawImage(img, 0, 0, width, height);

      let quality = 0.92;

      function tryCompress() {
        canvas.toBlob(
          (blob) => {
            if (!blob) return reject("Compression failed");
            // Reduce quality until under max size
            if (blob.size > maxSizeKB * 1024 && quality > 0.3) {
              quality -= 0.05;
              tryCompress();
            } else {
              resolve(blob);
            }
          },
          "image/jpeg",
          quality,
        );
      }

      tryCompress();
    };

    img.onerror = (err) => reject(err);
    img.src = URL.createObjectURL(file);
  });
};

export const compressImageToBase64 = (file, maxSizeKB = 800) => {
  return new Promise((resolve) => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      // Calculate new dimensions (increased max resolution for better quality)
      let { width, height } = img;
      const maxWidth = 1200; // Increased from 800
      const maxHeight = 1600; // Increased from 600

      // Only resize if image is larger than max dimensions
      if (width > maxWidth || height > maxHeight) {
        if (width > height) {
          if (width > maxWidth) {
            height = height * (maxWidth / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = width * (maxHeight / height);
            height = maxHeight;
          }
        }
      }

      canvas.width = width;
      canvas.height = height;

      // Draw and compress with higher quality settings
      ctx.drawImage(img, 0, 0, width, height);

      // Start with higher quality and reduce if needed
      let quality = 0.92; // Increased from 0.8 for better quality
      let compressedDataUrl;

      do {
        compressedDataUrl = canvas.toDataURL("image/jpeg", quality);
        quality -= 0.05; // Smaller steps for more gradual quality reduction
      } while (
        compressedDataUrl.length > maxSizeKB * 1024 * 1.37 &&
        quality > 0.3
      ); // Reduced minimum quality from 0.1 to 0.3

      resolve(compressedDataUrl);
    };

    img.src = URL.createObjectURL(file);
  });
};
