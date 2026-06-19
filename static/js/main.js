/**
 * NotesHub - Main JavaScript
 * Handles: navbar scroll, AOS, dark mode, search, animations, UI interactions
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Initialize AOS ──
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 700,
      easing: 'ease-out-cubic',
      once: true,
      offset: 60,
    });
  }

  // ── Navbar scroll effect ──
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }

  // ── Scroll progress bar ──
  const scrollBar = document.querySelector('.scroll-progress');
  if (scrollBar) {
    window.addEventListener('scroll', () => {
      const scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      scrollBar.style.width = scrolled + '%';
    }, { passive: true });
  }

  // ── Counter animation ──
  const counters = document.querySelectorAll('[data-count]');
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.dataset.count);
        animateCounter(el, target);
        counterObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => counterObserver.observe(c));

  function animateCounter(el, target) {
    const duration = 2000;
    const start = 0;
    const startTime = performance.now();
    const format = el.dataset.format || '';

    const update = (time) => {
      const elapsed = time - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(start + (target - start) * eased);
      el.textContent = current.toLocaleString() + format;
      if (progress < 1) requestAnimationFrame(update);
      else el.textContent = target.toLocaleString() + format;
    };
    requestAnimationFrame(update);
  }

  // ── Search debounce ──
  const searchInput = document.querySelector('#search-input');
  if (searchInput) {
    let timeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        const form = searchInput.closest('form');
        if (form && e.target.value.length >= 3) {
          // Optionally trigger live search
        }
      }, 400);
    });
  }

  // ── Hero search shortcut ──
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const heroSearch = document.querySelector('.hero-search-input');
      if (heroSearch) heroSearch.focus();
    }
  });

  // ── File upload drag & drop ──
  const dropzone = document.querySelector('.dropzone');
  if (dropzone) {
    const fileInput = dropzone.querySelector('input[type="file"]');
    const fileLabel = dropzone.querySelector('.dropzone-label');

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (fileInput && e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        updateFileLabel(fileInput, fileLabel);
      }
    });

    if (fileInput) {
      fileInput.addEventListener('change', () => updateFileLabel(fileInput, fileLabel));
    }
  }

  function updateFileLabel(input, label) {
    if (input.files && input.files[0] && label) {
      const file = input.files[0];
      const sizeKB = (file.size / 1024).toFixed(1);
      const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
      label.innerHTML = `
        <i class="bi bi-file-earmark-check-fill text-success me-2"></i>
        <strong>${file.name}</strong>
        <span class="text-muted ms-2">(${sizeMB > 1 ? sizeMB + ' MB' : sizeKB + ' KB'})</span>
      `;
    }
  }

  // ── Toast notifications ──
  window.showToast = function(message, type = 'success', duration = 4000) {
    const container = document.querySelector('.toast-container') || createToastContainer();
    const toast = document.createElement('div');
    const icons = { success: 'check-circle-fill', danger: 'x-circle-fill', warning: 'exclamation-triangle-fill', info: 'info-circle-fill' };
    toast.className = `alert alert-${type} notif-toast d-flex align-items-center gap-2 shadow mb-2`;
    toast.style.cssText = 'max-width: 360px; border-radius: 12px; pointer-events: all;';
    toast.innerHTML = `<i class="bi bi-${icons[type] || 'info-circle-fill'}"></i><span>${message}</span>
      <button type="button" class="btn-close btn-close-white ms-auto" style="font-size:0.7rem;"></button>`;
    toast.querySelector('.btn-close').addEventListener('click', () => dismissToast(toast));
    container.appendChild(toast);
    setTimeout(() => dismissToast(toast), duration);
  };

  function createToastContainer() {
    const c = document.createElement('div');
    c.className = 'toast-container';
    document.body.appendChild(c);
    return c;
  }

  function dismissToast(toast) {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(120%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }

  // ── Reply toggle ──
  document.querySelectorAll('.reply-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const commentId = btn.dataset.commentId;
      const form = document.querySelector(`#reply-form-${commentId}`);
      if (form) {
        form.classList.toggle('d-none');
        if (!form.classList.contains('d-none')) {
          form.querySelector('textarea')?.focus();
        }
      }
    });
  });

  // ── Star rating ──
  const ratingInputs = document.querySelectorAll('.star-rating-input');
  ratingInputs.forEach(input => {
    input.addEventListener('change', async (e) => {
      const noteId = e.target.dataset.noteId;
      const rating = e.target.value;
      try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        const response = await fetch(`/notes/${noteId}/rate/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/x-www-form-urlencoded' },
          body: `rating=${rating}`,
        });
        const data = await response.json();
        if (data.success) showToast(`You rated this note ${rating} ⭐`, 'success');
      } catch (err) {
        showToast('Could not submit rating', 'danger');
      }
    });
  });

  // ── Forum upvote ──
  document.querySelectorAll('.upvote-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const answerId = btn.dataset.answerId;
      try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        const response = await fetch(`/forum/answer/${answerId}/upvote/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken },
        });
        const data = await response.json();
        btn.querySelector('.vote-count').textContent = data.count;
        btn.classList.toggle('voted', data.voted);
        showToast(data.voted ? 'Upvoted! 👍' : 'Vote removed', 'info');
      } catch (err) {
        showToast('Could not submit vote', 'danger');
      }
    });
  });

  // ── Notification badge update ──
  async function updateNotifCount() {
    if (!document.querySelector('.notif-badge')) return;
    try {
      const response = await fetch('/notifications/count/');
      const data = await response.json();
      const badge = document.querySelector('.notif-badge');
      if (badge) {
        badge.textContent = data.count;
        badge.style.display = data.count > 0 ? 'flex' : 'none';
      }
    } catch (e) {}
  }

  // Poll every 60 seconds
  if (document.body.dataset.userLoggedIn === 'true') {
    updateNotifCount();
    setInterval(updateNotifCount, 60000);
  }

  // ── Smooth anchor scroll ──
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Animate cards on scroll ──
  const cards = document.querySelectorAll('.note-card, .category-card, .glass-card');
  if ('IntersectionObserver' in window) {
    const cardObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in-up');
          cardObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    cards.forEach(card => cardObserver.observe(card));
  }

  // Auto-dismiss Django messages
  document.querySelectorAll('.auto-dismiss').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.4s';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

});
