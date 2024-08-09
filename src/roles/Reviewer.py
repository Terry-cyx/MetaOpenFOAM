

from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger


from actions.ReviewerAction import ReviewerAction
from actions.RunnerAction import RunnerAction

class Reviewer(Role):
    name: str = "Xingyu"
    profile: str = "Reviewer"
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([ReviewerAction])

        # 订阅消息
        self._watch({RunnerAction})
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # todo will be SimpleWriteCode()
        
        context_all = self.get_memories()

        context = [context_all[0],context_all[-1]]

        subtasks = await todo.run(context)


        for i in subtasks:
           
           self.rc.env.publish_message(Message(content=i, cause_by=ReviewerAction))

        return Message(content=str(len(subtasks)), role=self.profile, cause_by=type(todo))

