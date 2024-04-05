document.addEventListener('DOMContentLoaded', function () {
  const btn = document.querySelector('.btn.animate');

  btn.addEventListener('click', function (e) {
    e.preventDefault();
    const section = document.querySelector(this.getAttribute('href'));
    section.scrollIntoView({ behavior: 'smooth' });
  });
});