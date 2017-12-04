import aiomysql


class DB:
    def __init__(self, host, username, password, db, loop):
        self.host = host
        self.username = username
        self.password = password
        self.db = db
        self.loop = loop
        loop.run_until_complete(self.connect())

    async def connect(self):
        try:
            self.pool = await aiomysql.create_pool(host=self.host, port=3306,
                                                   user=self.username, password=self.password,
                                                   db=self.db, loop=self.loop)
        except Exception as e:
            print("Couldn't connect to database.")
            print(e)

    async def execute(self, qry, assoc=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor if assoc else None) as cur:
                r = await cur.execute(qry)
                return r, cur.lastrowid

    async def fetch(self, qry, assoc=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor if assoc else None) as cur:
                await cur.execute(qry)
                r = await cur.fetchall()
                return r

    async def fetchone(self, qry, assoc=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor if assoc else None) as cur:
                await cur.execute(qry)
                r = await cur.fetchone()
                return r

    async def fetchdict(self, qry):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(qry)
                return await cur.fetchone()

    async def fetchdicts(self, qry):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(qry)
                return await cur.fetchall()

