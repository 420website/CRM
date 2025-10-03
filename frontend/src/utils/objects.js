import { ObjectServices } from "../services/objectService";

export const getPhoto = async (registrationId) => {
  const result = await ObjectServices.get_photo(registrationId);

  if (result.success) {
    const buffer = Buffer.from(
      photoRes.data,
      photoRes.data instanceof ArrayBuffer ? undefined : "binary",
    );

    const file = new File([buffer], newFileName, {
      type: "application/pdf",
    });
  }
};
