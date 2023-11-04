-- GPT generated queries

-- name: contributing_employees
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

-- name: customer_orders
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
-- :end
/*This query selects the customer name, order date, and status from a hypothetical Customers table and an Orders table;
  calculating the total value of each order on-the-fly with a correlated subquery that sums the product of quantity and unit price from an OrderDetails table.
  It joins the Customers and Orders tables on their common CustomerID field. It filters the results to include orders between :sdate, and :edate, and only includes those orders that contain the product with ProductID :product_id. It orders the results by the TotalValue in descending order. */
