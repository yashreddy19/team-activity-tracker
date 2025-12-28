const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const sendBtn = document.getElementById("sendBtn");

// Force dark mode
document.documentElement.setAttribute("data-theme", "dark");

function addMessage(text, type, isLoading = false) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  if (isLoading) {
    div.className += " loading";
    div.innerHTML = '<span>Fetching activity…</span>';
  } else {
    div.innerText = text;
  }
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function updateMessage(element, text) {
  element.className = element.className.replace(" loading", "");
  element.innerText = text;
  chat.scrollTop = chat.scrollHeight;
}

function setLoading(loading) {
  sendBtn.disabled = loading;
  input.disabled = loading;
  if (loading) {
    sendBtn.style.opacity = "0.6";
  } else {
    sendBtn.style.opacity = "1";
  }
}

function send() {
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";
  
  const loadingMsg = addMessage("", "bot", true);
  setLoading(true);

  fetch("/api/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        updateMessage(loadingMsg, data.data);
      } else {
        updateMessage(
          loadingMsg,
          data.message ||
          (data.errors && data.errors.join(", ")) ||
          "Something went wrong"
        );
      }
    })
    .catch(() => {
      updateMessage(loadingMsg, "Server error. Please try again.");
    })
    .finally(() => {
      setLoading(false);
      input.focus();
    });
}

// Enter key handler
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

// Focus input on load
input.focus();




  