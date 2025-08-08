// Clear form on page load so browser won't keep the old value (UX choice)
window.onload = function () {
  const form = document.getElementById("moodForm");
  if (form) form.reset();
};
