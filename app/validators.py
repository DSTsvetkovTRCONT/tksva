from wtforms.validators import  ValidationError
from dwh import rows_in_download_for_railway, rows_in_download_for_station
from psql import get_dwh_table_info
from datetime import datetime


class DateIsEqualOrLaterStartDate():
    def __call__(self, form, field):    
        if str(type(form.start_date.data)) != "<class 'datetime.date'>":
            raise ValidationError(f'Невозможно проверить, чтобы начальная дата была меньше или равна конечной, т.к. так как начальная дата не явялется датой ({str(type(form.start_date.data))})!') 
        if field.data < form.start_date.data:
            raise ValidationError('Выберите конечную дату равную или более позднюю, чем начальная!')

              
class DownloadForRailway1048575():
    def __call__(self, form, field):
        if str(type(form.start_date.data)) != "<class 'datetime.date'>":
            raise ValidationError(f'Невозможно проверить, чтобы начальная дата была меньше или равна конечной, т.к. так как начальная дата не явялется датой ({str(type(form.start_date.data))})!') 

        if form.start_date.data > form.finish_date.data:
            raise ValidationError(f'Невозможна проверка на размер выгрузки так как конечная дата меньше начальной {form.start_date.data} > {form.finish_date.data}!') 
        
        try:
            self.result = rows_in_download_for_railway(form.railway_name.data, form.start_date.data, form.finish_date.data)
        except Exception as e:
            raise ValidationError(f'Невозможна проверка на размер выгрузки (ошибка DWH) {e}!')  
                   
        if self.result > 1048575:
            raise ValidationError(f'При заданных условиях выгрузка будет содержать {self.result} строк. Столько не может быть выгружено в Эксель!')        

class DownloadForStation1048575():
    def __call__(self, form, field):
        if str(type(form.start_date.data)) != "<class 'datetime.date'>":
            raise ValidationError(f'Невозможно проверить, чтобы начальная дата была меньше или равна конечной, т.к. так как начальная дата не явялется датой ({str(type(form.start_date.data))})!') 


        if form.start_date.data > form.finish_date.data:
            raise ValidationError(f'Невозможна проверка на размер выгрузки так как конечная дата меньше начальной {form.start_date.data} > {form.finish_date.data}!') 
        
        try:
            self.result = rows_in_download_for_station(form.station_name.data, form.start_date.data, form.finish_date.data)
        except Exception as e:
            raise ValidationError(f'Невозможна проверка на размер выгрузки (ошибка DWH) {e}!')  
        
        if self.result > 1048575:
            raise ValidationError(f'При заданных условиях выгрузка будет содержать {self.result} строк. Столько не может быть выгружено в Эксель!')        


class DateInRange():
    def __call__(self, form, field):
        table_info_dict = get_dwh_table_info()
        # railways_list = table_info_dict['railway_names'].split('|')
        # vstations_list = table_info_dict['station_names'].split('|')
        min_date_in_dwh_table = datetime.strptime(table_info_dict['min_date'], "%Y-%m-%d %H:%M:%S")
        max_date_in_dwh_table = datetime.strptime(table_info_dict['max_date'], "%Y-%m-%d %H:%M:%S")
        

        if min_date_in_dwh_table.date() > field.data:
            raise ValidationError(f'Минимальная дата в DWH {min_date_in_dwh_table}. Задайте дату больше или равную ей!')  
        if max_date_in_dwh_table.date() < field.data:
            raise ValidationError(f'Максимальная дата в DWH {max_date_in_dwh_table}. Задайте дату меньше или равную ей!')   
