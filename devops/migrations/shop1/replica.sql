CREATE SUBSCRIPTION rpc_sub_shop1
CONNECTION 'host=administration port=5432 dbname=vinlab user=replicator password=replicator'
PUBLICATION rpc_pub;

CREATE PUBLICATION rkd_pub1 FOR TABLE 
    Receipts,
    Receipt_positions,
    Orders,
    Ordered_goods;

ALTER SEQUENCE receipt_positions_id_seq RESTART WITH 100001;

CREATE PUBLICATION clients_from_shop1 FOR TABLE Clients;

-- CREATE SUBSCRIPTION clients_from_shop2
-- CONNECTION 'host=shop2 port=5432 dbname=vinlab user=replicator password=replicator'
-- PUBLICATION clients_from_shop1;

-- CREATE SUBSCRIPTION clients_from_shop1
-- CONNECTION 'host=shop1 port=5432 dbname=vinlab user=replicator password=replicator'
-- PUBLICATION clients_from_shop2;