const fileInput = document.getElementById('fileInput');
const fileNameLabel = document.getElementById('file-name');
const dropZone = fileInput.closest('label');

function showFileName(file) {
  fileNameLabel.textContent = file.name;
  fileNameLabel.classList.remove('hidden');
}

fileInput.addEventListener('change', function() {
  if (this.files && this.files[0]) {
    showFileName(this.files[0]);
  } else {
    fileNameLabel.classList.add('hidden');
  }
});

dropZone.addEventListener('dragenter', function(e) {
  e.preventDefault();
  e.stopPropagation();
  this.classList.add('border-indigo-500', 'bg-indigo-50');
});

dropZone.addEventListener('dragover', function(e) {
  e.preventDefault();
  e.stopPropagation();
  this.classList.add('border-indigo-500', 'bg-indigo-50');
});

dropZone.addEventListener('dragleave', function(e) {
  e.preventDefault();
  e.stopPropagation();
  this.classList.remove('border-indigo-500', 'bg-indigo-50');
});

dropZone.addEventListener('drop', function(e) {
  e.preventDefault();
  e.stopPropagation();
  this.classList.remove('border-indigo-500', 'bg-indigo-50');
  const files = e.dataTransfer.files;
  if (files && files[0]) {
    fileInput.files = files;
    showFileName(files[0]);
  }
});
