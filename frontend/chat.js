const chatToggle = document.getElementById("chat-toggle");
const chatPopup = document.getElementById("chat-popup");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");
const chatMessages = document.getElementById("chat-messages");

// --- Added Step 2: New Chat Button Reference ---
const newChatBtn = document.getElementById("new-chat-btn");

// session memory
let sessionId = localStorage.getItem("session_id");

// --- Added Step 2: New Chat Event Listener ---
newChatBtn.addEventListener("click", function () {
    // remove session id from storage
    localStorage.removeItem("session_id");
    
    // reset local variable
    sessionId = null;
    
    // clear chat messages from UI
    chatMessages.innerHTML = "";
});

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
        const response = await fetch("https://college-ai-helpdesk-3.onrender.com/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                session_id: sessionId
            })
        });

        const data = await response.json();

        // save session if first time
        if (!sessionId && data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem("session_id", sessionId);
        }

        loading.textContent = data.answer;

    } catch (error) {
        loading.textContent = "Something went wrong. Please try again.";
    }
}