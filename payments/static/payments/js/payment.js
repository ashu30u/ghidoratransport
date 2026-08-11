// Ghidora Transport — Payment module interactions

function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    if (!btn) return;
    const original = btn.textContent;
    btn.textContent = "Copied!";
    btn.classList.add("copied-flash");
    setTimeout(() => {
      btn.textContent = original;
      btn.classList.remove("copied-flash");
    }, 1500);
  });
}

function downloadQr(url, filename) {
  const link = document.createElement("a");
  link.href = url;
  link.download = filename || "ghidora_payment_qr.png";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

// Screenshot preview / delete / replace
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("id_screenshot");
  const previewWrap = document.getElementById("screenshot-preview-wrap");
  const previewImg = document.getElementById("screenshot-preview-img");
  const previewName = document.getElementById("screenshot-preview-name");
  const deleteBtn = document.getElementById("screenshot-delete-btn");
  const replaceBtn = document.getElementById("screenshot-replace-btn");

  if (!input) return;

  input.addEventListener("change", () => {
    const file = input.files[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      alert("File too large. Maximum allowed size is 10 MB.");
      input.value = "";
      return;
    }

    previewWrap.classList.remove("d-none");
    previewName.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewImg.classList.remove("d-none");
      };
      reader.readAsDataURL(file);
    } else {
      previewImg.classList.add("d-none");
    }
  });

  if (deleteBtn) {
    deleteBtn.addEventListener("click", () => {
      input.value = "";
      previewWrap.classList.add("d-none");
      previewImg.src = "";
    });
  }

  if (replaceBtn) {
    replaceBtn.addEventListener("click", () => input.click());
  }
});

// Simple client-side submit animation (button loading state)
document.addEventListener("submit", (e) => {
  const form = e.target;
  if (!form.classList || !form.classList.contains("glass-form")) return;
  const submitBtn = form.querySelector("[type=submit]");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.dataset.originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing...';
  }
});
