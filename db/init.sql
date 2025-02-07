-- Create the capitol trades table with a composite unique constraint
CREATE TABLE capitol_trades (
    id SERIAL PRIMARY KEY,
    politician VARCHAR(255) NOT NULL,
    party VARCHAR(255) NOT NULL,
    traded_company_name VARCHAR(255) NOT NULL,
    traded_company_ticker VARCHAR(50),
    trade_filed_date DATE NOT NULL,
    trade_owner VARCHAR(100) NOT NULL,
    trade_type VARCHAR(50) NOT NULL,
    trade_size VARCHAR(50) NOT NULL,
    stock_price DECIMAL(10,2),
    published_datetime TIMESTAMP NOT NULL,
    traded_datetime TIMESTAMP NOT NULL,
    trade_id VARCHAR(1000), -- Added original trade_id as optional field

    -- Composite unique constraint on the combination of fields that make a trade unique
    CONSTRAINT unique_trade UNIQUE (
        politician,
        traded_company_name,
        trade_filed_date,
        trade_owner,
        trade_type,
        trade_size,
        traded_datetime
    )
);

-- Create an index to improve query performance on the unique constraint
CREATE INDEX idx_capitol_trades_unique
ON capitol_trades (
    politician,
    traded_company_name,
    trade_filed_date,
    trade_owner,
    trade_type,
    trade_size,
    traded_datetime
);

-- Updated upsert function to include trade_id
CREATE OR REPLACE FUNCTION upsert_capitol_trade(
    p_politician VARCHAR(255),
    p_party VARCHAR(255),
    p_traded_company_name VARCHAR(255),
    p_traded_company_ticker VARCHAR(50),
    p_trade_filed_date DATE,
    p_trade_owner VARCHAR(100),
    p_trade_type VARCHAR(50),
    p_trade_size VARCHAR(50),
    p_stock_price DECIMAL(10,2),
    p_published_datetime TIMESTAMP,
    p_traded_datetime TIMESTAMP,
    p_trade_id VARCHAR(1000)
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO capitol_trades (
        politician,
        party,
        traded_company_name,
        traded_company_ticker,
        trade_filed_date,
        trade_owner,
        trade_type,
        trade_size,
        stock_price,
        published_datetime,
        traded_datetime,
        trade_id
    ) VALUES (
        p_politician,
        p_party,
        p_traded_company_name,
        p_traded_company_ticker,
        p_trade_filed_date,
        p_trade_owner,
        p_trade_type,
        p_trade_size,
        p_stock_price,
        p_published_datetime,
        p_traded_datetime,
        p_trade_id
    )
    ON CONFLICT ON CONSTRAINT unique_trade
    DO UPDATE SET
        party = EXCLUDED.party,
        traded_company_ticker = EXCLUDED.traded_company_ticker,
        stock_price = EXCLUDED.stock_price,
        published_datetime = EXCLUDED.published_datetime,
        trade_id = EXCLUDED.trade_id;
END;
$$ LANGUAGE plpgsql;