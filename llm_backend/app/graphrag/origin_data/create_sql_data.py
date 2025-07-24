import pymysql
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from faker import Faker
import os

# 数据库连接信息
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'snowball2019',
    'database': 'graphrag'
}

# 初始化Faker生成器
fake = Faker(['zh_CN'])

# 智能家居产品类别
CATEGORIES = [
    "智能音箱", "智能灯具", "智能插座", "智能门锁", "智能摄像头", 
    "智能窗帘", "智能扫地机器人", "智能冰箱", "智能洗衣机", "智能空调",
    "智能电视", "智能体重秤", "智能手环", "智能开关", "智能马桶",
    "智能净水器", "智能空气净化器", "智能加湿器", "智能电饭煲", "智能门铃"
]

# 品牌列表（供应商）
SUPPLIERS = [
    "小米智能家居", "华为智能生活", "苹果智能家庭", "亚马逊智能科技", "谷歌智能设备", 
    "三星智能家电", "飞利浦智能照明", "海尔智慧家庭", "美的智能科技", "格力智能电器",
    "博世智能系统", "西门子智能家居", "松下智能电器", "索尼智能科技", "LG智能家电"
]

# 物流公司
SHIPPERS = [
    "顺丰速运", "京东物流", "中通快递", "圆通速递", "申通快递",
    "韵达快递", "百世快递", "天天快递", "德邦物流", "邮政EMS"
]

# 连接数据库
def connect_to_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("数据库连接成功")
        return conn
    except pymysql.Error as err:
        print(f"数据库连接失败: {err}")
        return None

# 重置数据库
def reset_database(conn):
    cursor = conn.cursor()
    
    # 禁用外键检查
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # 获取所有表名
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 删除所有表
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
        print(f"表 `{table}` 已删除")
    
    # 重新启用外键检查
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("数据库已重置")

# 创建表结构
def create_tables(conn):
    cursor = conn.cursor()
    
    # 创建类别表 (Categories)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categories (
        CategoryID INT AUTO_INCREMENT PRIMARY KEY,
        CategoryName VARCHAR(50) NOT NULL,
        Description TEXT,
        Picture LONGBLOB
    )
    """)
    print("创建表: Categories")
    
    # 创建供应商表 (Suppliers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Suppliers (
        SupplierID INT AUTO_INCREMENT PRIMARY KEY,
        CompanyName VARCHAR(100) NOT NULL,
        ContactName VARCHAR(50),
        ContactTitle VARCHAR(50),
        Address VARCHAR(100),
        City VARCHAR(50),
        Region VARCHAR(50),
        PostalCode VARCHAR(20),
        Country VARCHAR(50),
        Phone VARCHAR(20),
        Fax VARCHAR(20),
        HomePage TEXT
    )
    """)
    print("创建表: Suppliers")
    
    # 创建物流公司表 (Shippers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Shippers (
        ShipperID INT AUTO_INCREMENT PRIMARY KEY,
        CompanyName VARCHAR(100) NOT NULL,
        Phone VARCHAR(20)
    )
    """)
    print("创建表: Shippers")
    
    # 创建员工表 (Employees)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
        LastName VARCHAR(50) NOT NULL,
        FirstName VARCHAR(50) NOT NULL,
        Title VARCHAR(50),
        TitleOfCourtesy VARCHAR(10),
        BirthDate DATE,
        HireDate DATE,
        Address VARCHAR(100),
        City VARCHAR(50),
        Region VARCHAR(50),
        PostalCode VARCHAR(20),
        Country VARCHAR(50),
        HomePhone VARCHAR(20),
        Extension VARCHAR(10),
        Photo LONGBLOB,
        Notes TEXT,
        ReportsTo INT,
        FOREIGN KEY (ReportsTo) REFERENCES Employees(EmployeeID)
    )
    """)
    print("创建表: Employees")
    
    # 创建客户表 (Customers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        CustomerID CHAR(5) PRIMARY KEY,
        CompanyName VARCHAR(100) NOT NULL,
        ContactName VARCHAR(50),
        ContactTitle VARCHAR(50),
        Address VARCHAR(100),
        City VARCHAR(50),
        Region VARCHAR(50),
        PostalCode VARCHAR(20),
        Country VARCHAR(50),
        Phone VARCHAR(20),
        Fax VARCHAR(20)
    )
    """)
    print("创建表: Customers")
    
    # 创建产品表 (Products)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        ProductID INT AUTO_INCREMENT PRIMARY KEY,
        ProductName VARCHAR(100) NOT NULL,
        SupplierID INT,
        CategoryID INT,
        QuantityPerUnit VARCHAR(50),
        UnitPrice DECIMAL(10, 2) DEFAULT 0,
        UnitsInStock INT DEFAULT 0,
        UnitsOnOrder INT DEFAULT 0,
        ReorderLevel INT DEFAULT 0,
        Discontinued TINYINT(1) NOT NULL DEFAULT 0,
        FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
        FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
    )
    """)
    print("创建表: Products")
    
    # 创建订单表 (Orders)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        OrderID INT AUTO_INCREMENT PRIMARY KEY,
        CustomerID CHAR(5),
        EmployeeID INT,
        OrderDate DATETIME,
        RequiredDate DATETIME,
        ShippedDate DATETIME,
        ShipVia INT,
        Freight DECIMAL(10, 2) DEFAULT 0,
        ShipName VARCHAR(100),
        ShipAddress VARCHAR(100),
        ShipCity VARCHAR(50),
        ShipRegion VARCHAR(50),
        ShipPostalCode VARCHAR(20),
        ShipCountry VARCHAR(50),
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
        FOREIGN KEY (ShipVia) REFERENCES Shippers(ShipperID)
    )
    """)
    print("创建表: Orders")
    
    # 创建订单明细表 (Order Details)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS `Order Details` (
        OrderID INT,
        ProductID INT,
        UnitPrice DECIMAL(10, 2) NOT NULL,
        Quantity INT NOT NULL DEFAULT 1,
        Discount FLOAT NOT NULL DEFAULT 0,
        PRIMARY KEY (OrderID, ProductID),
        FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
    )
    """)
    print("创建表: Order Details")
    
    conn.commit()
    print("表结构创建成功")

# 生成类别数据
def generate_categories(conn):
    cursor = conn.cursor()
    
    for category in CATEGORIES:
        description = f"{category}是智能家居领域的重要组成部分，{fake.paragraph()}"
        
        cursor.execute("""
        INSERT INTO Categories (CategoryName, Description)
        VALUES (%s, %s)
        """, (category, description))
    
    conn.commit()
    print(f"已生成 {len(CATEGORIES)} 条类别数据")

# 生成供应商数据
def generate_suppliers(conn):
    cursor = conn.cursor()
    
    for supplier in SUPPLIERS:
        contact_name = fake.name()
        contact_title = random.choice(["销售经理", "市场总监", "CEO", "CTO", "销售代表", "业务经理"])
        address = fake.address()
        city = fake.city()
        region = fake.province()
        postal_code = fake.postcode()
        country = "中国"
        phone = fake.phone_number()
        fax = fake.phone_number()
        home_page = f"http://www.{supplier.lower().replace(' ', '')}.com"
        
        cursor.execute("""
        INSERT INTO Suppliers (CompanyName, ContactName, ContactTitle, Address, City, Region, 
                              PostalCode, Country, Phone, Fax, HomePage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (supplier, contact_name, contact_title, address, city, region, 
              postal_code, country, phone, fax, home_page))
    
    conn.commit()
    print(f"已生成 {len(SUPPLIERS)} 条供应商数据")

# 生成物流公司数据
def generate_shippers(conn):
    cursor = conn.cursor()
    
    for shipper in SHIPPERS:
        phone = fake.phone_number()
        
        cursor.execute("""
        INSERT INTO Shippers (CompanyName, Phone)
        VALUES (%s, %s)
        """, (shipper, phone))
    
    conn.commit()
    print(f"已生成 {len(SHIPPERS)} 条物流公司数据")

# 生成员工数据
def generate_employees(conn, num_employees=20):
    cursor = conn.cursor()
    
    # 职位列表
    titles = ["销售代表", "销售经理", "市场专员", "市场经理", "产品经理", "客户经理", "区域经理", "销售总监", "市场总监", "CEO"]
    
    # 称谓
    title_of_courtesy = ["先生", "女士", "小姐", "博士", "教授"]
    
    employees = []
    
    for i in range(num_employees):
        last_name = fake.last_name()
        first_name = fake.first_name()
        title = random.choice(titles)
        title_courtesy = random.choice(title_of_courtesy)
        birth_date = fake.date_of_birth(minimum_age=22, maximum_age=60)
        hire_date = fake.date_between(start_date='-10y', end_date='today')
        address = fake.address()
        city = fake.city()
        region = fake.province()
        postal_code = fake.postcode()
        country = "中国"
        home_phone = fake.phone_number()
        extension = str(random.randint(100, 999))
        notes = fake.paragraph()
        
        # 先插入没有上级的员工
        reports_to = None
        if i > 0 and random.random() > 0.3:  # 70%的员工有上级
            reports_to = random.choice(employees)
        
        cursor.execute("""
        INSERT INTO Employees (LastName, FirstName, Title, TitleOfCourtesy, BirthDate, HireDate,
                              Address, City, Region, PostalCode, Country, HomePhone, Extension, Notes, ReportsTo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (last_name, first_name, title, title_courtesy, birth_date, hire_date,
              address, city, region, postal_code, country, home_phone, extension, notes, reports_to))
        
        # 保存员工ID用于后续引用
        employees.append(cursor.lastrowid)
    
    conn.commit()
    print(f"已生成 {num_employees} 条员工数据")

# 生成客户数据
def generate_customers(conn, num_customers=100):
    cursor = conn.cursor()
    
    # 公司类型
    company_types = [
        "科技公司", 
        "电子商务", 
        "智能科技", 
        "信息技术", 
        "数字科技", 
        "互联网服务", 
        "金融科技", 
        "生物科技", 
        "云计算", 
        "人工智能", 
        "区块链技术", 
        "大数据分析", 
        "移动应用开发", 
        "网络安全", 
        "虚拟现实", 
        "物联网"
    ]
        # 职位
    titles = ["采购经理", "采购总监", "CEO", "CTO", "运营总监", "技术总监", "项目经理", "总经理"]
    
    # 用于跟踪已生成的客户ID
    generated_ids = set()
    
    for i in range(num_customers):
        # 生成唯一的5位客户ID (字母+数字)
        while True:
            customer_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2)) + ''.join(random.choices('0123456789', k=3))
            if customer_id not in generated_ids:
                generated_ids.add(customer_id)
                break
        
        company_name = fake.company() + random.choice(company_types)
        contact_name = fake.name()
        contact_title = random.choice(titles)
        address = fake.address()
        city = fake.city()
        region = fake.province()
        postal_code = fake.postcode()
        country = "中国"
        phone = fake.phone_number()
        fax = fake.phone_number() if random.random() > 0.3 else None
        
        cursor.execute("""
        INSERT INTO Customers (CustomerID, CompanyName, ContactName, ContactTitle, Address, City, Region,
                              PostalCode, Country, Phone, Fax)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (customer_id, company_name, contact_name, contact_title, address, city, region,
              postal_code, country, phone, fax))
        
        # 每100个客户提交一次，避免事务过大
        if (i + 1) % 100 == 0:
            conn.commit()
            print(f"已生成 {i + 1} 条客户数据")
    
    conn.commit()
    print(f"已生成 {num_customers} 条客户数据")

# 生成产品数据
def generate_products(conn, num_products=100):
    cursor = conn.cursor()
    
    # 获取所有供应商ID
    cursor.execute("SELECT SupplierID FROM Suppliers")
    supplier_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取所有类别ID
    cursor.execute("SELECT CategoryID FROM Categories")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    # 产品型号
    models = ["Pro", "Lite", "Plus", "Max", "Mini", "Ultra", "Standard", "Elite", "Basic", "Advanced"]
    
    # 产品规格
    quantity_units = ["1个/盒", "2个/包", "1台/箱", "1套/箱", "3个/套", "1个/件", "5个/套", "1台/件"]
    
    for i in range(num_products):
        category_id = random.choice(category_ids)
        
        # 获取类别名称
        cursor.execute("SELECT CategoryName FROM Categories WHERE CategoryID = %s", (category_id,))
        category_name = cursor.fetchone()[0]
        
        supplier_id = random.choice(supplier_ids)
        
        # 获取供应商名称
        cursor.execute("SELECT CompanyName FROM Suppliers WHERE SupplierID = %s", (supplier_id,))
        supplier_name = cursor.fetchone()[0]
        
        # 生成产品名称
        product_name = f"{supplier_name.split('智能')[0]} {category_name} {random.choice(models)}"
        
        quantity_per_unit = random.choice(quantity_units)
        unit_price = round(random.uniform(99, 9999), 2)
        units_in_stock = random.randint(0, 1000)
        units_on_order = random.randint(0, 200)
        reorder_level = random.randint(10, 100)
        discontinued = 1 if random.random() < 0.05 else 0  # 5%的产品已停产
        
        cursor.execute("""
        INSERT INTO Products (ProductName, SupplierID, CategoryID, QuantityPerUnit, UnitPrice,
                             UnitsInStock, UnitsOnOrder, ReorderLevel, Discontinued)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (product_name, supplier_id, category_id, quantity_per_unit, unit_price,
              units_in_stock, units_on_order, reorder_level, discontinued))
    
    conn.commit()
    print(f"已生成 {num_products} 条产品数据")

# 生成订单和订单明细数据
def generate_orders(conn, num_orders=1000):
    cursor = conn.cursor()
    
    # 获取所有客户ID
    cursor.execute("SELECT CustomerID FROM Customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取所有员工ID
    cursor.execute("SELECT EmployeeID FROM Employees")
    employee_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取所有物流公司ID
    cursor.execute("SELECT ShipperID FROM Shippers")
    shipper_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取所有产品ID和价格
    cursor.execute("SELECT ProductID, UnitPrice, Discontinued FROM Products")
    product_data = cursor.fetchall()
    
    # 过滤掉已停产的产品
    active_products = [(pid, price) for pid, price, disc in product_data if disc == 0]
    
    for i in range(num_orders):
        customer_id = random.choice(customer_ids)
        employee_id = random.choice(employee_ids)
        
        # 获取客户信息
        cursor.execute("SELECT CompanyName, Address, City, Region, PostalCode, Country FROM Customers WHERE CustomerID = %s", (customer_id,))
        customer_info = cursor.fetchone()
        company_name, address, city, region, postal_code, country = customer_info
        
        order_date = fake.date_time_between(start_date='-2y', end_date='now')
        required_date = order_date + timedelta(days=random.randint(3, 14))
        
        # 80%的订单已发货
        shipped = random.random() < 0.8
        shipped_date = order_date + timedelta(days=random.randint(1, 5)) if shipped else None
        
        ship_via = random.choice(shipper_ids)
        freight = round(random.uniform(10, 500), 2)
        
        cursor.execute("""
        INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, RequiredDate, ShippedDate, ShipVia,
                           Freight, ShipName, ShipAddress, ShipCity, ShipRegion, ShipPostalCode, ShipCountry)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (customer_id, employee_id, order_date, required_date, shipped_date, ship_via,
              freight, company_name, address, city, region, postal_code, country))
        
        order_id = cursor.lastrowid
        
        # 为每个订单生成1-5个订单明细
        num_details = random.randint(1, 5)
        
        # 随机选择产品，确保不重复
        selected_products = random.sample(active_products, min(num_details, len(active_products)))
        
        for product_id, list_price in selected_products:
            quantity = random.randint(1, 20)
            
            # 价格可能有小幅波动
            unit_price = round(float(list_price) * random.uniform(0.95, 1.05), 2)
            
            # 折扣 (0%, 5%, 10%, 15%, 20%)
            discount = random.choice([0, 0.05, 0.1, 0.15, 0.2])
            
            cursor.execute("""
            INSERT INTO `Order Details` (OrderID, ProductID, UnitPrice, Quantity, Discount)
            VALUES (%s, %s, %s, %s, %s)
            """, (order_id, product_id, unit_price, quantity, discount))
        
        # 每100个订单提交一次，避免事务过大
        if (i + 1) % 100 == 0:
            conn.commit()
            print(f"已生成 {i + 1} 条订单数据")
    
    conn.commit()
    print(f"已生成 {num_orders} 条订单数据")

# 生成客户评论数据
def generate_reviews(conn, num_reviews):
    """生成产品评论数据"""
    cursor = conn.cursor()
    
    # 创建评论表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reviews (
        ReviewID INT AUTO_INCREMENT PRIMARY KEY,
        ProductID INT NOT NULL,
        CustomerID CHAR(5) NOT NULL,
        Rating DECIMAL(2,1) NOT NULL,
        ReviewText TEXT NOT NULL,
        ReviewDate DATE NOT NULL,
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
    )
    """)
    print("创建表: Reviews")
    
    # 获取所有产品ID
    cursor.execute("SELECT ProductID, CategoryID, ProductName FROM Products")
    products = cursor.fetchall()
    
    # 获取所有客户ID
    cursor.execute("SELECT CustomerID FROM Customers")
    customers = cursor.fetchall()
    
    # 获取类别名称映射
    cursor.execute("SELECT CategoryID, CategoryName FROM Categories")
    category_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 添加这些变量定义
    specific_features = ["语音识别", "远程控制", "自动调节", "智能学习", "节能模式"]
    unique_features = ["一键控制", "智能场景", "自动升级", "多用户管理", "定时功能"]
    specific_use_cases = ["家庭聚会", "日常使用", "办公环境", "户外活动", "夜间使用"]
    specific_contexts = ["早晨起床", "晚上睡前", "做饭时", "看电影时", "工作时"]
    feature_highlights = ["智能联动", "省电模式", "快速启动", "静音设计", "高清画质"]
    specific_issues = ["连接稳定性", "电池寿命", "噪音控制", "散热问题", "信号强度"]
    
    # 产品特性
    positive_points = [
        "质量很好", "做工精细", "性价比高", "外观漂亮", "功能齐全",
        "操作简单", "反应灵敏", "续航时间长", "音质出色", "画质清晰",
        "稳定性好", "兼容性强", "安装方便", "节能环保", "智能化程度高"
    ]
    
    negative_points = [
        "价格偏高", "做工一般", "功能单一", "操作复杂", "反应迟钝",
        "续航时间短", "音质一般", "画质模糊", "稳定性差", "兼容性差",
        "安装困难", "耗电量大", "智能化程度低", "售后服务差", "使用说明不清"
    ]
    
    # 评论模板
    positive_templates = [
        "这款{category}质量很好，{positive_point}。总体来说很满意。",
        "非常满意这次购买，{positive_point}，送货也很快。",
        "这是我用过的最好的{category}之一，{positive_point}，性价比很高。",
        "{category}的设计很人性化，{positive_point}，值得推荐。",
        "这款{category}的{specific_feature}功能很实用，{positive_point}。",
        "使用了一个月，{positive_point}，没有发现任何问题。",
        "这款产品的{unique_feature}特别好用，在{specific_use_case}时特别方便。",
        "在{specific_context}时使用效果很好，特别是{feature_highlight}功能。"
    ]
    
    neutral_templates = [
        "这款产品优缺点都有，{positive_point}，但{negative_point}。",
        "{category}的质量还可以，{positive_point}，不过{negative_point}。",
        "总体来说还行，{positive_point}，就是{negative_point}。",
        "这款{category}一般，{positive_point}，但是{specific_issue}有点问题。",
        "在{specific_context}使用还不错，但在其他情况下表现一般。"
    ]
    
    negative_templates = [
        "不推荐这款{category}，{negative_point}，很失望。",
        "使用一周后出现故障，{negative_point}，售后服务也不好。",
        "这款产品有严重问题，{negative_point}，已经申请退款。",
        "对这款{category}非常不满意，{negative_point}，浪费钱。",
        "{specific_issue}问题很严重，完全不值这个价格。"
    ]
    
    # 添加更多随机性的辅助函数
    def get_random_sentence_starter():
        starters = [
            "说实话，", "老实讲，", "不得不说，", "必须承认，", "坦白讲，",
            "个人认为，", "我觉得，", "我发现，", "使用后感觉，", "体验下来，",
            "购买后，", "收到货后，", "试用了几天，", "用了一段时间，", "经过一段时间使用，",
            "从我的使用体验来看，", "作为一个经常使用此类产品的人，", "作为第一次购买这类产品的新手，",
            "对比了市面上几款同类产品后，", "在多次对比之后选择了这款，"
        ]
        return random.choice(starters)
    
    def get_random_connector():
        connectors = [
            "而且", "并且", "同时", "此外", "另外",
            "不仅如此", "除此之外", "值得一提的是", "特别是", "尤其是",
            "最重要的是", "更让我满意的是", "让我惊喜的是", "令人意外的是", "最让我失望的是",
            "但是", "不过", "然而", "可惜的是", "遗憾的是"
        ]
        return random.choice(connectors)
    
    def get_random_ending():
        endings = [
            "总体来说还是很满意的。", "整体体验不错。", "推荐给有需要的朋友。", "性价比很高。", "值得购买。",
            "希望厂家能改进这些问题。", "期待下一代产品能有所改进。", "不太推荐购买。", "建议慎重考虑。", "可以考虑其他品牌的同类产品。",
            "这个价位能买到这样的产品已经很不错了。", "对得起这个价格。", "有点贵了，但质量确实好。", "便宜没好货，这句话在这里很适用。", "价格虽高，但物有所值。"
        ]
        return random.choice(endings)
    
    def get_random_time_period():
        periods = [
            "刚收到时", "第一天使用时", "使用一周后", "用了一个月后", "长期使用下来",
            "在冬天使用时", "在夏天使用时", "在家里使用时", "在办公室使用时", "在旅行中使用时",
            "在早上使用时", "在晚上使用时", "在周末使用时", "在工作日使用时", "在特殊场合使用时"
        ]
        return random.choice(periods)
    
    def get_random_comparison():
        comparisons = [
            "比我之前用的产品好多了", "和同价位其他产品相比更胜一筹", "在同类产品中算是中等水平", "和其他品牌相比略显逊色", "在同价位产品中表现最好",
            "比我预期的要好", "没有达到我的期望", "和广告宣传的一样好", "和描述的有些差距", "比我想象的要差一些",
            "和朋友推荐的一样好用", "没有网上评价说的那么好", "比实体店看到的品质更好", "和官方展示的有差距", "比同事使用的同款要好"
        ]
        return random.choice(comparisons)
    
    # 生成评论数据
    for i in range(num_reviews):
        # 随机选择产品和客户
        product = random.choice(products)
        product_id = product[0]
        category_id = product[1]
        product_name = product[2]
        category = category_map.get(category_id, "产品")
        
        customer = random.choice(customers)
        customer_id = customer[0]
        
        # 随机生成评分 (1-5分)
        rating = round(random.uniform(1, 5), 1)
        
        # 根据评分选择评论模板或生成自定义评论
        if random.random() < 0.7:  # 70%概率使用模板
            if rating >= 4:
                template = random.choice(positive_templates)
            elif rating >= 3:
                template = random.choice(neutral_templates)
            else:
                template = random.choice(negative_templates)
            
            positive_point = random.choice(positive_points)
            negative_point = random.choice(negative_points)
            
            # 格式化评论文本
            review_text = template.format(
                category=category,
                positive_point=positive_point,
                negative_point=negative_point,
                specific_feature=random.choice(specific_features),
                unique_feature=random.choice(unique_features),
                specific_use_case=random.choice(specific_use_cases),
                specific_context=random.choice(specific_contexts),
                feature_highlight=random.choice(feature_highlights),
                specific_issue=random.choice(specific_issues)
            )
        else:  # 30%概率生成更自然的自定义评论
            if rating >= 4:
                # 生成正面评价
                review_parts = []
                review_parts.append(get_random_sentence_starter())
                review_parts.append(f"这款{product_name if random.random() < 0.5 else category}")
                review_parts.append(random.choice([
                    "真的很不错", "超出我的预期", "非常满意", "很好用", "品质很好",
                    "做工精细", "设计很人性化", "功能很强大", "性价比很高", "值得推荐"
                ]))
                review_parts.append("。")
                
                if random.random() < 0.8:  # 80%概率添加具体优点
                    review_parts.append(get_random_connector())
                    review_parts.append(random.choice([
                        f"{random.choice(specific_features)}功能特别实用",
                        f"{random.choice(feature_highlights)}设计很贴心",
                        f"在{random.choice(specific_contexts)}时表现尤为出色",
                        f"特别适合{random.choice(specific_use_cases)}",
                        f"{random.choice(unique_features)}是我最喜欢的部分"
                    ]))
                    review_parts.append("。")
                
                if random.random() < 0.4:  # 40%概率添加对比
                    review_parts.append(get_random_comparison())
                    review_parts.append("。")
                
                if random.random() < 0.6:  # 60%概率添加小缺点
                    review_parts.append("如果非要说缺点的话，")
                    review_parts.append(random.choice([
                        f"可能就是{random.choice(negative_points)}",
                        f"{random.choice(specific_issues)}还有提升空间",
                        "价格稍微贵了一点",
                        "说明书不够详细",
                        "配件可以再多一些"
                    ]))
                    review_parts.append("。")
                
                review_parts.append(get_random_ending())
                
                review_text = "".join(review_parts)
            
            elif rating >= 3:
                # 生成中性评价
                review_parts = []
                review_parts.append(get_random_sentence_starter())
                review_parts.append(f"这款{product_name if random.random() < 0.5 else category}")
                review_parts.append(random.choice([
                    "总体来说还可以", "优缺点都有", "中规中矩", "基本符合预期", "一般般",
                    "没有特别惊喜", "也没有特别失望", "质量还行", "功能基本满足需求", "性价比一般"
                ]))
                review_parts.append("。")
                
                # 添加优点
                review_parts.append(random.choice([
                    f"优点是{random.choice(positive_points)}",
                    f"{get_random_time_period()}，{random.choice(specific_features)}表现不错",
                    f"在{random.choice(specific_contexts)}时使用体验还不错",
                    f"{random.choice(feature_highlights)}设计得比较合理"
                ]))
                review_parts.append("。")
                
                # 添加缺点
                review_parts.append(get_random_connector())
                review_parts.append(random.choice([
                    f"缺点是{random.choice(negative_points)}",
                    f"{random.choice(specific_issues)}有点问题",
                    "使用久了会发现一些小问题",
                    f"在{random.choice(specific_use_cases)}场景下表现一般"
                ]))
                review_parts.append("。")
                
                review_parts.append(get_random_ending())
                
                review_text = "".join(review_parts)
            
            else:
                # 生成负面评价
                review_parts = []
                review_parts.append(get_random_sentence_starter())
                review_parts.append(f"这款{product_name if random.random() < 0.5 else category}")
                review_parts.append(random.choice([
                    "很失望", "不推荐购买", "有严重问题", "不值这个价格", "质量太差",
                    "完全不符合预期", "使用体验很差", "存在明显缺陷", "功能实现得很糟糕", "性价比极低"
                ]))
                review_parts.append("。")
                
                # 添加具体问题
                review_parts.append(random.choice([
                    f"主要问题在于{random.choice(negative_points)}",
                    f"{random.choice(specific_issues)}简直无法忍受",
                    f"使用不到一周就出现了{random.choice(['故障', '问题', '异常', '损坏', '失灵'])}",
                    f"在{random.choice(specific_contexts)}时完全不能正常工作"
                ]))
                review_parts.append("。")
                
                if random.random() < 0.3:  # 30%概率提到唯一优点
                    review_parts.append("唯一值得称赞的可能就是")
                    review_parts.append(random.choice([
                        "外观设计还不错", 
                        "包装很精美", 
                        "送货速度快", 
                        "售后服务态度好",
                        "价格便宜"
                    ]))
                    review_parts.append("。")
                
                if random.random() < 0.7:  # 70%概率添加结论
                    review_parts.append(random.choice([
                        "已经申请退款了。",
                        "不推荐任何人购买。",
                        "希望厂家能重视这些问题。",
                        "这钱花得太冤枉了。",
                        "以后不会再考虑这个品牌的产品。"
                    ]))
                
                review_text = "".join(review_parts)
        
        # 生成评论日期 (过去2年内)
        review_date = fake.date_between(start_date='-2y', end_date='today')
        
        # 插入数据库
        cursor.execute("""
        INSERT INTO Reviews (ProductID, CustomerID, Rating, ReviewText, ReviewDate)
        VALUES (%s, %s, %s, %s, %s)
        """, (product_id, customer_id, rating, review_text, review_date))
        
        # 每500条评论提交一次
        if (i + 1) % 500 == 0:
            conn.commit()
            print(f"已生成 {i + 1} 条评论数据")
    
    conn.commit()
    print(f"已生成 {num_reviews} 条评论数据")

import os

def export_to_csv(conn):
    # 确保目录存在
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录
    export_dir = os.path.join(script_dir, 'exported_data')
    os.makedirs(export_dir, exist_ok=True)  # 创建文件夹，如果已存在则不报错
    
    print(f"数据将导出到: {export_dir}")
    
    # 创建SQLAlchemy引擎
    from sqlalchemy import create_engine
    engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    # 导出类别数据
    categories_df = pd.read_sql("SELECT * FROM Categories", engine)
    categories_df.to_csv(os.path.join(export_dir, 'categories.csv'), index=False, encoding='utf-8')
    
    # 导出供应商数据
    suppliers_df = pd.read_sql("SELECT * FROM Suppliers", engine)
    suppliers_df.to_csv(os.path.join(export_dir, 'suppliers.csv'), index=False, encoding='utf-8')
    
    # 导出产品数据
    products_df = pd.read_sql("""
    SELECT p.*, c.CategoryName, s.CompanyName as SupplierName
    FROM Products p
    JOIN Categories c ON p.CategoryID = c.CategoryID
    JOIN Suppliers s ON p.SupplierID = s.SupplierID
    """, engine)
    products_df.to_csv(os.path.join(export_dir, 'products.csv'), index=False, encoding='utf-8')
    
    # 导出客户数据
    customers_df = pd.read_sql("SELECT * FROM Customers", engine)
    customers_df.to_csv(os.path.join(export_dir, 'customers.csv'), index=False, encoding='utf-8')
    
    # 导出员工数据
    employees_df = pd.read_sql("SELECT * FROM Employees", engine)
    employees_df.to_csv(os.path.join(export_dir, 'employees.csv'), index=False, encoding='utf-8')
    
    # 导出物流公司数据
    shippers_df = pd.read_sql("SELECT * FROM Shippers", engine)
    shippers_df.to_csv(os.path.join(export_dir, 'shippers.csv'), index=False, encoding='utf-8')
    
    # 导出订单数据
    orders_df = pd.read_sql("""
    SELECT o.*, c.CompanyName as CustomerName, e.LastName, e.FirstName, s.CompanyName as ShipperName
    FROM Orders o
    JOIN Customers c ON o.CustomerID = c.CustomerID
    JOIN Employees e ON o.EmployeeID = e.EmployeeID
    JOIN Shippers s ON o.ShipVia = s.ShipperID
    """, engine)
    orders_df.to_csv(os.path.join(export_dir, 'orders.csv'), index=False, encoding='utf-8')
    
    # 导出订单明细数据
    order_details_df = pd.read_sql("""
    SELECT od.*, p.ProductName, p.QuantityPerUnit
    FROM `Order Details` od
    JOIN Products p ON od.ProductID = p.ProductID
    """, engine)
    order_details_df.to_csv(os.path.join(export_dir, 'order_details.csv'), index=False, encoding='utf-8')
    
    # 导出销售报表
    sales_report_df = pd.read_sql("""
    SELECT 
        od.OrderID, 
        o.OrderDate,
        c.CustomerID,
        c.CompanyName as CustomerName,
        e.EmployeeID,
        CONCAT(e.FirstName, ' ', e.LastName) as EmployeeName,
        p.ProductID,
        p.ProductName,
        cat.CategoryName,
        s.CompanyName as SupplierName,
        od.UnitPrice,
        od.Quantity,
        od.Discount,
        ROUND(od.UnitPrice * od.Quantity * (1 - od.Discount), 2) as ExtendedPrice
    FROM `Order Details` od
    JOIN Orders o ON od.OrderID = o.OrderID
    JOIN Customers c ON o.CustomerID = c.CustomerID
    JOIN Employees e ON o.EmployeeID = e.EmployeeID
    JOIN Products p ON od.ProductID = p.ProductID
    JOIN Categories cat ON p.CategoryID = cat.CategoryID
    JOIN Suppliers s ON p.SupplierID = s.SupplierID
    ORDER BY o.OrderDate
    """, engine)
    sales_report_df.to_csv(os.path.join(export_dir, 'sales_report.csv'), index=False, encoding='utf-8')
    
    # 添加评论数据导出
    reviews_df = pd.read_sql("""
    SELECT r.ReviewID, r.ProductID, p.ProductName, r.CustomerID, c.CompanyName as CustomerName,
           r.Rating, r.ReviewText, r.ReviewDate, cat.CategoryName
    FROM Reviews r
    JOIN Products p ON r.ProductID = p.ProductID
    JOIN Customers c ON r.CustomerID = c.CustomerID
    JOIN Categories cat ON p.CategoryID = cat.CategoryID
    ORDER BY r.ReviewDate DESC
    """, engine)
    
    reviews_df.to_csv(os.path.join(export_dir, 'reviews.csv'), index=False, encoding='utf-8')
    print(f"评论数据已导出到: {os.path.join(export_dir, 'reviews.csv')}")
    
    print("数据已导出到CSV文件")

# 主函数
def main():
    conn = connect_to_db()
    if conn:
        try:
            # 重置数据库
            reset_database(conn)
            
            # 创建表结构
            create_tables(conn)
            
            # 生成数据
            generate_categories(conn)
            generate_suppliers(conn)
            generate_shippers(conn)
            generate_employees(conn, 3)  # 20名员工
            generate_customers(conn, 20) # 100个客户
            generate_products(conn, 10)  # 100个产品
            generate_orders(conn, 100)   # 1000个订单
            generate_reviews(conn, 30)   # 5000条评论
            
            # 导出数据到CSV
            export_to_csv(conn)
            
            print("数据生成完成！")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    main()
