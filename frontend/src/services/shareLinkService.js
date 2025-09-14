import api, { apiCall } from "./api";

export const ShareLinkServices = {
  get_share_link: async (attachment_id) => {
    return apiCall(
      () => api.post("/share-links/", { attachment_id }),
      "Getting legacy data failed.",
    );
  },

  access_link: async (token) => {
    return apiCall(
      () => api.get(`/share-links/${token}`),
      "Uploading legacy data failed.",
    );
  },
};
