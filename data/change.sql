BEGIN TRANSACTION;
UPDATE orders
SET status = 'validated'
WHERE status = 'pending';
COMMIT;
