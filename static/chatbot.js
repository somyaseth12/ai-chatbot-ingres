// Send message to chatbot
async function sendMessage() {

    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    let message = input.value.trim();

    if (message === "") return;

    // Show user message
    chatBox.innerHTML += `
        <div class="message user">
            <div class="bubble">${message}</div>
        </div>
    `;

    input.value = "";

    // Auto scroll
    chatBox.scrollTop = chatBox.scrollHeight;

    try {

        // 🔹 Send message to backend
        const response = await fetch("/get-response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // 🔹 Show bot response
        chatBox.innerHTML += `
            <div class="message bot">
                <div class="bubble">${data.response}</div>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

        // 🔥 NEW: Check if trend graph needed
        if (data.response && data.response.toLowerCase().includes("trend graph")) {

            const graphResponse = await fetch("/get-trend-chart", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message }) // send full query
            });

            const graphData = await graphResponse.json();

            if (graphData.image) {
                chatBox.innerHTML += `
                    <div class="message bot">
                        <div class="bubble">
                            <img src="${graphData.image}" style="max-width:100%; border-radius:10px;">
                        </div>
                    </div>
                `;
            } else if (graphData.error) {
                chatBox.innerHTML += `
                    <div class="message bot">
                        <div class="bubble">⚠ ${graphData.error}</div>
                    </div>
                `;
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (error) {

        chatBox.innerHTML += `
            <div class="message bot">
                <div class="bubble">⚠ Server error. Please try again.</div>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;
    }
}


// Send message when Enter key is pressed
document.getElementById("user-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});