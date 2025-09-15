const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector("#send-btn");

let userMessage = null; // Variable to store user's message
const API_URL = "http://127.0.0.1:8000/chat";
const inputInitHeight = chatInput.scrollHeight;

// === Create Chat Bubble ===
const createChatLi = (message, className) => {
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", `${className}`);

  if (className === "outgoing") {
    chatLi.innerHTML = `<p>${message}</p>`;
  } else {
    chatLi.innerHTML = `
      <span class="material-symbols-outlined">smart_toy</span>
      <p>${message}</p>
      <button class="speak-btn" title="Read aloud">🔊</button>
    `;
  }

  return chatLi;
};

// === Text-to-Speech ===
const speakText = (text) => {
  if ("speechSynthesis" in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    window.speechSynthesis.cancel(); // Stop any ongoing speech
    window.speechSynthesis.speak(utterance);
  } else {
    alert("Sorry, your browser does not support text-to-speech.");
  }
};

// === Send message to backend ===
const sendMessageToAPI = (input) => {
  const formData = new FormData();
  formData.append("input", input);

  fetch(API_URL, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      const responseMessage = data.response;
      const li = createChatLi(responseMessage, "incoming");
      chatbox.appendChild(li);
      chatbox.scrollTo(0, chatbox.scrollHeight);

      // 🎧 Attach speak button
      const speakBtn = li.querySelector(".speak-btn");
      if (speakBtn) {
        speakBtn.addEventListener("click", () => speakText(responseMessage));
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      chatbox.appendChild(createChatLi("Oops! Something went wrong.", "error"));
      chatbox.scrollTo(0, chatbox.scrollHeight);
    });
};

// === Handle user sending message ===
const handleChat = () => {
  const input = chatInput.value.trim();
  if (!input) return;

  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  chatbox.appendChild(createChatLi(input, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  sendMessageToAPI(input);
};

// === Reset conversation ===
const sendMessagesToAPI = (isNewChat) => {
  const formData = new FormData();
  formData.append("new_chat", isNewChat);

  fetch(API_URL, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      const responseMessage = data.response;
      const li = createChatLi(responseMessage, "incoming");
      chatbox.appendChild(li);
      chatbox.scrollTo(0, chatbox.scrollHeight);

      const speakBtn = li.querySelector(".speak-btn");
      if (speakBtn) {
        speakBtn.addEventListener("click", () => speakText(responseMessage));
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      chatbox.appendChild(createChatLi("Oops! Something went wrong.", "error"));
      chatbox.scrollTo(0, chatbox.scrollHeight);
    });
};

// === Speech-to-Text ===
const micBtn = document.querySelector("#mic-btn");
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  micBtn.style.display = "flex"; // Show mic only if supported

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.lang = "en-US";
  recognition.interimResults = false;

  micBtn.addEventListener("click", () => {
    recognition.start();
    micBtn.style.color = "red"; // Recording indicator
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
    chatInput.focus();
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    micBtn.style.color = "#007aff";
  };

  recognition.onend = () => {
    micBtn.style.color = "#007aff";
  };
} else {
  console.warn("Speech Recognition not supported in this browser.");
  micBtn.style.display = "none";
}

// === Event Listeners ===
document.querySelector("#refresh-btn").addEventListener("click", () => {
  sendMessagesToAPI("True");
});

sendChatBtn.addEventListener("click", handleChat);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleChat();
  }
});

closeBtn.addEventListener("click", () =>
  document.body.classList.remove("show-chatbot")
);
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);
