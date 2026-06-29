// @ts-check
import path from "path";
import { themes as prismThemes } from "prism-react-renderer";

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Awesome System Prompts",
  tagline: "A curated list of system prompts for AI models",
  favicon: "img/favicon.ico",
  future: {
    v4: true,
  },
  url: "https://ruskicoder.github.io",
  baseUrl: "/system-prompts/",
  projectName: "system-prompts",
  organizationName: "ruskicoder",
  trailingSlash: false,
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  deploymentBranch: "gh-pages",
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },
  plugins: [path.resolve(__dirname, "src/plugins/dynamic-pages")],
  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/",
          sidebarPath: "./sidebars.js",
          editUrl:
            "https://github.com/ruskicoder/system-prompts/edit/master/platform-prompts/",
          exclude: ["assets/**"],
        },
        blog: false,
        theme: {
          customCss: ["./static/css/custom.css"],
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: "System Prompts",
        logo: {
          alt: "System Prompts",
          src: "img/logo.svg",
          srcDark: "img/logo-dark.svg",
        },
        items: [
          {
            href: "https://github.com/ruskicoder/system-prompts",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      prism: {
        theme: prismThemes.oneLight,
        darkTheme: prismThemes.oneDark,
      },
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: true,
        },
      },
    }),
};

export default config;
