#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
光纤出射端面模拟 - 最终版本
标准SMF-28光纤 @ 1550nm
"""

import numpy as np
import matplotlib.pyplot as plt
from LightPipes import *

# 字体设置：中文宋体，英文Times New Roman
plt.rcParams['font.serif'] = ['SimSun', 'Times New Roman', 'serif']  # 宋体为中文，Times New Roman为英文
plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Arial Unicode MS']
plt.rcParams['font.family'] = 'serif'  # 使用serif字体族
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10  # 设置默认字体大小

class SMF28Simulator:
    def __init__(self):
        """SMF-28单模光纤模拟器 @ 1550nm"""
        
        # 光纤参数
        self.wavelength = 1550e-9       # 1550nm通信波长
        self.core_radius = 4.5e-6       # 纤芯半径 9μm/2
        self.cladding_radius = 62.5e-6  # 包层半径 125μm/2
        self.na = 0.12                  # 数值孔径 (调整以确保单模)
        
        # 模拟参数
        self.grid_size = 512
        self.physical_size = 500e-6     # 500μm窗口
        
        # 初始化LightPipes
        self.lp = Begin(self.physical_size, self.wavelength, self.grid_size)
        
        # 计算V数和模场直径
        self.v_number = (2 * np.pi * self.core_radius * self.na) / self.wavelength
        self.mfd = self.calculate_mfd()
        
        print(f"SMF-28光纤参数 @ {self.wavelength*1e9:.0f}nm:")
        print(f"  纤芯直径: {self.core_radius*2*1e6:.1f} μm")
        print(f"  V数: {self.v_number:.3f} ({'单模' if self.v_number < 2.405 else '多模'})")
        print(f"  模场直径: {self.mfd*1e6:.1f} μm")
    
    def calculate_mfd(self):
        """计算模场直径"""
        if self.v_number < 2.405:
            w0_over_a = 0.65 + 1.619/self.v_number**1.5 + 2.879/self.v_number**6
            return 2 * w0_over_a * self.core_radius
        else:
            return 2 * self.core_radius
    
    def create_fiber_mode(self):
        """创建单模光纤基模"""
        beam = self.lp
        beam = GaussBeam(beam, self.mfd/2)
        beam = CircAperture(beam, self.cladding_radius)
        return beam
    
    def flat_endface(self, distance=1e-3):
        """平面端面模拟"""
        beam = self.create_fiber_mode()
        beam = Fresnel(beam, distance)
        return beam
    
    def concave_endface(self, curvature_radius=50e-6, aperture_factor=2.0, distance=1e-3):
        """
        凹面端面模拟
        
        Parameters:
        - curvature_radius: 曲率半径 (m)
        - aperture_factor: 凹面孔径 = core_radius * aperture_factor
        - distance: 传播距离 (m)
        """
        beam = self.create_fiber_mode()
        
        # 创建凹面相位掩模
        x = np.linspace(-self.physical_size/2, self.physical_size/2, self.grid_size)
        y = np.linspace(-self.physical_size/2, self.physical_size/2, self.grid_size)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        
        # 凹面孔径
        aperture_radius = self.core_radius * aperture_factor
        
        # 球面相位延迟
        k = 2 * np.pi / self.wavelength
        phase_mask = np.zeros_like(R)
        valid_region = R <= aperture_radius
        phase_mask[valid_region] = k * R[valid_region]**2 / (2 * curvature_radius)
        
        # 应用相位和孔径
        beam = SubPhase(beam, phase_mask)
        beam = CircAperture(beam, aperture_radius)
        beam = Fresnel(beam, distance)
        
        return beam
    
    def analyze_beam(self, beam):
        """分析光束参数"""
        intensity = Intensity(beam)
        
        # 1/e² 光束宽度
        center_idx = self.grid_size // 2
        x_profile = intensity[center_idx, :]
        max_intensity = np.max(intensity)
        threshold = max_intensity / (np.e**2)
        
        x_coords = np.linspace(-self.physical_size/2, self.physical_size/2, self.grid_size)
        x_indices = np.where(x_profile > threshold)[0]
        
        if len(x_indices) > 0:
            beam_width = (x_indices[-1] - x_indices[0]) * self.physical_size / self.grid_size
        else:
            beam_width = 0
        
        return {
            'intensity': intensity,
            'beam_width': beam_width,
            'max_intensity': max_intensity,
            'x_coords': x_coords,
            'x_profile': x_profile
        }
    
    def parameter_study(self):
        """参数研究：曲率半径对光束的影响"""
        
        curvature_radii = np.array([30, 50, 75, 100, 150, 200]) * 1e-6  # μm to m
        distance = 1e-3  # 1mm传播距离
        
        # 计算不同曲率半径的光束宽度
        beam_widths_flat = []
        beam_widths_concave = []
        
        print("\n计算不同曲率半径的影响...")
        for radius in curvature_radii:
            # 平面端面
            flat_beam = self.flat_endface(distance)
            flat_analysis = self.analyze_beam(flat_beam)
            beam_widths_flat.append(flat_analysis['beam_width'])
            
            # 凹面端面
            concave_beam = self.concave_endface(radius, 2.0, distance)
            concave_analysis = self.analyze_beam(concave_beam)
            beam_widths_concave.append(concave_analysis['beam_width'])
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1: 光束宽度对比
        ax1 = axes[0, 0]
        curvature_um = curvature_radii * 1e6
        beam_widths_flat_um = np.array(beam_widths_flat) * 1e6
        beam_widths_concave_um = np.array(beam_widths_concave) * 1e6
        
        ax1.plot(curvature_um, beam_widths_flat_um, 'b-o', linewidth=2, 
                markersize=6, label='平面端面')
        ax1.plot(curvature_um, beam_widths_concave_um, 'r-s', linewidth=2, 
                markersize=6, label='凹面端面')
        
        ax1.set_xlabel('曲率半径 (μm)', fontsize=11)
        ax1.set_ylabel('光束宽度 (μm)', fontsize=11)
        ax1.set_title('光束宽度 vs 曲率半径', fontsize=12, pad=15)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 调整刻度标签，避免重叠
        ax1.tick_params(axis='x', labelsize=9, rotation=45)
        ax1.tick_params(axis='y', labelsize=9)
        
        # 图2: 强度分布对比 (典型曲率半径)
        test_radius = 50e-6
        flat_beam = self.flat_endface(distance)
        concave_beam = self.concave_endface(test_radius, 2.0, distance)
        
        flat_analysis = self.analyze_beam(flat_beam)
        concave_analysis = self.analyze_beam(concave_beam)
        
        extent = [-self.physical_size/2*1e6, self.physical_size/2*1e6,
                 -self.physical_size/2*1e6, self.physical_size/2*1e6]
        
        ax2 = axes[0, 1]
        im1 = ax2.imshow(flat_analysis['intensity'], extent=extent, cmap='hot', aspect='equal')
        ax2.set_title(f'平面端面\n光束宽度: {flat_analysis["beam_width"]*1e6:.1f}μm', 
                     fontsize=11, pad=15)
        ax2.set_xlabel('X (μm)', fontsize=10)
        ax2.set_ylabel('Y (μm)', fontsize=10)
        ax2.tick_params(labelsize=8)
        
        ax3 = axes[1, 0]
        im2 = ax3.imshow(concave_analysis['intensity'], extent=extent, cmap='hot', aspect='equal')
        ax3.set_title(f'凹面端面 (R={test_radius*1e6:.0f}μm)\n光束宽度: {concave_analysis["beam_width"]*1e6:.1f}μm', 
                     fontsize=11, pad=15)
        ax3.set_xlabel('X (μm)', fontsize=10)
        ax3.set_ylabel('Y (μm)', fontsize=10)
        ax3.tick_params(labelsize=8)
        
        # 图4: 径向强度分布对比
        ax4 = axes[1, 1]
        x_coords_um = flat_analysis['x_coords'] * 1e6
        
        flat_profile_norm = flat_analysis['x_profile'] / np.max(flat_analysis['x_profile'])
        concave_profile_norm = concave_analysis['x_profile'] / np.max(concave_analysis['x_profile'])
        
        ax4.plot(x_coords_um, flat_profile_norm, 'b-', linewidth=2, label='平面端面')
        ax4.plot(x_coords_um, concave_profile_norm, 'r--', linewidth=2, label='凹面端面')
        
        ax4.set_xlabel('径向位置 (μm)', fontsize=11)
        ax4.set_ylabel('归一化强度', fontsize=11)
        ax4.set_title('径向强度分布', fontsize=12, pad=15)
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(labelsize=9)
        
        plt.tight_layout(pad=3.0)  # 增加子图间距
        plt.savefig('fiber_simulation_results.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 输出数值结果
        print(f"\n结果分析 (传播距离: {distance*1e3:.1f}mm):")
        print(f"平面端面光束宽度: {beam_widths_flat[-1]*1e6:.1f} μm")
        print(f"凹面端面光束宽度 (R={curvature_radii[-1]*1e6:.0f}μm): {beam_widths_concave[-1]*1e6:.1f} μm")
        print(f"发散增加: {(beam_widths_concave[-1]/beam_widths_flat[-1]-1)*100:.1f}%")
        
        return {
            'curvature_radii': curvature_radii,
            'beam_widths_flat': beam_widths_flat,
            'beam_widths_concave': beam_widths_concave
        }


def main():
    """主程序"""
    print("=== SMF-28光纤出射端面模拟 ===")
    
    # 创建模拟器
    simulator = SMF28Simulator()
    
    # 运行参数研究
    print("\n开始参数研究...")
    results = simulator.parameter_study()
    
    print("\n✅ 模拟完成！生成图片: fiber_simulation_results.png")
    
    # 物理解释
    print("\n📊 物理解释:")
    print("- 凹面端面相当于在光纤出射口添加发散元件")
    print("- 曲率半径越小，发散效果越强")
    print("- 在通信波长1550nm下，效果更加明显")


if __name__ == "__main__":
    main() 