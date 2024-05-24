let conversationHistory = [];
let conversations = JSON.parse(localStorage.getItem('conversations')) || [];
let currentConversation = [];
let currentConversationIndex = null;

document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

document.getElementById('new-convo-btn').addEventListener('click', function() {
    saveConversation();
    startNewConversation();
});

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const maxNewTokens = parseInt(document.getElementById('max-new-tokens').value);
    const temperature = document.getElementById('temperature') ? parseFloat(document.getElementById('temperature').value) : null;
    const topK = document.getElementById('top-k') ? parseInt(document.getElementById('top-k').value) : null;
    const topP = document.getElementById('top-p') ? parseFloat(document.getElementById('top-p').value) : null;

    if (userInput.trim() !== '') {
        addMessageToChatbox('user', userInput);
        conversationHistory.push({ role: 'user', content: userInput });
        currentConversation.push({ role: 'user', content: userInput });

        document.getElementById('loading-spinner').style.display = 'block'; // Mostrar el spinner de carga
        document.getElementById('send-btn').disabled = true; // Deshabilitar el botón de envío

        const context = conversationHistory.map(msg => msg.content).join('\n');

        const body = {
            prompt: context,
            max_new_tokens: maxNewTokens,
            fields: ['generated_text', 'input_token_count', 'output_token_count', 'latency']
        };

        if (temperature !== null) body.temperature = temperature;
        if (topK !== null) body.top_k = topK;
        if (topP !== null) body.top_p = topP;

        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('loading-spinner').style.display = 'none'; // Ocultar el spinner de carga
            document.getElementById('send-btn').disabled = false; // Habilitar el botón de envío
            addMessageToChatbox('ai', data.generated_text);

            conversationHistory.push({ role: 'ai', content: data.generated_text });
            currentConversation.push({ role: 'ai', content: data.generated_text });

            // Mostrar información de tokens y latencia
            document.getElementById('input-token-count').innerText = 'Input Token Count: ' + data.input_token_count;
            document.getElementById('output-token-count').innerText = 'Output Token Count: ' + data.output_token_count;
            document.getElementById('latency').innerText = 'Latency: ' + data.latency.toFixed(2) + ' seconds';
            document.getElementById('info-container').style.display = 'block';
        })
        .catch(error => {
            document.getElementById('loading-spinner').style.display = 'none'; // Ocultar el spinner de carga
            document.getElementById('send-btn').disabled = false; // Habilitar el botón de envío
            console.error('Error:', error);
        });

        document.getElementById('user-input').value = '';
    }
}

function addMessageToChatbox(sender, message) {
    const chatbox = document.getElementById('chatbox');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    
    const avatar = document.createElement('img');
    avatar.classList.add('avatar');
    if (sender === 'user') {
        avatar.src = '/static/user-avatar.png'; // Cambia esto a la ruta de tu imagen de usuario
    } else {
        avatar.src = '/static/ai-avatar.png'; // Cambia esto a la ruta de tu imagen de AI
    }
    
    const textElement = document.createElement('div');
    textElement.classList.add('text');
    textElement.innerText = message;
    
    messageElement.appendChild(avatar);
    messageElement.appendChild(textElement);
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function saveConversation() {
    if (currentConversation.length > 0) {
        const now = new Date();
        const conversation = {
            title: `Conversation ${conversations.length + 1} (${modelName})`,
            date: now.toLocaleString(),
            messages: currentConversation
        };
        conversations.unshift(conversation); // Insertar al principio
        localStorage.setItem('conversations', JSON.stringify(conversations));
        currentConversation = [];
        displayConversations();
    }
}

function startNewConversation() {
    conversationHistory = [];
    currentConversation = [];
    const now = new Date();
    const conversation = {
        title: `Conversation ${conversations.length + 1} (${modelName})`,
        date: now.toLocaleString(),
        messages: []
    };
    conversations.unshift(conversation);
    localStorage.setItem('conversations', JSON.stringify(conversations));
    currentConversationIndex = 0;
    document.getElementById('conversation-title').innerText = `${conversation.title} - ${conversation.date}`;
    document.getElementById('chatbox').innerHTML = '';
    document.getElementById('chatbox-container').style.display = 'flex';
    displayConversations();
}

function displayConversations() {
    const conversationContainer = document.getElementById('conversations');
    conversationContainer.innerHTML = '';
    conversations.forEach((conv, index) => {
        const conversationElement = document.createElement('div');
        conversationElement.classList.add('conversation');
        conversationElement.innerText = `${conv.title} - ${conv.date}`;
        conversationElement.addEventListener('click', () => loadConversation(index));
        const deleteBtn = document.createElement('button');
        deleteBtn.classList.add('delete-btn');
        deleteBtn.innerText = 'Delete';
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteConversation(index);
        });
        conversationElement.appendChild(deleteBtn);
        if (index === currentConversationIndex) {
            conversationElement.classList.add('selected');
        }
        conversationContainer.appendChild(conversationElement);
    });
}

function loadConversation(index) {
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML = '';
    conversationHistory = conversations[index].messages;
    document.getElementById('conversation-title').innerText = `${conversations[index].title} - ${conversations[index].date}`;
    conversationHistory.forEach(msg => {
        addMessageToChatbox(msg.role, msg.content);
    });
    currentConversationIndex = index;
    document.getElementById('chatbox-container').style.display = 'flex';
    displayConversations();
}

function deleteConversation(index) {
    conversations.splice(index, 1);
    localStorage.setItem('conversations', JSON.stringify(conversations));
    if (currentConversationIndex === index) {
        document.getElementById('chatbox-container').style.display = 'none';
        document.getElementById('conversation-title').innerText = '';
    }
    currentConversationIndex = null;
    displayConversations();
}

window.addEventListener('beforeunload', saveConversation);
window.addEventListener('load', displayConversations);
