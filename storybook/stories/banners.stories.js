import alertBannerHtml from "../html/alert-banner.html?raw";
import alertBannerErrorHtml from "../html/alert-banner-error.html?raw";
import alertBannerSuccessHtml from "../html/alert-banner-success.html?raw";

import bellyBandHtml from "../html/belly-band.html?raw";

export default {
  title: "AYR/Banners",
  parameters: {
    docs: {
      description: {
        component:
          "A collection of banner components styled according to AYR design standards.",
      },
    },
  },
};

export const AlertBannerDefault = () => alertBannerHtml;
export const AlertBannerErrorHtml = () => alertBannerErrorHtml;
export const AlertBannerSuccessHtml = () => alertBannerSuccessHtml;

export const BellyBand = () => bellyBandHtml;
