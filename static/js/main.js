// main.js - Inicialização e Orquestração Principal

import { checkAuth, setupAuthButtons, initAuthForms } from './auth.js';
import { initBookSearch } from './books.js';
import { initBookModal } from './book-details.js';
import { initFavoritesModal } from './favorites.js';
import { initRatingModal } from './ratings.js';

// Inicialização principal
document.addEventListener('DOMContentLoaded', async ()=>{
  // 1. Verificar autenticação
  const { isLoggedIn, username, userId } = await checkAuth();

  // 2. Configurar botões de autenticação
  setupAuthButtons(isLoggedIn, userId, username);

  // 3. Inicializar formulários de autenticação
  initAuthForms();

  // 4. Inicializar busca de livros
  initBookSearch();

  // 5. Inicializar modal de livro
  initBookModal();

  // 6. Inicializar modal de favoritos
  initFavoritesModal();

  // 7. Inicializar modal de avaliações
  initRatingModal();

  // 8. Fechar modais ao clicar fora
  setupModalClickOutside();
});

// Configurar fechamento de modais ao clicar fora
function setupModalClickOutside() {
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
}

