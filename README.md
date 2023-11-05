# PyQuickSQL
For a more thorough explanation see [example.ipynb](example.ipynb)  
### How to use the query loader:
```python
import quicksql as qq
queries = qq.LoadSQL('path/to/queries.sql')
```
Printing the queries should give you something like this:
```text
LoadSQL('path/to/queries.sql')
Query Name: examplequery_1, Params: order_avg, num_orders
Query Name: examplequery_2, Params: sdate, edate, product_id
```
These are callable objects that return the string given the non-optional **params.  
They are equivalent to an f-string + a lambda but loaded from an sql file and stored in the LoadSQL object.  
`print(str(queries))` will give you the raw SQL string.  
  
How to use them:
```python
print(queries.examplequery_2(product_id=10,sdate='1-10-2022',edate=qq.NoStr("DATE'4-11-2023'"),something_not_a_param='test'))
```
```text
Unused variables: something_not_a_param in query examplequery_2
```
Above will be printed as a warning with invalid inclusions, no non-verbose option yet.
```sql
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
```

### How to use the file cache:
This is very similar to functool's `cache`, with the main difference being that `@qq.file_cache` caches the asset to memory
and to you system's default temporary directory. If the memory cache ever fails (eg a restarted kernel) it will load the asset from it's pickled file.
```python
from random import randint
import quicksql as qq
@qq.file_cache()
def test_mem(size:int):
    return [randint(0,10) for _ in range(size)]

print(test_mem(8))
```
`[10, 3, 4, 9, 2, 2, 4, 2]`
```python
print(test_mem(8))
```
`[10, 3, 4, 9, 2, 2, 4, 2]`

To clear the cache: `qq.clear_cache()`

For more examples and how to configure see [example.ipynb](example.ipynb)