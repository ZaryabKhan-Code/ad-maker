$(document).ready(function () {
  const chatMessages = $("#chat-messages");
  const username = $("#username").val() || "You";
  let botHasInitiated = false;

  function scrollToBottom() {
      chatMessages.scrollTop(chatMessages[0].scrollHeight);
  }
  function disableChat() {
    $("#chat-input").prop("disabled", true);
    $("#send-button").prop("disabled", true);
    chatMessages.append(`<div id="loading-animation" class="chat-message chat-bot"><i class="fas fa-spinner fa-spin"></i> Loading...</div>`);
    scrollToBottom(); // Ensure chat scrolls down to show this loading animation
}

function enableChat() {
    $("#chat-input").prop("disabled", false);
    $("#send-button").prop("disabled", false);
    $("#loading-animation").remove();  // Remove the loading animation from the chat messages
    $("#chat-input").focus();
}
  function initiateBotConversation() {
      if (botHasInitiated) {
          return;
      }

      $.ajax({
          url: "/bot",
          method: "GET",
          dataType: "json",
          success: function (data) {
              if (data && data.initial_message && data.initial_message.trim() !== "") {
                  chatMessages.append(`<div class="chat-message chat-bot"><strong>Bot:</strong> ${data.initial_message.trim()}</div>`);
                  botHasInitiated = true;
                  scrollToBottom();
                  enableChat();  // Enable chat after the bot initiates the conversation
              }
          },
          error: function (error) {
              console.error("Error initiating conversation with bot:", error);
              enableChat();  // Enable chat in case of error as well
          }
      });
  }

  function sendMessage() {
    const chatInput = $("#chat-input");
    const userMessage = chatInput.val().trim();

    if (!userMessage) return;

    chatMessages.append(`<div class="chat-message chat-user"><strong>${username}:</strong> ${userMessage}</div>`);
    chatInput.val("");
    scrollToBottom();

    disableChat();

    $.ajax({
        url: "/api/chat",
        method: "POST",
        dataType: "json",
        contentType: "application/json", 
        data: JSON.stringify({ user_message: userMessage }),
        success: function (response) {
            let botMessage = '';

            if (response && typeof response === 'object' && response.bot_message) {
                botMessage = response.bot_message;
            } else if (typeof response === 'string') {
                botMessage = response;
            }

            chatMessages.append(`<div class="chat-message chat-bot"><strong>Bot:</strong> ${botMessage}</div>`);
            scrollToBottom();

            if (botMessage.toLowerCase().includes("email")) {
                $('#myModal').modal('show');
            }

            enableChat();
        },
        error: function () {
            chatMessages.append(`<div class="chat-message chat-bot"><strong>Bot:</strong> Error in response.</div>`);
            scrollToBottom();
            console.error("There was an error in sending the message!");

            enableChat();
        }
    });
}


  $("#send-button").click(function () {
      sendMessage();
  });

  $("#chat-input").keypress(function (e) {
      if (e.which === 13) {
          e.preventDefault();
          sendMessage();
      }
  });

  disableChat();  
  initiateBotConversation();
});
