// ratings.js - Sistema de Avaliações

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
    updateStarDisplay(selectedRating, true);
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
        star.style.filter = 'grayscale(0%) brightness(1)';
        star.style.opacity = '1';
        star.style.transform = 'scale(1)';
      } else {
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
          s.style.filter = 'grayscale(0%) brightness(1)';
          s.style.opacity = '1';
          s.style.transform = 'scale(1.15)';
        } else {
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
        s.classList.remove('filled', 'active');

        if(i < selectedRating){
          s.classList.add('active');
          s.style.filter = 'grayscale(0%) brightness(1)';
          s.style.opacity = '1';
          console.log('Star', i, 'set to ACTIVE (yellow)');
        } else {
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
  const ratingsModal = document.getElementById('ratings-modal');
  if (ratingsModal && ratingsModal.style.display === 'flex') {
    ratingsModal.dataset.wasOpen = 'true';
    ratingsModal.style.display = 'none';
  }

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
          window.showRatings();
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

// Avaliar livro
window.rateBook = async function(bookId){
  const currentUserId = localStorage.getItem('user_id');

  if(!currentUserId){
    showToast('Faça login para avaliar livros', 'warning', 'Login necessário');
    setTimeout(() => window.openAuthModal('login'), 500);
    return;
  }

  // Verificar se o usuário já avaliou este livro
  try {
    const res = await fetch(`/api/ratings/${bookId}/check?user_id=${currentUserId}`);
    const data = await res.json();

    if(res.ok && data.ja_avaliou) {
      showToast('Livro já avaliado! Acesse "Minhas Avaliações" para editar sua avaliação.', 'info', 'Já avaliado');
      return;
    }
  } catch(e) {
    console.error('Erro ao verificar avaliação:', e);
  }

  window.openRatingModal(bookId);
};

// Inicializar event listeners do modal de rating
export function initRatingModal() {
  const ratingModal = document.getElementById('rating-modal');
  const closeRatingModal = document.getElementById('close-rating-modal');

  if(closeRatingModal){
    closeRatingModal.addEventListener('click', ()=> {
      ratingModal.style.display = 'none';
      const ratingsModal = document.getElementById('ratings-modal');
      if(ratingsModal && ratingsModal.dataset.wasOpen === 'true') {
        ratingsModal.style.display = 'flex';
        ratingsModal.dataset.wasOpen = 'false';
      }
    });
  }

  if(ratingModal){
    ratingModal.addEventListener('click', (e)=> {
      if(e.target === ratingModal) {
        ratingModal.style.display = 'none';
        const ratingsModal = document.getElementById('ratings-modal');
        if(ratingsModal && ratingsModal.dataset.wasOpen === 'true') {
          ratingsModal.style.display = 'flex';
          ratingsModal.dataset.wasOpen = 'false';
        }
      }
    });
  }

  // Fechar modal de avaliações
  const ratingsClose = document.querySelector('.ratings-close');
  if(ratingsClose){
    ratingsClose.addEventListener('click', ()=>{
      document.getElementById('ratings-modal').style.display = 'none';
    });
  }
}

