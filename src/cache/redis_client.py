import redis
import json
from typing import Optional, Any
from datetime import timedelta

class RedisCache:
    """Cliente Redis para cache de dados"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Erro ao buscar cache: {e}")
            return None
    
    def set(self, key: str, value: Any, expire_seconds: int = 3600):
        """Salva valor no cache com TTL"""
        try:
            self.client.setex(
                key,
                timedelta(seconds=expire_seconds),
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
            return False
    
    def delete(self, key: str):
        """Remove chave do cache"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Erro ao deletar cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            print(f"Erro ao verificar cache: {e}")
            return False
    
    def clear_all(self):
        """Limpa todo o cache"""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")
            return False