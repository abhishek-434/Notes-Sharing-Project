/**
 * NotesHub - Dark Mode Toggle
 * Persists preference in localStorage and respects system preference
 */

(function() {
  const STORAGE_KEY = 'noteshub-theme';
  const html = document.documentElement;

  // Determine initial theme
  function getInitialTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    html.setAttribute('data-bs-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);

    // Apply to body if available
    const body = document.body;
    if (body) {
      body.setAttribute('data-theme', theme);
    }

    // Update toggle icon
    const toggleIcon = document.querySelector('#dark-mode-icon');
    if (toggleIcon) {
      toggleIcon.className = theme === 'dark'
        ? 'bi bi-moon-stars-fill'
        : 'bi bi-sun-fill';
    }

    const toggle = document.querySelector('.dark-toggle');
    if (toggle) {
      toggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }

  // Apply immediately to prevent flash
  const initialTheme = getInitialTheme();
  applyTheme(initialTheme);

  // Setup toggle after DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
    // Sync body theme
    if (document.body) {
      document.body.setAttribute('data-theme', initialTheme);
    }

    const toggleBtn = document.querySelector('.dark-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const current = html.getAttribute('data-theme') || 'dark';
        applyTheme(current === 'dark' ? 'light' : 'dark');
      });
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
      if (!localStorage.getItem(STORAGE_KEY)) {
        applyTheme(e.matches ? 'light' : 'dark');
      }
    });
  });
})();

