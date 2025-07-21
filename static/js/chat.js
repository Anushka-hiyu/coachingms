/*chat.js*/
document.addEventListener("DOMContentLoaded", function () {
  const chatBox = document.getElementById("chat-box");
  if (chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
  }

  const form = document.getElementById("message-form");
  const input = form.querySelector("input[type='text']");

  form.addEventListener("submit", function () {
    setTimeout(() => {
      input.value = "";
    }, 100);
  });
});