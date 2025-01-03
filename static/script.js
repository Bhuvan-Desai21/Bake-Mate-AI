document.getElementById("send-button").addEventListener("click", () => {
    const userInput = document.getElementById("user-input");
    const chatLog = document.getElementById("chat-log");

    const message = userInput.value.trim();
    if (!message) {
        alert("Please type a message.");
        return;
    }

    // Append user's message to chat log
    chatLog.innerHTML += `<div><strong>You:</strong> ${message}</div>`;

    // Send message to backend
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.response) {
                chatLog.innerHTML += `<div><strong>AI:</strong> ${data.response}</div>`;
            } else if (data.error) {
                chatLog.innerHTML += `<div><strong>Error:</strong> ${data.error}</div>`;
            }
        })
        .catch((error) => {
            chatLog.innerHTML += `<div><strong>Error:</strong> Unable to communicate with server.</div>`;
        });

    userInput.value = "";
    chatLog.scrollTop = chatLog.scrollHeight; // Auto-scroll to the bottom
});
