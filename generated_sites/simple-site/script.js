document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  toggle.addEventListener('click', function () {
    nav.classList.toggle('hidden');
  });
});
