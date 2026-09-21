from __future__ import annotations


class WifiLabError(Exception):
    """Errore previsto e già formulato per l'utente della CLI."""


class ConfigurationError(WifiLabError):
    """Configurazione assente, malformata o incoerente."""


class CommandExecutionError(WifiLabError):
    """Errore durante l'avvio o l'esecuzione di un comando esterno."""


class ProcessExitedError(WifiLabError):
    """Un processo in background è terminato prima del previsto."""

