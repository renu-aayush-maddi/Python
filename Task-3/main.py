import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row

def execute(sql):
    print("SQL:",sql)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return cur

class Field:
    def __init__(self, name=None):
        self.name = name

    def set_name(self, name):
        self.name = name


class CharField(Field):
    def __init__(self, max_length):
        super().__init__()
        self.max_length = max_length

    def sql(self):
        return f"{self.name} VARCHAR({self.max_length}) NOT NULL"


class IntegerField(Field):
    def __init__(self, nullable=False):
        super().__init__()
        self.nullable = nullable

    def sql(self):
        return f"{self.name} INTEGER" +("" if self.nullable else "NOT NULL")


class ForeignKey(Field):
    def __init__(self,to):
        super().__init__()
        self.to = to

    def set_name(self,name):
        self.name = name
        self.col = f"{name}_id"

    def sql(self):
        return f"{self.col} INTEGER NOT NULL"

class Query:
    def __init__(self,model):
        self.model = model
        self.where = []
        self.order = ""

    def filter(self, **kw):
        for k, v in kw.items():
            if "_gte" in k:
                f = k.split("_")[0]
                self.where.append(f"{f} >= {v}")
            else:
                if isinstance(v, str):
                    v = f"'{v}'"
                self.where.append(f"{k} = {v}")
        return self

    def order_by(self, f):
        if f.startswith("-"):
            self.order = f"ORDER BY {f[1:]} DESC"
        else:
            self.order = f"ORDER BY {f}"
        return self

    def all(self):
        sql = f"SELECT * FROM {self.model.table}"
        if self.where:
            sql += " WHERE " + " AND ".join(self.where)
        if self.order:
            sql += " " + self.order

        rows = execute(sql).fetchall()
        return [self.model(**dict(r)) for r in rows]

class Model:
    def __init_subclass__(cls):
        cls.table = cls.__name__.lower()
        cls.fields = {}

        for k, v in cls.__dict__.items():
            if isinstance(v, Field):
                v.set_name(k)
                cls.fields[k] = v

    def __init__(self, **kw):
        self.id = kw.get("id")
        self.data = {}

        for k, v in kw.items():
            self.data[k] = v

    @classmethod
    def create_table(cls):
        cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]

        for f in cls.fields.values():
            cols.append(f.sql())

        sql = f"CREATE TABLE IF NOT EXISTS {cls.table} ({', '.join(cols)})"
        execute(sql)

    def save(self):
        keys = []
        vals = []

        for name, f in self.fields.items():
            col = getattr(f, "col", name)
            keys.append(col)

            if isinstance(f, ForeignKey):
                val = self.data.get(name)
                vals.append(str(val.id if hasattr(val, "id") else val))
            else:
                val = self.data.get(name)
                if isinstance(val, str):
                    val = f"'{val}'"
                vals.append(str(val))

        sql = f"INSERT INTO {self.table} ({', '.join(keys)}) VALUES ({', '.join(vals)})"
        cur = execute(sql)
        self.id = cur.lastrowid

    @classmethod
    def filter(cls, **kw):
        return Query(cls).filter(**kw)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data})"


if __name__ == "__main__":
    
    class User(Model):
        name = CharField(100)
        email = CharField(255)
        age = IntegerField(nullable=True)

    User.create_table()
    
    u = User(name="Alice", email="alice@mail.com", age=25)
    u.save()
    
    print(User.filter(age_gte=20).order_by("-name").all())