import uuid as id
import pickle as pkl
import os
from functools import cache
import re

_mem_cache = {}
cache_dir = os.environ.get('QQ_CACHE_DIR', None)
if cache_dir is None:
    import tempfile
    cache_dir=os.path.join(tempfile.gettempdir(),'qqcache')
    os.makedirs(cache_dir, exist_ok=True)

_FQS = re.compile(r"--\s*name\s*:\s*")
_FNAM = re.compile(r"\W")
#the previous regex but includes
_VIN = re.compile(r":\w+")


class NA(object): #so None is still valid
    pass


#files will be loaded in even with new interpreter run, unless use_mem_cache=True
def file_cache(use_mem_cache=True):
    """
    :param use_mem_cache: If true, will cache in memory as well as file
    :return: A decorator that will cache the result of a function in a file
    """

    def wrapper1(func):
        def wrapper(*args, **kwargs):
            #so its readable and too lazy to figure out a unique type hash, so don't use long collections as args unless most of the query is before it.
            key=re.sub(r'\s','_',re.sub(r"[^A-Za-z\s]", '', str([*args, *kwargs.items()])))[:256]
            c_name= f'{func.__name__}_{key}'
            file_name = os.path.join(cache_dir,f"{c_name}.pkl")
            if use_mem_cache:
                val = _mem_cache.get(c_name, NA())
                incache = type(val) is not NA
                if incache:
                    return val
            try:
                with open(file_name, 'rb') as file:
                    result = pkl.load(file)
            except FileNotFoundError:
                f_dir=os.path.dirname(file_name)
                if not os.path.exists(f_dir):
                    os.makedirs(f_dir)
                result = func(*args, **kwargs)
                #File cache is always a backup so restarting an interpreter is safe, Need to explicitly clear cache if the remote dataset changes
                with open(file_name, 'wb') as file:
                    pkl.dump(result, file)
            if use_mem_cache:
                _mem_cache[c_name] = result
            return result
        return wrapper
    return wrapper1


def clear_cache(clr_mem=True, clr_file=True):
    """
    :param clr_mem: If true, will clear memory cache
    :param clr_file: If true, will clear file cache
    :return: None
    """

    if clr_mem:
        _mem_cache.clear()
        print("Memory cache cleared")
    if clr_file:
        for file in os.listdir(cache_dir):
            os.remove(os.path.join(cache_dir, file))
        print("File cache cleared")


#need to add closed parentheses for it to work idk why, maybe an optional arg thing.
@file_cache()
def test_cache(*args, **kwargs):
    return args, kwargs


class Query:
    """
    This is a convenience wrapper to generate SQL queries with named variables. It is basically the same as a lambda **g: f-string
    but it takes the SQL variable notation so it can parse a query from a .sql file.
    """

    def __init__(self, name, query):
        """
        :param name: Name of query
        :param query: SQL query with :var_name variables
        """

        self.name = name
        self.query = query
        self._rvrs=_VIN.findall(query)
        self.vars = [v[1:] for v in self._rvrs]

    def __call__(self, **kwargs):
        #Can't use python string methods here as it might conflict with SQL syntax
        oq=self.query
        for v in zip(self._rvrs, self.vars):
            rp=kwargs.get(v[1],None)
            if rp is None:
                raise ValueError(f"Missing value for variable {v[1]}")
            oq=oq.replace(v[0], str(rp) if type(rp) is not str else f"'{rp}'")
        chk_nkg=kwargs.keys()-self.vars
        if len(chk_nkg)>0:
            print(f"Unused variables: {', '.join(chk_nkg)} in query {self.name}")
        return oq

    @cache
    def __str__(self):
        return f"-- Query:: {self.name}\n{self.query}"




class LoadSQL:
    """
    An object that holds all the named queries from a .sql file.
    Names are specified with -- name: <name> and queries are separated by the next -- name: or -- :end.
    """

    def __init__(self, path):
        """
        :param path: Path to .sql file
        """
        self.path = path
        end_marker = '-- :end'
        with open(path, 'r') as file:
            qf = file.read()

        qdefs = _FQS.split(qf)
        for qdef in qdefs[1:]:
            name, query = qdef.split('\n', 1)
            name = name.strip()

            # Validate that the name is a valid Python identifier
            if not name.isidentifier():
                raise ValueError(f"The name '{name}' is not a valid Python identifier.")

            # Truncate the query if end marker is present
            end_idx = query.rfind(end_marker)
            if end_idx != -1:
                query = query[:end_idx]

            setattr(self, name, Query(name, query.rstrip()))

    @cache
    def __str__(self):
        _s = '\n\n'
        return f"Queries from:: {self.path}\n\n{_s.join([str(qr) for nm, qr in self.__dict__.items() if nm != 'path']) if len(self.__dict__) > 1 else 'No queries found.'}"

    @cache
    def __repr__(self):
        _s = '\n'
        return f"LoadSQL({self.path})\n{_s.join([f'Query Name: '+nm+', Params: '+', '.join(qr.vars) for nm, qr in self.__dict__.items() if nm != 'path']) if len(self.__dict__) > 1 else 'No queries found.'}"