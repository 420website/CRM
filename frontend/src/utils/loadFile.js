import { PDFDocument } from "pdf-lib";

export const fetchPdfArrayBuffer = async (source) => {
  if (source instanceof File) {
    // Local file upload
    return await source.arrayBuffer();
  }

  if (
    typeof source === "string" &&
    source.startsWith("data:application/pdf;base64,")
  ) {
    // Data URL
    const base64 = source.split(",")[1];
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }

  if (typeof source === "string") {
    // Assume remote URL (e.g. presigned S3 URL)
    const response = await fetch(source);
    return await response.arrayBuffer();
  }

  throw new Error("Unsupported PDF source");
};

export const getPdfPageCount = async (source) => {
  const arrayBuffer = await fetchPdfArrayBuffer(source);
  const pdfDoc = await PDFDocument.load(arrayBuffer);
  return pdfDoc.getPageCount();
};

export const loadPDF = async (id, file, setDocumentPreview, setTotalPages) => {
  const blobUrl = URL.createObjectURL(file);

  const reader = new FileReader();
  reader.onload = async (e) => {
    const arrayBuffer = await file.arrayBuffer();
    const pdfDoc = await PDFDocument.load(arrayBuffer);

    setDocumentPreview({
      id: id,
      type: "application/pdf",
      url: blobUrl,
      filename: file.name,
      is_local: true,
    });

    setTotalPages(pdfDoc.getPageCount());

    pdfDoc.destroy();
  };
  reader.readAsDataURL(file); // pdf.js requires ArrayBuffer
};

export const loadImage = (id, file, setDocumentPreview) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    setDocumentPreview({
      id: id,
      type: "image",
      url: e.target.result,
      filename: file.name,
    });
  };
  reader.readAsDataURL(file);
};

export const loadWord = (file, setDocumentPreview) => {
  const blobUrl = URL.createObjectURL(file);

  setDocumentPreview({
    type: "document",
    url: blobUrl,
    filename: file.name,
    is_local: true,
  });
};

export const loadDocument = (
  file,
  setDocumentPreview,
  setCurrentPage,
  setTotalPages,
) => {
  if (file.type.startsWith("image/")) {
    loadImage(file, setDocumentPreview);
  } else if (file.type === "application/pdf") {
    loadPDF(file, setDocumentPreview, setCurrentPage, setTotalPages);
  } else if (
    file.type ===
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
    file.type === "application/msword"
  ) {
    loadWord(file, setDocumentPreview);
  } else {
    console.warn("Unsupported file type:", file.type);
  }
};
