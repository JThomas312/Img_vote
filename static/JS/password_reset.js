
function copyPassword(pwd) {
  navigator.clipboard.writeText(pwd).then(function() {
    var btn = document.getElementById('copy-btn');
    btn.textContent = 'Copied!';
    btn.classList.add('text-green-700', 'border-green-300', 'bg-green-50');
    btn.classList.remove('text-indigo-700', 'border-indigo-200');
    setTimeout(function() {
      btn.textContent = 'Copy';
      btn.classList.remove('text-green-700', 'border-green-300', 'bg-green-50');
      btn.classList.add('text-indigo-700', 'border-indigo-200');
    }, 2000);
  });
}
