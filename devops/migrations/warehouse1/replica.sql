CREATE SUBSCRIPTION rpc_sub_warehouse1
CONNECTION 'host=administration port=5432 dbname=vinlab user=replicator password=replicator'
PUBLICATION rpc_pub;
