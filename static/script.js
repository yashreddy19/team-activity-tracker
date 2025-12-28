document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM fully loaded");

  const chat = document.getElementById("chat");
  const input = document.getElementById("msg");
  const sendBtn = document.getElementById("sendBtn");

  if (!chat || !input || !sendBtn) {
    console.error("❌ Required DOM elements not found");
    return;
  }

  // Force dark mode
  document.documentElement.setAttribute("data-theme", "dark");

  function addMessage(text, type, isLoading = false) {
    const div = document.createElement("div");
    div.className = `message ${type}`;

    if (isLoading) {
      div.classList.add("loading");
      div.innerHTML = "<span>Fetching activity…</span>";
    } else {
      div.innerText = text;
    }

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
  }

  function updateMessage(element, text) {
    element.classList.remove("loading");
    element.innerText = text;
    chat.scrollTop = chat.scrollHeight;
  }

  function setLoading(loading) {
    sendBtn.disabled = loading;
    input.disabled = loading;
    sendBtn.style.opacity = loading ? "0.6" : "1";
  }

  // ✅ Welcome message (shown on every refresh if chat is empty)
  function showWelcomeMessage() {
    if (chat.children.length === 0) {
      addMessage(
        "👋 Hi! I’m your Team Activity Tracker.\n\n" +
          "You can ask things like:\n" +
          "• What is John working on?\n" +
          "• Show me Sarah’s recent Jira activity\n" +
          "• What has Mike committed this week?\n\n" +
          "How can I help you today?",
        "bot"
      );
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
      body: JSON.stringify({ message }),
    })
      .then((res) => res.json())
      .then((data) => {
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

  // Button click handler
  sendBtn.addEventListener("click", send);

  // 🔥 Show welcome message on EVERY refresh
  showWelcomeMessage();

  input.focus();
});






  