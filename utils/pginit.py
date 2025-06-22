import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import dotenv

dotenv.load_dotenv()

host = os.getenv("PG_HOST")
port = os.getenv("PG_PORT")
user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
default_db = os.getenv("PG_DB")

create_tables_sql = """
-- Таблица пользователей
CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Username VARCHAR(100) NOT NULL,
    Email VARCHAR(150) NOT NULL,
    Password VARCHAR(100) NOT NULL,
    RegistrationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE
);

-- Таблица категорий
CREATE TABLE Categories (
    CategoryID SERIAL PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL,
    Description VARCHAR(500) NULL
);

-- Таблица товаров
CREATE TABLE Products (
    ProductID SERIAL PRIMARY KEY,
    ProductName VARCHAR(200) NOT NULL,
    CategoryID INT REFERENCES Categories(CategoryID),
    Price DECIMAL(10,2) NOT NULL,
    InStock INT DEFAULT 0
);

-- Таблица заказов
CREATE TABLE Orders (
    OrderID SERIAL PRIMARY KEY,
    UserID INT REFERENCES Users(UserID),
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(12,2) NOT NULL,
    Status VARCHAR(20) DEFAULT 'Pending'
);

-- Таблица деталей заказа
CREATE TABLE OrderDetails (
    OrderDetailID SERIAL PRIMARY KEY,
    OrderID INT REFERENCES Orders(OrderID),
    ProductID INT REFERENCES Products(ProductID),
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL
);
"""

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=default_db
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) 
    
    cursor = conn.cursor()
    
    print("Создание баз данных...")
    for i in range(1, 21):
        db_name = f"user224-{i}"
        try:
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            if cursor.fetchone():
                print(f"База данных {db_name} уже существует, пропускаем создание")
            else:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                print(f"База данных {db_name} успешно создана")
        except Exception as e:
            print(f"Ошибка при создании базы данных {db_name}: {e}")
    
    cursor.close()
    conn.close()
    
    print("\nСоздание таблиц в каждой базе данных...")
    for i in range(1, 21):
        db_name = f"user224-{i}"
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            
            cursor.execute(create_tables_sql)
            
            print(f"Таблицы в базе данных {db_name} успешно созданы")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при создании таблиц в базе данных {db_name}: {e}")
    
    print("\nПроцесс завершен успешно!")
    
except Exception as e:
    print(f"Произошла ошибка: {e}")