import mujoco as mj
import mediapy as media
import matplotlib.pyplot as plt
import time
from datetime import datetime
import itertools
import numpy as np
from mujoco.glfw import glfw
from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R

from mujoco_base import MuJoCoBase

# TODO:
# 增加至两条弹簧的现象
# 多次实验 记录每次跳跃最大高度和弹簧刚度的关系
# 在空中：


# 驱动器直接使用motor如何控制 麻烦
# equality 如何hinge连接 weld夹心饼
# 获得质心的位置速度加速度 不容易


FSM_AIR = 0
FSM_STANCE = 1
FSM_TAKEOFF = 2

    
class HopperData:
    def __init__(self):
        self.time_datas = []
        # 能量
        self.kinetic_energy_datas = []
        self.potential_energy_datas = []
        self.total_energy_datas = []
        # 位置
        self.jump_height_datas = []
        self.hip_pos_sensor_datas = []
        # 速度
        self.hip_vel_sensor_datas = []
        self.velocity_sensor_datas = []
        # 加速度
        self.acceleration_sensor_datas = []
        # 力
        self.ground_force_x_sensor_datas = []
        self.ground_force_y_sensor_datas = []
        self.ground_force_z_sensor_datas = []
        # 其他
        self.spring_length_datas = []   # 弹簧长度
        self.theta_datas = []  # 小腿leg连杆与地面的夹角
        
    def clear_data(self):
        """
        清空数据
        """
        for attr in dir(self):
            if attr.endswith('_datas') or attr.endswith('times'):
                setattr(self, attr, [])
    
    def save_data(self, save_dir:str = "./temp/sensor_data/"):
        """
        保存数据，默认保存在temp文件夹
        """
        import csv  
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        print("当前时间为",date_time)
        filename = save_dir + "sensor_data_" + date_time + ".csv"
        with open(filename, mode='w', newline='') as file:
            # 重构这个 减少层数
            writer = csv.writer(file)
            headers = [attr.replace('_datas', '').replace('_', ' ').title() for attr in dir(self) if attr.endswith('_datas')]
            writer.writerow(headers)
            for i in range(len(self.time_datas)):
                row = []
                for attr in dir(self):
                    if attr.endswith('_datas'):
                        data = getattr(self, attr)
                        if i < len(data):
                            row.append(data[i])
                        else:
                            row.append(None)
                writer.writerow(row)

    def plot_data(self):
        row = 6
        column = 1
        plt.figure(1)
        plt.clf()
        
        plt.subplot(row, column, 1)
        plt.plot(self.time_datas, self.kinetic_energy_datas, label='Kinetic Energy')
        plt.plot(self.time_datas, self.potential_energy_datas, label='Potential Energy')
        plt.plot(self.time_datas, self.total_energy_datas, label='Total Energy')
        plt.xlabel('Time')
        plt.ylabel('Energy')
        plt.legend()
        
        plt.subplot(row, column, 2)
        plt.plot(self.time_datas, self.jump_height_datas, label='foot_height')
        plt.xlabel('Time')
        plt.ylabel('position')
        plt.legend()
        plt.draw()
        
        plt.subplot(row, column, 3)
        plt.plot(self.time_datas, self.velocity_sensor_datas, label='velocity')
        plt.xlabel('Time')
        plt.ylabel('velocity')
        plt.legend()
        plt.draw()
        
        plt.subplot(row, column, 4)
        plt.plot(self.time_datas, self.acceleration_sensor_datas, label='acceleration')
        plt.xlabel('Time')
        plt.ylabel('acceleration')
        plt.legend()
        plt.draw()
        
        plt.subplot(row, column, 5)
        plt.plot(self.time_datas, self.ground_force_x_sensor_datas, label='ground_force_x')
        plt.plot(self.time_datas, self.ground_force_y_sensor_datas, label='ground_force_y')
        plt.plot(self.time_datas, self.ground_force_z_sensor_datas, label='ground_force_z')
        plt.xlabel('Time')
        plt.ylabel('ground_force')
        plt.legend()
        plt.draw()
        
        plt.subplot(row, column, 6)
        plt.plot(self.time_datas, self.theta_datas, label='theta')
        plt.plot(self.time_datas, self.hip_pos_sensor_datas, label='hip_pos_sensor')
        plt.xlabel('Time')
        plt.ylabel('angle')
        plt.legend()
        plt.draw()
        
        plt.pause(0.0001)     

    def save_image(self, save_dir:str = "./temp/image/"):
        row = 6
        column = 1
        plt.figure(2, figsize=(5, 8))
        
        plt.subplot(row, column, 1)
        plt.plot(self.time_datas, self.kinetic_energy_datas, label='Kinetic Energy')
        plt.plot(self.time_datas, self.potential_energy_datas, label='Potential Energy')
        plt.plot(self.time_datas, self.total_energy_datas, label='Total Energy')
        plt.xlabel('Time')
        plt.ylabel('Energy')
        plt.legend()
        
        plt.subplot(row, column, 2)
        plt.plot(self.time_datas, self.jump_height_datas, label='foot_height')
        plt.xlabel('Time')
        plt.ylabel('position')
        plt.legend()
        
        plt.subplot(row, column, 3)
        plt.plot(self.time_datas, self.velocity_sensor_datas, label='velocity')
        plt.xlabel('Time')
        plt.ylabel('velocity')
        plt.legend()
        
        plt.subplot(row, column, 4)
        plt.plot(self.time_datas, self.acceleration_sensor_datas, label='acceleration')
        plt.xlabel('Time')
        plt.ylabel('acceleration')
        plt.legend()
        
        plt.subplot(row, column, 5)
        plt.plot(self.time_datas, self.ground_force_x_sensor_datas, label='ground_force_x')
        plt.plot(self.time_datas, self.ground_force_y_sensor_datas, label='ground_force_y')
        plt.plot(self.time_datas, self.ground_force_z_sensor_datas, label='ground_force_z')
        plt.xlabel('Time')
        plt.ylabel('ground_force')
        plt.legend()
        
        plt.subplot(row, column, 6)
        plt.plot(self.time_datas, self.theta_datas, label='theta')
        plt.plot(self.time_datas, self.hip_pos_sensor_datas, label='hip_pos_sensor')
        plt.xlabel('Time')
        plt.ylabel('angle')
        plt.legend()
        
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = save_dir + "data_image_" + date_time + ".png"
        plt.savefig(filename)

    def get_jump_height(self):
        indices = [i for i, x in enumerate(self.time_datas) if abs(x - 1) < 0.1]
        print(indices)
        

class Hopper1(MuJoCoBase):
    def __init__(self, xml_path):
        super().__init__(xml_path)
        self.simend = 5  # 停止时间
        self.Hz = 20
        self.is_plot_data = True
        self.is_plot_data = False
        glfw.set_key_callback(self.window, self.keyboard)
        self.fsm = None
        # self.step_no = 0
        # 储存用于画图和分析的数据
        self.hopperdata = HopperData()
        

    def reset(self):
        # Set camera configuration
        self.cam.azimuth = 89.608063
        self.cam.elevation = -11.588379
        self.cam.distance = 5.0
        self.cam.lookat = np.array([0.0, 0.0, 1.5])
        # self.model.opt.gravity = [0,0,-1]
        self.fsm = FSM_TAKEOFF # 有限状态机（Finite State Machine）
        # self.step_no = 0
        # pservo-hip
        # self.set_position_servo(0, 100)
        # vservo-hip
        # self.set_velocity_servo(1, 10)
        # pservo-knee
        # self.set_position_servo(2, 1000)
        # vservo-knee
        # self.set_velocity_servo(3, 0)
        mj.set_mjcb_control(self.controller)
    
    def keyboard(self, window, key, scancode, act, mods):
        """
        绑定键盘回调函数
        """
        if act == glfw.PRESS and key == glfw.KEY_BACKSPACE:
            mj.mj_resetData(self.model, self.data)
            mj.mj_forward(self.model, self.data)
            self.fsm = FSM_TAKEOFF # 有限状态机（Finite State Machine）
            self.data.clear_data()
            plt.clf()
        if act == glfw.PRESS and key == glfw.KEY_ESCAPE: 
            # 默认按escape退出即保存所有数据
            self.hopperdata.save_data()
            self.hopperdata.save_image()
            model_text_dir = "./temp/model.txt"
            data_text_dir = "./temp/data.txt"
            mj.mj_printModel(self.model, model_text_dir)
            mj.mj_printData(self.model, self.data, data_text_dir)       
            glfw.set_window_should_close(window, True)
        if act == glfw.PRESS and key == glfw.KEY_A: 
            self.hopperdata.clear_data()
            plt.clf()
            pservo_hip_left_id = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_ACTUATOR, "pservo_hip_left")
            pservo_hip_right_id = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_ACTUATOR, "pservo_hip_right")
            # print('left_hip_roll_id', left_hip_roll_id)
            # 这里的数字的单位是什么
            # self.data.ctrl[pservo_hip_left_id] = -47
            # self.data.ctrl[pservo_hip_right_id] = 47
            # mj.mj_resetDataKeyframe(self.model, self.data, 0)
            self.fsm = FSM_TAKEOFF
            
            # print(self.data.qpos)
        if act == glfw.PRESS and key == glfw.KEY_D: 
            print(self.data.sensordata)
            
    def controller(self, model, data):
        """
        控制关节的行为
        """
        # return
        # 之后不要直接读取位置，而是通过传感器读取位置，给传感器扰动，以符合现实传感器波动导致机器不稳的情况
        # z_foot = data.sensordata[0]
        # body_no = 3
        # z_foot = data.xpos[body_no, 2]
        # vz_torso = data.qvel[1]
        # height = self.data.qpos[8] - self.model.qpos0[8]
        spring_siteid:int = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_TENDON, "tendon1")
        spring_length = self.data.ten_length[spring_siteid]
        pservo_hip_left_id = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_ACTUATOR, "pservo_hip_left")
        pservo_hip_right_id = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_ACTUATOR, "pservo_hip_right")
        vservo_hip_left_id = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_ACTUATOR, "vservo_hip_left")
        vservo_hip_right_id = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_ACTUATOR, "vservo_hip_right")
        
        mj.mj_energyPos(model, data)
        mj.mj_energyVel(model, data)
        
        # Take off
        during_time = self.data.time - self.start_time
        # print(during_time)
        # print(spring_length)
        if self.fsm == FSM_TAKEOFF and spring_length > 1.64 and during_time > 1:
            self.fsm = FSM_AIR

        if self.fsm == FSM_AIR:
            self.data.ctrl[pservo_hip_left_id] = 0
            self.data.ctrl[pservo_hip_right_id] = 0
            self.set_position_servo(pservo_hip_left_id, 10)
            self.set_velocity_servo(vservo_hip_left_id,10)
            self.set_position_servo(pservo_hip_right_id, 10)
            self.set_velocity_servo(vservo_hip_right_id,10)

        if self.fsm == FSM_TAKEOFF:
            self.data.ctrl[pservo_hip_left_id] = -0.7
            self.data.ctrl[pservo_hip_right_id] = 0.7
            self.set_position_servo(pservo_hip_left_id, 3000)
            self.set_velocity_servo(vservo_hip_left_id,100)
            self.set_position_servo(pservo_hip_right_id, 3000)
            self.set_velocity_servo(vservo_hip_right_id,100)
            
    def bind_data(self):
        """
        收集数据
        """
        spring_siteid:int = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_TENDON, "tendon1")
        spring_length = self.data.ten_length[spring_siteid]
        # height = self.data.qpos[8] - self.model.qpos0[8]    # 底座的位置-初始位置，为了让时间为0时高度为0
        # print(self.data.qpos)
        # 让这个不要随着模型变化修改
        height = self.data.qpos[13]
        self.hopperdata.time_datas.append(self.data.time)
        self.hopperdata.kinetic_energy_datas.append(self.data.energy[1])
        self.hopperdata.potential_energy_datas.append(self.data.energy[0])
        self.hopperdata.total_energy_datas.append(self.data.energy[0] + self.data.energy[1])
        self.hopperdata.spring_length_datas.append(spring_length)
        self.hopperdata.jump_height_datas.append(height)
        self.hopperdata.hip_pos_sensor_datas.append(self.data.sensordata[0]*180/3.1415)
        self.hopperdata.hip_vel_sensor_datas.append(self.data.sensordata[1])
        self.hopperdata.acceleration_sensor_datas.append(self.data.sensordata[4])
        self.hopperdata.velocity_sensor_datas.append(self.data.sensordata[7])
        q = self.data.xquat[5]
        if np.array_equal(q, np.array([0, 0, 0, 0])):
            self.hopperdata.theta_datas.append(None)
            # print("跳过")
        else:
            r = R.from_quat(q)
            # 将旋转矩阵转换为欧拉角
            euler_angles = r.as_euler('zyx', degrees=True)  # 这里假设是绕z、y、x轴的欧拉角
            self.hopperdata.theta_datas.append(euler_angles[1]+90)            
        id=0
        result = np.zeros((6,1), dtype=np.float64)
        mj.mj_contactForce(self.model, self.data, id, result);
        self.hopperdata.ground_force_x_sensor_datas.append(result[0,0])
        self.hopperdata.ground_force_y_sensor_datas.append(result[1,0])
        self.hopperdata.ground_force_z_sensor_datas.append(result[2,0])
        
    def simulate(self):
        self.start_time = self.data.time
        while not glfw.window_should_close(self.window):
            
            self.bind_data()    # 收集数据
            
            current_simstart = self.data.time   # 当前一帧的开始时间
            while (self.data.time - current_simstart < 1.0/self.Hz):
                mj.mj_step(self.model, self.data)            
            if self.data.time >= self.simend:
                break
            
            # get framebuffer viewport
            viewport_width, viewport_height = glfw.get_framebuffer_size(
                self.window)
            viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)

            # Update scene and render
            self.cam.lookat[0] = self.data.qpos[0]
            mj.mjv_updateScene(self.model, self.data, self.opt, None, self.cam,
                               mj.mjtCatBit.mjCAT_ALL.value, self.scene)
            mj.mjr_render(viewport, self.scene, self.context)
            # swap OpenGL buffers (blocking call due to v-sync)
            glfw.swap_buffers(self.window)
            # process pending GUI events, call GLFW callbacks
            glfw.poll_events()
            if self.is_plot_data:
                self.hopperdata.plot_data()         
        glfw.terminate()
    
    def initial_state(self):
        # self.model.body_pos[1,2] = 3.5
        # self.cam.lookat[0] = self.data.qpos[0]
        mj.mj_resetDataKeyframe(self.model, self.data, 0)
        mj.mj_step(self.model, self.data)
        # 可以通过 self.model.body_pos 来改变物体的初始位置
        # print(f"body_pos\n{self.model.body_pos}")
        print(self.data.qpos)
        
        while not glfw.window_should_close(self.window):
            viewport_width, viewport_height = glfw.get_framebuffer_size(
                self.window)
            viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)
            mj.mjv_updateScene(self.model, self.data, self.opt, None, self.cam,
                                mj.mjtCatBit.mjCAT_ALL.value, self.scene)
            mj.mjr_render(viewport, self.scene, self.context)
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        glfw.terminate()
        
    def set_position_servo(self, actuator_no, kp):
        self.model.actuator_gainprm[actuator_no, 0] = kp
        self.model.actuator_biasprm[actuator_no, 1] = -kp
    
    def set_velocity_servo(self, actuator_no, kv):
        self.model.actuator_gainprm[actuator_no, 0] = kv
        self.model.actuator_biasprm[actuator_no, 2] = -kv

def main():
    xml_path = "./xml/hopper1/scene2.xml"
    i = 0
    tendon_stiffness_data = []
    max_height_data = []
    while True:
        sim = Hopper1(xml_path)
        sim.simend = 2
        sim.reset()
        sim.model.tendon_stiffness[0] = sim.model.tendon_stiffness[0] + 100
        print(sim.model.tendon_stiffness)
        tendon_stiffness_data.append(sim.model.tendon_stiffness[0])
        sim.simulate()
        i += 1
        if (i>50):
            break
    print(tendon_stiffness_data)
    print(max_height_data)
    
    # sim.initial_state()

if __name__ == "__main__":
    main()
