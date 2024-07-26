def DownloadForStationForm(**kwargs):
    return f"""SELECT 
                    *
                FROM 
                    audit._sales__execution_orders
                WHERE 
                    `Ст. Отправления` = '{kwargs["station_name"]}' AND 
                    `SVOD.Дата отправки` BETWEEN '{kwargs["start_date"]}' AND '{kwargs["finish_date"]}'"""

def DownloadForRailwayForm(**kwargs):
    return f"""SELECT 
    *
FROM 
    audit._sales__execution_orders
WHERE 
    `Дор. Отправления` = '{kwargs["railway_name"]}' AND 
    `SVOD.Дата отправки` BETWEEN '{kwargs["start_date"]}' AND '{kwargs["finish_date"]}'"""