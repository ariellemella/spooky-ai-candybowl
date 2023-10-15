import asyncio
import os 

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor
from viam.components.camera import Camera


#Env Variables for Robot Connectivity 
robot_secret = os.getenv('ROBOT_SECRET') 
robot_address = os.getenv('ROBOT_ADDRESS') 


async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)

async def handMovement(dcmotor):

    #Hand jumps out, motor goes forward
    await dcmotor.set_power(power=1)
    await dcmotor.go_for(rpm=60, revolutions=1)

    #Hand goes in, motor goes backwards 
    await dcmotor.set_power(power=-1)
    await dcmotor.go_for(rpm=-60, revolutions=1)


async def main():
    robot = await connect()
    
    #Components 
    pi = Board.from_robot(robot, "pi")
    dcmotor = Motor.from_robot(robot, "dcmotor")
    pumpcam = Camera.from_robot(robot, "pumpcam")
    
    await handMovement(dcmotor)
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
