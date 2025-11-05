// auth.js - Autenticação (Login, Registro, Logout)

// Modal de autenticação
window.openAuthModal = function(mode = 'login'){
  const authModal = document.getElementById('auth-modal');
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

// Configurar logout
function setupLogoutButton(userId, username) {
  const btnLogout = document.getElementById('btn-logout');

  if(btnLogout){
    // Remover listeners antigos para evitar duplicação
    btnLogout.replaceWith(btnLogout.cloneNode(true));
    const newBtnLogout = document.getElementById('btn-logout');

    newBtnLogout.addEventListener('click', async ()=>{
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

      // Atualizar interface sem recarregar
      document.getElementById('user-info').style.display = 'none';

      const btnLoginAgain = document.getElementById('btn-login');
      if(btnLoginAgain) btnLoginAgain.style.display = 'block';

      const btnFavoritesAgain = document.getElementById('btn-favorites');
      if(btnFavoritesAgain) btnFavoritesAgain.style.display = 'none';

      const btnRatingsAgain = document.getElementById('btn-ratings');
      if(btnRatingsAgain) btnRatingsAgain.style.display = 'none';
    });
  }
}

// Atualizar interface após login
function updateUIAfterLogin(userId, username) {
  // Atualizar interface sem recarregar
  document.getElementById('username').textContent = username;
  document.getElementById('user-info').style.display = 'flex';

  const btnLogin = document.getElementById('btn-login');
  if(btnLogin) btnLogin.style.display = 'none';

  const btnFavorites = document.getElementById('btn-favorites');
  if(btnFavorites) {
    btnFavorites.style.display = 'block';
    // Adicionar event listener para favoritos
    btnFavorites.replaceWith(btnFavorites.cloneNode(true));
    const newBtnFavorites = document.getElementById('btn-favorites');
    newBtnFavorites.addEventListener('click', () => window.showFavorites());
  }

  const btnRatings = document.getElementById('btn-ratings');
  if(btnRatings) {
    btnRatings.style.display = 'block';
    // Adicionar event listener para avaliações
    btnRatings.replaceWith(btnRatings.cloneNode(true));
    const newBtnRatings = document.getElementById('btn-ratings');
    newBtnRatings.addEventListener('click', () => window.showRatings());
  }

  // Configurar botão de logout
  setupLogoutButton(userId, username);
}

// Inicializar formulários de autenticação
export function initAuthForms() {
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

          // Fechar modal
          const authModal = document.getElementById('auth-modal');
          if(authModal) authModal.style.display = 'none';

          updateUIAfterLogin(data.user_id, data.username);

          // Limpar campos do formulário
          document.getElementById('login-username').value = '';
          document.getElementById('login-password').value = '';
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

        if(res.status === 201){
          showToast('✅ Cadastro realizado com sucesso!', 'success');

          // Limpar campos
          document.getElementById('register-username').value = '';
          document.getElementById('register-email').value = '';
          document.getElementById('register-password').value = '';

          // Mudar para formulário de login após 1.5s
          setTimeout(() => {
            window.switchToLogin();
          }, 1500);
        }else{
          showToast(data.error || 'Falha no cadastro', 'error');
        }
      }catch(e){
        showToast('Erro: ' + e.message, 'error');
      }
    });
  }

  // Fechar modal de autenticação
  const authModal = document.getElementById('auth-modal');
  const authClose = document.querySelector('.auth-close');

  if(authClose){
    authClose.addEventListener('click', ()=> authModal.style.display = 'none');
  }
}

// Verificar se usuário está logado
export async function checkAuth() {
  const userId = localStorage.getItem('user_id');
  let isLoggedIn = false;
  let username = '';

  if(userId){
    try{
      const res = await fetch('/auth/me', {
        headers: { 'Authorization': 'Bearer ' + userId }
      });
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

  return { isLoggedIn, username, userId };
}

// Configurar botões de login/logout e favoritos/avaliações
export function setupAuthButtons(isLoggedIn, userId, username) {
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

        // Atualizar interface sem recarregar
        document.getElementById('user-info').style.display = 'none';

        const btnLogin = document.getElementById('btn-login');
        if(btnLogin) btnLogin.style.display = 'block';

        const btnFavorites = document.getElementById('btn-favorites');
        if(btnFavorites) btnFavorites.style.display = 'none';

        const btnRatings = document.getElementById('btn-ratings');
        if(btnRatings) btnRatings.style.display = 'none';
      });
    }
  }else{
    // Mostrar botão de login e ocultar favoritos e avaliações
    document.getElementById('user-info').style.display = 'none';
    if(btnFavoritesHeader) btnFavoritesHeader.style.display = 'none';
    if(btnRatingsHeader) btnRatingsHeader.style.display = 'none';

    if(btnLogin){
      btnLogin.style.display = 'block';
      btnLogin.addEventListener('click', ()=> window.openAuthModal());
    }
  }
}

