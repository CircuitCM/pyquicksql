"""Parses queries from an sql file, and turns them into callable f-strings. Also a file cache decorator for slow queries and multi-session permanence."""

__version__ = '1.0'

from ._quicksql import file_cache,test_cache,Query,LoadSQL,clear_cache,NoStr
