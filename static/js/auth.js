// JS simples para registro/login usando a API /auth
function q(id){return document.getElementById(id)}

function setResult(id, message, type){
  const el = q(id);
  if(!el) return;
  el.textContent = message || '';
  el.classList.remove('error','success');
  if(type) el.classList.add(type);
}

function setButtonState(button, disabled, text){
  if(!button) return;
  button.disabled = !!disabled;
  if(text !== undefined){
    button._origText = button._origText || button.textContent;
    button.textContent = text || button._origText;
  }else if(button._origText){
    button.textContent = button._origText;
  }
  if(disabled) button.classList.add('loading'); else button.classList.remove('loading');
}

function validateUsername(username){
  if(!username || username.trim().length === 0) return 'Informe o usuário.';
  if(username.length < 3) return 'Usuário muito curto (mínimo 3 caracteres).';
  return null;
}

function validatePassword(password){
  if(!password || password.length === 0) return 'Informe a senha.';
  if(password.length < 6) return 'Senha muito curta (mínimo 6 caracteres).';
  return null;
}

function validateEmail(email){
  if(!email || email.trim().length === 0) return 'Informe o email.';
  // simples validação
  if(!/^[^@]+@[^@]+\.[^@]+$/.test(email)) return 'Email inválido.';
  return null;
}

// Register - Cadastrar e mudar para login
q('btn-register').addEventListener('click', async ()=>{
  const username = q('reg-username').value.trim();
  const email = q('reg-email').value.trim();
  const password = q('reg-password').value;

  // Limpar mensagem anterior
  setResult('reg-result', '', null);

  // Validações
  const uErr = validateUsername(username);
  if(uErr){ setResult('reg-result', uErr, 'error'); return; }

  const eErr = validateEmail(email);
  if(eErr){ setResult('reg-result', eErr, 'error'); return; }

  const pErr = validatePassword(password);
  if(pErr){ setResult('reg-result', pErr, 'error'); return; }

  const btn = q('btn-register');
  setButtonState(btn, true, 'Registrando...');

  try{
    const res = await fetch('/auth/register', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({username, password, email})
    });

    const data = await res.json();

    if(res.status === 201){
      // Cadastro realizado com sucesso!
      setResult('reg-result', '✅ Cadastro realizado com sucesso!', 'success');
      setButtonState(btn, false);

      // Limpar campos
      q('reg-username').value = '';
      q('reg-email').value = '';
      q('reg-password').value = '';

      // Aguardar 1.5s e mudar para aba de login
      setTimeout(() => {
        setResult('reg-result', '', null);

        // Mudar para aba de login
        const loginTab = document.querySelector('.tab[data-target="#login-form"]');
        if(loginTab) {
          loginTab.click();
        }
      }, 1500);
    }else{
      // Erro no registro
      const msg = data.error || 'Falha ao registrar. Tente novamente.';
      setResult('reg-result', msg, 'error');
      setButtonState(btn, false);
    }
  }catch(e){
    setResult('reg-result', 'Erro de conexão: ' + e.message, 'error');
    setButtonState(btn, false);
  }
});

// Login
q('btn-login').addEventListener('click', async ()=>{
  const usernameOrEmail = q('login-username').value.trim();
  const password = q('login-password').value;
  setResult('login-result', '', null);

  // Validação
  if(!usernameOrEmail){
    setResult('login-result', 'Informe usuário ou email', 'error');
    return;
  }
  const pErr = validatePassword(password);
  if(pErr){ setResult('login-result', pErr, 'error'); return }

  const btn = q('btn-login');
  setButtonState(btn, true, 'Entrando...');
  try{
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({username: usernameOrEmail, password})
    });
    const data = await res.json();

    console.log('Login response:', res.status, data);

    if(res.ok && data.user_id){
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('username', data.username);
      console.log('Salvou user_id:', data.user_id);
      setResult('login-result', 'Login realizado. Redirecionando...', 'success');
      setTimeout(()=> window.location.href = '/dashboard', 600);
    }else{
      const msg = data.error || 'Falha no login';
      setResult('login-result', msg, 'error');
      alert(msg);
    }
  }catch(e){
    console.error('Erro login:', e);
    setResult('login-result', 'Erro ao conectar: '+e.message, 'error');
    alert('Erro ao conectar: '+e.message);
  }
  finally{ setButtonState(btn, false); }
});

// Quick account check (se botão existir)
const btnMe = q('btn-me');
if(btnMe){
  btnMe.addEventListener('click', async ()=>{
    const userId = localStorage.getItem('user_id');
    setResult('me-result', '', null);
    setResult('me-result', 'Consultando...', null);
    if(!userId){ setResult('me-result', 'Nenhuma sessão. Faça login.', 'error'); return }
    try{
      const res = await fetch('/auth/me', { headers: { 'Authorization': 'Bearer '+userId }});
      const data = await res.json();
      setResult('me-result', res.ok ? ('Logado como '+data.username) : (data.error || JSON.stringify(data)), res.ok ? 'success' : 'error');
      if(!res.ok){ alert(data.error || 'Sessão inválida'); }
    }catch(e){ setResult('me-result', 'Erro: '+e.message, 'error'); alert('Erro: '+e.message) }
  });
}

const btnLogout = q('btn-logout');
if(btnLogout){
  btnLogout.addEventListener('click', ()=>{
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    setResult('me-result', 'Logout realizado.', null);
    window.location.href = '/';
  });
}
