"""
Sistema de Avaliação de Estrelas para Biblioteca
Estrutura completa com banco de dados e lógica de negócio
"""

# ==================== ESTRUTURA DO BANCO DE DADOS ====================

"""
Tabela: avaliacoes
+-----------------+------------------+-------------------------------+
| Campo           | Tipo             | Descrição                     |
+-----------------+------------------+-------------------------------+
| id              | INT (PK)         | ID único da avaliação         |
| livro_id        | INT (FK)         | Referência ao livro           |
| usuario_id      | INT (FK)         | Referência ao usuário         |
| estrelas        | INT (1-5)        | Nota de 1 a 5 estrelas        |
| comentario      | TEXT (opcional)  | Comentário do usuário         |
| data_avaliacao  | DATETIME         | Data/hora da avaliação        |
+-----------------+------------------+-------------------------------+

CONSTRAINT: Um usuário pode avaliar um livro apenas uma vez
INDEX: livro_id, usuario_id (para consultas rápidas)
"""

# SQL para criar a tabela
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livro_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    estrelas INTEGER NOT NULL CHECK(estrelas >= 1 AND estrelas <= 5),
    comentario TEXT,
    data_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (livro_id) REFERENCES livros(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    UNIQUE(livro_id, usuario_id)
);

CREATE INDEX idx_livro_avaliacoes ON avaliacoes(livro_id);
CREATE INDEX idx_usuario_avaliacoes ON avaliacoes(usuario_id);
"""


# ==================== CLASSE DE AVALIAÇÃO ====================

from datetime import datetime
from typing import Optional, List, Dict

class Avaliacao:
    """Classe que representa uma avaliação de livro"""
    
    def __init__(self, livro_id: int, usuario_id: int, estrelas: int, 
                 comentario: Optional[str] = None, id: Optional[int] = None):
        self.id = id
        self.livro_id = livro_id
        self.usuario_id = usuario_id
        self.estrelas = self._validar_estrelas(estrelas)
        self.comentario = comentario
        self.data_avaliacao = datetime.now()
    
    @staticmethod
    def _validar_estrelas(estrelas: int) -> int:
        """Valida se a nota está entre 1 e 5"""
        if not isinstance(estrelas, int) or estrelas < 1 or estrelas > 5:
            raise ValueError("Estrelas devem ser um inteiro entre 1 e 5")
        return estrelas
    
    def to_dict(self) -> Dict:
        """Converte a avaliação para dicionário"""
        return {
            'id': self.id,
            'livro_id': self.livro_id,
            'usuario_id': self.usuario_id,
            'estrelas': self.estrelas,
            'comentario': self.comentario,
            'data_avaliacao': self.data_avaliacao.isoformat()
        }


# ==================== CLASSE DE GERENCIAMENTO ====================

class GerenciadorAvaliacoes:
    """Gerencia todas as operações relacionadas a avaliações"""
    
    def __init__(self, conexao_db):
        """
        Inicializa o gerenciador
        Args:
            conexao_db: Conexão com o banco de dados (sqlite3, psycopg2, etc)
        """
        self.db = conexao_db
    
    def adicionar_avaliacao(self, livro_id: int, usuario_id: int, 
                           estrelas: int, comentario: Optional[str] = None) -> bool:
        """
        Adiciona ou atualiza uma avaliação
        Returns: True se sucesso, False se falha
        """
        try:
            avaliacao = Avaliacao(livro_id, usuario_id, estrelas, comentario)
            
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO avaliacoes (livro_id, usuario_id, estrelas, comentario)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(livro_id, usuario_id) 
                DO UPDATE SET estrelas=?, comentario=?, data_avaliacao=CURRENT_TIMESTAMP
            """, (livro_id, usuario_id, estrelas, comentario, estrelas, comentario))
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar avaliação: {e}")
            return False
    
    def remover_avaliacao(self, livro_id: int, usuario_id: int) -> bool:
        """Remove uma avaliação específica"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                DELETE FROM avaliacoes 
                WHERE livro_id = ? AND usuario_id = ?
            """, (livro_id, usuario_id))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao remover avaliação: {e}")
            return False
    
    def obter_media_livro(self, livro_id: int) -> Optional[float]:
        """
        Calcula a média de estrelas de um livro
        Returns: Média arredondada para 1 casa decimal, ou None se sem avaliações
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT AVG(estrelas) as media, COUNT(*) as total
            FROM avaliacoes 
            WHERE livro_id = ?
        """, (livro_id,))
        
        resultado = cursor.fetchone()
        if resultado and resultado[1] > 0:
            return round(resultado[0], 1)
        return None
    
    def obter_estatisticas_livro(self, livro_id: int) -> Dict:
        """
        Retorna estatísticas completas de um livro
        """
        cursor = self.db.cursor()
        
        # Média e total
        cursor.execute("""
            SELECT AVG(estrelas) as media, COUNT(*) as total
            FROM avaliacoes WHERE livro_id = ?
        """, (livro_id,))
        media_total = cursor.fetchone()
        
        # Distribuição por estrelas
        cursor.execute("""
            SELECT estrelas, COUNT(*) as quantidade
            FROM avaliacoes WHERE livro_id = ?
            GROUP BY estrelas
            ORDER BY estrelas DESC
        """, (livro_id,))
        distribuicao = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'media': round(media_total[0], 1) if media_total[0] else 0,
            'total_avaliacoes': media_total[1],
            'distribuicao': {
                5: distribuicao.get(5, 0),
                4: distribuicao.get(4, 0),
                3: distribuicao.get(3, 0),
                2: distribuicao.get(2, 0),
                1: distribuicao.get(1, 0)
            }
        }
    
    def obter_avaliacoes_livro(self, livro_id: int, limite: int = 10) -> List[Dict]:
        """
        Retorna as avaliações mais recentes de um livro
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT a.id, a.livro_id, a.usuario_id, a.estrelas, 
                   a.comentario, a.data_avaliacao, u.nome as usuario_nome
            FROM avaliacoes a
            LEFT JOIN usuarios u ON a.usuario_id = u.id
            WHERE a.livro_id = ?
            ORDER BY a.data_avaliacao DESC
            LIMIT ?
        """, (livro_id, limite))
        
        avaliacoes = []
        for row in cursor.fetchall():
            avaliacoes.append({
                'id': row[0],
                'livro_id': row[1],
                'usuario_id': row[2],
                'estrelas': row[3],
                'comentario': row[4],
                'data_avaliacao': row[5],
                'usuario_nome': row[6]
            })
        return avaliacoes
    
    def usuario_ja_avaliou(self, livro_id: int, usuario_id: int) -> bool:
        """Verifica se o usuário já avaliou o livro"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM avaliacoes 
            WHERE livro_id = ? AND usuario_id = ?
        """, (livro_id, usuario_id))
        return cursor.fetchone()[0] > 0
    
    def obter_livros_mais_bem_avaliados(self, limite: int = 10, 
                                        min_avaliacoes: int = 5) -> List[Dict]:
        """
        Retorna os livros com melhor média, com mínimo de avaliações
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT l.id, l.titulo, l.autor, 
                   AVG(a.estrelas) as media, 
                   COUNT(a.id) as total_avaliacoes
            FROM livros l
            INNER JOIN avaliacoes a ON l.id = a.livro_id
            GROUP BY l.id
            HAVING COUNT(a.id) >= ?
            ORDER BY media DESC, total_avaliacoes DESC
            LIMIT ?
        """, (min_avaliacoes, limite))
        
        livros = []
        for row in cursor.fetchall():
            livros.append({
                'id': row[0],
                'titulo': row[1],
                'autor': row[2],
                'media': round(row[3], 1),
                'total_avaliacoes': row[4]
            })
        return livros


# ==================== FUNÇÕES AUXILIARES ====================

def renderizar_estrelas_texto(media: float) -> str:
    """
    Renderiza estrelas em formato texto
    Exemplo: 4.3 -> "★★★★☆ (4.3)"
    """
    estrelas_cheias = int(media)
    tem_meia = (media - estrelas_cheias) >= 0.5
    
    resultado = "★" * estrelas_cheias
    if tem_meia:
        resultado += "⯨"
        estrelas_vazias = 4 - estrelas_cheias
    else:
        estrelas_vazias = 5 - estrelas_cheias
    
    resultado += "☆" * estrelas_vazias
    return f"{resultado} ({media})"


def calcular_porcentagem_distribuicao(distribuicao: Dict[int, int]) -> Dict[int, float]:
    """Calcula a porcentagem de cada nota"""
    total = sum(distribuicao.values())
    if total == 0:
        return {i: 0.0 for i in range(1, 6)}
    
    return {
        estrela: round((qtd / total) * 100, 1) 
        for estrela, qtd in distribuicao.items()
    }


# ==================== EXEMPLO DE USO ====================

if __name__ == "__main__":
    import sqlite3
    
    # Conectar ao banco
    conn = sqlite3.connect('biblioteca.db')
    
    # Criar tabela
    conn.executescript(CREATE_TABLE_SQL)
    
    # Inicializar gerenciador
    gerenciador = GerenciadorAvaliacoes(conn)
    
    # Adicionar avaliações de exemplo
    gerenciador.adicionar_avaliacao(livro_id=1, usuario_id=1, estrelas=5, 
                                    comentario="Excelente livro!")
    gerenciador.adicionar_avaliacao(livro_id=1, usuario_id=2, estrelas=4, 
                                    comentario="Muito bom")
    gerenciador.adicionar_avaliacao(livro_id=1, usuario_id=3, estrelas=5)
    
    # Obter estatísticas
    stats = gerenciador.obter_estatisticas_livro(1)
    print(f"Média: {stats['media']}")
    print(f"Total de avaliações: {stats['total_avaliacoes']}")
    print(f"Distribuição: {stats['distribuicao']}")
    
    # Renderizar estrelas
    print(renderizar_estrelas_texto(stats['media']))
    
    # Listar avaliações
    avaliacoes = gerenciador.obter_avaliacoes_livro(1)
    for av in avaliacoes:
        print(f"{av['usuario_nome']}: {'★' * av['estrelas']}")
    
    conn.close()