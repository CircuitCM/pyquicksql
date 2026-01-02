"""Parses queries from an sql file, and turns them into callable f-strings. Also a file cache decorator for slow queries and multi-session permanence, supports async functions."""

__version__ = '1.0.3'


from ._quicksql import LoadSQL, NoStr, Query, clear_cache, file_cache, test_cache

__all__ = ["file_cache", "test_cache", "Query", "LoadSQL", "clear_cache", "NoStr"]
