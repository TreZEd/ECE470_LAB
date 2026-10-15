#!/usr/bin/env python

'''

lab3pkg_hanoi/lab3_ur3e.py

@brief: UR3e class include functions for controlling the UR3e arm and the gripper

@author: Songjie Xiao
@date: Monday 2023/03/17

'''
import time
import rospy

# IMPORT! headers for ROS messages and include useful message types
from lab3_header import *

class UR3e():

    def __init__(self):

        # define variables here
        # store the current position of the arm
        self.current_position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        # store the current state of the suction cup
        self.current_io_0 = False

        # Initialize publisher for ur3e_driver_ece470/setjoint with buffer size of 10
        self.pub_setjoint = rospy.Publisher('ur3e_driver_ece470/setjoint', JointTrajectory, queue_size=10)

        # TODO: define a ROS publisher for /ur3e_driver_ece470/setio message with buffer size of 10
        self.pub_setio = rospy.Publisher(
            '/ur3e_driver_ece470/setio',
            Digital,
            queue_size=10
        )

        # Initialize subscriber to /joint_states, each time /joint_states publishes a new message, the function position_callback is called
        self.sub_position = rospy.Subscriber('/joint_states', JointState, self.position_callback)

        # TODO: define a ROS subscriber for /ur_hardware_interface/io_states message and corresponding callback function
        self.sub_io = rospy.Subscriber(
            '/ur_hardware_interface/io_states',
            IOStates,
            self.gripper_input_callback
        )
    
    def init_array(self, home, Q):

        # initialize the home position and Q array
        self.home = home
        self.Q = Q

    def gripper_input_callback(self, msg):
        """
        TODO: define a ROS topic callback function for getting the state of suction cup
        Whenever /ur_hardware_interface/io_states publishes info, this callback function is called.
        """
        ############## Your Code Start Here ##############
        for digital_input in msg.digital_in_states:
            if digital_input.pin == 0:
                self.current_io_0 = digital_input.state
                return

        rospy.logwarn_throttle(
            5.0,
            "IOStates feedback does not contain digital input pin 0"
        )#warn
        pass

        ############## Your Code End Here ##############


    def position_callback(self, msg):
        """
        TODO: define a ROS topic callback function for getting the current position of the arm
        Whenever /joint_states publishes info, this callback function is called.
        """
        ############## Your Code Start Here ##############
        # 顺序与 move_arm() 中的 msg.joint_names 保持一致
        joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint"
        ]

        position_by_name = dict(zip(msg.name, msg.position))

        # 保存当前关节角度，单位为弧度
        self.current_position = [
            position_by_name[name] for name in joint_names
        ]
        pass

        ############### Your Code End Here ###############


    def gripper(self, io_0):
        """
        TODO: define a function for ROS Publisher to publish your message to the Topic "ur3e_driver_ece470/setio",
        so that we can control the state of suction cup.
        """
        ############## Your Code Start Here ##############
        msg = Digital()
        msg.pin = 0
        msg.state = bool(io_0)

        self.pub_setio.publish(msg)

        # 给吸盘留出动作时间，可根据实际设备调整
        rospy.sleep(0.5)
        pass
    
        ############### Your Code End Here ###############


    def move_arm(self, dest):
        """
        Function for moving the arm to a desired location
        """
        # define msg
        msg = JointTrajectory()
        msg.joint_names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
        point = JointTrajectoryPoint()
        point.positions = dest
        point.time_from_start = rospy.Duration(2)
        msg.points.append(point)
        # publish msg
        self.pub_setjoint.publish(msg)
        time.sleep(2.5)


    def move_block(self, start_loc, start_height, end_loc, end_height):
        """
        TODO: define move_block function which is used to move a block from start to end location
        which includes moving the arm to the start location, gripping the block, moving the arm to the end location, and releasing the block

        Hint: Use the Q array to map out your towers by location and height.
        """
        ############## Your Code Start Here ##############

        indices = (start_loc, start_height, end_loc, end_height)
        if any(index not in (0, 1, 2) for index in indices):
            raise ValueError("塔位置和高度的索引必须为 0、1 或 2")

        # Q 的第一维是高度，第二维是塔位置
        pick_position = self.Q[start_height][start_loc]
        place_position = self.Q[end_height][end_loc]

        # 1. 移动到 home 中转姿态
        self.move_arm(self.home)

        # 2. 移动到取物位置
        self.move_arm(pick_position)

        # 3. 开启吸盘
        self.gripper(True)

        # 4. 带着方块返回 home
        self.move_arm(self.home)

        # 5. 移动到放物位置
        self.move_arm(place_position)

        # 6. 关闭吸盘，释放方块
        self.gripper(False)

        # 7. 返回 home
        self.move_arm(self.home)
        pass

        ############### Your Code End Here ###############





