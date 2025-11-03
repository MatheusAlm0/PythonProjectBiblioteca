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
    info: '#3b82f6'
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

// Função global para abrir modal de avaliação
window.openRatingModal = function(bookId, currentStars = 0, currentComment = '', isEditing = false) {
  const userId = localStorage.getItem('user_id');
  const modal = document.getElementById('rating-modal');
  const submitBtn = document.getElementById('submit-rating');
  const cancelBtn = document.getElementById('cancel-rating');
  const commentInput = document.getElementById('rating-comment');
  const ratingText = document.getElementById('rating-text');
  const charCount = document.getElementById('char-count');
  let selectedRating = 0;

  // Textos descritivos para cada nota
  const ratingDescriptions = {
    1: '⭐ Muito Ruim',
    2: '⭐⭐ Ruim',
    3: '⭐⭐⭐ Regular',
    4: '⭐⭐⭐⭐ Bom',
    5: '⭐⭐⭐⭐⭐ Excelente!'
  };

  // Reset e preparar modal
  const starContainer = document.querySelector('.star-rating');
  starContainer.innerHTML = `
    <span class="star" data-rating="1">⭐</span>
    <span class="star" data-rating="2">⭐</span>
    <span class="star" data-rating="3">⭐</span>
    <span class="star" data-rating="4">⭐</span>
    <span class="star" data-rating="5">⭐</span>
  `;

  commentInput.value = '';
  ratingText.textContent = 'Selecione uma nota';
  ratingText.classList.remove('has-rating');
  charCount.textContent = '0';

  // Preencher dados atuais (modo edição)
  if(currentStars > 0){
    selectedRating = currentStars;
    updateStarDisplay(selectedRating, true); // true = usar classe active (amarelo permanente)
    ratingText.textContent = ratingDescriptions[selectedRating];
    ratingText.classList.add('has-rating');
  }
  if(currentComment){
    commentInput.value = currentComment;
    charCount.textContent = currentComment.length;
  }

  // Função para atualizar display das estrelas
  function updateStarDisplay(rating, useActive = false) {
    const stars = document.querySelectorAll('.star-rating .star');
    stars.forEach((star, i) => {
      if(i < rating){
        // Estrelas selecionadas: amarelas
        star.style.filter = 'grayscale(0%) brightness(1)';
        star.style.opacity = '1';
        star.style.transform = 'scale(1)';
      } else {
        // Estrelas não selecionadas: cinza
        star.style.filter = 'grayscale(100%) brightness(1.1)';
        star.style.opacity = '0.5';
        star.style.transform = 'scale(1)';
      }
    });
  }

  // Event listeners para as estrelas
  const stars = document.querySelectorAll('.star');
  stars.forEach(star => {
    // Hover
    star.addEventListener('mouseenter', function(){
      const rating = parseInt(this.dataset.rating);
      const allStars = document.querySelectorAll('.star-rating .star');
      allStars.forEach((s, i) => {
        if(i < rating){
          // Hover: mostrar preview amarelo
          s.style.filter = 'grayscale(0%) brightness(1)';
          s.style.opacity = '1';
          s.style.transform = 'scale(1.15)';
        } else {
          // Manter cinza
          s.style.filter = 'grayscale(100%) brightness(1.1)';
          s.style.opacity = '0.5';
          s.style.transform = 'scale(1)';
        }
      });
      ratingText.textContent = ratingDescriptions[rating];
      ratingText.classList.add('has-rating');
    });

    // Mouse leave
    star.addEventListener('mouseleave', function(){
      const allStars = document.querySelectorAll('.star-rating .star');
      if(selectedRating > 0) {
        // Restaurar para o estado selecionado
        allStars.forEach((s, i) => {
          if(i < selectedRating){
            s.style.filter = 'grayscale(0%) brightness(1)';
            s.style.opacity = '1';
            s.style.transform = 'scale(1)';
          } else {
            s.style.filter = 'grayscale(100%) brightness(1.1)';
            s.style.opacity = '0.5';
            s.style.transform = 'scale(1)';
          }
        });
        ratingText.textContent = ratingDescriptions[selectedRating];
        ratingText.classList.add('has-rating');
      } else {
        // Nenhuma selecionada: todas cinza
        allStars.forEach(s => {
          s.style.filter = 'grayscale(100%) brightness(1.1)';
          s.style.opacity = '0.5';
          s.style.transform = 'scale(1)';
        });
        ratingText.textContent = 'Selecione uma nota';
        ratingText.classList.remove('has-rating');
      }
    });

    // Click
    star.addEventListener('click', function(){
      selectedRating = parseInt(this.dataset.rating);
      const allStars = document.querySelectorAll('.star-rating .star');

      console.log('Clicked star with rating:', selectedRating);

      allStars.forEach((s, i) => {
        // Remover todas as classes e estilos primeiro
        s.classList.remove('filled', 'active');

        if(i < selectedRating){
          // Estrelas selecionadas: amarelas (sem grayscale)
          s.classList.add('active');
          s.style.filter = 'grayscale(0%) brightness(1)';
          s.style.opacity = '1';
          console.log('Star', i, 'set to ACTIVE (yellow)');
        } else {
          // Estrelas não selecionadas: cinza
          s.style.filter = 'grayscale(100%) brightness(1.1)';
          s.style.opacity = '0.5';
          console.log('Star', i, 'set to INACTIVE (gray)');
        }
      });

      // Animar a estrela clicada
      this.style.animation = 'starPop 0.3s ease-out';

      ratingText.textContent = ratingDescriptions[selectedRating];
      ratingText.classList.add('has-rating');

      // Feedback tátil (se disponível)
      if (navigator.vibrate) {
        navigator.vibrate(10);
      }
    });
  });

  // Contador de caracteres
  commentInput.addEventListener('input', function(){
    charCount.textContent = this.value.length;
  });

  // Botão de cancelar
  if(cancelBtn) {
    cancelBtn.onclick = () => {
      modal.style.display = 'none';
      // Reabrir modal de avaliações se estava aberto
      const ratingsModal = document.getElementById('ratings-modal');
      if(ratingsModal && ratingsModal.dataset.wasOpen === 'true') {
        ratingsModal.style.display = 'flex';
        ratingsModal.dataset.wasOpen = 'false';
      }
    };
  }

  // Botão de submit
  submitBtn.onclick = () => {
    if(selectedRating === 0){
      showToast('Por favor, selecione uma nota de 1 a 5 estrelas', 'warning', 'Avaliação incompleta');
      // Animação de shake nas estrelas
      const starRating = document.querySelector('.star-rating');
      starRating.style.animation = 'none';
      setTimeout(() => {
        starRating.style.animation = 'shake 0.5s';
      }, 10);
      return;
    }
    const comment = commentInput.value.trim();
    window.saveRating(bookId, selectedRating, comment, isEditing);
    modal.style.display = 'none';
  };

  modal.style.display = 'flex';
};

// Função global para salvar avaliação
window.saveRating = async function(bookId, stars, comment, reopenRatingsModal = false) {
  const userId = localStorage.getItem('user_id');

  try{
    const payload = {
      google_books_id: bookId,
      estrelas: stars
    };
    if(comment) payload.comentario = comment;

    const res = await fetch(`/api/users/${userId}/ratings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + userId
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(res.ok) {
      showToast(data.message || 'Avaliação salva com sucesso!', 'success');
      // Só reabrir modal de avaliações se vier da edição
      if(reopenRatingsModal) {
        setTimeout(() => {
          if(window.showRatings) window.showRatings();
        }, 500);
      }
    } else {
      showToast(data.error || 'Erro ao salvar avaliação', 'error');
    }
  }catch(e){
    showToast('Erro: ' + e.message, 'error');
  }
};

document.addEventListener('DOMContentLoaded', async ()=>{
  const userId = localStorage.getItem('user_id');
  let isLoggedIn = false;
  let username = '';

  // Verificar se está logado (mas não redirecionar se não estiver)
  if(userId){
    try{
      const res = await fetch('/auth/me', { headers: { 'Authorization': 'Bearer '+userId }});
      const data = await res.json();
      if(res.ok){
        isLoggedIn = true;
        username = data.username || 'Usuário';
        document.getElementById('username').textContent = username;
      }else{
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
      }
    }catch(e){
      console.error('Erro ao validar sessão:', e);
      localStorage.removeItem('user_id');
      localStorage.removeItem('username');
    }
  }

  // Atualizar botão de login/logout
  const btnLogout = document.getElementById('btn-logout');
  const btnLogin = document.getElementById('btn-login');
  const btnFavoritesHeader = document.getElementById('btn-favorites');
  const btnRatingsHeader = document.getElementById('btn-ratings');

  if(isLoggedIn){
    // Mostrar nome do usuário, botão de sair, favoritos e avaliações
    document.getElementById('user-info').style.display = 'flex';
    if(btnLogin) btnLogin.style.display = 'none';
    if(btnFavoritesHeader) {
      btnFavoritesHeader.style.display = 'block';
      // Adicionar event listener para favoritos
      btnFavoritesHeader.addEventListener('click', () => window.showFavorites());
    }
    if(btnRatingsHeader) {
      btnRatingsHeader.style.display = 'block';
      btnRatingsHeader.addEventListener('click', () => window.showRatings());
    }

    if(btnLogout){
      btnLogout.addEventListener('click', async ()=>{
        try{
          await fetch('/auth/logout', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({user_id: userId})
          });
        }catch(e){
          console.error('Erro ao fazer logout:', e);
        }
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        showToast('Você saiu com sucesso!', 'info', 'Até logo!');
        setTimeout(() => location.reload(), 1000);
      });
    }
  }else{
    // Mostrar botão de login e ocultar favoritos e avaliações
    document.getElementById('user-info').style.display = 'none';
    if(btnFavoritesHeader) btnFavoritesHeader.style.display = 'none';
    if(btnRatingsHeader) btnRatingsHeader.style.display = 'none';
    if(btnLogin){
      btnLogin.style.display = 'block';
      btnLogin.addEventListener('click', ()=> openAuthModal());
    }
  }

  // Elementos do dashboard
  const searchInput = document.getElementById('search-input');
  const btnSearch = document.getElementById('btn-search');
  const resultsContainer = document.getElementById('results-container');
  const loading = document.getElementById('loading');
  const bookModal = document.getElementById('book-modal');
  const closeModal = document.querySelector('.close-modal');

  // Variáveis para rastrear de onde o modal foi aberto
  let openedFromFavorites = false;
  let openedFromRatings = false;

  // Buscar livros
  if(btnSearch && searchInput){
    btnSearch.addEventListener('click', ()=> searchBooks(searchInput.value.trim()));
    searchInput.addEventListener('keypress', (e)=> {
      if(e.key === 'Enter') searchBooks(searchInput.value.trim());
    });
  }

  // Fechar modal
  if(closeModal){
    closeModal.addEventListener('click', ()=> {
      bookModal.style.display = 'none';

      // Se foi aberto dos favoritos, reabre o modal de favoritos
      if (openedFromFavorites) {
        openedFromFavorites = false;
        document.getElementById('favorites-modal').style.display = 'flex';
      }

      // Se foi aberto das avaliações, reabre o modal de avaliações
      if (openedFromRatings) {
        openedFromRatings = false;
        document.getElementById('ratings-modal').style.display = 'flex';
      }
    });
  }
  if(bookModal){
    bookModal.addEventListener('click', (e)=> {
      if(e.target === bookModal) {
        bookModal.style.display = 'none';

        // Se foi aberto dos favoritos, reabre o modal de favoritos
        if (openedFromFavorites) {
          openedFromFavorites = false;
          document.getElementById('favorites-modal').style.display = 'flex';
        }

        // Se foi aberto das avaliações, reabre o modal de avaliações
        if (openedFromRatings) {
          openedFromRatings = false;
          document.getElementById('ratings-modal').style.display = 'flex';
        }
      }
    });
  }

  // Função buscar livros
  async function searchBooks(query){
    console.log('searchBooks called with query:', query);

    if(!query){
      showToast('Digite o nome de um livro para buscar', 'warning');
      return;
    }

    console.log('Mostrando loading...');
    loading.style.display = 'block';
    resultsContainer.innerHTML = '';

    try{
      console.log('Fazendo fetch para /api/books...');
      const res = await fetch('/api/books', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + userId
        },
        body: JSON.stringify({ findBook: query })
      });

      console.log('Response status:', res.status);
      const data = await res.json();
      console.log('Response data:', data);

      if(!res.ok) throw new Error(data.error || 'Erro ao buscar livros');

      displayBooks(data);
    }catch(e){
      console.error('Erro na busca:', e);
      resultsContainer.innerHTML = `
        <div class="error-message">
          <h3>❌ Erro na busca</h3>
          <p>${e.message}</p>
        </div>
      `;
    }finally{
      console.log('Escondendo loading...');
      loading.style.display = 'none';
    }
  }

  // Exibir livros
  function displayBooks(books){
    console.log('displayBooks called with:', books);

    if(!books || books.length === 0){
      resultsContainer.innerHTML = `
        <div class="no-results">
          <div class="no-results-icon">📚</div>
          <h3>Nenhum livro encontrado</h3>
          <p>Tente buscar com outros termos</p>
        </div>
      `;
      return;
    }

    console.log('Exibindo', books.length, 'livros');

    // Criar grid de cards
    const booksHTML = books.map(book => {
      const thumbnail = book.imageLinks?.thumbnail || book.imageLinks?.smallThumbnail || '';
      const authors = Array.isArray(book.authors) ? book.authors.join(', ') : (book.authors || 'Autor desconhecido');
      const description = book.description || 'Sem descrição disponível';
      const shortDescription = description.length > 120 ? description.substring(0, 120) + '...' : description;

      // Extrair ano de publicação se existir
      const publishedYear = book.publishedDate ? book.publishedDate.split('-')[0] : '';

      return `
        <div class="book-card" onclick="loadBookDetails('${book.id}')">
          <div class="book-thumbnail">
            ${thumbnail ?
              `<img src="${thumbnail}" alt="${book.title}" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'book-no-cover\\'>📚</div>'">` :
              `<div class="book-no-cover">📚</div>`
            }
          </div>
          <div class="book-info">
            <h3 class="book-title">${book.title}</h3>
            <p class="book-author">${authors}</p>
            ${publishedYear ? `<p class="book-year">${publishedYear}</p>` : ''}
            <p class="book-description">${shortDescription}</p>
            <div class="book-card-footer">
              <span class="book-card-cta">Ver detalhes →</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    resultsContainer.innerHTML = `<div class="books-grid">${booksHTML}</div>`;
    console.log('Livros exibidos com sucesso em grid');
  }

  // Carregar detalhes
  window.loadBookDetails = async function(bookId, fromFavorites = false, fromRatings = false){
    console.log('loadBookDetails called with bookId:', bookId, 'fromFavorites:', fromFavorites, 'fromRatings:', fromRatings);

    // Definir flags se foi aberto dos favoritos ou avaliações
    openedFromFavorites = fromFavorites;
    openedFromRatings = fromRatings;

    // Fechar modal de favoritos se estiver aberto
    const favoritesModal = document.getElementById('favorites-modal');
    if (favoritesModal && favoritesModal.style.display === 'flex') {
      favoritesModal.style.display = 'none';
    }

    // Fechar modal de avaliações se estiver aberto
    const ratingsModal = document.getElementById('ratings-modal');
    if (ratingsModal && ratingsModal.style.display === 'flex') {
      ratingsModal.style.display = 'none';
    }

    const bookDetails = document.getElementById('book-details');
    bookDetails.innerHTML = '<div class="loading"><div class="spinner"></div><p>Carregando...</p></div>';
    bookModal.style.display = 'flex';

    try{
      console.log('Fetching book details from:', `/api/books/${bookId}`);
      const res = await fetch(`/api/books/${bookId}`, {
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + userId }
      });

      console.log('Book details response status:', res.status);
      const data = await res.json();
      console.log('Book details data:', data);

      if(!res.ok) throw new Error(data.error || 'Erro ao carregar detalhes');

      // Backend retorna {book: {...}, avaliacoes: [...]}
      // Precisamos mesclar book com avaliacoes
      const bookData = {
        ...data.book,
        avaliacoes: data.avaliacoes || []
      };

      console.log('Merged book data:', bookData);
      displayBookDetails(bookData);
    }catch(e){
      console.error('Erro ao carregar detalhes:', e);
      bookDetails.innerHTML = `
        <div class="error-message">
          <h3>❌ Erro</h3>
          <p>${e.message}</p>
        </div>
      `;
    }
  };

  // Exibir detalhes
  function displayBookDetails(book){
    console.log('displayBookDetails called with:', book);
    console.log('book.title:', book.title);
    console.log('book.authors:', book.authors);
    console.log('book.imageLinks:', book.imageLinks);

    if(!book || !book.title){
      const bookDetails = document.getElementById('book-details');
      bookDetails.innerHTML = `
        <div class="error-message">
          <h3>❌ Erro</h3>
          <p>Dados do livro inválidos ou incompletos</p>
          <pre>${JSON.stringify(book, null, 2)}</pre>
        </div>
      `;
      return;
    }

    const bookDetails = document.getElementById('book-details');
    const thumbnail = book.imageLinks?.thumbnail || '';
    const authors = Array.isArray(book.authors) && book.authors.length > 0
      ? book.authors.join(', ')
      : 'Autor desconhecido';
    const publisher = book.publisher || '';
    const publishedDate = book.publishedDate || '';
    const publisherInfo = [publisher, publishedDate].filter(x => x).join(' - ');
    const title = book.title || 'Título não disponível';
    const description = book.description || 'Sem descrição disponível.';

    bookDetails.innerHTML = `
      <div class="book-detail-header">
        ${thumbnail ?
          `<img src="${thumbnail}" alt="${title}" onerror="this.style.display='none'">` :
          `<div class="book-no-image">📚</div>`
        }
        <div>
          <h2>${title}</h2>
          <p class="author">${authors}</p>
          ${publisherInfo ? `<p class="publisher">${publisherInfo}</p>` : ''}
          ${book.pageCount ? `<p class="pages">📄 ${book.pageCount} páginas</p>` : ''}
          ${book.language ? `<p class="language">🌐 Idioma: ${book.language.toUpperCase()}</p>` : ''}
        </div>
      </div>
      <div class="book-detail-body">
        <h3>📖 Descrição</h3>
        <p>${description}</p>

        ${book.categories && book.categories.length > 0 ? `
          <h3>🏷️ Categorias</h3>
          <p>${book.categories.join(', ')}</p>
        ` : ''}

        ${book.avaliacoes && book.avaliacoes.length > 0 ? `
          <h3>⭐ Avaliações</h3>
          <div class="avaliacoes">
            ${book.avaliacoes.map(av => `
              <div class="avaliacao">
                <strong>${av.usuario_nome}</strong> - ${'⭐'.repeat(av.estrelas)}
                ${av.comentario ? `<p>${av.comentario}</p>` : ''}
                <small>${new Date(av.data_avaliacao).toLocaleDateString('pt-BR')}</small>
              </div>
            `).join('')}
          </div>
        ` : ''}

        <div class="book-actions">
          <button class="btn-primary" onclick="addToFavorites('${book.id}')">❤️ Favoritar</button>
          <button class="btn-secondary" onclick="rateBook('${book.id}')">⭐ Avaliar</button>
          ${book.previewLink ? `<a href="${book.previewLink}" target="_blank" class="btn-link">👁️ Prévia</a>` : ''}
          ${book.infoLink ? `<a href="${book.infoLink}" target="_blank" class="btn-link">ℹ️ Mais informações</a>` : ''}
        </div>
      </div>
    `;
    console.log('Book details displayed successfully');
  }

  // Adicionar aos favoritos
  window.addToFavorites = async function(bookId){
    if(!isLoggedIn){
      showToast('Faça login para adicionar livros aos favoritos', 'warning', 'Login necessário');
      setTimeout(() => openAuthModal('login'), 500);
      return;
    }
    try{
      const res = await fetch(`/api/users/${userId}/favorites`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + userId
        },
        body: JSON.stringify({ book_id: bookId })
      });
      const data = await res.json();
      if(res.ok) showToast('Livro adicionado aos favoritos!', 'success');
      else showToast(data.error || 'Erro ao adicionar favorito', 'error');
    }catch(e){
      showToast('Erro: ' + e.message, 'error');
    }
  };

  // Avaliar livro
  window.rateBook = async function(bookId){
    if(!isLoggedIn){
      showToast('Faça login para avaliar livros', 'warning', 'Login necessário');
      setTimeout(() => openAuthModal('login'), 500);
      return;
    }

    // Verificar se o usuário já avaliou este livro
    try {
      const res = await fetch(`/api/ratings/${bookId}/check?user_id=${userId}`);
      const data = await res.json();

      if(res.ok && data.ja_avaliou) {
        showToast('Livro já avaliado! Acesse "Minhas Avaliações" para editar sua avaliação.', 'info', 'Já avaliado');
        return;
      }
    } catch(e) {
      console.error('Erro ao verificar avaliação:', e);
      // Se der erro na verificação, continua e deixa abrir o modal
    }

    window.openRatingModal(bookId);
  };

  // Gerenciar fechamento do modal de rating
  const ratingModal = document.getElementById('rating-modal');
  const closeRatingModal = document.getElementById('close-rating-modal');

  if(closeRatingModal){
    closeRatingModal.addEventListener('click', ()=> {
      ratingModal.style.display = 'none';
      // Reabrir modal de avaliações se estava aberto
      const ratingsModal = document.getElementById('ratings-modal');
      if(ratingsModal && ratingsModal.dataset.wasOpen === 'true') {
        ratingsModal.style.display = 'flex';
        ratingsModal.dataset.wasOpen = 'false';
      }
    });
  }

  // Fechar ao clicar fora do modal
  if(ratingModal){
    ratingModal.addEventListener('click', (e)=> {
      if(e.target === ratingModal) {
        ratingModal.style.display = 'none';
        // Reabrir modal de avaliações se estava aberto
        const ratingsModal = document.getElementById('ratings-modal');
        if(ratingsModal && ratingsModal.dataset.wasOpen === 'true') {
          ratingsModal.style.display = 'flex';
          ratingsModal.dataset.wasOpen = 'false';
        }
      }
    });
  }

  // Modal de autenticação
  const authModal = document.getElementById('auth-modal');
  const authClose = document.querySelector('.auth-close');

  if(authClose){
    authClose.addEventListener('click', ()=> authModal.style.display = 'none');
  }

  window.openAuthModal = function(mode = 'login'){
    const loginForm = document.getElementById('login-form-container');
    const registerForm = document.getElementById('register-form-container');

    if(mode === 'login'){
      loginForm.style.display = 'block';
      registerForm.style.display = 'none';
    }else{
      loginForm.style.display = 'none';
      registerForm.style.display = 'block';
    }

    authModal.style.display = 'flex';
  };

  window.switchToRegister = function(){
    document.getElementById('login-form-container').style.display = 'none';
    document.getElementById('register-form-container').style.display = 'block';
  };

  window.switchToLogin = function(){
    document.getElementById('register-form-container').style.display = 'none';
    document.getElementById('login-form-container').style.display = 'block';
  };

  // Login
  const loginForm = document.getElementById('login-form');
  if(loginForm){
    loginForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;

      try{
        const res = await fetch('/auth/login', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({username, password})
        });
        const data = await res.json();

        if(res.ok){
          localStorage.setItem('user_id', data.user_id);
          localStorage.setItem('username', data.username);
          showToast(`Bem-vindo(a), ${data.username}!`, 'success', 'Login realizado!');
          setTimeout(() => location.reload(), 1000);
        }else{
          showToast(data.error || 'Falha no login', 'error');
        }
      }catch(e){
        showToast('Erro: ' + e.message, 'error');
      }
    });
  }

  // Registro
  const registerForm = document.getElementById('register-form');
  if(registerForm){
    registerForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const username = document.getElementById('register-username').value;
      const email = document.getElementById('register-email').value;
      const password = document.getElementById('register-password').value;

      try{
        const res = await fetch('/auth/register', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({username, email, password})
        });
        const data = await res.json();

        if(res.ok){
          showToast('Cadastro realizado com sucesso! Faça login.', 'success');
          btnModalLogin.click(); // Muda para o formulário de login
        }else{
          showToast(data.error || 'Falha no cadastro', 'error');
        }
      }catch(e){
        showToast('Erro: ' + e.message, 'error');
      }
    });
  }

  // Fechar modal de favoritos
  const favoritesClose = document.querySelector('.favorites-close');
  if(favoritesClose){
    favoritesClose.addEventListener('click', ()=>{
      document.getElementById('favorites-modal').style.display = 'none';
    });
  }

  // Fechar modal de avaliações
  const ratingsClose = document.querySelector('.ratings-close');
  if(ratingsClose){
    ratingsClose.addEventListener('click', ()=>{
      document.getElementById('ratings-modal').style.display = 'none';
    });
  }

  // Os event listeners dos botões de favoritos e avaliações agora são
  // adicionados dentro do bloco de login (linhas 72-83)

  // Fechar modais ao clicar fora
  window.addEventListener('click', (e) => {
    const bookModal = document.getElementById('book-modal');
    const authModal = document.getElementById('auth-modal');
    const favoritesModal = document.getElementById('favorites-modal');
    const ratingsModal = document.getElementById('ratings-modal');

    if (e.target === bookModal) {
      bookModal.style.display = 'none';
    }

    if (e.target === authModal) {
      authModal.style.display = 'none';
    }

    if (e.target === favoritesModal) {
      favoritesModal.style.display = 'none';
    }

    if (e.target === ratingsModal) {
      ratingsModal.style.display = 'none';
    }
  });
});

// Função para mostrar favoritos
window.showFavorites = async function() {
  const userId = localStorage.getItem('user_id');

  if (!userId) {
    openAuthModal();
    return;
  }

  const modal = document.getElementById('favorites-modal');
  const content = document.getElementById('favorites-content');

  content.innerHTML = '<p style="text-align: center; padding: 40px;">Carregando favoritos...</p>';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/api/users/${userId}/favorites`);
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Erro ao carregar favoritos');
    }

    if (!data.favorite_books || data.favorite_books.length === 0) {
      content.innerHTML = `
        <div class="no-favorites">
          <div class="no-favorites-icon">💔</div>
          <div class="no-favorites-text">Nenhum livro favorito ainda</div>
          <div class="no-favorites-subtext">Explore livros e adicione aos seus favoritos!</div>
        </div>
      `;
      return;
    }

    // Buscar detalhes de cada livro favorito
    const bookPromises = data.favorite_books.map(bookId =>
      fetch(`/api/books/${bookId}`).then(r => r.json())
    );

    const books = await Promise.all(bookPromises);

    content.innerHTML = books.map(book => {
      const bookData = book.book || book;
      const thumbnail = bookData.imageLinks?.thumbnail || bookData.imageLinks?.smallThumbnail || '/static/img/book-placeholder.png';
      const title = bookData.title || 'Título desconhecido';
      const authors = bookData.authors ? bookData.authors.join(', ') : 'Autor desconhecido';

      return `
        <div class="favorite-item" onclick="loadBookDetails('${bookData.id}', true)">
          <img src="${thumbnail}" alt="${title}" onerror="this.src='/static/img/book-placeholder.png'">
          <div class="favorite-item-title">${title}</div>
          <div class="favorite-item-author">${authors}</div>
          <div class="favorite-item-actions" onclick="event.stopPropagation()">
            <button class="btn-remove-favorite" onclick="removeFavorite('${bookData.id}')">🗑️ Remover</button>
          </div>
        </div>
      `;
    }).join('');

  } catch (error) {
    console.error('Erro ao carregar favoritos:', error);
    content.innerHTML = `
      <div class="no-favorites">
        <div class="no-favorites-icon">⚠️</div>
        <div class="no-favorites-text">Erro ao carregar favoritos</div>
        <div class="no-favorites-subtext">${error.message}</div>
      </div>
    `;
  }
}

// Função para remover favorito
async function removeFavorite(bookId) {
  const userId = localStorage.getItem('user_id');

  showConfirm(
    'Remover dos Favoritos',
    'Tem certeza que deseja remover este livro dos seus favoritos?',
    async () => {
      try {
        const res = await fetch(`/api/users/${userId}/favorites/${bookId}`, {
          method: 'DELETE'
        });

        const data = await res.json();

        if (res.ok) {
          showToast('Livro removido dos favoritos!', 'success', 'Removido!');
          window.showFavorites(); // Recarregar lista
        } else {
          showToast(data.error || 'Erro ao remover favorito', 'error');
        }
      } catch (error) {
        console.error('Erro ao remover favorito:', error);
        showToast('Erro ao remover favorito: ' + error.message, 'error');
      }
    }
  );
}

// Função para mostrar avaliações
// Função para mostrar avaliações
window.showRatings = async function() {
  const userId = localStorage.getItem('user_id');

  if (!userId) {
    openAuthModal();
    return;
  }

  const ratingsModal = document.getElementById('ratings-modal');
  const ratingsList = document.getElementById('ratings-list');

  ratingsList.innerHTML = '<p style="text-align: center; padding: 40px;">Carregando avaliações...</p>';

  ratingsModal.style.display = 'flex';

  try {
    const res = await fetch(`/api/ratings/user/${userId}`);
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Erro ao carregar avaliações');
    }

    if (!data.ratings || data.ratings.length === 0) {
      ratingsList.innerHTML = `
        <div class="no-ratings">
          <div class="no-ratings-icon">⭐</div>
          <div class="no-ratings-text">Nenhuma avaliação ainda</div>
          <div class="no-ratings-subtext">Avalie livros para aparecerem aqui!</div>
        </div>
      `;
      return;
    }

    // Buscar detalhes de cada livro avaliado
    const bookPromises = data.ratings.map(rating =>
      fetch(`/api/books/${rating.google_books_id}`).then(r => r.json())
    );

    const books = await Promise.all(bookPromises);

    ratingsList.innerHTML = data.ratings.map((rating, index) => {
      const book = books[index];
      const bookData = book.book || book;
      const thumbnail = bookData.imageLinks?.thumbnail || bookData.imageLinks?.smallThumbnail || '/static/img/book-placeholder.png';
      const title = bookData.title || 'Título desconhecido';
      const authors = bookData.authors ? bookData.authors.join(', ') : 'Autor desconhecido';
      const dataAvaliacao = new Date(rating.data_avaliacao).toLocaleDateString('pt-BR');

      // Gerar estrelas preenchidas e vazias
      let starsHtml = '';
      for (let i = 1; i <= 5; i++) {
        if (i <= rating.estrelas) {
          starsHtml += '<span class="star filled">⭐</span>';
        } else {
          starsHtml += '<span class="star empty">☆</span>';
        }
      }

      return `
        <div class="rating-item" onclick="loadBookDetails('${bookData.id}', false, true)">
          <div class="rating-item-image">
            <img src="${thumbnail}" alt="${title}" onerror="this.src='/static/img/book-placeholder.png'">
          </div>
          <div class="rating-item-info">
            <h3 class="rating-item-title">${title}</h3>
            <div class="rating-item-author">${authors}</div>
            <div class="rating-stars">
              ${starsHtml}
              <span style="margin-left: 8px; color: #6b7280;">(${rating.estrelas}/5)</span>
            </div>
            ${rating.comentario ? `<div class="rating-item-comment">"${rating.comentario}"</div>` : ''}
            <div class="rating-item-date">Avaliado em: ${dataAvaliacao}</div>
          </div>
          <div class="rating-item-actions" onclick="event.stopPropagation()">
            <button class="btn-edit-rating" onclick="editRating('${rating.google_books_id}', ${rating.estrelas}, '${rating.comentario ? rating.comentario.replace(/'/g, "\\'") : ''}')">✏️ Editar</button>
            <button class="btn-delete-rating" onclick="deleteRating('${rating.google_books_id}')">🗑️ Remover</button>
          </div>
        </div>
      `;
    }).join('');

  } catch (error) {
    console.error('Erro ao carregar avaliações:', error);
    ratingsList.innerHTML = `
      <div class="no-ratings">
        <div class="no-ratings-icon">⚠️</div>
        <div class="no-ratings-text">Erro ao carregar avaliações</div>
        <div class="no-ratings-subtext">${error.message}</div>
      </div>
    `;
  }
}

// Função para editar avaliação
window.editRating = async function(bookId, currentStars, currentComment) {
  // Fechar modal de avaliações se estiver aberto
  const ratingsModal = document.getElementById('ratings-modal');
  if (ratingsModal && ratingsModal.style.display === 'flex') {
    ratingsModal.dataset.wasOpen = 'true';
    ratingsModal.style.display = 'none';
  }

  // Passar true para isEditing para reabrir modal de avaliações após salvar
  window.openRatingModal(bookId, currentStars, currentComment, true);
};

// Função para deletar avaliação
window.deleteRating = async function(bookId) {
  const userId = localStorage.getItem('user_id');

  if (!userId) {
    showToast('Você precisa estar logado para remover avaliações', 'error');
    return;
  }

  showConfirm(
    'Remover Avaliação',
    'Tem certeza que deseja remover esta avaliação?',
    async () => {
      try {
        const res = await fetch(`/api/ratings/${bookId}?user_id=${userId}`, {
          method: 'DELETE'
        });

        const data = await res.json();

        if (res.ok) {
          showToast('Avaliação removida com sucesso!', 'success', 'Removido!');
          window.showRatings(); // Recarregar lista
        } else {
          showToast(data.error || 'Erro ao remover avaliação', 'error');
        }
      } catch (error) {
        console.error('Erro ao remover avaliação:', error);
        showToast('Erro ao remover avaliação: ' + error.message, 'error');
      }
    }
  );
}

