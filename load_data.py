from contextlib import closing
from vertica_python import connect
import pandas as pd
from config import ConnectToVerticaDB as Con_vert

def TotalFraudTable(date_from,date_to,city_id,week,year):
    _date_from = date_from
    _date_to = date_to
    _city_id = city_id
    _week = week
    _year = year
    with closing(connect(host = Con_vert.host,
                         port= Con_vert.port,
                         user= Con_vert.user,
                         password= Con_vert.password,
                         data_base= Con_vert.data_base,
                         read_timeout= Con_vert.read_timeout)
                         ) as con:


        sql=("""
            WITH args AS (
            SELECT
                CAST(%s AS INTEGER) date_from
                , CAST(%s AS INTEGER) date_to
                , CAST(%s AS INTEGER) city_id)
            SELECT
                driver_ext_id AS "Длинный позывной"
                , tp.driver_id AS "Короткий позывной"
                , successful_order_counter AS "Успешных поездок"
                , fraud_orders AS "Поездок отобрано на фрод"
                , verified_orders AS "Проверено поездок"
                , ISNULL(fraud.fraud, '0') AS "Подтверждённых фрод поездок"
                , successful_order_counter - ISNULL(fraud.fraud, '0') AS "Успешных за вычетом фродовых"
                , bonus / 100 AS "Получен бонус план"
            FROM
                (SELECT
                    temp.driver_id
                    , driver_ext_id
                    , successful_order_counter
                    , ISNULL(verified.verified, '0') verified_orders
                    , ISNULL(fraud.fraud, '0') fraud_orders
                    , bonus
                FROM 
                    (SELECT 
                        ROW_NUMBER() OVER(PARTITION BY driver_ext_id ORDER BY update_ts DESC) rnk
                        ,*
                    FROM facts.FS_Drivers_period_counter_history main
                    LEFT JOIN args ON TRUE
                    WHERE "week" = %s AND "year" = %s AND launch_region_id = city_id AND successful_order_counter >= 130
                    ) temp
                LEFT JOIN
                    (SELECT driver_id, SUM(fraud) AS fraud
                    FROM 
                        (SELECT CAST(driver_id AS DECIMAL(20,0)) driver_id, COUNT(driver_id) AS fraud
                        FROM facts.FS_Fraud_orders
                        LEFT JOIN args ON TRUE
                        WHERE "date" BETWEEN date_from AND date_to AND launch_region_id = city_id
                        GROUP BY driver_id
                        ) fraud
                    GROUP BY fraud.driver_id
                    ) fraud
                    ON temp.driver_id = fraud.driver_id
                LEFT JOIN
                    (SELECT CAST(driver_id AS DECIMAL(20,0)) driver_id, COUNT(driver_id) AS verified
                    FROM facts.FS_Fraud_orders
                    LEFT JOIN args ON TRUE
                    WHERE "date" BETWEEN date_from AND date_to AND launch_region_id = city_id AND state = 'VERIFIED'
                    GROUP BY driver_id
                    ) verified
                    ON temp.driver_id = verified.driver_id
                WHERE rnk = 1) tp
            LEFT JOIN 
                (SELECT
                    COUNT(DISTINCT o.id) AS fraud
                    , o.driver_id
                FROM facts.FS_Orders o
                LEFT JOIN facts.FS_Fraud_orders fo
                    ON o.id = fo.id
                LEFT JOIN facts.FS_Fraud_verifies fv
                    ON fo.id = fv.order_id
                LEFT JOIN 
                    (SELECT
                        id
                        , order_pattern_id
                        , session_id
                        , resolution
                        , ROW_NUMBER() OVER(PARTITION BY order_pattern_id ORDER BY id DESC) AS rnk
                    FROM facts.FS_Fraud_resolutions
                    GROUP BY order_pattern_id, resolution, id, session_id
                    ) fr
                    ON fv.id = fr.session_id AND rnk = 1
                LEFT JOIN args ON TRUE
                WHERE
                    fo.launch_region_id = city_id
                    AND fo."date" BETWEEN date_from AND date_to
                    AND resolution = 'YES'
                GROUP BY o.driver_id
                ORDER BY o.driver_id DESC
                ) fraud
                ON tp.driver_id = fraud.driver_id
             """)

        df = pd.read_sql_query(sql, con, params=[_date_from,_date_to,_city_id,_week,_year])
        df.loc[df['Успешных за вычетом фродовых'] >= 180, 'К списанию'] = 0
        df.loc[df['Успешных за вычетом фродовых'] < 180, 'К списанию'] = df['Получен бонус план'] - 600
        df.loc[df['Успешных за вычетом фродовых'] < 160, 'К списанию'] = df['Получен бонус план'] - 400
        df.loc[df['Успешных за вычетом фродовых'] < 130, 'К списанию'] = df['Получен бонус план']
        df = df.drop_duplicates(subset=['Длинный позывной', 'Короткий позывной'], keep='first')
        return df

def FraudDetalizationTable(date_from, date_to, city_id, drv_ids):
    _date_from = date_from
    _date_to = date_to
    _city_id = city_id
    _drv_ids = drv_ids
    with closing(connect(host = Con_vert.host,
                         port= Con_vert.port,
                         user= Con_vert.user,
                         password= Con_vert.password,
                         data_base= Con_vert.data_base,
                         read_timeout= Con_vert.read_timeout)
                         ) as con:
        sql=("""
    	    WITH args AS (
	    SELECT
               CAST(%s AS INTEGER) date_from
               , CAST(%s AS INTEGER) date_to
               , CAST(%s AS INTEGER) city_id)
	    SELECT
               DISTINCT o.id
               , o.driver_id
               , drv.ext_id
	    FROM facts.FS_Orders o
	    LEFT JOIN facts.FS_Fraud_orders fo
               ON o.id = fo.id
	    LEFT JOIN facts.FS_Fraud_verifies fv
               ON fo.id = fv.order_id
            LEFT JOIN (
               SELECT
                   id
                   , order_pattern_id
                   , session_id
                   , resolution
                   , ROW_NUMBER() OVER(PARTITION BY order_pattern_id ORDER BY id DESC) AS rnk
               FROM facts.FS_Fraud_resolutions
               GROUP BY order_pattern_id, resolution, id, session_id
                   ) fr
               ON fv.id = fr.session_id AND rnk = 1
	    LEFT JOIN args ON TRUE
	    LEFT JOIN facts.FS_Drivers drv
               ON o.driver_id = drv.id
	    WHERE
               fo.launch_region_id = city_id
               AND fo."date" BETWEEN date_from AND date_to
               AND resolution = 'YES'
               AND o.driver_id IN %s
	    ORDER BY o.driver_id DESC
            """)
        df = pd.read_sql_query(sql, con, params=[_date_from, _date_to, _city_id, _drv_ids])

        cols = df.columns.tolist()
        cols = cols[-1:] + cols[1:2] + cols[0:1]
        df = df[cols]
        return df
