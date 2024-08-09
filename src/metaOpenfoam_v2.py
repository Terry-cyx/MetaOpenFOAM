
import asyncio

from metagpt.context import Context
from metagpt.schema import Message
from metagpt.environment.base_env import Environment

from qa_module import AsyncQA_tutorial, AsyncQA_tutorial_name, AsyncQA_allrun, AsyncQA_Ori
from roles.Architect import Architect
from roles.InputWriter import InputWriter
from roles.Reviewer import Reviewer
from roles.Runner import Runner
import config_path
from Statistics import Statistics, global_statistics
import time

async def main():
    overall_stats = Statistics()
    for _ in range(config_path.run_times):
        global_statistics.reset()
        start_time = time.time()
        global_statistics.runtimes = _ + 1
        print("runtimes:",_ + 1)
        config_path.should_stop = False
        await run_instance()

        global_statistics.running_time = time.time() - start_time
        global_statistics.save_to_file(config_path.Case_PATH)
        overall_stats.save(global_statistics)

    overall_stats.average(config_path.run_times)
    overall_stats.display()
    overall_stats.save_ave_file(config_path.Case_PATH)

async def run_instance():
    async_qa = AsyncQA_tutorial()
    async_qa.init_instance()
    
    async_qa_name = AsyncQA_tutorial_name()
    async_qa_name.init_instance()
    async_qa_allrun = AsyncQA_allrun()
    async_qa_allrun.init_instance()
    async_qa_ori = AsyncQA_Ori()
    async_qa_ori.init_instance()

    context = Context() # Load config2.yaml
    env = Environment(context=context)
    architect = Architect(context=context)
    inputWriter = InputWriter(context=context)
    runner = Runner(context=context)
    reviewer = Reviewer(context=context)

    env.add_roles([architect, inputWriter,runner, reviewer])

    #env.publish_message(Message(content='do a DNS simulation of homogeneous isotropic turbulence with Grid N= 16^3', send_to=AgentA)) # 将用户的消息发送个Agent A，让Agent A开始工作。
    #do a DNS simulation of incompressible forcing homogeneous isotropic turbulence with Grid 16^3 using dnsFoam (success) loop 2
    #do a LES simulation (not parallel) of incompressible channel flow with Grid 50*10*10 using pimpleFoam, inlet velocity 1 m/s, length 5 cm, case name: incompressibleChannelFlow3 (success) loop 6
    #do a DNS simulation of incompressible forcing homogeneous isotropic turbulence with Grid 32^3 using dnsFoam (success)
    #do a RANS simulation of backward facing step with inlet velocity 1 m/s, without parallel (success) loop 12
    #do a simulation of flow around a cylinder with inlet velocity 1 m/s without parallel, case name: cylinder3
    #do a LES simulation (not parallel) of incompressible channel flow with Grid 50*10*10 using pimpleFoam, inlet velocity 1 m/s, length 5 cm and the blockMeshDict is already prepared.
    #do an incompressible lid driven cavity flow simulation with the top wall moves in the x direction at a speed of 1 m/s while the other 3 are stationary (no loop) (success)
    #do a LES simulation of compressible pitzDaily using rhoPimpleFoam, and the velocity of inlet is 100 m/s.
    #do a laminar simulation of incompressible planar Poiseuille flow of a non-Newtonian fluid with grid 1*20*1, modelled using the Maxwell viscoelastic laminar stress model, initially at rest, constant pressure gradient applied from time zero
    #do a compressible simulation of squareBendLiq of using rhoSimpleFoam with endTime 100 and writeInterval 10 (success)
    #do a RANS simulation of buoyantCavity using buoyantSimpleFoam, which investigate natural convection in a heat cavity with a temperature difference of 20K is maintained between the hot and cold; the remaining patches are treated as adiabatic (ex: 2)
    env.publish_message(Message(content=config_path.usr_requirment, send_to=Architect))
    while not env.is_idle and not config_path.should_stop: 
        await env.run()
        

if __name__ == "__main__":

    asyncio.run(main())