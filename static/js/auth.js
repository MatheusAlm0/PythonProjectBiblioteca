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

// Register
q('btn-register').addEventListener('click', async ()=>{
  const username = q('reg-username').value.trim();
  const email = q('reg-email').value.trim();
  const password = q('reg-password').value;
  setResult('reg-result', '', null);

  const uErr = validateUsername(username);
  const pErr = validatePassword(password);
  const eErr = validateEmail(email);
  if(uErr){ setResult('reg-result', uErr, 'error'); return }
  if(eErr){ setResult('reg-result', eErr, 'error'); return }
  if(pErr){ setResult('reg-result', pErr, 'error'); return }

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
      // Registro OK -> realizar login automaticamente
      setResult('reg-result', 'Registro realizado. Entrando...', 'success');
      // Fazer login automático
      try{
        setButtonState(btn, true, 'Entrando...');
        const loginRes = await fetch('/auth/login', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({username, password})
        });
        const loginData = await loginRes.json();
        if(loginRes.ok && loginData.token){
          localStorage.setItem('auth_token', loginData.token);
          // redirecionar para dashboard após breve pausa
          setResult('reg-result', 'Entrando... Redirecionando.', 'success');
          setTimeout(()=> window.location.href = '/dashboard', 500);
          return;
        }else{
          const msg = loginData.error || 'Registro efetuado, mas login automático falhou.';
          setResult('reg-result', msg, 'error');
          alert(msg);
        }
      }catch(e){
        setResult('reg-result', 'Erro no login automático: '+e.message, 'error');
        alert('Erro no login automático: '+e.message);
      }finally{
        setButtonState(btn, false);
      }

    }else{
      const msg = data.error || 'Falha ao registrar';
      setResult('reg-result', msg, 'error');
      // também mostrar alerta para visibilidade
      alert(msg);
    }
  }catch(e){ setResult('reg-result', 'Erro: '+e.message, 'error'); }
  finally{ setButtonState(btn, false); }
});

// Login
q('btn-login').addEventListener('click', async ()=>{
  const usernameOrEmail = q('login-username').value.trim();
  const password = q('login-password').value;
  setResult('login-result', '', null);

  // Não validar formato de usuário/ email aqui rigidamente; backend decide
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
    if(res.ok && data.token){
      localStorage.setItem('auth_token', data.token);
      setResult('login-result', 'Login realizado. Redirecionando...', 'success');
      // redirecionar para dashboard
      setTimeout(()=> window.location.href = '/dashboard', 600);
    }else{
      const msg = data.error || 'Falha no login';
      setResult('login-result', msg, 'error');
      // manter alerta para erros de autenticação do servidor (visibilidade)
      alert(msg);
    }
  }catch(e){setResult('login-result', 'Erro ao conectar: '+e.message, 'error'); alert('Erro ao conectar: '+e.message)}
  finally{ setButtonState(btn, false); }
});

// Quick account check
q('btn-me').addEventListener('click', async ()=>{
  const token = localStorage.getItem('auth_token');
  setResult('me-result', '', null);
  setResult('me-result', 'Consultando...', null);
  if(!token){ setResult('me-result', 'Nenhum token. Faça login.', 'error'); return }
  try{
    const res = await fetch('/auth/me', { headers: { 'Authorization': 'Bearer '+token }});
    const data = await res.json();
    setResult('me-result', res.ok ? ('Logado como '+data.username) : (data.error || JSON.stringify(data)), res.ok ? 'success' : 'error');
    if(!res.ok){ alert(data.error || 'Token inválido'); }
  }catch(e){ setResult('me-result', 'Erro: '+e.message, 'error'); alert('Erro: '+e.message) }
});

q('btn-logout').addEventListener('click', ()=>{
  localStorage.removeItem('auth_token');
  setResult('me-result', 'Logout realizado.', null);
});
