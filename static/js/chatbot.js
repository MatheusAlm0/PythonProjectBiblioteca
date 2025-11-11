// Chatbot Implementation
document.addEventListener('DOMContentLoaded', function() {
  const chatbotBtn = document.getElementById('chatbot-btn');
  const chatbotModal = document.getElementById('chatbot-modal');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotSend = document.getElementById('chatbot-send');
  const chatbotMessages = document.getElementById('chatbot-messages');

  if (!chatbotBtn || !chatbotModal) {
    console.log('Chatbot elements not found');
    return;
  }

  // Adicionar efeitos de hover no botão
  chatbotBtn.addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.15) translateY(-4px)';
    this.style.boxShadow = '0 16px 40px rgba(102, 126, 234, 0.6), 0 8px 16px rgba(0, 0, 0, 0.2)';
  });

  chatbotBtn.addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1)';
    this.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.5), 0 4px 12px rgba(0, 0, 0, 0.15)';
  });

  chatbotBtn.addEventListener('mousedown', function() {
    this.style.transform = 'scale(1.05)';
  });

  chatbotBtn.addEventListener('mouseup', function() {
    this.style.transform = 'scale(1.15) translateY(-4px)';
  });

  // Abrir chatbot
  chatbotBtn.addEventListener('click', function() {
    chatbotModal.style.display = 'block';
    chatbotBtn.style.display = 'none';
    chatbotInput.focus();
  });

  // Fechar chatbot
  chatbotClose.addEventListener('click', function() {
    chatbotModal.style.display = 'none';
    chatbotBtn.style.display = 'flex';
  });

  // Função para adicionar mensagem
  function addMessage(text, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chatbot-message ' + (isUser ? 'user' : 'bot');
    messageDiv.style.cssText = 'display: flex; gap: 10px; align-items: flex-start; animation: messageIn 0.3s ease-out;' +
      (isUser ? ' flex-direction: row-reverse;' : '');

    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const timeStr = hours + ':' + minutes;

    const avatar = isUser ? '' : '🤖';
    const avatarBg = isUser ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'linear-gradient(135deg, #6b4c3b 0%, #583a2e 100%)';
    const msgBg = isUser ? 'linear-gradient(135deg, #6b4c3b 0%, #583a2e 100%)' : 'white';
    const msgColor = isUser ? 'white' : '#1e293b';
    const contentAlign = isUser ? 'align-items: flex-end;' : '';

    messageDiv.innerHTML = '<div class="message-avatar" style="width: 32px; height: 32px; border-radius: 50%; background: ' + avatarBg + '; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;">' + avatar + '</div>' +
      '<div class="message-content" style="max-width: 70%; display: flex; flex-direction: column; gap: 4px; ' + contentAlign + '">' +
        '<p style="margin: 0; padding: 12px 16px; border-radius: 12px; background: ' + msgBg + '; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); font-size: 14px; line-height: 1.5; color: ' + msgColor + ';">' + text + '</p>' +
        '<span class="message-time" style="font-size: 11px; color: #94a3b8; padding: 0 4px;">' + timeStr + '</span>' +
      '</div>';

    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  // Função para adicionar loading
  function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chatbot-message bot';
    loadingDiv.id = 'loading-message';
    loadingDiv.style.cssText = 'display: flex; gap: 10px; align-items: flex-start;';
    loadingDiv.innerHTML = '<div class="message-avatar" style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #6b4c3b 0%, #583a2e 100%); display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;">🤖</div>' +
      '<div class="message-content" style="max-width: 70%; display: flex; flex-direction: column; gap: 4px;">' +
        '<div class="message-loading" style="display: flex; gap: 4px; padding: 12px 16px;">' +
          '<span style="width: 8px; height: 8px; border-radius: 50%; background: #94a3b8; animation: bounce 1.4s infinite ease-in-out;"></span>' +
          '<span style="width: 8px; height: 8px; border-radius: 50%; background: #94a3b8; animation: bounce 1.4s infinite ease-in-out; animation-delay: -0.16s;"></span>' +
          '<span style="width: 8px; height: 8px; border-radius: 50%; background: #94a3b8; animation: bounce 1.4s infinite ease-in-out; animation-delay: -0.32s;"></span>' +
        '</div>' +
      '</div>';

    chatbotMessages.appendChild(loadingDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  // Função para remover loading
  function removeLoading() {
    const loading = document.getElementById('loading-message');
    if (loading) {
      loading.remove();
    }
  }

  // Enviar mensagem
  async function sendMessage() {
    const message = chatbotInput.value.trim();
    if (!message) return;

    // Adicionar mensagem do usuário
    addMessage(message, true);
    chatbotInput.value = '';
    chatbotInput.style.height = 'auto';

    // Desabilitar botão
    chatbotSend.disabled = true;
    addLoading();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
      });

      const data = await response.json();

      removeLoading();

      if (response.ok && data.answer) {
        addMessage(data.answer, false);
      } else {
        // Mostrar erro específico do backend
        const errorMsg = data.error || 'Desculpe, ocorreu um erro. Por favor, tente novamente.';
        console.error('Erro do backend:', errorMsg);

        if (errorMsg.includes('GROQ_API_KEY') || errorMsg.includes('API key')) {
          addMessage('⚠️ Chatbot não configurado. Entre em contato com o administrador para configurar a GROQ_API_KEY.', false);
        } else {
          addMessage('Desculpe, ocorreu um erro: ' + errorMsg, false);
        }
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      removeLoading();
      addMessage('Erro ao conectar com o assistente. Verifique sua conexão.', false);
    } finally {
      chatbotSend.disabled = false;
      chatbotInput.focus();
    }
  }

  // Event listeners
  chatbotSend.addEventListener('click', sendMessage);

  chatbotInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-resize textarea
  chatbotInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
  });
});

