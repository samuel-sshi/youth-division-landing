// Navbar scroll effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// Simple mobile menu toggle
const menuToggle = document.querySelector('.menu-toggle');
const mobileMenu = document.getElementById('mobile-menu');
const mobileMenuClose = document.querySelector('.mobile-menu-close');
const mobileMenuLinks = document.querySelectorAll('.mobile-menu-links a');

function openMenu() {
  mobileMenu.classList.add('active');
  mobileMenu.setAttribute('aria-hidden', 'false');
  menuToggle.setAttribute('aria-expanded', 'true');
  document.body.classList.add('menu-open');
}

function closeMenu() {
  mobileMenu.classList.remove('active');
  mobileMenu.setAttribute('aria-hidden', 'true');
  menuToggle.setAttribute('aria-expanded', 'false');
  document.body.classList.remove('menu-open');
}

menuToggle.addEventListener('click', openMenu);

mobileMenuLinks.forEach(link => {
  link.addEventListener('click', closeMenu);
});

// Close menu when clicking the backdrop
mobileMenu.querySelector('.mobile-menu-backdrop').addEventListener('click', closeMenu);

// Close on escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
    closeMenu();
  }
});

// ---- Upcoming Events (data-driven from events.json) ----
(function renderEvents() {
  const grid = document.getElementById('event-grid');
  const months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];

  // All date math is done on plain YYYY-MM-DD strings in WIB (Asia/Jakarta)
  // so events never disappear a day early for visitors in other timezones.
  const today = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Jakarta', year: 'numeric', month: '2-digit', day: '2-digit'
  }).format(new Date()); // en-CA yields YYYY-MM-DD

  // A valid date string must be exactly YYYY-MM-DD with a real month/day range.
  const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

  fetch('events.json?v=3', { cache: 'no-store' })
    .then(res => {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(data => {
      let events = data.events || [];

      events = events
        .filter(ev => {
          const m = ISO_DATE.exec(ev.date);
          if (!m) return false;
          const [, y, mo, da] = m;
          // Lexicographic YYYY-MM-DD comparison is timezone-proof.
          return `${y}-${mo}-${da}` >= today;
        })
        .sort((a, b) => a.date.localeCompare(b.date));

      if (events.length === 0) {
        grid.innerHTML = `
          <div class="upcoming-empty" style="grid-column: 1 / -1;">
            <p>No upcoming events yet — check back soon or follow <a href="https://www.instagram.com/oneightywtc/" target="_blank" rel="noopener" style="color: var(--accent-2);">@oneightywtc</a>.</p>
          </div>`;
        return;
      }

      grid.innerHTML = events.map((ev) => {
        // ev.date is validated YYYY-MM-DD by the filter above.
        const [, y, mo, da] = ISO_DATE.exec(ev.date);
        const month = months[parseInt(mo, 10) - 1];
        const dayNum = parseInt(da, 10);

        let pills = '';
        if (ev.time) {
          pills += `<span class="meta-pill"><span>🕒</span> ${escapeHtml(ev.time)}</span>`;
        }
        if (ev.location) {
          pills += `<span class="meta-pill muted"><span>📍</span> ${escapeHtml(ev.location)}</span>`;
        }

        const link = ev.link
          ? `<a href="${escapeHtml(ev.link)}" target="_blank" rel="noopener" class="upcoming-link">See details →</a>`
          : '';

        const hasLongDesc = ev.description && ev.description.length > 120;
        const descClass = hasLongDesc ? 'desc' : 'desc desc-short';
        const readMoreBtn = hasLongDesc
          ? '<button class="read-more" type="button" aria-expanded="false">Read more</button>'
          : '';

        return `
          <div class="upcoming-card">
            <div class="upcoming-date">
              <span class="day-num">${dayNum}</span>
              <span class="month">${month}</span>
            </div>
            <h3>${escapeHtml(ev.name)}</h3>
            ${ev.description ? `<p class="${descClass}">${escapeHtml(ev.description)}</p>` : ''}
            ${readMoreBtn}
            <div class="upcoming-meta">${pills}</div>
            <div class="upcoming-actions">
              ${link}
            </div>
          </div>`;
      }).join('');

      // Wire up each read-more button strictly within its own card
      document.querySelectorAll('.upcoming-card').forEach(card => {
        const desc = card.querySelector('.desc');
        const btn = card.querySelector('.read-more');
        if (!desc || !btn) return;

        btn.addEventListener('click', () => {
          const expanded = desc.classList.contains('expanded');
          if (expanded) {
            desc.classList.remove('expanded');
            btn.textContent = 'Read more';
            btn.setAttribute('aria-expanded', 'false');
          } else {
            desc.classList.add('expanded');
            btn.textContent = 'Show less';
            btn.setAttribute('aria-expanded', 'true');
          }
        });
      });
    })
    .catch(err => {
      grid.innerHTML = `
        <div class="upcoming-empty" style="grid-column: 1 / -1;">
          <p>Couldn't load events right now. Follow <a href="https://www.instagram.com/oneightywtc/" target="_blank" rel="noopener" style="color: var(--accent-2);">@oneightywtc</a> for the latest.</p>
        </div>`;
      console.error('Failed to load events.json:', err);
    });
})();

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ---- Testimonies slider (in-site YouTube playback) ----
(function initTestimonies() {
  const slider = document.getElementById('testimony-slider');
  if (!slider) return;

  const track = document.getElementById('testimony-track');
  const dotsWrap = document.getElementById('testimony-dots');
  const prevBtn = slider.querySelector('.slider-btn--prev');
  const nextBtn = slider.querySelector('.slider-btn--next');
  const slides = Array.from(slider.querySelectorAll('.testimony-slide'));

  let index = 0;

  // Build navigation dots
  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.type = 'button';
    dot.className = 'testimony-dot' + (i === 0 ? ' active' : '');
    dot.setAttribute('aria-label', 'Go to testimony ' + (i + 1));
    dot.addEventListener('click', () => goTo(i));
    dotsWrap.appendChild(dot);
  });
  const dots = Array.from(dotsWrap.children);

  function render() {
    track.style.transform = 'translateX(' + (-index * 100) + '%)';
    dots.forEach((d, i) => d.classList.toggle('active', i === index));
  }

  function goTo(i) {
    index = (i + slides.length) % slides.length;
    render();
  }

  function next() { goTo(index + 1); }
  function prev() { goTo(index - 1); }

  prevBtn.addEventListener('click', prev);
  nextBtn.addEventListener('click', next);

  // Swap a thumbnail + play button for an autoplaying embedded player.
  slides.forEach(slide => {
    const player = slide.querySelector('.testimony-player');
    const playBtn = slide.querySelector('.testimony-play');
    if (!player || !playBtn) return;

    playBtn.addEventListener('click', () => {
      const videoId = player.getAttribute('data-video-id');
      const title = player.getAttribute('data-title') || 'YouTube video';
      player.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + videoId +
        '?autoplay=1&rel=0&playsinline=1" title="' + title +
        '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
    });
  });

  render();
})();
