import os

token = os.getenv('RUB_TOKEN')

prefix = ['!!', '``']

cogs = os.getenv('RUB_COGS', 'cogs.admin').split()

db_host = os.getenv('MYSQL_HOST', '127.0.0.1')
db_user = os.getenv('MYSQL_USER', 'root')
db_pass = os.getenv('MYSQL_PASSWORD', '')
db_name = os.getenv('MYSQL_DATABASE', 'rub')
