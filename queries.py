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
                SELECT propertytype,
                       ROUND(AVG(price * 1.0 / sqft), 2) AS avg_price_per_sqft
                FROM listings
                GROUP BY propertytype
                ORDER BY avg_price_per_sqft DESC;
            """,
        },
        {
            "title": "3. How does furnishing status impact property prices?",
            "sql": """
                SELECT p.furnishingstatus, ROUND(AVG(l.price), 2) AS average_price
                FROM listings l
                JOIN property_attributes p ON l.listingid = p.listingid
                GROUP BY p.furnishingstatus
                ORDER BY average_price DESC;
            """,
        },
        {
            "title": "4. Do properties closer to metro stations command higher prices?",
            "sql": """
                SELECT
                CASE
                    WHEN p.metrodistancekm <= 1 THEN 'Within 1 km'
                    WHEN p.metrodistancekm <= 3 THEN '1 - 3 km'
                    WHEN p.metrodistancekm <= 5 THEN '3 - 5 km'
                    ELSE 'More than 5 km'
                END AS metro_distance,
                COUNT(*) AS total_properties,
                ROUND(AVG(l.price), 2) AS average_price
            FROM listings l
            JOIN property_attributes p ON l.listingid = p.listingid
            GROUP BY metro_distance
            ORDER BY average_price DESC;
            """,
        },
        {
            "title": "5. Are rented properties priced differently from non-rented ones?",
            "sql": """
                SELECT
                    CASE
                        WHEN p.isrented = 1 THEN 'Rented'
                        ELSE 'Non Rented'
                    END AS rental_status,
                    COUNT(*) AS total_properties,
                    ROUND(AVG(l.price), 2) AS average_price
                FROM listings l
                JOIN property_attributes p ON l.listingid = p.listingid
                GROUP BY rental_status
                ORDER BY average_price DESC;
            """,
        },
        {
            "title": "6. How do bedrooms and bathrooms affect pricing?",
            "sql": """
                SELECT p.bedrooms, p.bathrooms, COUNT(*) AS total_properties, ROUND(AVG(l.price), 2) AS average_price
                FROM listings l
                JOIN property_attributes p ON l.listingid = p.listingid
                GROUP BY p.bedrooms, p.bathrooms
                ORDER BY p.bedrooms, p.bathrooms;
            """,
        },
        {
            "title": "7. Do properties with parking and power backup sell at higher prices?",
            "sql": """
                SELECT
                    CASE
                        WHEN p.parkingavailable = 1 THEN 'Parking'
                        ELSE 'No Parking'
                    END AS parking,
                    CASE
                        WHEN p.powerbackup = 1 THEN 'Power Backup'
                        ELSE 'No Power Backup'
                    END AS power_backup,
                    COUNT(*) AS total_properties,
                    ROUND(AVG(l.price), 2) AS average_price
                FROM listings l
                JOIN property_attributes p ON l.listingid = p.listingid
                GROUP BY p.parkingavailable, p.powerbackup
                ORDER BY average_price DESC;
            """,
        },
        {
            "title": "8. How does year built influence listing price?",
            "sql": """
                SELECT
                    CASE
                        WHEN p.yearbuilt BETWEEN 1990 AND 1995 THEN 'Between 1990 and 1995'
                        WHEN p.yearbuilt BETWEEN 1996 AND 2000 THEN 'Between 1996 and 2000'
                        WHEN p.yearbuilt BETWEEN 2001 AND 2005 THEN 'Between 2001 and 2005'
                        WHEN p.yearbuilt BETWEEN 2006 AND 2010 THEN 'Between 2006 and 2010'
                        WHEN p.yearbuilt BETWEEN 2011 AND 2015 THEN 'Between 2011 and 2015'
                        WHEN p.yearbuilt BETWEEN 2016 AND 2020 THEN 'Between 2016 and 2020'
                        WHEN p.yearbuilt BETWEEN 2021 AND 2025 THEN 'Between 2021 and 2025'
                        ELSE 'Other'
                    END AS built_between,
                    COUNT(*) AS total_properties,
                    ROUND(AVG(l.price), 2) AS average_price
                FROM listings l
                JOIN property_attributes p ON l.listingid = p.listingid
                GROUP BY built_between
                ORDER BY average_price DESC;
            """,
        },
        {
            "title": "9. Which cities have the highest average property prices?",
            "sql": """
                SELECT city, COUNT(*) AS total_listings, ROUND(AVG(price), 2) AS average_price
                FROM listings
                GROUP BY city
                ORDER BY average_price DESC
                LIMIT 10;
            """,
        },
        {
            "title": "10.How are properties distributed across price buckets?",
            "sql": """
                SELECT
                CASE
                    WHEN price < 1000000 THEN 'Below 1M'
                    WHEN price < 2000000 THEN '1M - 2M'
                    WHEN price < 3000000 THEN '2M - 3M'
                    WHEN price < 4000000 THEN '3M - 4M'
                    ELSE 'Above 4M'
                END AS price_bucket,
                COUNT(*) AS total_properties
            FROM listings
            GROUP BY price_bucket
            ORDER BY MIN(price);
            """,
        },
    ],
    "Sales & Market Performance": [
        {
            "title": "11.What is the average days on market by city?",
            "sql": """
                SELECT l.city, ROUND(AVG(s.daysonmarket), 0) AS average_days_on_market
                FROM listings l
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY l.city
                ORDER BY average_days_on_market DESC;
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
            "title": "12.Which property types sell the fastest?",
            "sql": """
                SELECT l.propertytype, ROUND(AVG(s.daysonmarket), 0) AS average_days_on_market
                FROM listings l
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY l.propertytype
                ORDER BY average_days_on_market ASC;
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
