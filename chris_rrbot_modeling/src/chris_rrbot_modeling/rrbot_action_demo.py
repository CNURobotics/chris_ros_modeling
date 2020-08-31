#!/usr/bin/python
# Software License Agreement (BSD License)
# Copyright (c) 2020
# Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
# Christopher Newport University
#
# All rights reserved.
#
# Released under BSD license; see associated LICENSE file for details

"""
Demo of JointTrajectoryAction with RRBot Demo
"""
import math

import actionlib
import roslib
import rospy
from control_msgs.msg import FollowJointTrajectoryGoal, FollowJointTrajectoryAction
from trajectory_msgs.msg import JointTrajectoryPoint

def main(argv):
    """
    Main method for JointTrajectoryAction demo for RRBot
    """
    #http://wiki.ros.org/open_industrial_ros_controllers/Tutorials/To%20program%20robot%20with%20open_industrial_ros_controllers

    try:
        rospy.init_node('rrbot_control_action', anonymous=True)
        rospy.loginfo("Set up action client for RRBot action demo  ...")
        client = actionlib.SimpleActionClient('/rrbot/position_controller/follow_joint_trajectory', FollowJointTrajectoryAction)

        goal = FollowJointTrajectoryGoal()
        goal.trajectory.joint_names.append("joint1")
        goal.trajectory.joint_names.append("joint2")
        print goal.trajectory.joint_names

        for i in range(0,20):
            # 1 cycle
            point = JointTrajectoryPoint()

            # Note: Action controller will add +/- 2pi based on position of arm
            point.positions =[(math.pi/2)*math.cos(math.pi*i/10), # 1 cycle
                              (math.pi/4)*math.cos(math.pi*i/5)]  # 2 cycles
            point.time_from_start = rospy.Duration(i*0.5)         # 10 seconds loop
            goal.trajectory.points.append(point)

        rospy.loginfo("  Wait for action server ...")
        client.wait_for_server()

        rospy.loginfo("Begin repeatedly sending trajectory command to RRBot controllers ...")
        while not rospy.is_shutdown():
            rospy.loginfo("     Send trajectory to controller ...")
            goal.trajectory.header.stamp = rospy.Time.now()+rospy.Duration(0.5)
            res = client.send_goal(goal)

            res = client.wait_for_result()
            rospy.loginfo("    Action result: {}".format(res))

        rospy.loginfo("RRBot Action Demo - Complete!")

    except rospy.ROSInterruptException:
        rospy.loginfo("RRBot Action Demo - Canceled!")
        pass
    finally:
        client.cancel_goal()

if __name__ == '__main__':
    main(sys.argv)
