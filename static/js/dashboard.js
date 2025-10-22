document.addEventListener('DOMContentLoaded', async ()=>{
  const token = localStorage.getItem('auth_token');
  if(!token){
    // não logado -> voltar para login
    alert('Você precisa fazer login');
    window.location.href = '/';
    return;
  }
  try{
    const res = await fetch('/auth/me', { headers: { 'Authorization': 'Bearer '+token }});
    const data = await res.json();
    if(!res.ok){
      alert(data.error || 'Sessão inválida. Faça login novamente.');
      localStorage.removeItem('auth_token');
      window.location.href = '/';
      return;
    }
    document.getElementById('username').textContent = data.username || 'Usuário';
  }catch(e){
    alert('Erro ao validar sessão: '+e.message);
    localStorage.removeItem('auth_token');
    window.location.href = '/';
  }

  const btnLogout = document.getElementById('btn-logout');
  if(btnLogout){
    btnLogout.addEventListener('click', ()=>{
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    });
  }
});

