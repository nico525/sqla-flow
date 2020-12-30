import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from sqla_flow.model import Workflow, State, WorkflowMeta, Transition
from sqla_flow.exc import FlowException, FlowQueryException


class FlowMixin:
    """FlowMixin will provide automatic columns and links to workflow entities"""

    @declared_attr
    def flow_workflow_id(cls):
        return sa.Column('flow_workflow_id', sa.Integer, sa.ForeignKey(Workflow.id), nullable=False)

    @declared_attr
    def flow_state_id(cls):
        return sa.Column('flow_state_id', sa.Integer, sa.ForeignKey(State.id), nullable=False)

    @declared_attr
    def flow_workflow(cls):
        return sa.orm.relationship(Workflow)

    @declared_attr
    def flow_state(cls):
        return sa.orm.relationship(State)

    def transition(self, transition: Transition = None, transition_id=None, transition_slug=None):
        if transition_id is not None and transition is None:
            transition = Transition.query.filter(Transition.source_state_id == self.flow_state_id, Transition.id == transition_id).one()
        if transition_slug is not None and transition is None:
            transition = Transition.query.filter(Transition.source_state_id == self.flow_state_id, Transition.slug == transition_slug).one()
        if transition is None:
            raise FlowException("Missing either transition, transition_id or transition_slug.")

        [hook.execute(flow_object=self) for hook in transition.pre_hooks()]
        self.flow_state_id = transition.destination_state_id
        [hook.execute(flow_object=self) for hook in transition.post_hooks()]

    def flow_mapping(self):
        """Standard function that is used to derive the workflow mapping."""

        return self.__tablename__

    def __init__(self, *args, **kwargs):
        super(FlowMixin, self).__init__(*args, **kwargs)
        if Workflow.query is None:
            raise FlowQueryException

        w = Workflow.query.filter(WorkflowMeta.class_name == self.flow_mapping()).one()
        self.flow_workflow_id = w.id
        self.flow_state_id = w.initial_state_id
