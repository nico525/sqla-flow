import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker
from sqla_flow.model import FlowBase, Workflow, State, Transition, WorkflowMeta, Function, Hook
from sqla_flow.mixins import FlowMixin
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(FlowMixin, Base):
    __tablename__ = "user"

    name = sa.Column(sa.String, primary_key=True)


engine = sa.create_engine('sqlite:///workflow.sqlite', echo=True)

FlowBase.metadata.drop_all(engine)
FlowBase.metadata.create_all(engine)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(bind=engine))
FlowBase.query = session.query_property()

#################### setup some data ######################
backlog = State(label="Backlog")
in_progress = State(label="In Progress")
done = State(label="Done")
closed = State(label="Closed")
cancelled = State(label="Cancelled")
wflow = Workflow(label="Hello World", initial_state=backlog)
cancel1 = Transition(label="Cancel", source_state=backlog, destination_state=cancelled, workflow=wflow)
cancel2 = Transition(label="Cancel", source_state=in_progress, destination_state=cancelled, workflow=wflow)
cancel3 = Transition(label="Cancel", source_state=done, destination_state=cancelled, workflow=wflow)
start = Transition(label="Start Development", source_state=backlog, destination_state=in_progress, workflow=wflow)
finish = Transition(label="Finish Development", source_state=in_progress, destination_state=done, workflow=wflow)
deploy = Transition(label="Deploy", source_state=done, destination_state=closed, workflow=wflow)
wf_meta = WorkflowMeta(workflow=wflow, class_name="user")
fn = Function(label="Print Datetime",
              body="""from datetime import datetime
def handle(hook, *args, **kwargs):
    print(f"{hook.when} - {datetime.now()} - {hook.transition.slug} - 1")
    #raise Exception('Missing Permission')""")
fn2 = Function(label="Print Test",
              body="""from datetime import datetime
def handle(hook, *args, **kwargs):
    print(f"{hook.when} - {datetime.now()} - {hook.transition.slug} - 2")""")
pre_hook = Hook(label="PRE Hook 1", order_no=1, when=Hook.When.PRE, function=fn, transition=cancel1)
pre_hook2 = Hook(label="PRE Hook 2", order_no=2, when=Hook.When.PRE, function=fn2, transition=cancel1)

session.add_all([backlog, in_progress, done, closed, cancelled, cancel1, cancel2, cancel3, start, finish, deploy,
                 wf_meta, fn, pre_hook, fn2, pre_hook2])

session.commit()

u = User(name="TestUser")
u.transition(transition=cancel1)

session.commit()
