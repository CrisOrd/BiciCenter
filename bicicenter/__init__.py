import pymysql
try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	pass

pymysql.install_as_MySQLdb()