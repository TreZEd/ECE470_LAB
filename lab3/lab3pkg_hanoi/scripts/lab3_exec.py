#!/usr/bin/env python

'''

lab3pkg_hanoi/lab3_exec.py

@brief: Hanoi implementation in ROS.
@author: Songjie Xiao
@date: Monday 2023/3/20

'''

import sys
import time
import rospy
import numpy as np

from lab3_ur3e import UR3e

def main():

	# Initialize ROS node
	rospy.init_node('lab3_node')

	# Definition of our tower

	# block contact position
	# | Q[0][0] Q[0][1] Q[0][2] |   Contact point of top block
	# | Q[1][0] Q[1][1] Q[1][2] |   Contact point of middle block
	# | Q[2][0] Q[2][1] Q[2][2] |   Contact point of bottom block
	# | Tower1  Tower2  Tower3  |

	# First index - From "top" to "bottom"
	# Second index - From "left" to "right"

	# How the arm will move (Suggestions)
	# 1. Go to the "home" position
	# 2. Drop to the "contact (start) block" position
	# 3. Rise back to the "home" position
	# 4. Drop to the corresponding "contact (end) block" position
	# 5. Rise back to the "home" position

	"""
	TODO: define position of our tower in Q array and home position of the arm
	"""
	############## Your Code Start Here ##############

	# home 中转姿态：填写实际测量的六个关节角度（度）
	home_deg = [np.nan] * 6

	# 第一维：高度，0=上层，1=中层，2=下层
	# 第二维：塔位置，0=第1塔，1=第2塔，2=第3塔
	# 第三维：六个关节角度
	Q_deg = np.array([
		# 上层接触位置
		[
			[np.nan] * 6,  # 第1塔上层
			[np.nan] * 6,  # 第2塔上层
			[np.nan] * 6,  # 第3塔上层
		],

		# 中层接触位置
		[
			[np.nan] * 6,  # 第1塔中层
			[np.nan] * 6,  # 第2塔中层
			[np.nan] * 6,  # 第3塔中层
		],

		# 下层接触位置
		[
			[np.nan] * 6,  # 第1塔下层
			[np.nan] * 6,  # 第2塔下层
			[np.nan] * 6,  # 第3塔下层
		],
	], dtype=float)

	# 防止尚未填写的位置进入运动流程
	if not np.isfinite(home_deg).all() or not np.isfinite(Q_deg).all():
		raise ValueError("请先填写 home 和 Q 中实际测量的六个关节角度")

	# 统一从度转换为弧度
	home = np.radians(home_deg)
	Q = np.radians(Q_deg)

	############### Your Code End Here ###############

	# This program will require two user inputs to specify the start location and end location of the block
	# TODO: modify the code below so that program can get two user inputs
	############## Your Code Start Here ##############

	# example code for getting user input is provided below
	input_done = 0
	start = 0
	mid = 1
	des = 2

	while not input_done:
		start_input = input("起始塔（1/2/3，0退出）：").strip()
		if start_input == "0":
			sys.exit()

		des_input = input("目标塔（1/2/3，0退出）：").strip()
		if des_input == "0":
			sys.exit()

		if start_input not in ("1", "2", "3") or \
				des_input not in ("1", "2", "3"):
			print("请输入 1、2 或 3。")
			continue

		if start_input == des_input:
			print("起始塔和目标塔不能相同。")
			continue

		start = int(start_input) - 1
		des = int(des_input) - 1
		mid = 3 - start - des
		input_done = 1

	############### Your Code End Here ###############

	rospy.loginfo("Sending Goals ...")

	# Main manipulation code defined here
	# move_arm function is used to move the arm to a desired position
	# move_block function is used to move a block from start to end location
	# which includes moving the arm to the start location, gripping the block, moving the arm to the end location, and releasing the block
	# TODO: here to define a series of move_block or move_arm function calls to solve the Hanoi Tower problem
	############## Your Code Start Here ##############

	# initialize ur3e class
	ur3e = UR3e()
	ur3e.init_array(home, Q)
	time.sleep(2)
	
	# example code for moving the arm to home position is provided below
	# ur3e.move_arm(home)
	# ur3e.move_block(start, 0, des, 2)
	# ...
	# ur3e.move_arm(home)
	ur3e.move_arm(home)
	############### Your Code End Here ###############

if __name__ == '__main__':
	try:
		main()
	# When Ctrl+C is executed, it catches the exception
	except rospy.ROSInterruptException:
		pass
