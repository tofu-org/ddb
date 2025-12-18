CREATE PUBLICATION rpc_pub FOR TABLE 
    Warehouses,
    Workers,
    List_of_goods,
    Shops,
    NSI_category_of_goods,
    NSI_unit_of_measure,
    NSI_of_supplies,
    -- потом убрать
    Supplies_from_warehouse,
    Invoices,
    Orders,
    Clients;

-- CREATE SUBSCRIPTION rkd_sub1
-- CONNECTION 'host=shop1 port=5432 dbname=vinlab user=replicator password=replicator'
-- PUBLICATION rkd_pub1;

-- CREATE SUBSCRIPTION rkd_sub2
-- CONNECTION 'host=shop2 port=5432 dbname=vinlab user=replicator password=replicator'
-- PUBLICATION rkd_pub2;

-- CREATE SUBSCRIPTION clients_from_shops2
-- CONNECTION 'host=shop2 port=5432 dbname=vinlab user=replicator password=replicator'
-- PUBLICATION clients_from_shop1;

-- CREATE SUBSCRIPTION clients_from_shops1
-- CONNECTION 'host=shop1 port=5432 dbname=vinlab user=replicator password=replicator'
-- PUBLICATION clients_from_shop2;

