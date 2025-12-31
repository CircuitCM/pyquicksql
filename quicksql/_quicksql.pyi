

from functools import cache

_mem_cache = ...
cache_dir = ...
if cache_dir is None:
    cache_dir = ...
_FQS = ...
_FNAM = ...
_VIN = ...
_alljopts = ...
class _NA:
    ...


def file_cache(use_mem_cache=..., threadsafe=...): # -> Callable[..., Callable[..., CoroutineType[Any, Any, Any | _NA]] | Callable[..., Any]]:
    
    ...

def clear_cache(clr_mem=..., clr_file=...): # -> None:
    
    ...

@file_cache()
def test_cache(*args, **kwargs): # -> tuple[tuple[Any, ...], dict[str, Any]]:
    ...

class NoStr:
    __slots__ = ...
    def __init__(self, string: str) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    
    def __repr__(self): # -> str:
        ...
    


class Query:
    
    def __init__(self, name, query) -> None:
        
        ...
    
    def __call__(self, **kwargs): # -> Any:
        ...
    
    @cache
    def __str__(self) -> str:
        ...
    


class LoadSQL:
    
    def __init__(self, path) -> None:
        
        ...
    
    @cache
    def __str__(self) -> str:
        ...
    
    @cache
    def __repr__(self): # -> str:
        ...
    


