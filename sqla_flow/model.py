import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqla_flow.utils import slugify
from enum import Enum
from sqlalchemy.ext.associationproxy import association_proxy

_Base = declarative_base()
_loaded_functions = {}


class FlowBase(_Base):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return f"flow_{cls.__name__.lower()}"


class _SlugMixin:
    label = sa.Column(sa.String)
    slug = sa.Column(sa.String, nullable=False, default=slugify("label"))
    description = sa.Column(sa.String)


class State(FlowBase, _SlugMixin):
    id = sa.Column(sa.Integer, primary_key=True)

    next_transitions = sa.orm.relationship("Transition", back_populates="source_state", foreign_keys="Transition.source_state_id")
    workflow_initializations = sa.orm.relationship("Workflow", back_populates="initial_state")


class Workflow(FlowBase, _SlugMixin):
    id = sa.Column(sa.Integer, primary_key=True)
    initial_state_id = sa.Column(sa.Integer, sa.ForeignKey(State.id))

    transitions = sa.orm.relationship("Transition", back_populates="workflow")
    classes = sa.orm.relationship("WorkflowMeta", back_populates="workflow")
    initial_state = sa.orm.relationship("State", back_populates="workflow_initializations")


class WorkflowMeta(FlowBase):
    workflow_id = sa.Column(sa.Integer, sa.ForeignKey(Workflow.id), nullable=False, primary_key=True)
    class_name = sa.Column(sa.String, nullable=False, primary_key=True)

    workflow = sa.orm.relationship("Workflow", back_populates="classes")


class Transition(FlowBase, _SlugMixin):
    id = sa.Column(sa.Integer, primary_key=True)
    workflow_id = sa.Column(sa.Integer, sa.ForeignKey(Workflow.id), nullable=False)
    source_state_id = sa.Column(sa.Integer, sa.ForeignKey(State.id), nullable=False)
    destination_state_id = sa.Column(sa.Integer, sa.ForeignKey(State.id), nullable=False)

    source_state = sa.orm.relationship("State", back_populates="next_transitions", foreign_keys=source_state_id)
    destination_state = sa.orm.relationship("State", foreign_keys=destination_state_id)
    workflow = sa.orm.relationship("Workflow", back_populates="transitions")
    hooks = sa.orm.relationship("Hook", back_populates="transition", order_by="asc(Hook.order_no)")

    def pre_hooks(self):
        for hook in self.hooks:
            if hook.when == Hook.When.PRE:
                yield hook

    def post_hooks(self):
        for hook in self.hooks:
            if hook.when == Hook.When.POST:
                yield hook


class Function(FlowBase, _SlugMixin):
    id = sa.Column(sa.Integer, primary_key=True)
    body = sa.Column(sa.String, nullable=False)
    version = sa.Column(sa.Integer, nullable=False)

    hooks = sa.orm.relationship("Hook", back_populates="function")

    __mapper_args__ = {
        "version_id_col": version
    }

    def get(self):
        func = _loaded_functions.get(self.id, None)
        if not func or func["version"] != self.version:
            func = {"function": self._load(), "version": self.version}
            _loaded_functions[self.id] = func
        return func["function"]

    def _load(self):
        func_body = "def _wrapper(*args, **kwargs):\n"
        for line in self.body.split("\n"):
            func_body += "\t" + line + "\n"
        func_body += "\thandle(*args, **kwargs)\n"
        exec(func_body)
        return eval("_wrapper")


class Hook(FlowBase, _SlugMixin):
    class When(Enum):
        PRE = 1
        POST = 2

    id = sa.Column(sa.Integer, primary_key=True)
    order_no = sa.Column(sa.Integer, nullable=False)
    when = sa.Column(sa.Enum(When), nullable=False)
    function_id = sa.Column(sa.Integer, sa.ForeignKey(Function.id), nullable=False)
    transition_id = sa.Column(sa.Integer, sa.ForeignKey(Transition.id), nullable=False)

    function = sa.orm.relationship("Function", lazy='joined', back_populates="hooks")
    transition = sa.orm.relationship("Transition", lazy='joined', back_populates="hooks")

    __table_args__ = (
        sa.UniqueConstraint(transition_id, order_no, when, name='uq_transition_order'),
    )

    def execute(self, flow_object):
        # TODO: Think about adding try/catch
        self.function.get()(hook=self, payload=flow_object)