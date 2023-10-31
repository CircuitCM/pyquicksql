import uuid as id
import pickle as pkl
import os
from functools import cache
import re

_mem_cache = {}

class NA(object): #so None is still valid
    pass

#will work after restarting the kernel, maybe add a compression option in the future
def file_cache(use_mem_cache=True):
    def wrapper1(func):
        def wrapper(*args, **kwargs):
            #so its readable and too lazy to figure out a unique type hash, so don't use long collections as args
            key=re.sub(r'\s','_',re.sub(r"[^A-Za-z\s]", '', str([*args, *kwargs.items()])))[:256]
            c_name= f'{func.__name__}_{key}'
            file_name = f"{os.getcwd()}/cache/{c_name}.pkl"
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
                with open(file_name, 'wb') as file:
                    pkl.dump(result, file)
            if use_mem_cache:
                _mem_cache[c_name] = result
            return result
        return wrapper
    return wrapper1


def clear_cache(clr_mem=True, clr_file=True):
    if clr_mem:
        _mem_cache.clear()
        print("Memory cache cleared")
    if clr_file:
        fls=f"{os.getcwd()}/cache"
        for file in os.listdir(f"{os.getcwd()}/cache"):
            os.remove(f'{fls}/{file}')
        print("File cache cleared")

#need to add closed parentheses for it to work idk why
@file_cache()
def test_cache(*args, **kwargs):
    return args, kwargs

_FQS = re.compile(r"--\s*name\s*:\s*")
_FNAM = re.compile(r"\W")
_VIN = re.compile(r":\w+")


class Query:

    def __init__(self, name, query):
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

    def __str__(self):
        return f"-- Query:: {self.name}\n{self.query}"


class LoadSQL:

    def __init__(self, path):
        self.path = path
        with open(path, 'r') as file:
            qf=file.read()

        qdefs = _FQS.split(qf)
        for qdef in qdefs[1:]:
            name, query = qdef.split('\n', 1)
            name = _FNAM.sub('_', name)
            setattr(self, name, Query(name,query.rstrip()))

    def __str__(self):
        _s='\n\n'
        return f"Queries from:: {self.path}\n\n{_s.join([str(qr) for nm,qr in self.__dict__.items() if nm != 'path']) if len(self.__dict__)>1 else {'No queries found.'}}"