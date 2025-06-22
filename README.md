# Effect of concave fiber end faces with different curvature radii on the output light

# SMF-28光纤出射端面模拟

基于LightPipes的光纤凹面端面效应研究。

## 项目特点

🔬 **标准SMF-28光纤参数**
- 纤芯直径：9μm
- 包层直径：125μm  
- 工作波长：1550nm (通信波长)
- V数 < 2.405 (确保单模传输)

📊 **物理建模**
- 精确的球面相位延迟计算
- 凹面孔径限制效应
- 菲涅尔衍射传播

## 快速开始

### 运行模拟
```bash
# 在conda环境中运行
python run_in_env.py

# 或手动激活环境
conda activate fiber_optics
python fiber_simulation.py
```

### 输出结果
- `fiber_simulation_results.png` - 完整分析图表
- 控制台数值结果

## 文件说明

| 文件 | 说明 |
|------|------|
| `fiber_simulation.py` | 主要模拟代码 |
| `run_in_env.py` | 环境运行脚本 |
| `activate_env.bat` | 环境激活脚本 |
| `requirements.txt` | 依赖包列表 |

## 模拟参数

- **曲率半径范围**：30-200μm
- **传播距离**：1mm
- **凹面孔径**：纤芯半径的2倍
- **网格分辨率**：512×512
- **物理窗口**：100μm×100μm

## 物理原理

凹面端面引入额外的相位延迟：
```
δ = k × R² / (2 × Rc)
```
其中：
- k = 2π/λ (波数)
- R = 径向坐标
- Rc = 曲率半径

## 预期结果

- 凹面端面增加光束发散
- 曲率半径越小，发散越明显
- 在1550nm通信波长下效应更显著

## 环境要求

- Python 3.7+
- LightPipes ≥ 2.1.0
- NumPy, Matplotlib, SciPy

## 致谢

感谢LightPipes团队提供优秀的物理光学模拟工具。 
