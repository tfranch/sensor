from datetime import datetime
import pymongo
import time


def main():
    from sense_hat import SenseHat
    sense = SenseHat()
    sense.clear()
    sense.low_light = True
    sense.set_imu_config(True, True, True)
    sensor_start = sense.get_accelerometer()
    sensor_sensitivity = .0001
    move_list = []
    ex_coll = get_db('zs5_mongo', 'sensor')['freezer']
    while True:
        sensor_in = sense.get_accelerometer()
        move_size = (sensor_in['roll'] - sensor_start['roll']) ** 2 + (
                    sensor_in['pitch'] - sensor_start['pitch']) ** 2 + (sensor_in['yaw'] - sensor_start['yaw']) ** 2
        sensor_start = sensor_in
        if move_size >= sensor_sensitivity:
            sense.show_letter('M')
            move_dict = {'move_ts': datetime.utcnow().timestamp(), **sensor_in}
            ex_coll.insert_one(move_dict)
        time.sleep(.2)
        sense.clear()


def get_db(server, db):
    if server == 'zs5_mongo':
        client = pymongo.MongoClient('192.168.1.201', 27017, username='torben', password='Mantra0099')
    db = client[db]
    return db


if __name__ == '__main__':
    main()
