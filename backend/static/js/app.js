function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a PDF or DOCX file");
    return;
  }

  document.getElementById("fileInfo").innerText = `Uploading: ${file.name}`;

  const formData = new FormData();
  formData.append("file", file);

  fetch("/analyze", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => displayResults(data))
  .catch(err => console.error(err));
}

function displayResults(data) {
  if (data.error) {
    document.getElementById("results").innerHTML = `<p style="color:red">${data.error}</p>`;
    return;
  }

  let html = `<h3>Results for ${data.filename}</h3>`;
  html += `<p>Keyword Match Score: ${data.score}%</p>`;
  html += `<p>Matched Keywords: ${data.matched_keywords.join(", ")}</p>`;
  document.getElementById("results").innerHTML = html;
}
