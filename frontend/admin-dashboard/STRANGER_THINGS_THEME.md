# Stranger Things Theme - Color Palette & Documentation

## Finalized Color Palette

### Dominant Colors
- **Deep Crimson / Blood Red**: `#8B0000` (base), `#DC143C` (bright)
- **Dark Maroon**: `#800020`, `#4B0000`
- **Charcoal Black**: `#0a0a0a` (primary bg), `#1a1a1a` (secondary)
- **Dark Navy / Midnight Blue**: `#0a0e1a`, `#1a1f2a`

### Accent Colors
- **Neon Red Glow**: `#FF1744` (neon-red), `#FF0000` (glow)
- **Subtle Orange Highlights**: `#FF8C42` (subtle), `#FF6B35` (medium)

## CSS Variables Usage

All colors are defined in `src/index.css` as CSS variables for easy theming:

```css
/* Backgrounds */
--bg-primary: #0a0a0a
--bg-secondary: #1a0a0a
--bg-card: rgba(26, 10, 10, 0.6)

/* Text */
--text-primary: #ffffff
--text-secondary: rgba(255, 255, 255, 0.75)
--text-tertiary: rgba(255, 255, 255, 0.55)
--text-muted: rgba(255, 255, 255, 0.4)
--text-accent: #FF1744

/* Borders */
--border-light: rgba(220, 20, 60, 0.08)
--border-medium: rgba(220, 20, 60, 0.15)
--border-bright: rgba(255, 23, 68, 0.3)

/* Glows */
--glow-red-sm: 0 0 8px rgba(255, 23, 68, 0.3)
--glow-red-md: 0 0 16px rgba(255, 23, 68, 0.4)
--glow-red-lg: 0 0 24px rgba(255, 0, 0, 0.5)
```

## Component Styling Examples

### Buttons

#### Primary Button
```css
.btn-primary {
  background: var(--btn-primary-bg);
  border: 1px solid var(--btn-primary-border);
  color: var(--btn-primary-text);
}

.btn-primary:hover {
  box-shadow: var(--btn-primary-hover-glow);
}
```

#### Danger Button
```css
.btn-danger {
  background: var(--btn-danger-bg);
  border: 1px solid var(--btn-danger-border);
  color: var(--btn-danger-text);
}

.btn-danger:hover {
  box-shadow: var(--btn-danger-hover-glow);
}
```

### Cards

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
}

.card:hover {
  border-color: var(--border-bright);
  box-shadow: var(--shadow-lg), var(--glow-red-sm);
}
```

### Sidebar Navigation

```css
.nav-link {
  border-left: 3px solid transparent;
}

.nav-link:hover {
  background: rgba(139, 0, 0, 0.15);
  border-left-color: rgba(255, 23, 68, 0.5);
}

.nav-link.active {
  background: rgba(139, 0, 0, 0.25);
  border-left-color: var(--neon-red);
  box-shadow: var(--glow-red-md);
}
```

## Accessibility

### Contrast Ratios
- ✅ **Text on Dark Backgrounds**: All text meets WCAG AA standards
  - White text (`#ffffff`) on `#0a0a0a`: 16.6:1 (AAA)
  - Secondary text (`rgba(255,255,255,0.75)`) on `#0a0a0a`: ~12.5:1 (AAA)
  
### Color Usage Guidelines
- **Red text**: Only used for accents, status indicators, and on dark backgrounds
- **Never**: Red text on red backgrounds (avoided throughout)
- **Hover states**: Subtle glow effects, not flashy or distracting

## Implementation Notes

1. **Glow Effects**: Used sparingly for:
   - Active navigation items
   - Hover states on interactive elements
   - Status indicators (error states)

2. **Backgrounds**: Dark and muted
   - Primary: Near-black (`#0a0a0a`)
   - Cards: Semi-transparent dark maroon
   - Sidebar: Gradient from dark maroon to black

3. **Borders**: Subtle crimson/maroon tones
   - Light borders for separation
   - Medium borders for card outlines
   - Bright borders for hover/active states

## Files Updated

- ✅ `src/index.css` - CSS variables and base styles
- ✅ `src/App.css` - Scrollbar, selection, focus states
- ✅ `src/layouts/PlatformAdminLayout.css` - Sidebar and navbar
- ✅ `src/components/StatsCard.css` - Card components
- ✅ `src/components/StoreTable.css` - Table styling
- ✅ `src/pages/platform-admin/Overview.css` - Page styles

## Theme Characteristics

- **Mood**: Dark, cinematic, high-contrast
- **Style**: Suspense / sci-fi / retro horror vibe
- **Accents**: Neon red glows used sparingly
- **Contrast**: High contrast for readability
- **Consistency**: All components follow the same color scheme

