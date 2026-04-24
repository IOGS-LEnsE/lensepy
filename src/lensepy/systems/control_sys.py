# -*- coding: utf-8 -*-
import numpy as np
import control as ct
from matplotlib import pyplot as plt

s = ct.TransferFunction.s

class PIDSystem:

    def __init__(self, Kp=1, Ki=0, Kd=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def set_Kp(self, Kp):
        self.Kp = Kp

    def set_Ki(self, Ki):
        self.Ki = Ki

    def set_Kd(self, Kd):
        self.Kd = Kd

    def get_pid(self):
        C = self.Kp + self.Ki / s + self.Kd * s
        return C


class OpenSystem:

    def __init__(self, num=[1], den=[1]):
        self.den = den
        self.num = num

    def set_den(self, den):
        self.den = den

    def set_num(self, num):
        self.num = num

    def get_syst(self):
        S = ct.tf(self.num, self.den)
        return S


class FirstOrder(OpenSystem):

    def __init__(self, G=1, tau=1, stype='low'):
        self.G = G
        self.tau = tau
        if stype == 'low':
            super().__init__([G], [tau, 1])
        else:
            super().__init__([G], [tau, 1])

class SecondOrder(OpenSystem):

    def __init__(self, G=1, w0=1000, m=0.707, stype='low'):
        self.G = G
        self.w0 = w0
        self.m = m
        if stype == 'low':
            super().__init__([G], [(1/self.w0)**2, 2*self.m/self.w0 , 1])
        else:
            super().__init__([G], [(1/self.w0)**2, 2*self.m/self.w0, 1])

if __name__ == '__main__':
    syst1 = FirstOrder(1, 0.1)
    syst2 = SecondOrder(5, 1000, 0.4)
    pid_sys = PIDSystem(0.1, 50, 0)

    C = pid_sys.get_pid()
    G = syst2.get_syst()

    print(G)

    T = ct.feedback(G * C, 1)

    t_vect = np.linspace(0, 0.1, 1000)
    t, y_open = ct.step_response(G, t_vect)
    t, y_loop = ct.step_response(T, t_vect)

    plt.plot(t, y_open, label='open')
    plt.plot(t, y_loop, label='loop')
    plt.legend()
    plt.grid()
    plt.show()