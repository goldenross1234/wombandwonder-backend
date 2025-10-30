document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.querySelector("#id_image");
  const previewField = document.querySelector("img[src*='hero']") || document.createElement("img");

  if (fileInput) {
    fileInput.addEventListener("change", function (event) {
      const [file] = event.target.files;
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewField.src = e.target.result;
          previewField.style.maxHeight = "200px";
          previewField.style.borderRadius = "10px";
          previewField.style.marginTop = "10px";
          fileInput.parentNode.appendChild(previewField);
        };
        reader.readAsDataURL(file);
      }
    });
  }
});
