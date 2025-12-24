import requests
from typing import List, Dict
from datetime import datetime
from config.config import Config
from src.cache.redis_client import RedisCache
from src.utils.api_retry import retry_on_rate_limit


class OddsAPI:
    """Serviço para buscar odds com descoberta dinâmica de ligas (soccer)"""

    def __init__(self):
        self.api_key = Config.ODDS_API_KEY
        self.base_url = Config.ODDS_API_BASE_URL
        self.cache = RedisCache()

    # ==========================================================
    # ✅ COMPATIBILIDADE (NÃO QUEBRAR O BettingAgent ANTIGO)
    # ==========================================================
    def get_odds_for_match(self, sport: str = 'soccer_epl') -> List[Dict]:
        """
        Alias para manter compatibilidade com código antigo (BettingAgent).
        O BettingAgent chama get_odds_for_match(sport).
        """
        return self.get_odds_for_sport(sport)

    # =========================
    # 🔹 DESCOBERTA DE LIGAS
    # =========================
    @retry_on_rate_limit(max_retries=3)
    def get_available_soccer_sports(self) -> List[str]:
        """
        Descobre dinamicamente TODAS as ligas de futebol disponíveis na Odds API
        Cache: 24h
        """
        cache_key = "odds:available_soccer_sports"

        cached = self.cache.get(cache_key)
        if cached:
            print("📦 Usando cache (ligas de futebol)")
            return cached

        if not self.api_key:
            return []

        url = f"{self.base_url}/sports"
        params = {"apiKey": self.api_key}

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        sports = response.json()

        soccer_sports = [
            sport["key"]
            for sport in sports
            if sport.get("active") and str(sport.get("key", "")).startswith("soccer_")
        ]

        self.cache.set(cache_key, soccer_sports, expire_seconds=86400)
        print(f"⚽ {len(soccer_sports)} ligas de futebol encontradas")

        return soccer_sports

    # =========================
    # 🔹 BUSCA DE ODDS (GENÉRICA)
    # =========================
    @retry_on_rate_limit(max_retries=3)
    def get_odds_for_sport(self, sport: str) -> List[Dict]:
        """
        Busca odds para uma liga específica
        Cache: 12 HORAS (economia de créditos)
        """
        cache_key = f"odds:{sport}:{datetime.now().strftime('%Y-%m-%d')}"

        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Usando cache (odds {sport})")
            return cached

        if not self.api_key:
            return []

        url = f"{self.base_url}/sports/{sport}/odds"

        params = {
            "apiKey": self.api_key,
            "regions": "us,uk,eu",
            "markets": "h2h,totals,spreads",
            "oddsFormat": "decimal",
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        formatted = self._format_odds(response.json())
        self.cache.set(cache_key, formatted, expire_seconds=43200)  # 12 HORAS

        return formatted

    # =========================
    # 🔹 BUSCA DE ODDS (MASSIVA)
    # =========================
    def get_all_soccer_odds(self) -> List[Dict]:
        """
        Busca odds de TODAS as ligas de futebol disponíveis
        """
        all_odds: List[Dict] = []

        sports = self.get_available_soccer_sports()

        for sport in sports:
            try:
                odds = self.get_odds_for_sport(sport)
                all_odds.extend(odds)
            except Exception as e:
                print(f"⚠️ Falha ao buscar odds de {sport}: {e}")

        print(f"💰 Total de jogos com odds: {len(all_odds)}")
        return all_odds

    # =========================
    # 🔹 FORMATADORES
    # =========================
    def _format_odds(self, data: List[Dict]) -> List[Dict]:
        formatted: List[Dict] = []

        for game in data:
            game_data = {
                "match_id": game.get("id"),
                "home_team": game.get("home_team"),
                "away_team": game.get("away_team"),
                "commence_time": game.get("commence_time"),
                "markets": {},
            }

            for bookmaker in game.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    key = market.get("key")

                    if key == "totals":
                        self._extract_totals(market, game_data["markets"])
                    elif key == "h2h":
                        self._extract_h2h(market, game_data["markets"])
                    elif key == "spreads":
                        self._extract_spreads(market, game_data["markets"])

            if game_data["markets"]:
                formatted.append(game_data)

        return formatted

    def _extract_totals(self, market: Dict, markets_dict: Dict):
        """Extrai Over e Under"""
        for outcome in market.get("outcomes", []):
            point = outcome.get("point", 2.5)
            price = outcome.get("price")

            if outcome.get("name") == "Over":
                key = f"over_{point}"
            elif outcome.get("name") == "Under":
                key = f"under_{point}"
            else:
                continue

            if price is None:
                continue

            # Pega a melhor odd (maior)
            if key not in markets_dict or price > markets_dict[key]:
                markets_dict[key] = price

    def _extract_h2h(self, market: Dict, markets_dict: Dict):
        """Extrai 1X2 (casa, empate, fora)"""
        for outcome in market.get("outcomes", []):
            name = outcome.get("name", "")
            price = outcome.get("price")
            
            if price is None:
                continue
            
            # Extrai empate (pode ser usado futuramente)
            if name == "Draw":
                key = "draw"
                if key not in markets_dict or price > markets_dict[key]:
                    markets_dict[key] = price

    def _extract_spreads(self, market: Dict, markets_dict: Dict):
        """Extrai Handicaps/Spreads"""
        for outcome in market.get("outcomes", []):
            point = outcome.get("point")
            price = outcome.get("price")

            if point is None or price is None:
                continue

            key = f"spread_{point}"
            # Pega a melhor odd (maior)
            if key not in markets_dict or price > markets_dict[key]:
                markets_dict[key] = price