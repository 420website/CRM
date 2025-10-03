import api, { apiCall } from "./api";

export const ShareLinkServices = {
  get_share_link: async (attachment_id) => {
    return apiCall(
      () => api.post("/share-links/", { attachment_id }),
      "Creating share link failed.",
    );
  },

  get_metadata: async (token) => {
    return apiCall(
      () => api.get(`/share-links/${token}/metadata`),
      "Getting share link metadata failed.",
    );
  },

  access_link: async (token) => {
    return apiCall(
      () =>
        api.get(`/share-links/${token}`, {
          responseType: "arraybuffer",
        }),
      "Getting share link failed.",
    );
  },
};
