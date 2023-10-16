import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor
from viam.components.camera import Camera
from viam.services.vision import VisionClient


#Env Variables for Robot Connectivity 
robot_secret = os.getenv('ROBOT_SECRET') 
robot_address = os.getenv('ROBOT_ADDRESS') 

#Robot Connectivity 
async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)

async def jumpscare(dcmotor):    
    #Hand jumps out, motor goes forward
    await dcmotor.set_power(power=.75)
    await dcmotor.go_for(rpm=70, revolutions=1)

    #Hand goes in, motor goes backwards 
    await dcmotor.set_power(power=-.75)
    await dcmotor.go_for(rpm=-70, revolutions=1)


async def trickOrTreater(dcmotor, detections_test):
    #Searching for trick or treaters to scare! 
    while True: 
        detections = await detections_test.get_detections_from_camera("pumpcam")
        seen = False 

        for d in detections:
            if d.confidence > 0.6:
                if d.class_name == "Person":
                    print("gotcha!")
                    seen = True
        if seen: 
            await jumpscare(dcmotor)
        else: 
            print ("no one is around to take some candy")


async def main():
    robot = await connect()
    
    #Components and Services 
    dcmotor = Motor.from_robot(robot, "dcmotor")
    detections_test = VisionClient.from_robot(robot, "detections_test")

    await trickOrTreater(dcmotor, detections_test)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
