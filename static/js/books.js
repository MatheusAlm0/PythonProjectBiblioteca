// books.js - Busca e Exibição de Livros

// Função buscar livros
async function searchBooks(query){
  const userId = localStorage.getItem('user_id');
  const loading = document.getElementById('loading');
  const resultsContainer = document.getElementById('results-container');

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
  const resultsContainer = document.getElementById('results-container');

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

// Inicializar busca de livros
export function initBookSearch() {
  const searchInput = document.getElementById('search-input');
  const btnSearch = document.getElementById('btn-search');

  if(btnSearch && searchInput){
    btnSearch.addEventListener('click', ()=> searchBooks(searchInput.value.trim()));
    searchInput.addEventListener('keypress', (e)=> {
      if(e.key === 'Enter') searchBooks(searchInput.value.trim());
    });
  }
}

// Exportar funções
export { searchBooks, displayBooks };

