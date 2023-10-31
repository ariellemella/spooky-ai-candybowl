import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.motor import Motor
from viam.services.vision import VisionClient


#Env Variables for Robot Connectivity 
robot_secret = os.getenv('ROBOT_SECRET') 
robot_address = os.getenv('ROBOT_ADDRESS') 

COSTUMES = ["witch", "mummy", "vampire", "cowboy", "zombie"]

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


async def trickOrTreater(dcmotor, detections_test, costume_det):
    #Searching for trick or treaters to scare! 
    while True: 
        people_detections = await detections_test.get_detections_from_camera("pumpcam")
        costume_detections = await costume_det.get_detections_from_camera("pumpcam")
        seen = False 

        print ("no one is around to take some candy")

        for d in people_detections:
            if d.confidence > 0.6:
                if d.class_name == "Person":
                    print("gotcha!")
                    seen = True
        if seen: 
            await jumpscare(dcmotor)
        else: 
           for d in costume_detections:
            if d.confidence > 0.6:
                if d.class_name in COSTUMES:
                    print("happy Halloween! take a treat!")
                    seen = True


async def main():
    robot = await connect()
    
    #Components and Services 
    dcmotor = Motor.from_robot(robot, "dcmotor")
    detections_test = VisionClient.from_robot(robot, "detections_test")
    costume_det = VisionClient.from_robot(robot, "costume_det")

    await trickOrTreater(dcmotor, detections_test, costume_det)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
