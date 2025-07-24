@echo off

REM Neo4j Admin导入命令
REM 适用于Neo4j 2025.02.0及更高版本
REM 生成时间: 2025-03-21 17:08:23

neo4j-admin database import full neo4j --overwrite-destination ^
  --nodes=Product="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\product_nodes.csv" ^
  --nodes=Category="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\category_nodes.csv" ^
  --nodes=Supplier="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\supplier_nodes.csv" ^
  --nodes=Customer="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\customer_nodes.csv" ^
  --nodes=Employee="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\employee_nodes.csv" ^
  --nodes=Shipper="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\shipper_nodes.csv" ^
  --nodes=Order="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\order_nodes.csv" ^
  --nodes=Review="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\review_nodes.csv" ^
  --relationships=BELONGS_TO="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\product_category_edges.csv" ^
  --relationships=SUPPLIED_BY="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\product_supplier_edges.csv" ^
  --relationships=PLACED="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\customer_order_edges.csv" ^
  --relationships=PROCESSED="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\employee_order_edges.csv" ^
  --relationships=SHIPPED_VIA="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\order_shipper_edges.csv" ^
  --relationships=CONTAINS="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\order_product_edges.csv" ^
  --relationships=REPORTS_TO="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\employee_reports_to_edges.csv" ^
  --relationships=WROTE="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\customer_review_edges.csv" ^
  --relationships=ABOUT="E:\my_graphrag\graphrag_2.1.0\graphrag\origin_data\data\neo4j_admin\review_product_edges.csv" ^
  --delimiter="," ^
  --array-delimiter=";" ^
  --skip-bad-relationships=true ^
  --skip-duplicate-nodes=true
