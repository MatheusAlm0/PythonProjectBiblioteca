// favorites.js - Sistema de Favoritos

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
window.removeFavorite = async function(bookId) {
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
          window.showFavorites();
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

// Adicionar aos favoritos
window.addToFavorites = async function(bookId){
  const currentUserId = localStorage.getItem('user_id');

  if(!currentUserId){
    showToast('Faça login para adicionar livros aos favoritos', 'warning', 'Login necessário');
    setTimeout(() => window.openAuthModal('login'), 500);
    return;
  }

  try{
    const res = await fetch(`/api/users/${currentUserId}/favorites`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + currentUserId
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

// Inicializar event listeners do modal de favoritos
export function initFavoritesModal() {
  const favoritesClose = document.querySelector('.favorites-close');
  if(favoritesClose){
    favoritesClose.addEventListener('click', ()=>{
      document.getElementById('favorites-modal').style.display = 'none';
    });
  }
}

