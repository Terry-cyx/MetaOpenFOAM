

from metagpt.roles.role import Role
from metagpt.schema import Message

from metagpt.logs import logger


from actions.InputWriterAction import InputWriterAction
from actions.ArchitectAction import ArchitectAction
from actions.ReviewerAction import ReviewerAction

class InputWriter(Role):
    name: str = "Yuxuan"
    profile: str = "InputWriter"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([InputWriterAction]) 

        self._watch({ArchitectAction, ReviewerAction})
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # todo will be SimpleWriteCode()
        #print('self.rc.history3:',self.rc.history)
        number_subtasks = self.get_memories(k=1)[0]
        print('number_subtasks',number_subtasks)

        context = self.get_memories(k=1+int(number_subtasks.content))

        if context: 
            context = context[:-1]
    
        print('get_memories_InputWriter',context)
        code_text = await todo.run(context)

        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        #msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        return msg
    