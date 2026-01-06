# Sciemo.ai Design System Analysis

A comprehensive breakdown of the sciemo.ai website design for reference and inspiration.

---

## Platform & Framework

| Property | Value |
|----------|-------|
| **Framework** | Webflow |
| **Hosting** | Webflow CDN (cdn.prod.website-files.com) |
| **Asset ID** | 68dbe40f728e9286ccbe587b |

---

## Color Palette

### Primary Colors

| Name | Hex Value | Usage |
|------|-----------|-------|
| **Off-White** | `#F7F7F7` | Page background |
| **Near-Black** | `#1B1C1C` | Primary text, headers, card accents |
| **Coral/Salmon** | `#E8846B` | Accent color, decorative elements, CTAs |

### Secondary Colors

| Name | Hex Value | Usage |
|------|-----------|-------|
| **Light Gray** | `#E8E8E8` | Card backgrounds, subtle fills |
| **Medium Gray** | `#6B6B6B` | Secondary text |
| **White** | `#FFFFFF` | Card backgrounds, contrast elements |

### Color Ratios
- **90%** Neutral (off-white, grays, black)
- **10%** Accent (coral) - used sparingly for maximum impact

---

## Typography

### Font Stack

```css
/* Primary Fonts - Google Fonts */
font-family: 'Noto Sans', sans-serif;      /* Body text */
font-family: 'Cousine', monospace;          /* Navigation, labels */
font-family: 'Victor Mono', monospace;      /* Code-like elements */
font-family: 'IBM Plex Mono', monospace;    /* Technical text */
```

### Type Scale

| Element | Font | Size (Est.) | Weight | Style |
|---------|------|-------------|--------|-------|
| **Hero Headline** | Condensed Sans | 72-96px | 400 | Uppercase, periods after words |
| **Section Headline** | Condensed Sans | 48-64px | 400 | Uppercase, periods |
| **Card Title** | Condensed Sans | 24-32px | 400 | Uppercase |
| **Subheading/Label** | Cousine/Monospace | 12-14px | 400 | Uppercase, letter-spaced |
| **Body Text** | Noto Sans | 16-18px | 400 | Sentence case |
| **Navigation** | Cousine | 14px | 400 | Uppercase |
| **Button Text** | Cousine | 14px | 400 | Uppercase |

### Typography Characteristics
- **Headlines**: Condensed sans-serif with periods after each word ("CALCULATE. ORCHESTRATE. ACCELERATE.")
- **Labels**: Monospace, all-caps, generously letter-spaced
- **Body**: Clean sans-serif with comfortable line-height (~1.6)
- **Font smoothing**: Applied globally for crisp rendering

```css
body {
  -webkit-font-smoothing: antialiased;
  -moz-font-smoothing: antialiased;
  -o-font-smoothing: antialiased;
}
```

---

## Layout System

### Grid Structure

```
Desktop: 12-column grid, ~1200-1400px max-width
Tablet: 8-column grid
Mobile: 4-column grid
```

### Section Patterns

#### Hero Section
- Left-aligned text (60% width)
- Right-aligned decorative graphic (40% width)
- Generous vertical padding (~120-160px)

#### Feature Cards (4-Column)
```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ ░░░░░░░ │ │ ░░░░░░░ │ │ ░░░░░░░ │ │ ░░░░░░░ │  <- Dark header bar
│         │ │         │ │         │ │         │
│ Icon    │ │ Icon    │ │ Icon    │ │ Icon    │
│ Title   │ │ Title   │ │ Title   │ │ Title   │
│ Desc    │ │ Desc    │ │ Desc    │ │ Desc    │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

#### Product Sections (2-Column)
```
┌─────────────────────────┐ ┌─────────────────────────┐
│ + PRODUCTS              │ │ ░░░░░░░░░░░░░░░░░░░░░░░ │
│                         │ │                         │
│ LARGE HEADLINE          │ │ Icon                    │
│                         │ │ PRODUCT NAME            │
│ Subheading              │ │                         │
│ Body text description   │ │ Description text        │
│                         │ │                         │
│ [CTA BTN] [SEC BTN]     │ │ ☑ Metric  ☑ Metric     │
└─────────────────────────┘ └─────────────────────────┘
```

### Spacing Scale

| Size | Pixels | Usage |
|------|--------|-------|
| **xs** | 4px | Inline spacing |
| **sm** | 8px | Tight spacing |
| **md** | 16px | Default component spacing |
| **lg** | 24px | Section inner padding |
| **xl** | 48px | Between components |
| **2xl** | 80px | Section vertical padding |
| **3xl** | 120px | Hero sections |

---

## Components

### Navigation Bar

```
┌──────────────────────────────────────────────────────────────────┐
│ sciemo          ABOUT  PRODUCTS  JOIN US  INSIGHTS   [BOOK DEMO] │
└──────────────────────────────────────────────────────────────────┘
```

**Styling:**
- Sticky positioning
- Border: 1px solid black
- Background: Off-white
- Logo: Lowercase, bold
- Links: Uppercase, monospace, letter-spaced
- CTA: Bordered button with coral/orange background

### Buttons

#### Primary Button
```css
.btn-primary {
  background-color: #1B1C1C;
  color: #FFFFFF;
  padding: 12px 24px;
  font-family: 'Cousine', monospace;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: none;
}
```

#### Secondary Button
```css
.btn-secondary {
  background-color: transparent;
  color: #1B1C1C;
  padding: 12px 24px;
  font-family: 'Cousine', monospace;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid #1B1C1C;
}
```

#### CTA Button (Navigation)
```css
.btn-cta {
  background-color: #E8846B;
  color: #1B1C1C;
  padding: 12px 24px;
  border: 1px solid #1B1C1C;
}
```

### Feature Cards

```css
.feature-card {
  background-color: #E8E8E8;
  border: 1px solid #1B1C1C;
  position: relative;
}

.feature-card::before {
  /* Dark header bar */
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
  background-color: #1B1C1C;
}

.feature-card-icon {
  color: #E8846B;
  margin-bottom: 16px;
}

.feature-card-title {
  font-size: 18px;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
```

### Metric Tags/Pills

```css
.metric-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #1B1C1C;
  font-family: 'Cousine', monospace;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-tag::before {
  content: '✓';
}
```

### Section Labels

```css
.section-label {
  font-family: 'Cousine', monospace;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #1B1C1C;
}

.section-label::before {
  content: '+';
  color: #E8846B;
  margin-right: 8px;
}
```

---

## Visual Elements

### Decorative Graphics

The site uses abstract geometric illustrations featuring:
- **Circles**: Coral/salmon colored (#E8846B), varying sizes
- **Lines**: Thin black connecting lines
- **Pattern**: Node-and-edge style, suggesting data/network connections

```
Example illustration structure:

        ●─────────┐
                  │
    ●───●        ●
    │
    └────────────●
```

### Icons

- **Style**: Simple line icons, monochrome
- **Source**: Custom SVGs hosted on Webflow CDN
- **Colors**: Black primary, coral accent
- **Examples**: Checkmarks, plus signs, chat bubbles, abstract shapes

---

## Responsive Behavior

### Breakpoints (Estimated)

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| **Desktop** | >1200px | Full layout, 4-col cards |
| **Tablet** | 768-1199px | 2-col cards, reduced spacing |
| **Mobile** | <768px | 1-col, burger menu, stacked layout |

### Mobile Adaptations
- Navigation collapses to hamburger menu
- Cards stack vertically
- Headlines reduce in size
- Horizontal scrolling disabled

---

## Design Principles Summary

### 1. Minimal Color, Maximum Impact
- Two-color foundation (black + off-white)
- Single accent color used sparingly
- Color draws attention to key elements only

### 2. Technical Aesthetic
- Monospace fonts convey precision/data
- Condensed headlines feel modern/bold
- Clean geometric shapes

### 3. Generous Whitespace
- Content breathes
- Sections clearly separated
- No visual clutter

### 4. Consistent Components
- All cards follow same structure
- Buttons have clear hierarchy
- Labels use consistent styling

### 5. Bold Typography Hierarchy
- Headlines demand attention
- Clear distinction between heading levels
- Periods add distinctive rhythm to headlines

---

## Key Takeaways for Implementation

1. **Limit your palette** - 2-3 colors maximum, one accent
2. **Choose distinctive typography** - Mix condensed + monospace
3. **Use whitespace generously** - Don't fear empty space
4. **Create component consistency** - Cards, buttons, labels should feel unified
5. **Add visual interest through geometry** - Simple shapes > complex illustrations
6. **Headlines with personality** - Periods, caps, and condensed fonts create impact

---

## Assets Reference

### SVG Icons Used
- Check mark: `68dc13290ebdb8ad41541f5f_66fff690148483aab6b4d8b9_Check.svg`
- Plus: `68dc1b1aecafcc78511d62c1_6703965a66c1c5b3274a53ac_Plus.svg`
- Chat dots: `68dc1ba735551d7a857d3d1f_67039a7bd8fb552c4935857f_ChatDots.svg`
- Menu burger: `68dfc5c5df11693b43c525ca_circum_menu-burger.svg`
- Close: `68dfc5c5c23a76a9b19dc03b_system-uicons_cross.svg`

### Font Loading
```html
<link href="https://fonts.googleapis.com/css?family=Cousine:regular|Victor+Mono:regular|Noto+Sans:regular,700|IBM+Plex+Mono:regular" rel="stylesheet">
```

---

*Analysis generated from sciemo.ai - January 2026*
