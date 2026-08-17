// Navbar scroll effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// Simple mobile menu toggle (basic placeholder)
const menuToggle = document.querySelector('.menu-toggle');
menuToggle.addEventListener('click', () => {
  alert('Mobile menu placeholder — add menu overlay here.');
});

// ---- Upcoming Events (data-driven from events.json) ----
(function renderEvents() {
  const grid = document.getElementById('event-grid');
  const months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];

  // Today at 00:00 local time — events on or after today are "upcoming"
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  fetch('events.json', { cache: 'no-store' })
    .then(res => {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(data => {
      let events = data.events || [];

      // Keep only future events, then sort ascending by date
      events = events
        .filter(ev => {
          const d = new Date(ev.date + 'T00:00:00');
          return !isNaN(d) && d >= today;
        })
        .sort((a, b) => new Date(a.date) - new Date(b.date));

      if (events.length === 0) {
        grid.innerHTML = `
          <div class="upcoming-empty" style="grid-column: 1 / -1;">
            <p>No upcoming events yet — check back soon or follow <a href="https://www.instagram.com/oneightywtc/" target="_blank" rel="noopener" style="color: var(--accent-2);">@oneightywtc</a>.</p>
          </div>`;
        return;
      }

      grid.innerHTML = events.map((ev, index) => {
        const d = new Date(ev.date + 'T00:00:00');
        const month = months[d.getMonth()];
        const dayNum = d.getDate();
        const idBase = `event-${index}`;

        // Build meta pills
        let pills = '';
        if (ev.time) {
          pills += `<span class="meta-pill"><span>🕒</span> ${escapeHtml(ev.time)}</span>`;
        }
        if (ev.location) {
          pills += `<span class="meta-pill muted"><span>📍</span> ${escapeHtml(ev.location)}</span>`;
        }

        // Button link
        const link = ev.link
          ? `<a href="${escapeHtml(ev.link)}" target="_blank" rel="noopener" class="upcoming-link">See details →</a>`
          : '';

        // Read more if description is long
        const readMore = ev.description && ev.description.length > 120
          ? `<button class="read-more" data-target="${idBase}-desc">Read more</button>`
          : '';

        return `
          <div class="upcoming-card">
            <div class="upcoming-date">
              <span class="day-num">${dayNum}</span>
              <span class="month">${month}</span>
            </div>
            <h3>${escapeHtml(ev.name)}</h3>
            ${ev.description ? `<p id="${idBase}-desc" class="desc">${escapeHtml(ev.description)}</p>` : ''}
            ${readMore}
            <div class="upcoming-meta">${pills}</div>
            <div class="upcoming-actions">
              ${link}
            </div>
          </div>`;
      }).join('');

      // Wire up read more buttons
      document.querySelectorAll('.read-more').forEach(btn => {
        btn.addEventListener('click', () => {
          const target = document.getElementById(btn.dataset.target);
          if (target) {
            target.classList.toggle('expanded');
            btn.textContent = target.classList.contains('expanded') ? 'Show less' : 'Read more';
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
