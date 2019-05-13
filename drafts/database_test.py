from sqlalchemy import Column, Integer, String, Sequence, Index
from sqlalchemy import func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, remote, foreign
from sqlalchemy_utils import LtreeType, Ltree


Base = declarative_base()

engine = create_engine('postgresql://USER:PASSWORD@localhost/MYDATABASE')

id_seq = Sequence('nodes_id_seq')


class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, id_seq, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(LtreeType, nullable=False)

    parent = relationship(
                'Node',
                primaryjoin=(remote(path) == foreign(func.subpath(path, 0, -1))),
                backref='children',
                viewonly=True
            )

    def __init__(self, name, parent=None):
        _id = engine.execute(id_seq)
        self.id = _id
        self.name = name
        ltree_id = Ltree(str(_id))
        self.path = ltree_id if parent is None else parent.path + ltree_id

    __table_args__ = (
        Index('ix_nodes_path', path, postgresql_using='gist'),
    )
   def __str__(self):
        return self.name

    def __repr__(self):
        return 'Node({})'.format(self.name)


Base.metadata.create_all(engine)
