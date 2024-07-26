import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient
from viam.components.base import Base

# 
SECRET = "3rn6lwpqwh5xzra3sy33x8ul94b5s20zf66ghe6v9bny577z"

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=SECRET)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('robot7-main.wkhwbmlw2g.viam.cloud', opts)


async def main():
    numCycles = 200  # how many times to repeat the main loop

    # Connect to robot client and set up components
    robot = await connect()
    base = Base.from_robot(robot, "base")

    # Grab the vision service for the detector
    detector = VisionClient.from_robot(robot, "happy")

    # Main loop. Detect the baby
    for _ in range(numCycles):
        # make sure that your camera name in the app matches "my-camera"
        detections = await detector.get_detections_from_camera("cam")
        for d in detections:
            if d.confidence > 0.8:
                if d.class_name.lower() == "baby":
                    print(f"Baby found at {d.x}, {d.y}!")
                    # move the robot in the direction of the baby
                    if d.x < 0.4:
                        await base.spin(velocity=100, angle=80)
                    elif d.x > 0.6:
                        await base.spin(velocity=100, angle=-80)
                    await base.move_straight(velocity=100, distance=100)

    # Pause then close the connection
    await asyncio.sleep(100)
    await robot.close()

if __name__ == "__main__":
    print("Starting up... ")
    asyncio.run(main())
    print("Done.")
