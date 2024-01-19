module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: ["eslint:recommended", "eslint-config-airbnb-base", "eslint-config-prettier"],
  parserOptions: {
    ecmaVersion: "latest",
  },
  plugins: ["html"],
  rules: {
    curly: "error",
    eqeqeq: "error",
    "func-names": "off",
    "no-param-reassign": "off",
    "no-plusplus": "off",
    "no-restricted-syntax": "off",
    "no-use-before-define": "off",
    "prefer-arrow-callback": "error",
    "prefer-const": "error",
    "prefer-template": "error",
    quotes: "off",
    "no-console": "off",
    "no-alert": "off",
  },
};
