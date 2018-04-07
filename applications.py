from sqlalchemy import create_engine, Column, Integer, String, Sequence, Table, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, aliased
import os

#engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:///test.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# 'application' is the application we are interested in
# 'dependency' is another application on which our application is dependent
dependencies_table = Table('dependencies_table', Base.metadata,
                          Column('application', Integer, ForeignKey('application.id')),
                          Column('dependency', Integer, ForeignKey('application.id'))
                          )

class Application(Base):
    __tablename__ = 'application'
    id = Column(Integer, Sequence('application_id_seq'), primary_key=True)
    app_name = Column(String(255))
    dependencies = relationship("Application",
                            secondary=dependencies_table,
                            primaryjoin=(dependencies_table.c.application == id),
                            secondaryjoin=(dependencies_table.c.dependency == id),
                            backref=backref('dependencies_table', lazy='joined'),lazy='joined')



    def __repr__(self):
        return(f"Application<id='{self.id}', "
               f"app_name='{self.app_name}'")

    def add_dependency(self, application):
        print(f'Adding dependency for {self.app_name} on {application}')
        self.dependencies.append(application)

    # SELECT application.app_name
    # FROM application, dependency_table
    # WHERE dependency_table.application = ?
    # AND dependency_table.dependency = application.id
    def list_dependencies(self, app):
        print(f'application == {self.app_name}')
        Dependency = aliased(Application, name='dependency')

        # this at least doesn't error, but also doesn't work
        # deps = session.query(Application.app_name) \
        #     .filter(Application.dependencies.any(id=app.id))

        s = text(
            "SELECT application.app_name "
            "FROM application, dependencies_table "
            "WHERE dependencies_table.application = :id "
            "AND dependencies_table.dependency = application.id "
        )
        deps = engine.connect().execute(s, id=app.id)

        # deps = session.query(Dependency, Application)\
        #     .outerjoin(
        #     (and_(Dependency, dependencies_table.c.application==self.id,
        #           Application, dependencies_table.c.dependency==Application.id)
        #      )
        # )

        dep_list = [dep[0] for dep in deps]
        return dep_list



if not os.path.exists('test.db'):
    Base.metadata.create_all(engine)

    applications = ['AECore', 'CSMS', 'CSAT', 'CSAS', 'AERuntime']
    for a in applications:
        session.add(Application(app_name=a))
    session.commit()

    for app in session.query(Application):
        print (app.id, app.app_name)
        for dependent_app in session.query(Application):
            if app.id != dependent_app.id:
                app.add_dependency(dependent_app)
    session.commit()

print('Reflecting on metadata)')
print (Base.metadata.reflect(engine))
print (Base.metadata)

for dep in session.query(dependencies_table):
    print(dep.application, dep.dependency)


for application in session.query(Application):
    print(f'{application.app_name} is dependent on:')
    #for name, in session_query()
    deps = application.list_dependencies(application)
    print(deps)
