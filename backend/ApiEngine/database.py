import pymysql.cursors
import oracledb
import pymssql


class Base:
    cursor = None
    conn = None

    def execute(self, sql, args=None):
        """执行单条sql语句"""
        try:
            self.cursor.execute(sql, args)
            return self.cursor.fetchone()
        except Exception as e:
            raise f"单条数据查询错误！错误为：{e}"

    def execute_all(self, sql, args=None):
        """执行全部sql语句"""
        try:
            self.cursor.execute(sql, args)
            return self.cursor.fetchall()
        except Exception as e:
            raise f"多条数据查询错误！错误为：{e}"

    def __del__(self):
        """断开连接"""
        self.cursor.close()
        self.conn.close()


class DBMysql(Base):
    """mysql数据库"""

    def __init__(self, config):
        """初始化数据库连接"""
        self.conn = pymysql.connect(**config, autocommit=True, charset="utf8")
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)


class DBSqlserver(Base):
    """sqlserver数据库"""

    def __init__(self, config):
        """初始化数据库连接"""
        self.conn = pymssql.connect(**config, autocommit=True, charset="utf8")
        self.cursor = self.conn.cursor()


class DBOracle(Base):
    """oracle数据库"""

    def __init__(self, config):
        """初始化数据库连接"""
        self.conn = oracledb.connect(**config, autocommit=True, charset="utf8")
        self.cursor = self.conn.cursor()


class DBClient:
    """数据库连接工具"""

    def init_connect(self, db):
        """初始化数据库连接工具"""
        if isinstance(db, dict):
            self.create_db_connect(db)
        else:
            for config in db:
                self.create_db_connect(config)

    def create_db_connect(self, config):
        """创建数据库连接"""
        if not config:
            raise TypeError("数据库配置格式有误！")

        if not config.get('name'):
            raise ValueError('数据库配置的name字段不能为空！')

        if config.get('type').lower() == 'mysql' and config.get('config'):
            dbc = DBMysql(config.get('config'))

        elif config.get('type').lower() == 'sqlserver' and config.get('config'):
            dbc = DBSqlserver(config.get('config'))

        elif config.get('type').lower() == 'oracle' and config.get('config'):
            dbc = DBOracle(config.get('config'))

        else:
            raise ValueError('您传入的数据库配置有误：{}'.format(config))
        setattr(self, config.get('name'), dbc)

    def close_connect(self):
        """断开连接"""
        for db in list(self.__dict__.keys()):
            delattr(self, db)
