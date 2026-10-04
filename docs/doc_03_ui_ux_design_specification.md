# HelpLink — UI/UX Design Specification
**Document ID:** DOC-03  
**Version:** 1.1  
**Status:** Approved Specification  
**Product:** HelpLink (Community Social-Impact Web Platform)  
**Visual Style:** Public-Interest Modern | Trustworthy | Minimalist | High-Contrast Accessible  

---

## 1. Visual Identity & Design Philosophy

HelpLink is designed to feel like an authoritative, clean, and welcoming public utility—a modern civic digital space rather than a noisy ad-driven directory.

Key visual attributes:
- **Trust & Clarity**: Dominant crisp backgrounds with deep slate typography and calming ocean/emerald accents.
- **Content-First Hierarchy**: High readability typography, generous padding, and prominent search inputs.
- **Card-Driven Discovery**: Information organized into structured, scannable cards with distinct badge indicators for status, location, category, and resource types.
- **Restrained Micro-interactions**: Smooth 150ms transitions on hover, clear active focus rings for keyboard users, and subtle elevate animations.

---

## 2. Color Palette & Design Tokens

```css
:root {
  /* Brand Primary & Neutrals */
  --color-brand: #0F172A;              /* Deep Slate / Charcoal */
  --color-primary: #2563EB;            /* Vibrant Public Royal Blue */
  --color-primary-hover: #1D4ED8;
  --color-accent-emerald: #059669;      /* Eco/Community Emerald Green */
  --color-accent-emerald-light: #ECFDF5;
  
  /* Backgrounds & Surfaces */
  --color-bg: #F8FAFC;                 /* Clean light grey backdrop */
  --color-surface: #FFFFFF;            /* Pure white surface */
  --color-surface-hover: #F1F5F9;

  /* Typography */
  --color-text-main: #0F172A;          /* High contrast body */
  --color-text-secondary: #475569;     /* Subtitle and helper text */
  --color-text-muted: #64748B;         /* Captions & dates */

  /* Borders & Dividers */
  --color-border: #E2E8F0;
  --color-border-hover: #CBD5E1;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03);

  /* Border Radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```
