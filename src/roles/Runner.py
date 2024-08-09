

from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger

from actions.RunnerAction import RunnerAction
from actions.InputWriterAction import InputWriterAction

class Runner(Role):
    name: str = "Foamer"
    profile: str = "Runner"
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([RunnerAction]) 

        self._watch({InputWriterAction})
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # todo will be SimpleWriteCode()
        context = self.get_memories()
        msg = await todo.run(context)
        msg = Message(content=msg, role=self.profile, cause_by=type(todo))
        return msg
