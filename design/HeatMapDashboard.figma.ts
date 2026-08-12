/**
 * Figma Code Connect — Heat Map Dashboard
 *
 * Maps Figma design components to Streamlit dashboard implementations.
 * Sync tokens via design/figma-tokens.json.
 *
 * @figma https://www.figma.com/design/PLACEHOLDER/Heat-Map-Dashboard
 */

import figma from "@figma/code-connect";

// ── Design Tokens ──────────────────────────────────────────────
figma.connect("color/accent/primary", {
  example: () => "#00d4ff",
  metadata: { token: "ACCENT_PRIMARY", file: "src/dashboard/design/tokens.py" },
});

figma.connect("color/background/primary", {
  example: () => "#0a0e17",
  metadata: { token: "BG_PRIMARY", file: "src/dashboard/design/tokens.py" },
});

// ── Navigation ─────────────────────────────────────────────────
figma.connect("Navigation/SidebarMenu", {
  example: () => ({
    component: "streamlit-option-menu",
    implementation: "src/dashboard/components/nav.py",
    icons: "Material Symbols (Bootstrap Icons via option_menu)",
  }),
  props: {
    items: figma.enum("Role", {
      Customer: ["Live View", "Historical Analysis", "Analytics"],
      Admin: ["Users", "Shops", "Cameras", "Live View", "Historical Analysis", "Analytics"],
    }),
  },
});

// ── Page Header ────────────────────────────────────────────────
figma.connect("Layout/PageHeader", {
  example: () => ({
    function: "page_header(title, subtitle, icon)",
    file: "src/dashboard/components/theme.py",
  }),
  props: {
    title: figma.string("Title"),
    subtitle: figma.string("Subtitle"),
    icon: figma.string("Material Symbol name"),
  },
});

// ── Metric Card ────────────────────────────────────────────────
figma.connect("Data/MetricCard", {
  example: () => ({
    component: "st.metric",
    styling: "div[data-testid='stMetric'] in theme.py",
  }),
  props: {
    label: figma.string("Label"),
    value: figma.string("Value"),
  },
});

// ── Filter Bar ─────────────────────────────────────────────────
figma.connect("Layout/FilterBar", {
  example: () => ({
    functions: ["filter_bar_start()", "filter_bar_end()"],
    file: "src/dashboard/components/theme.py",
    className: "hm-filter-bar",
  }),
});

// ── Login Card ─────────────────────────────────────────────────
figma.connect("Auth/LoginCard", {
  example: () => ({
    page: "src/dashboard/pages/login.py",
    className: "hm-login-card",
  }),
});
