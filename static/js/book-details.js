// book-details.js - Detalhes do Livro e Modal

// Variáveis para rastrear de onde o modal foi aberto
let openedFromFavorites = false;
let openedFromRatings = false;

// Carregar detalhes
window.loadBookDetails = async function(bookId, fromFavorites = false, fromRatings = false){
  const userId = localStorage.getItem('user_id');
  const bookModal = document.getElementById('book-modal');
  const bookDetails = document.getElementById('book-details');

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

  const bookDetails = document.getElementById('book-details');

  if(!book || !book.title){
    bookDetails.innerHTML = `
      <div class="error-message">
        <h3>❌ Erro</h3>
        <p>Dados do livro inválidos ou incompletos</p>
        <pre>${JSON.stringify(book, null, 2)}</pre>
      </div>
    `;
    return;
  }

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

// Inicializar modal de livro
export function initBookModal() {
  const bookModal = document.getElementById('book-modal');
  const closeModal = document.querySelector('.close-modal');

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
}

// Exportar funções
export { displayBookDetails };

