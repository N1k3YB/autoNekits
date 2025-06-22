DECLARE @counter INT = 1;
DECLARE @dbname NVARCHAR(50);
DECLARE @sql NVARCHAR(MAX);

WHILE @counter <= 20
BEGIN
    SET @dbname = 'user224-' + CAST(@counter AS NVARCHAR);
    
    -- Создание базы данных
    SET @sql = 'CREATE DATABASE [' + @dbname + ']';
    EXEC sp_executesql @sql;
    
    -- Переключение на созданную базу данных и создание таблиц
    SET @sql = 'USE [' + @dbname + ']; 
    
    -- Таблица пользователей
    CREATE TABLE Users (
        UserID INT PRIMARY KEY IDENTITY(1,1),
        Username NVARCHAR(100) NOT NULL,
        Email NVARCHAR(150) NOT NULL,
        Password NVARCHAR(100) NOT NULL,
        RegistrationDate DATETIME DEFAULT GETDATE(),
        IsActive BIT DEFAULT 1
    );
    
    -- Таблица категорий
    CREATE TABLE Categories (
        CategoryID INT PRIMARY KEY IDENTITY(1,1),
        CategoryName NVARCHAR(100) NOT NULL,
        Description NVARCHAR(500) NULL
    );
    
    -- Таблица товаров
    CREATE TABLE Products (
        ProductID INT PRIMARY KEY IDENTITY(1,1),
        ProductName NVARCHAR(200) NOT NULL,
        CategoryID INT FOREIGN KEY REFERENCES Categories(CategoryID),
        Price DECIMAL(10,2) NOT NULL,
        InStock INT DEFAULT 0
    );
    
    -- Таблица заказов
    CREATE TABLE Orders (
        OrderID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT FOREIGN KEY REFERENCES Users(UserID),
        OrderDate DATETIME DEFAULT GETDATE(),
        TotalAmount DECIMAL(12,2) NOT NULL,
        Status NVARCHAR(20) DEFAULT ''Pending''
    );
    
    -- Таблица деталей заказа
    CREATE TABLE OrderDetails (
        OrderDetailID INT PRIMARY KEY IDENTITY(1,1),
        OrderID INT FOREIGN KEY REFERENCES Orders(OrderID),
        ProductID INT FOREIGN KEY REFERENCES Products(ProductID),
        Quantity INT NOT NULL,
        UnitPrice DECIMAL(10,2) NOT NULL
    );';
    
    EXEC sp_executesql @sql;
    
    SET @counter = @counter + 1;
END