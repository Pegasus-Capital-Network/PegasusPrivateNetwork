const reveal = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('visible'); io.unobserve(e.target); } });
},{threshold:.12});
reveal.forEach(el=>io.observe(el));

// Keep the original Netlify form and its existing submission history.
// Do not mirror a request into Supabase or automatically retry an uncertain POST.
const form = document.forms.namedItem('request-access');
const status = document.getElementById('form-status');
let submitting = false;
if (form) form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (submitting || !form.reportValidity()) return;
  const button = form.querySelector('button[type="submit"]');
  submitting = true;
  button.disabled = true;
  status.textContent = 'Sending your request…';
  const payload = new URLSearchParams(new FormData(form)).toString();
  try {
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(payload));
    const key = 'ppn-request-' + Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
    let previous;
    try { previous = sessionStorage.getItem(key); } catch (_) { /* Storage may be unavailable. */ }
    if (previous) {
      status.textContent = previous === 'sent'
        ? 'This request has already been sent. Thank you.'
        : 'A matching request was already attempted. Receipt is uncertain; please do not send it again until it has been checked.';
      return;
    }
    try { sessionStorage.setItem(key, 'pending'); } catch (_) { /* In-flight protection remains active. */ }
    const response = await fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: payload
    });
    if (!response.ok) throw new Error('Receipt could not be confirmed');
    try { sessionStorage.setItem(key, 'sent'); } catch (_) { /* Do not retry. */ }
    status.textContent = 'Thank you. Your request has been sent. This is an expression of interest only, with no investment commitment.';
    button.textContent = 'Request sent';
  } catch (_) {
    status.textContent = 'We could not confirm receipt. Please do not resubmit immediately; your request may have reached us. No automatic retry will be made.';
  }
});
