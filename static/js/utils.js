// utils.js - Utilitários: Toast Notifications e Modals de Confirmação

// Sistema de Notificações Toast
function showToast(message, type = 'info', title = '') {
  console.log('showToast called:', { message, type, title });

  // Garantir que as animações estejam disponíveis
  if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(400px);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(400px);
          opacity: 0;
        }
      }
      @keyframes pulseScale {
        0%, 100% {
          transform: scale(1);
        }
        50% {
          transform: scale(1.15);
        }
      }
    `;
    document.head.appendChild(style);
  }

  const container = document.getElementById('toast-container');
  console.log('Toast container found:', container);

  if (!container) {
    console.error('Toast container not found!');
    return;
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  // Adicionar estilos inline críticos para garantir formatação
  toast.style.cssText = `
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 300px;
    max-width: 400px;
    position: relative;
    overflow: hidden;
    margin-bottom: 12px;
    animation: slideIn 0.3s ease-out;
  `;

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };

  const titles = {
    success: title || 'Sucesso!',
    error: title || 'Erro!',
    warning: title || 'Atenção!',
    info: title || 'Informação'
  };

  const borderColors = {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#6b4c3b'
  };

  toast.style.borderLeft = `4px solid ${borderColors[type]}`;

  toast.innerHTML = `
    <div class="toast-icon" style="font-size: 24px; flex-shrink: 0;">${icons[type]}</div>
    <div class="toast-content" style="flex: 1;">
      <div class="toast-title" style="font-weight: 600; color: #1e293b; margin-bottom: 4px; font-size: 14px;">${titles[type]}</div>
      <div class="toast-message" style="color: #64748b; font-size: 13px; line-height: 1.4;">${message}</div>
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()" style="background: none; border: none; color: #94a3b8; cursor: pointer; padding: 4px; font-size: 20px; line-height: 1;">×</button>
  `;

  container.appendChild(toast);
  console.log('Toast added to container:', toast);

  // Auto remover após 3 segundos
  setTimeout(() => {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Sistema de Modal de Confirmação Personalizado
function showConfirm(title, message, onConfirm, onCancel = null) {
  const modal = document.getElementById('confirm-modal');
  const titleEl = document.getElementById('confirm-title');
  const messageEl = document.getElementById('confirm-message');
  const confirmBtn = document.getElementById('confirm-ok');
  const cancelBtn = document.getElementById('confirm-cancel');
  const iconEl = document.querySelector('.confirm-icon');

  if (!modal || !titleEl || !messageEl || !confirmBtn || !cancelBtn) return;

  titleEl.textContent = title;
  messageEl.textContent = message;

  // Adicionar animação no ícone
  if (iconEl) {
    iconEl.style.animation = 'pulseScale 2s ease-in-out infinite';
  }

  // Limpar listeners antigos
  const newConfirmBtn = confirmBtn.cloneNode(true);
  const newCancelBtn = cancelBtn.cloneNode(true);
  confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
  cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

  // Adicionar efeitos de hover ao botão cancelar
  newCancelBtn.addEventListener('mouseenter', () => {
    newCancelBtn.style.background = '#f1f5f9';
    newCancelBtn.style.color = '#475569';
    newCancelBtn.style.transform = 'scale(1.02)';
  });
  newCancelBtn.addEventListener('mouseleave', () => {
    newCancelBtn.style.background = '#ffffff';
    newCancelBtn.style.color = '#64748b';
    newCancelBtn.style.transform = 'scale(1)';
  });

  // Adicionar efeitos de hover ao botão confirmar
  newConfirmBtn.addEventListener('mouseenter', () => {
    newConfirmBtn.style.background = 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)';
    newConfirmBtn.style.transform = 'scale(1.02)';
    newConfirmBtn.style.boxShadow = 'inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 8px 24px rgba(239, 68, 68, 0.4)';
  });
  newConfirmBtn.addEventListener('mouseleave', () => {
    newConfirmBtn.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    newConfirmBtn.style.transform = 'scale(1)';
    newConfirmBtn.style.boxShadow = 'inset 0 1px 0 rgba(255, 255, 255, 0.2)';
  });

  // Adicionar novos listeners de click
  newConfirmBtn.addEventListener('click', () => {
    modal.style.display = 'none';
    if (onConfirm) onConfirm();
  });

  newCancelBtn.addEventListener('click', () => {
    modal.style.display = 'none';
    if (onCancel) onCancel();
  });

  // Fechar ao clicar fora
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
      if (onCancel) onCancel();
    }
  });

  modal.style.display = 'flex';
}

// Exportar funções para uso global
window.showToast = showToast;
window.showConfirm = showConfirm;

