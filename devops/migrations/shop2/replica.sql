CREATE SUBSCRIPTION rpc_sub_shop2
CONNECTION 'host=administration port=5432 dbname=vinlab user=replicator password=replicator'
PUBLICATION rpc_pub;

CREATE PUBLICATION rkd_pub2 FOR TABLE 
    Receipts,
    Receipt_positions,
    Orders,
    Ordered_goods;

ALTER SEQUENCE receipt_positions_id_seq RESTART WITH 200001;

CREATE PUBLICATION clients_from_shop2 FOR TABLE Clients;