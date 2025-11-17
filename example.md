## Using PyQuickSQL Query Loader
In your sql file you must specify the start of a query with `-- name: queryname`, and the parameters within the query using `:paramname`.
You can optionally end a query with `-- :end`. See `example.sql`.

Now we can import quicksql and load up some queries.


```python
import quicksql, os
queries = quicksql.LoadSQL(os.path.join(os.getcwd(),'example.sql'))
queries
```




    LoadSQL(C:\Users\charl\PycharmProjects\PyQuickSQL\example.sql)
    Query Name: contributing_employees, Params: order_avg, num_orders
    Query Name: customer_orders, Params: product_id, edate, sdate




```python
print(str(queries))
```

    Queries from:: C:\Users\charl\PycharmProjects\PyQuickSQL\example.sql
    
    -- Query:: contributing_employees
    SELECT
      EmployeeID,
      COUNT(OrderID) AS NumberOfOrders,
      AVG(TotalAmount) AS AverageOrderAmount
    FROM
      Orders
    GROUP BY
      EmployeeID
    HAVING
      COUNT(OrderID) > :num_orders AND AVG(TotalAmount) > :order_avg
    ORDER BY
      AverageOrderAmount DESC;
    /* This query selects the EmployeeID, counts the number of orders, and calculates the average order amount from an Orders table.
       It groups the results by EmployeeID, and includes only those employees who have more than :num_orders orders and where the average order amount is greater than $:order_avg.
       It orders the results by the average order amount in descending order. */
    
    -- Query:: customer_orders
    SELECT
      c.CustomerName,
      o.OrderDate,
      o.Status,
      (SELECT SUM(od.Quantity * od.UnitPrice) FROM OrderDetails od WHERE od.OrderID = o.OrderID) AS TotalValue
    FROM
      Customers c
    INNER JOIN Orders o ON c.CustomerID = o.CustomerID
    WHERE
      o.OrderDate BETWEEN :sdate AND :edate
      AND EXISTS (SELECT 1 FROM OrderDetails od WHERE od.OrderID = o.OrderID AND od.ProductID = :product_id)
    ORDER BY
      TotalValue DESC;
    

And lastly we can produce a query given the arguments specified above.


```python
print(queries.contributing_employees(num_orders=5,order_avg=1000)+'\n\n')
print(queries.customer_orders(product_id=10,sdate='1-10-2022',edate=quicksql.NoStr("DATE'4-11-2023'"),something_not_a_param='test')+'\n\n')
print(queries.contributing_employees(num_orders=6)+'\n\n')
```

    SELECT
      EmployeeID,
      COUNT(OrderID) AS NumberOfOrders,
      AVG(TotalAmount) AS AverageOrderAmount
    FROM
      Orders
    GROUP BY
      EmployeeID
    HAVING
      COUNT(OrderID) > 5 AND AVG(TotalAmount) > 1000
    ORDER BY
      AverageOrderAmount DESC;
    /* This query selects the EmployeeID, counts the number of orders, and calculates the average order amount from an Orders table.
       It groups the results by EmployeeID, and includes only those employees who have more than 5 orders and where the average order amount is greater than $1000.
       It orders the results by the average order amount in descending order. */
    
    
    Unused variables: something_not_a_param in query customer_orders
    SELECT
      c.CustomerName,
      o.OrderDate,
      o.Status,
      (SELECT SUM(od.Quantity * od.UnitPrice) FROM OrderDetails od WHERE od.OrderID = o.OrderID) AS TotalValue
    FROM
      Customers c
    INNER JOIN Orders o ON c.CustomerID = o.CustomerID
    WHERE
      o.OrderDate BETWEEN '1-10-2022' AND DATE'4-11-2023'
      AND EXISTS (SELECT 1 FROM OrderDetails od WHERE od.OrderID = o.OrderID AND od.ProductID = 10)
    ORDER BY
      TotalValue DESC;
    


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    Cell In[3], line 3
          1 print(queries.contributing_employees(num_orders=5,order_avg=1000)+'\n\n')
          2 print(queries.customer_orders(product_id=10,sdate='1-10-2022',edate=quicksql.NoStr("DATE'4-11-2023'"),something_not_a_param='test')+'\n\n')
    ----> 3 print(queries.contributing_employees(num_orders=6)+'\n\n')
    

    File ~\PycharmProjects\PyQuickSQL\quicksql\_quicksql.py:119, in Query.__call__(self, **kwargs)
        117     rp=kwargs.get(v[1],None)
        118     if rp is None:
    --> 119         raise ValueError(f"Missing value for variable {v[1]}")
        120     oq=oq.replace(v[0], str(rp) if type(rp) is not str else f"'{rp}'")
        121 chk_nkg=kwargs.keys()-self.vars
    

    ValueError: Missing value for variable order_avg


We can see that the first one returns the query string, the second returns while printing a warning with a notification of a variable not part of the query, and the third raises an error with a missing parameter.  
For now only unordered but not optional `**kwargs` are supported. If it is worth implementing `*args` in the future, that can be added.  
The parameters support any primitive type that can be converted into a string and collections of primitives eg tuples lists.  
However the default treatment of a string is to wrap it in single quotes `' '`.  
If we wanted to format our own SQL object and type reference then we can do that with `quicksql.NoStr`.  
It's only function is to not add `' '` to the string in the query argument `__call__` method.  


```python
quicksql.NoStr(f'ARRAY{[1,2,3,4]}::smallint[]')
```




    ARRAY[1, 2, 3, 4]::smallint[]



## Using PyQuickSQL's Session Transient Asset Cache
This is a utility made to prevent redundant reloading of the same small to (relatively) large data assets from a remote location, and to provide multi-session permanence through your file system if that is desirable.  
It works by caching the asset into a dictionary (default is `use_mem_cache=True`) and returning a copy, like functools @cache decorator.  
If the memory cache fails it will fall back to the file system cache (always enabled hence the name `quicksql.file_cache`), and load the pickled asset.    
If it can't find the pickled asset, it will lastly run the original function and save the asset to the enabled caches. 
To clear the cache you can call `quicksql.clear_cache(clr_mem=True, clr_file=True)`.

Before importing quicksql you can change the default cache, either in your system's environment variables or like below.
The default is `tempfile.gettempdir()`.


```python
import os 
os.environ['QQ_CACHE_DIR']='path/to/cachedir'
```

Now let's test:


```python
from random import randint
import quicksql

@quicksql.file_cache(use_mem_cache=True)
def test_mem_cache(size:int):
    return [randint(0,10) for _ in range(size)]


def test_file_cache(size:int):
    return [randint(0,10) for _ in range(size)]
#if you want your IDE to retain the functions original argument names, this is an easy way:
test_file_cache=quicksql.file_cache(use_mem_cache=False)(test_file_cache)

def test_random(size:int):
    return [randint(0,10) for _ in range(size)]
```


```python
print(test_mem_cache(8))
print(test_file_cache(8))
print(test_random(8))
```

    [8, 4, 6, 6, 2, 7, 1, 0]
    [0, 0, 10, 0, 6, 0, 1, 3]
    [1, 6, 3, 9, 6, 6, 1, 5]
    


```python
print(test_mem_cache(8))
print(test_file_cache(8))
print(test_random(8))
```

    [8, 4, 6, 6, 2, 7, 1, 0]
    [0, 0, 10, 0, 6, 0, 1, 3]
    [8, 1, 1, 3, 2, 10, 10, 7]
    


```python
quicksql.clear_cache(clr_mem=True,clr_file=True)
print(test_mem_cache(8))
print(test_file_cache(8))
print(test_random(8))
```

    Memory cache cleared.
    File cache cleared.
    [2, 7, 7, 2, 5, 10, 3, 0]
    [6, 2, 9, 9, 0, 8, 10, 7]
    [5, 5, 7, 7, 7, 1, 4, 10]
    

It's also possible to bootleg your own history by including descriptor arguments in your query function that aren't actually used in the query.  
For a simple sql query I like to do this by defining `*args` and taking the last of the list as the actual query arg.


```python
def test_memory(*sizes):
    return [randint(0,10) for _ in range(sizes[-1])]
test_memory=quicksql.file_cache(use_mem_cache=True)(test_memory)
```


```python
print(test_memory('Yesterday',8))
print(test_memory('Today','10:30',8))
```

    [10, 4, 3, 4, 8, 0, 7, 4]
    [8, 9, 4, 2, 2, 5, 3, 3]
    


```python
print(test_memory('Yesterday',8))
print(test_memory('Today','10:30',8))
print(test_memory('Today','11:30',8))
print(test_memory('Today','11:30',8))
quicksql.clear_cache(clr_mem=True,clr_file=True)
```

    [10, 4, 3, 4, 8, 0, 7, 4]
    [8, 9, 4, 2, 2, 5, 3, 3]
    [0, 9, 6, 8, 10, 6, 7, 2]
    [0, 9, 6, 8, 10, 6, 7, 2]
    Memory cache cleared.
    File cache cleared.
    

Lastly async functions are supported.


```python
import asyncio as aio
async def atest_memory(*sizes):
    await aio.sleep(.01)
    return [randint(0,10) for _ in range(sizes[-1])]
atest_memory=quicksql.file_cache(use_mem_cache=True)(atest_memory)
print(await atest_memory('Yesterday',8))
```

    [6, 2, 9, 5, 8, 6, 8, 7]
    


```python
print(await atest_memory('Yesterday',8))
```

    [6, 2, 9, 5, 8, 6, 8, 7]
    

### Notes:
The `file_cache` does not currently have great support for data management, you can save the pickled files yourself, change the cache directory, or add metadata as seen above. It would make sense to add a callable argument to specify the filetype and format of the saved asset, that could be implemented in the future.  
Like functools `cache` is meant to reduce the cost of expensive calls, `file_cache` is meant to reduce the startup time for users with slow remote data connections for example when resetting a jupyter notebook or python env.  
This is why there is only one function to clear the entire cache and `pickle` is used to support anything that might come out of a python function. Hence the example above might not be a good idea to use long term unless more functionality is added.  
The key generation is more rudimentary than functools `cache` as well, consisting of the stringified args removing chars that won't write to a file's name.
Features that might be helpful to add later:
- An optional argument in `file_cache` that takes a callable which saves the data asset according to it's spec. eg, dataframe or ndarray -> parquet or csv file.
- Specific cache deletions instead of deleting the entire thing (eg files or sub-directories).
- Extended management of data asset snapshots, such as a separate directory to save permanent files, ability to switch to different directories either as an argument included in `file_cache`, system-wide change, or specific arguments in the wrapped function (or all of them). System-wide is already possible by changing `quicksql._quicksql.cache_dir` after importing, this will change where clear_cache is enacted as well.
- The other reason to add a `file_cache` directory spec, would be connecting the same query to different data sources. That can also be handled using the method shown above.
- The cache delete will fail if there are other directories in the cache, change if subdirectory/multidirectory management is added.
