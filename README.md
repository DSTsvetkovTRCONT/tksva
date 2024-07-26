# Веб-интерфес (tksva) информационного ресурса службы внутреннего аудита (ИРСВА)

### Назначение ИРСВА
ИРСВА предназначен для организации системы непрерывного аудита.
На данном этапе развития ИРСВА предназначен для автоматизации контроля актирования выручки.
Ресурс по запросу пользователя предоставляет информацию о заказах в которых с большой вероятностью не учтена выручка по той или иной услуге.

### Доступ к ИРСВА
Пользователи ИРСВА - сотрудники ПАО Трансконтейнер отвечающие за учет выручки по той или иной услуге.
Пользовательский доступ к ресурсу осуществляется через веб-браузер через указание в адресной строке IP сервера, на котором развернута система.
Доступ возможен только с рабочих станций зарегистрированных в домене Трансконтейнера.  
Планируется регистрация субдомена sva.trcont.com для организации более удобного доступа.

### Состав ИРСВА
ИРСВА состоит из трех работающих параллельно систем:
- Инспектор (tksva_p). Система автоматически обновляет источники данных для поддержания их актаульности.
- Очередь Заданий (tksva_q). Система принимает от пользователей задания на выгрузку данных необходимых им для анализа, запускает скрипты формирующие выгрузки и по мере формирования выгрузок предоставляет доступ к ним.
- Веб-интерфейс (tksva). Система позволяет отправлять в Очередь Заданий задачи пользователей на подготовку и выгрузку данных и по по мере формирования выгрузок, скачивать их на локальную машину пользователя.

Системы работают на сервере под управлением ОС Linux, обмен информацией между системами осуществляется с помощью БД Postgresql.
Код и инструкции по развёртыванию каждой системы хранятся в отдельном репозитории.

Данный репозиторий относится к Веб-интерфейсу (tksva).
Репозитарии Инспектора (tksva_p) и Очереди Заданий (tksva_q) доступны по ссылкам:
- [Очередь Заданий (tksva_p)](https://github.com/DSTsvetkovTRCONT/tksva_q)
- [Инспектор (tksva_p)](https://github.com/DSTsvetkovTRCONT/tksva_p)

#### Использованные технологии
Python3.10, Flask, Gunicorn, Nginx

#### Описание алгоритма
На данном этапе развития проекта Веб-интерфейс ИРСВА обеспечивает доступ к двум видам выгрузок:
- выгрузка из таблицы DWH ***audit._sales__execution_orders*** с отбором по начальной и конечной дате и станции отправления (формируется на основании параметров переданных через форму **DownloadForStationForm** Веб-интерфейса tksva).
- выгрузка из таблицы DWH ***audit._sales__execution_orders*** с отбором по начальной и конечной дате и дороге отправления (формируется на основании параметров переданных через форму **DownloadForRailwayForm** Веб-интерфейса tksva).

Пользователь имеет доступ только к тем выгрузкам, задание на создание которых сам отправил в систему через Веб-интерфейс. Для этого пользователь должен зарегистрироваться в системе и в дальнейшем заходить в систему под своими логином и паралём. В дальнейшем планируется добавление функционала переиодической смены пользователем своего пароля, для соответствия корпоративным тербованиям к информационной безопасности.  
id, имя пользователя, адрес электронной почты пользователя, и хэш-пароля хранятся в таблице ***user*** БД Postgresql.

Задачи пользователя могут иметь статусы из списка (хранятся в поле **task_status** таблицы ***post*** БД Postgres):
- **"в очереди"** - задачи загруженные в очередь
- **"загружено n из m"** - подготавливаемая в настоящи момент Очередью Заданий задача. Подготовлено n строк. Всего должно быть получено m строк.
- **"готов к загрузке"** - выполненая задача. Файл готов к загрузке на локальную машину пользователя (хранится в папке /app/static/files_to_download/<user_id>/)
- **"файл загружен"** - пользователь загрузил файл на локальную машину, файл удален на сервере.
- **"скрыта пользователем"** - для задач для которых файл загружен пользователем, после нажатия пользователем кнопки "Очистить информацию о загруженных"
- **"скрыта менеджером очереди"** - для задач не скрытых пользователем в течение 72 часов после загрузки, а так же для задач подготовленных к выгрузке, при условии, что файл не был загружен пользователем. Перед установкой этого статуса удаляются соответствующие файлы на сервере, если не были ранее удалены после скачивания.

Так же, для анализа полезности, того или иного функционала ИРСВА в таблице ***post*** для каждой задачи сохраняется информация о форме, через которую задание было загружено в очередь (поле ***form_name***), параметры, переданные через форму (поле ***conditions***), имя файла в который Очередь Заданий выгружает результат выполнения скрипта-обработкичк (***file_to_download***),дата и время постановки задачи в очередь (***time_stamp***) и дата и время установки текущего статуса задачи (***task_status_time_stamp***).

Для того чтобы пользователь мог иметь представление о загрузке ИРСВА и мог примерно прогнозировать время готовности к выгрузке его задач, Веб-интерфейс отображает количество  количество задач пользователя в очереди и количество задач в очереди для всех пользовтелей.

#### Инструкция по развертыванию
На производственном сервере с работающим веб-сервером Nginx в домашней директории ползователя создаём директорию ***tksva*** в которую копируем все файлы репозитория.
В директории ***~/tksva*** создаём файл ***.env*** по образцу файла ***.envexample***.
Системы ИРСВА Веб-интерфейс (tksva) и Очередь Заданий (tksva_q) должны быть установлены на одном и том же сервере, в домашней директории одного и того же пользователя.

Обновляем пакеты:
```bash
sudo apt update
sudo apt -y upgrade
```
Устанавливаем пакет venv (если не был установлен ранее):
```bash
sudo apt install python3-venv
```
В директории tksva создаём и активируем виртуальное окружение:
```bash
cd ~/tksva
python3 -m venv .venv
source .venv/bin/activate
```
Из файла requirements.txt устанавливаем зависимости:
```bash
pip install -r requirements.txt
```
Выключаем виртуальное окружение:
```bash
deactivate
```
Создаём сервис Linux:
```bash
sudo nano /etc/systemd/system/tksva.service
```
```
[Unit]
Description=Gunicorn instance to serve tksva
After=network.target
[Service]
User=<username>
Group=www-data
WorkingDirectory=/home/<username>/tksva
Environment="PATH=/home/<username>/tksva/.venv/bin"
ExecStart=/home/<username>/tksva/.venv/bin/gunicorn --workers 3 --bind un>
[Install]
WantedBy=multi-user.target
```
Запускаем сервис, настраиваем его автозапуск:
```bash
sudo systemctl start tksva
sudo systemctl enable tksva
```
Настраиваем Nginx:
```bash
sudo nano /etc/nginx/sites-available/tksva
```
```
server {
    listen 80;
    server_name <IP>;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/<username>/tksva/tksva.sock;
    }
}
```
Применяем созданную конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
```
Добавляем пользователя www-data в группу текущего пользователя:
```bash
sudo usermod -a -G ${USER} www-data
```
Перезапускаем Nginx:
```
sudo nginx -s reload
```
Настраиваем брандмауэр:
```
sudo ufw delete allow 5000
sudo ufw allow 'Nginx Full'
```