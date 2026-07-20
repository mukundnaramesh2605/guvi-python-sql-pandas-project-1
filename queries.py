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
            "title": "13.What percentage of properties are sold above listing price?",
            "sql": """
                SELECT ROUND(
                SUM(CASE WHEN s.saleprice > l.price THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                2
            ) AS percentage_sold_above_listing
            FROM listings l
            JOIN sales s ON l.listingid = s.listingid;
            """,
        },
        {
            "title": "14.What is the sale-to-list price ratio by city?",
            "sql": """
                SELECT l.city, ROUND(AVG(s.saleprice / l.price), 4) AS sale_to_list_ratio
                FROM listings l
                JOIN sales s ON s.listingid = l.listingid
                GROUP BY l.city
                ORDER BY sale_to_list_ratio DESC;
            """,
        },
        {
            "title": "15.Which listings took more than 90 days to sell?",
            "sql": """
                SELECT listingid, daysonmarket
                FROM sales
                WHERE daysonmarket > 90
                ORDER BY daysonmarket DESC;
            """,
        },
        {
            "title": "16.How does metro distance affect time on market?",
            "sql": """
                SELECT
                    CASE
                        WHEN p.metrodistancekm <= 1 THEN 'Within 1 km'
                        WHEN p.metrodistancekm <= 3 THEN '1 - 3 km'
                        WHEN p.metrodistancekm <= 5 THEN '3 - 5 km'
                        ELSE 'More than 5 km'
                    END AS metro_distance,
                    AVG(s.daysonmarket) AS average_days_on_market
                FROM property_attributes p
                JOIN sales s ON s.listingid = p.listingid
                GROUP BY metro_distance
                ORDER BY average_days_on_market DESC;
            """,
        },
        {
            "title": "17.What is the monthly sales trend?",
            "sql": """
                SELECT strftime('%Y-%m', datesold) AS month, COUNT(*) AS total_sales_per_month
                FROM sales
                GROUP BY month
                ORDER BY month ASC;
            """,
        },
        {
            "title": "18.Which properties are currently unsold?",
            "sql": """
                SELECT city, COUNT(*) AS total_unsold_properties
                FROM listings l
                WHERE NOT EXISTS (SELECT 1 FROM sales s WHERE s.listingid = l.listingid)
                GROUP BY city
                ORDER BY total_unsold_properties DESC;
            """,
        },
    ],
    "Agent Performance": [
        {
            "title": "19.Which agents have closed the most sales?",
            "sql": """
                SELECT a.agentid, a.name, COUNT(s.listingid) AS closed_sales
                FROM listings l
                JOIN sales s ON s.listingid = l.listingid
                JOIN agents a ON a.agentid = l.agentid
                GROUP BY a.agentid, a.name
                ORDER BY closed_sales DESC;
            """,
        },
        {
            "title": "20.Who are the top agents by total sales revenue?",
            "sql": """
                SELECT
                a.agentid,
                a.name,
                COUNT(s.listingid) AS no_of_listings_sold,
                SUM(s.saleprice) AS total_sales_revenue,
                ROUND(AVG(s.saleprice), 2) AS average_sales_revenue
            FROM listings l
            JOIN sales s ON s.listingid = l.listingid
            JOIN agents a ON a.agentid = l.agentid
            GROUP BY a.agentid, a.name
            ORDER BY total_sales_revenue DESC;
            """,
        },
        {
            "title": "21.Which agents close deals fastest?",
            "sql": """
                SELECT a.agentid, a.name, COUNT(*) AS total_deals_closed, ROUND(AVG(s.daysonmarket), 0) AS days_taken_to_close_deal
                    FROM listings l
                    JOIN sales s ON s.listingid = l.listingid
                    JOIN agents a ON a.agentid = l.agentid
                    GROUP BY a.agentid, a.name
                    ORDER BY days_taken_to_close_deal ASC, total_deals_closed DESC
                    LIMIT 10;
            """,
        },
        {
            "title": "22.Does experience correlate with deals closed?",
            "sql": """
                SELECT
                    CASE
                        WHEN experienceyears <= 5  THEN '0-5 yrs'
                        WHEN experienceyears <= 10 THEN '6-10 yrs'
                        WHEN experienceyears <= 15 THEN '11-15 yrs'
                        WHEN experienceyears <= 20 THEN '16-20 yrs'
                        ELSE '21+ yrs'
                    END AS experience_band,
                    COUNT(*) AS num_agents,
                    ROUND(AVG(dealsclosed),0) AS avg_deals
                    FROM agents
                    GROUP BY experience_band
                    ORDER BY MIN(experienceyears);
            """,
        },
        {
            "title": "23.Do agents with higher ratings close deals faster?",
            "sql": """
                SELECT a.agentid, a.name, rating, ROUND(AVG(s.daysonmarket), 0) AS days_taken_to_close_deal
                FROM listings l
                JOIN sales s ON s.listingid = l.listingid
                JOIN agents a ON a.agentid = l.agentid
                GROUP BY a.agentid, a.name , rating
                ORDER BY rating ASC, days_taken_to_close_deal ASC;
            """,
        },
        {
            "title": "24.What is the average commission earned by each agent?",
            "sql": """
                SELECT a.agentid, a.name, ROUND(AVG(s.saleprice * (a.commissionrate / 100)), 2) AS avg_commission_per_sale
                    FROM listings l
                    JOIN sales s ON s.listingid = l.listingid
                    JOIN agents a ON a.agentid = l.agentid
                    GROUP BY a.agentid, a.name
                    ORDER BY avg_commission_per_sale DESC;
            """,
        },
        {
            "title": "25.Which agents currently have the most active listings?",
            "sql": """
                SELECT a.agentid, a.name, COUNT(l.listingid) AS active_listings
                    FROM listings l
                    JOIN agents a ON a.agentid = l.agentid
                    WHERE NOT EXISTS (SELECT 1 FROM sales s WHERE l.listingid = s.listingid)
                    GROUP BY a.agentid, a.name
                    ORDER BY active_listings DESC;
            """,
        },
    ],
    "Buyer & Financing Behavior": [
        {
            "title": "26.What percentage of buyers are investors vs end users?",
            "sql": """
                SELECT buyertype,
                    COUNT(*) AS num_buyers,
                    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM buyers), 2) AS percentage
                FROM buyers
                GROUP BY buyertype;
            """,
        },
        {
            "title": "27.Which cities have the highest loan uptake rate?",
            "sql": """
                SELECT l.city, SUM(b.loantaken) AS no_of_loans_taken, ROUND(100.0 * SUM(b.loantaken) / COUNT(*), 2) AS loan_uptake_rate
                    FROM buyers b
                    JOIN listings l ON l.listingid = b.saleid
                    GROUP BY l.city
                    ORDER BY loan_uptake_rate DESC;
            """,
        },
        {
            "title": "28.What is the average loan amount by buyer type?",
            "sql": """
                SELECT buyertype, ROUND(AVG(loanamount), 2) AS averageloanamount
                    FROM buyers
                    WHERE loanamount > 0
                    GROUP BY buyertype;
            """,
        },
        {
            "title": "29.Which payment mode is most commonly used?",
            "sql": """
                SELECT paymentmode, COUNT(*) AS num_buyers
                    FROM buyers
                    GROUP BY paymentmode
                    ORDER BY num_buyers DESC;
            """,
        },
        {
            "title": "30.Do loan-backed purchases take longer to close?",
            "sql": """
                SELECT
                    CASE
                        WHEN b.loantaken = 1 THEN 'Loan Taken'
                        ELSE 'No Loan'
                    END AS loan_status,
                    ROUND(AVG(s.daysonmarket), 2) AS average_days_on_market
                FROM buyers b
                JOIN sales s ON b.saleid = s.listingid
                GROUP BY loan_status
                ORDER BY average_days_on_market DESC;
            """,
        },
    ],
}
