#!/usr/bin/env python

import rospy
import geometry_msgs.msg
import visualization_msgs.msg
import tf
import math

from networktables import NetworkTables
import sys

if len(sys.argv) < 2:
    print('need to input server IP as argument!');
    print('for exmaple: 10.75.89.2');
    exit(0)

serverIp = sys.argv[1]
NetworkTables.initialize(server=serverIp)
sd = NetworkTables.getTable('SmartDashboard')
odom_x = sd.getAutoUpdateValue('odom_x', defaultValue=0, writeDefault=False)
odom_y = sd.getAutoUpdateValue('odom_y', defaultValue=0, writeDefault=False)
odom_z = sd.getAutoUpdateValue('odom_z', defaultValue=0, writeDefault=False)

rospy.init_node('frc_odometry_visualize', anonymous=True)

# yaw & pitch: world; roll: rotated (nose pointing)
def buildMarker(id, x, y, z, yaw, pitch, roll, cm, newcome=False):
    marker = visualization_msgs.msg.Marker()
    marker.header.frame_id = '/map'
    marker.ns = 'aruco'
    marker.id = id
    marker.type = marker.CUBE
    marker.action = marker.DELETE if newcome else marker.ADD
    marker.scale.x = cm/100.0
    marker.scale.y = cm/100.0
    marker.scale.z = 0.20
    marker.color.a = 1.0
    marker.color.r = 1.0
    marker.color.g = 1.0
    marker.color.b = 0.0
    q = tf.transformations.quaternion_from_euler(yaw/180.0*math.pi, pitch/180.0*math.pi, roll/180.0*math.pi, 'rzxz')
    marker.pose.orientation = geometry_msgs.msg.Quaternion(*q)
    marker.pose.position = geometry_msgs.msg.Point(x, y, z)
    return marker

def buildPose(x, y, z, yaw, pitch, roll):
    q = tf.transformations.quaternion_from_euler(yaw/180.0*math.pi, pitch/180.0*math.pi, roll/180.0*math.pi, 'rzxz')
    pose = geometry_msgs.msg.PoseStamped()
    pose.header.frame_id = '/map'
    pose.header.stamp = rospy.Time.now()
    pose.pose.position = geometry_msgs.msg.Point(x, y, z)
    pose.pose.orientation = geometry_msgs.msg.Quaternion(*q)
    return pose

cm = 75
odom_pub = rospy.Publisher('drive_odom', visualization_msgs.msg.MarkerArray)
markerArr = visualization_msgs.msg.MarkerArray()
pose_pub = rospy.Publisher('drive_odom_pose', geometry_msgs.msg.PoseStamped)
rate = rospy.Rate(3)
while not rospy.is_shutdown():
    if len(markerArr.markers)>0:
        markerArr.markers[0] = buildMarker( 0, odom_x.value, odom_y.value, 0, odom_z.value, 0, 0, cm )
    else:
        markerArr.markers.append(buildMarker( 0, odom_x.value, odom_y.value, 0, odom_z.value, 0, 0, cm ))
    odom_pub.publish(markerArr)
    pose_pub.publish(buildPose(odom_x.value, odom_y.value, 0, odom_z.value, 0, 0))
    rate.sleep()
