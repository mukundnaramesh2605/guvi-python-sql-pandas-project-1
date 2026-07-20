"""30 curated SQL insight queries for the BrickView dashboard, grouped by theme."""

SQL_QUERIES = {
    "Property & Pricing Analysis": [
        {
            "title": "1. What is the average listing price by city?",
            "sql": """
                SELECT city, ROUND(AVG(price), 2) AS average_listing_price
                FROM listings
                GROUP BY city
                ORDER BY average_listing_price DESC;
            """,
        },
        {
            "title": "2. What is the average price per square foot by property type?",
            "sql": """
                SELECT p.furnishingstatus, ROUND(AVG(l.price), 2) AS average_price
                FROM listings l
                JOIN property_attributes p ON l.listingid = p.listingid
                GROUP BY p.furnishingstatus
                ORDER BY average_price DESC;
            """,
        },
        {
            "title": "3. How does furnishing status impact property prices?",
            "sql": """
                SELECT pa.furnishingstatus, ROUND(AVG(l.price), 2) AS avg_price, COUNT(*) AS listings
                FROM listings l
                JOIN property_attributes pa ON pa.listingid = l.listingid
                GROUP BY pa.furnishingstatus
                ORDER BY avg_price DESC;
            """,
        },
        {
            "title": "Do properties closer to metro stations command higher prices?",
            "sql": """
                SELECT CASE
                           WHEN pa.metrodistancekm <= 1 THEN '0-1 km'
                           WHEN pa.metrodistancekm <= 3 THEN '1-3 km'
                           WHEN pa.metrodistancekm <= 5 THEN '3-5 km'
                           ELSE '5+ km'
                       END AS metro_distance_bucket,
                       ROUND(AVG(l.price), 2) AS avg_price,
                       COUNT(*) AS listings
                FROM listings l
                JOIN property_attributes pa ON pa.listingid = l.listingid
                GROUP BY metro_distance_bucket
                ORDER BY MIN(pa.metrodistancekm);
            """,
        },
        {
            "title": "Are rented properties priced differently from non-rented ones?",
            "sql": """
                SELECT CASE WHEN pa.isrented = 1 THEN 'Rented' ELSE 'Not Rented' END AS rental_status,
                       ROUND(AVG(l.price), 2) AS avg_price,
                       COUNT(*) AS listings
                FROM listings l
                JOIN property_attributes pa ON pa.listingid = l.listingid
                GROUP BY rental_status;
            """,
        },
        {
            "title": "How do bedrooms and bathrooms affect pricing?",
            "sql": """
                SELECT pa.bedrooms, pa.bathrooms,
                       ROUND(AVG(l.price), 2) AS avg_price,
                       COUNT(*) AS listings
                FROM listings l
                JOIN property_attributes pa ON pa.listingid = l.listingid
                GROUP BY pa.bedrooms, pa.bathrooms
                ORDER BY pa.bedrooms, pa.bathrooms;
            """,
        },
        {
            "title": "Do properties with parking and power backup sell at higher prices?",
            "sql": """
                SELECT CASE WHEN pa.parkingavailable = 1 THEN 'Yes' ELSE 'No' END AS parking_available,
                       CASE WHEN pa.powerbackup = 1 THEN 'Yes' ELSE 'No' END AS power_backup,
                       ROUND(AVG(l.price), 2) AS avg_price,
                       COUNT(*) AS listings
                FROM listings l
                JOIN property_attributes pa ON pa.listingid = l.listingid
                GROUP BY parking_available, power_backup
                ORDER BY avg_price DESC;
            """,
        },
        {
            "title": "How does year built influence listing price?",
            "sql": """
                SELECT pa.yearbuilt, ROUND(AVG(l.price), 2) AS avg_price, COUNT(*) AS listings
                FROM listings l
                JOIN property_attributes pa ON pa.listingid = l.listingid
                GROUP BY pa.yearbuilt
                ORDER BY pa.yearbuilt;
            """,
        },
        {
            "title": "Which cities have the highest average property prices?",
            "sql": """
                SELECT city, ROUND(AVG(price), 2) AS avg_price
                FROM listings
                GROUP BY city
                ORDER BY avg_price DESC
                LIMIT 10;
            """,
        },
        {
            "title": "How are properties distributed across price buckets?",
            "sql": """
                SELECT CASE
                           WHEN price < 250000 THEN '< 250K'
                           WHEN price < 500000 THEN '250K - 500K'
                           WHEN price < 750000 THEN '500K - 750K'
                           WHEN price < 1000000 THEN '750K - 1M'
                           ELSE '1M+'
                       END AS price_bucket,
                       COUNT(*) AS listings
                FROM listings
                GROUP BY price_bucket
                ORDER BY MIN(price);
            """,
        },
    ],
    "Sales & Market Performance": [
        {
            "title": "Average days on market by city",
            "sql": """
                SELECT l.city, ROUND(AVG(s.daysonmarket), 1) AS avg_days_on_market
                FROM sales s
                JOIN listings l ON l.listingid = s.listingid
                GROUP BY l.city
                ORDER BY avg_days_on_market;
            """,
        },
        {
            "title": "Which property types sell the fastest?",
            "sql": """
                SELECT l.propertytype, ROUND(AVG(s.daysonmarket), 1) AS avg_days_on_market
                FROM sales s
                JOIN listings l ON l.listingid = s.listingid
                GROUP BY l.propertytype
                ORDER BY avg_days_on_market;
            """,
        },
        {
            "title": "What percentage of properties sold above listing price?",
            "sql": """
                SELECT ROUND(100.0 * SUM(CASE WHEN s.saleprice > l.price THEN 1 ELSE 0 END) / COUNT(*), 2)
                           AS pct_sold_above_list
                FROM sales s
                JOIN listings l ON l.listingid = s.listingid;
            """,
        },
        {
            "title": "Sale-to-list price ratio by city",
            "sql": """
                SELECT l.city, ROUND(AVG(s.saleprice * 1.0 / l.price), 3) AS sale_to_list_ratio
                FROM sales s
                JOIN listings l ON l.listingid = s.listingid
                GROUP BY l.city
                ORDER BY sale_to_list_ratio DESC;
            """,
        },
        {
            "title": "Which listings took more than 90 days to sell?",
            "sql": """
                SELECT l.listingid, l.city, l.propertytype, l.price, s.saleprice, s.daysonmarket
                FROM sales s
                JOIN listings l ON l.listingid = s.listingid
                WHERE s.daysonmarket > 90
                ORDER BY s.daysonmarket DESC;
            """,
        },
        {
            "title": "How does metro distance affect time on market?",
            "sql": """
                SELECT CASE
                           WHEN pa.metrodistancekm <= 1 THEN '0-1 km'
                           WHEN pa.metrodistancekm <= 3 THEN '1-3 km'
                           WHEN pa.metrodistancekm <= 5 THEN '3-5 km'
                           ELSE '5+ km'
                       END AS metro_distance_bucket,
                       ROUND(AVG(s.daysonmarket), 1) AS avg_days_on_market
                FROM sales s
                JOIN property_attributes pa ON pa.listingid = s.listingid
                GROUP BY metro_distance_bucket
                ORDER BY MIN(pa.metrodistancekm);
            """,
        },
        {
            "title": "What is the monthly sales trend?",
            "sql": """
                SELECT strftime('%Y-%m', datesold) AS month,
                       COUNT(*) AS sales_count,
                       ROUND(SUM(saleprice), 2) AS total_revenue
                FROM sales
                GROUP BY month
                ORDER BY month;
            """,
        },
        {
            "title": "Which properties are currently unsold?",
            "sql": """
                SELECT l.listingid, l.city, l.propertytype, l.price, l.datelisted
                FROM listings l
                LEFT JOIN sales s ON s.listingid = l.listingid
                WHERE s.listingid IS NULL
                ORDER BY l.datelisted;
            """,
        },
    ],
    "Agent Performance": [
        {
            "title": "Which agents have closed the most sales?",
            "sql": """
                SELECT a.agentid, a.name, COUNT(s.listingid) AS sales_closed
                FROM agents a
                JOIN listings l ON l.agentid = a.agentid
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY a.agentid, a.name
                ORDER BY sales_closed DESC
                LIMIT 10;
            """,
        },
        {
            "title": "Who are the top agents by total sales revenue?",
            "sql": """
                SELECT a.agentid, a.name, ROUND(SUM(s.saleprice), 2) AS total_revenue
                FROM agents a
                JOIN listings l ON l.agentid = a.agentid
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY a.agentid, a.name
                ORDER BY total_revenue DESC
                LIMIT 10;
            """,
        },
        {
            "title": "Which agents close deals fastest?",
            "sql": """
                SELECT a.agentid, a.name, ROUND(AVG(s.daysonmarket), 1) AS avg_days_on_market
                FROM agents a
                JOIN listings l ON l.agentid = a.agentid
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY a.agentid, a.name
                ORDER BY avg_days_on_market ASC
                LIMIT 10;
            """,
        },
        {
            "title": "Does experience correlate with deals closed?",
            "sql": """
                SELECT experienceyears, ROUND(AVG(dealsclosed), 2) AS avg_deals_closed, COUNT(*) AS agents
                FROM agents
                GROUP BY experienceyears
                ORDER BY experienceyears;
            """,
        },
        {
            "title": "Do agents with higher ratings close deals faster?",
            "sql": """
                SELECT ROUND(a.rating, 1) AS rating, ROUND(AVG(s.daysonmarket), 1) AS avg_days_on_market
                FROM agents a
                JOIN listings l ON l.agentid = a.agentid
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY ROUND(a.rating, 1)
                ORDER BY rating DESC;
            """,
        },
        {
            "title": "What is the average commission earned by each agent?",
            "sql": """
                SELECT a.agentid, a.name, a.commissionrate,
                       ROUND(SUM(s.saleprice * a.commissionrate / 100.0), 2) AS total_commission_earned
                FROM agents a
                JOIN listings l ON l.agentid = a.agentid
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY a.agentid, a.name, a.commissionrate
                ORDER BY total_commission_earned DESC;
            """,
        },
        {
            "title": "Which agents currently have the most active listings?",
            "sql": """
                SELECT a.agentid, a.name, COUNT(l.listingid) AS active_listings
                FROM agents a
                JOIN listings l ON l.agentid = a.agentid
                LEFT JOIN sales s ON s.listingid = l.listingid
                WHERE s.listingid IS NULL
                GROUP BY a.agentid, a.name
                ORDER BY active_listings DESC
                LIMIT 10;
            """,
        },
    ],
    "Buyer & Financing Behavior": [
        {
            "title": "What percentage of buyers are investors vs end users?",
            "sql": """
                SELECT buyertype,
                       COUNT(*) AS buyers,
                       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM buyers), 2) AS pct_of_buyers
                FROM buyers
                GROUP BY buyertype;
            """,
        },
        {
            "title": "Which cities have the highest loan uptake rate?",
            "sql": """
                SELECT l.city,
                       ROUND(100.0 * SUM(CASE WHEN b.loantaken = 1 THEN 1 ELSE 0 END) / COUNT(*), 2)
                           AS loan_uptake_pct
                FROM buyers b
                JOIN sales s ON s.listingid = b.saleid
                JOIN listings l ON l.listingid = s.listingid
                GROUP BY l.city
                ORDER BY loan_uptake_pct DESC;
            """,
        },
        {
            "title": "What is the average loan amount by buyer type?",
            "sql": """
                SELECT buyertype, ROUND(AVG(loanamount), 2) AS avg_loan_amount
                FROM buyers
                WHERE loantaken = 1
                GROUP BY buyertype;
            """,
        },
        {
            "title": "Which payment mode is most commonly used?",
            "sql": """
                SELECT paymentmode, COUNT(*) AS buyers
                FROM buyers
                GROUP BY paymentmode
                ORDER BY buyers DESC;
            """,
        },
        {
            "title": "Do loan-backed purchases take longer to close?",
            "sql": """
                SELECT CASE WHEN b.loantaken = 1 THEN 'Loan' ELSE 'No Loan' END AS financing,
                       ROUND(AVG(s.daysonmarket), 1) AS avg_days_on_market
                FROM buyers b
                JOIN sales s ON s.listingid = b.saleid
                GROUP BY financing;
            """,
        },
    ],
}
