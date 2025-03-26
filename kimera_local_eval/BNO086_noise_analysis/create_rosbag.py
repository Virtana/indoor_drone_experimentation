#!/usr/bin/env python

import rospy
import rosbag
from sensor_msgs.msg import Imu
from std_msgs.msg import Header
import csv
from geometry_msgs.msg import Vector3, Quaternion
import argparse
import os
from datetime import datetime

def create_imu_bag(csv_file, output_bag, topic_name='/imu/data', frame_id='imu_link'):
    """
    Create a ROS bag file from IMU (accelerometer and gyroscope) CSV data.
    
    Args:
        csv_file (str): Path to input CSV file
        output_bag (str): Path to output ROS bag file
        topic_name (str): ROS topic name to publish IMU data
        frame_id (str): Frame ID for the IMU data
    """
    
    # Check if input file exists
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Input CSV file not found: {csv_file}")
    
    # Open the output bag file
    with rosbag.Bag(output_bag, 'w') as bag:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            
            # Skip header if present (modify as needed for your CSV format)
            headers = next(reader, None)
            
            for row in reader:
                try:
                    # Parse the CSV row - adjust indices based on your CSV format
                    # This example assumes format: timestamp, ax, ay, az, gx, gy, gz
                    timestamp = float(row[0]) / 1_000_000_000
                    gx = float(row[1])
                    gy = float(row[2])
                    gz = float(row[3])
                    ax = float(row[4])
                    ay = float(row[5])
                    az = float(row[6])
                    
                    # Create IMU message
                    imu_msg = Imu()
                    
                    # Set header
                    imu_msg.header = Header()
                    imu_msg.header.stamp = rospy.Time.from_sec(timestamp)
                    imu_msg.header.frame_id = frame_id
                    
                    # Set linear acceleration (accelerometer data)
                    imu_msg.linear_acceleration = Vector3()
                    imu_msg.linear_acceleration.x = ax
                    imu_msg.linear_acceleration.y = ay
                    imu_msg.linear_acceleration.z = az
                    
                    # Set angular velocity (gyroscope data)
                    imu_msg.angular_velocity = Vector3()
                    imu_msg.angular_velocity.x = gx
                    imu_msg.angular_velocity.y = gy
                    imu_msg.angular_velocity.z = gz
                    
                    # For a real IMU, you'd also have orientation (quaternion)
                    # Since we don't have it in CSV, we'll leave it as zero
                    imu_msg.orientation = Quaternion(0, 0, 0, 1)  # Default no rotation
                    
                    # Write to bag
                    bag.write(topic_name, imu_msg, imu_msg.header.stamp)
                    
                except (ValueError, IndexError) as e:
                    rospy.logwarn(f"Skipping malformed row: {row}. Error: {e}")
                    continue

if __name__ == '__main__':
    # Initialize ROS node (not strictly necessary for bag creation, but required for Time)
    rospy.init_node('csv_to_rosbag', anonymous=True)
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Convert IMU CSV data to ROS bag')
    parser.add_argument('input_csv', help='Input CSV file path')
    parser.add_argument('--output_bag', help='Output bag file path', default=None)
    parser.add_argument('--topic', help='ROS topic name', default='/imu/data')
    parser.add_argument('--frame_id', help='Frame ID for IMU data', default='imu_link')
    
    args = parser.parse_args()
    
    # Set default output bag name if not provided
    if args.output_bag is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_bag = f"imu_data_{timestamp}.bag"
    
    try:
        create_imu_bag(args.input_csv, args.output_bag, args.topic, args.frame_id)
        print(f"Successfully created ROS bag: {args.output_bag}")
    except Exception as e:
        print(f"Error creating ROS bag: {e}")