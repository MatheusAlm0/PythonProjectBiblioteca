logged_users = set()


def login_user(user_id):
    logged_users.add(user_id)
    print(f"[LOGIN] Usuário {user_id} está logado")
    print(f"[INFO] Total de usuários logados: {len(logged_users)}")


def logout_user(user_id):
    if user_id in logged_users:
        logged_users.remove(user_id)
        print(f"[LOGOUT] Usuário {user_id} saiu")
        print(f"[INFO] Total de usuários logados: {len(logged_users)}")
    else:
        print(f"[AVISO] Tentativa de logout de usuário não logado: {user_id}")


def is_logged_in(user_id):
    return user_id in logged_users


def get_logged_users():
    return list(logged_users)


def clear_all_sessions():
    logged_users.clear()
    print("[INFO] Todas as sessões foram limpas")