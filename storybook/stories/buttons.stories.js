import buttonHtml from "../html/govuk-button.html?raw";

export default {
  title: "GOV.UK/Button",
  parameters: {
    docs: {
      description: {
        component:
          "A button component styled according to GOV.UK design standards.",
      },
    },
  },
};

export const Primary = () => buttonHtml;
