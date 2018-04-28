import aiomysql


class DB:
    def __init__(self, host, username, password, db, loop):
        self.host = host
        self.username = username
        self.password = password
        self.db = db
        self.loop = loop

        self.pool = None
        loop.run_until_complete(self.connect())

    async def connect(self):
        try:
            self.pool = await aiomysql.create_pool(host=self.host, user=self.username, password=self.password,
                                                   db=self.db, loop=self.loop, charset='utf8', use_unicode=True)
        except Exception as e:
            print("Couldn't connect to database.")
            print(e)

    async def execute(self, qry, args=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                r = await cur.execute(qry, args=args)
                return r, cur.lastrowid

    async def fetch(self, qry, args=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(qry, args=args)
                r = await cur.fetchall()
                return r

    async def fetchone(self, qry, args=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(qry, args=args)
                r = await cur.fetchone()
                return r

    async def fetchdict(self, qry, args=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(qry, args=args)
                return await cur.fetchone()

    async def fetchdicts(self, qry, args=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(qry, args=args)
                return await cur.fetchall()

