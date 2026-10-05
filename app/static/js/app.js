/* HelpLink Frontend Application Logic */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Navigation Toggle
  const mobileToggle = document.getElementById('mobile-nav-toggle');
  const mobileDrawer = document.getElementById('mobile-nav-drawer');

  if (mobileToggle && mobileDrawer) {
    mobileToggle.addEventListener('click', () => {
      const isExpanded = mobileDrawer.classList.toggle('active');
      mobileToggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
    });
  }

  // 2. Toast Notification Auto Dismiss
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.3s ease';
      setTimeout(() => alert.remove(), 300);
    }, 4000);
  });

  // 3. Resource Bookmark / Save Toggle
  const saveButtons = document.querySelectorAll('.btn-save-toggle');
  saveButtons.forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const resourceId = btn.dataset.resourceId;
      if (!resourceId) return;

      try {
        const res = await fetch(`/resources/${resourceId}/toggle-save`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        if (res.status === 401) {
          window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
          return;
        }

        const data = await res.json();
        if (data.saved) {
          btn.classList.add('saved');
          btn.innerHTML = `❤️ Saved`;
          showToast('Resource saved to your bookmarks!');
        } else {
          btn.classList.remove('saved');
          btn.innerHTML = `🤍 Save`;
          showToast('Resource removed from bookmarks.');
        }
      } catch (err) {
        console.error('Failed to toggle save:', err);
      }
    });
  });

  // 4. Share Resource Functionality
  const shareButtons = document.querySelectorAll('.btn-share');
  shareButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const title = btn.dataset.title || document.title;
      const url = btn.dataset.url || window.location.href;

      if (navigator.share) {
        try {
          await navigator.share({ title: title, text: 'Check out this useful resource on HelpLink:', url: url });
        } catch (err) {
          copyToClipboard(url);
        }
      } else {
        copyToClipboard(url);
      }
    });
  });

  // 5. Report Modal & Keyboard ESC Listener
  const openReportBtn = document.getElementById('open-report-modal');
  const reportModal = document.getElementById('report-modal');
  const closeReportBtn = document.getElementById('close-report-modal');

  if (openReportBtn && reportModal) {
    openReportBtn.addEventListener('click', () => {
      reportModal.classList.add('active');
    });
  }

  if (closeReportBtn && reportModal) {
    closeReportBtn.addEventListener('click', () => {
      reportModal.classList.remove('active');
    });
  }

  if (reportModal) {
    reportModal.addEventListener('click', (e) => {
      if (e.target === reportModal) {
        reportModal.classList.remove('active');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && reportModal.classList.contains('active')) {
        reportModal.classList.remove('active');
      }
    });
  }
});

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Link copied to clipboard!');
  }).catch(() => {
    showToast('Failed to copy link.');
  });
}

function showToast(message) {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.position = 'fixed';
    toastContainer.style.bottom = '20px';
    toastContainer.style.right = '20px';
    toastContainer.style.zIndex = '9999';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = 'alert alert-info';
  toast.style.boxShadow = 'var(--shadow-lg)';
  toast.style.margin = '0 0 10px 0';
  toast.style.minWidth = '260px';
  toast.innerText = message;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
