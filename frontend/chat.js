const chatToggle = document.getElementById("chat-toggle");
const chatPopup = document.getElementById("chat-popup");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");
const chatMessages = document.getElementById("chat-messages");

chatToggle.addEventListener("click", function () {
    chatPopup.classList.toggle("active");
});

chatSend.addEventListener("click", function () {
    sendMessage();
});

chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

function addMessage(text, type) {
    const message = document.createElement("div");
    message.classList.add("message", type);
    message.textContent = text;
    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return message;
}

async function sendMessage() {
    const question = chatInput.value.trim();
    if (!question) return;

    addMessage(question, "user-message");
    chatInput.value = "";

    const loading = addMessage("Typing...", "bot-message");

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        loading.textContent = data.answer;
    } catch (error) {
        loading.textContent = "Something went wrong. Please try again.";
    }
}