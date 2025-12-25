function send() {
  const msgInput = document.getElementById("msg");
  const out = document.getElementById("out");
  const status = document.getElementById("status");

  const message = msgInput.value.trim();
  if (!message) return;

  status.innerText = "Fetching activity...";
  out.innerText = "";

  fetch("/api/chat/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => {
      status.innerText = "";
      out.innerText = data.data || "No response received";
    })
    .catch(err => {
      status.innerText = "";
      out.innerText = "Something went wrong. Check console.";
      console.error(err);
    });
}


  