# ADF检验MCP工具

## 📊 项目简介

ADF检验MCP工具是一个基于FastMCP框架的时间序列平稳性检验工具，使用经典的统计学方法进行异常检测。该工具无需训练数据，可以直接对任意长度的时间序列数据进行即时检测。

## 🔍 检测能力

### 支持的数据类型

1. **日志数据**
   - OpenSSH日志
   - 系统日志
   - 应用程序日志
   - Web服务器日志

2. **时间序列数据**
   - 金融数据（股价、汇率等）
   - 传感器数据（温度、压力、流量等）
   - 网络流量数据
   - 用户行为数据

3. **业务数据**
   - 销售数据
   - 用户活跃度数据
   - 服务器性能指标
   - 设备运行状态数据

### 检测的异常类型

- **趋势异常**：检测数据是否存在异常趋势
- **平稳性异常**：判断时间序列是否平稳
- **周期性异常**：识别异常的周期性模式
- **突变异常**：检测数据的突然变化

## 🚀 快速开始

### 环境要求

- **Python版本**：3.8+
- **操作系统**：Windows/Linux/macOS
- **内存要求**：至少2GB RAM
- **存储空间**：至少100MB可用空间

### 依赖包

```bash
fastmcp>=2.12.0      # FastMCP框架
numpy>=1.21.0        # 数值计算
pandas>=1.3.0        # 数据处理
scipy>=1.7.0         # 科学计算
statsmodels>=0.13.0  # 统计模型
```

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd adf-master
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   python adf_mcp_server.py
   ```

## 🔧 服务配置

### 服务端口

- **默认端口**：2230
- **服务地址**：http://127.0.0.1:2230/sse
- **传输协议**：SSE (Server-Sent Events)

### 启动服务

```bash
# 使用默认端口2230启动
python adf_mcp_server.py

# 服务启动后会显示：
# 🖥️  Server name:     adf-mcp
# 📦 Transport:       SSE
# 🔗 Server URL:      http://127.0.0.1:2230/sse
# 🏎️  FastMCP version: 2.12.2
```

### 服务状态检查

```bash
# 检查端口是否被占用
netstat -an | findstr :2230

# 停止服务（如果需要）
# 在服务运行的终端按 Ctrl+C
```

## 🛠️ 核心功能

### 1. 直接检测功能

- **单个序列检测**：对单个时间序列进行ADF检验
- **批量检测**：同时检测多个时间序列
- **文件分析**：直接分析CSV/TXT文件
- **结果解释**：提供详细的统计结果解释

### 2. 支持的文件格式

- **CSV文件**：支持逗号分隔值格式
- **TXT文件**：支持自定义分隔符的文本文件
- **数据要求**：至少包含10个数据点

### 3. 检测参数

- **回归类型**：无常数项(n)、有常数项(c)、有常数项和趋势项(ct)
- **滞后选择**：AIC准则、BIC准则、t统计量
- **显著性水平**：1%、5%、10%

## 📋 使用方法

### 1. 基础检测

```python
from adf_mcp.adf_core import ADFTester
import numpy as np

# 创建检验器
tester = ADFTester()

# 准备数据
data = np.random.normal(0, 1, 100).tolist()

# 执行检测
result = tester.test_stationarity(data)
print(f"是否平稳: {result['is_stationary']}")
print(f"p值: {result['p_value']:.6f}")
```

### 2. 文件分析

```python
import requests

# 分析CSV文件
response = requests.post("http://localhost:2230/tools/adf_analyze_file", json={
    "csv": "path/to/your/data.csv",
    "analysis_type": "log_analysis"
})

print(response.json())
```

### 3. 批量检测

```python
# 批量检测多个序列
data_dict = {
    "序列1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "序列2": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
    "序列3": [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
}

response = requests.post("http://localhost:2230/tools/adf_batch_test", json={
    "data_dict": data_dict,
    "regression": "c",
    "max_lags": 5
})
```

## 🎯 AI调用示例

### 自然语言请求

> "请帮我分析OpenSSH日志数据，检测日志活动的时间序列平稳性"

### AI自动调用

AI会自动识别您的请求并调用相应的MCP工具：

```json
{
  "tool": "adf_analyze_file",
  "parameters": {
    "csv": "E:\\software\\MCP__Proj\\100MCP\\adf-master\\OpenSSH_2k.log_structured.csv",
    "analysis_type": "log_analysis",
    "regression": "c",
    "max_lags": 10,
    "lags_method": "aic"
  }
}
```

## 📊 输出结果

### 检测结果格式

```json
{
  "status": "success",
  "analysis_type": "log_analysis",
  "file_path": "data.csv",
  "data_summary": {
    "time_series_length": 250,
    "value_range": {
      "min": 0,
      "max": 15,
      "mean": 8.0,
      "std": 3.2
    }
  },
  "adf_result": {
    "statistic": -2.345678,
    "p_value": 0.123456,
    "is_stationary": false,
    "lags_used": 5,
    "regression_description": "常数项",
    "lags_method_description": "AIC准则"
  },
  "interpretation": "在5%显著性水平下，时间序列是非平稳的...",
  "recommendations": [
    "时间序列是非平稳的，建议进行差分处理",
    "可以考虑使用ARIMA模型进行建模"
  ]
}
```

### 结果解释

- **is_stationary**: true表示平稳，false表示非平稳
- **p_value**: p值小于0.05表示平稳，大于等于0.05表示非平稳
- **statistic**: ADF统计量，绝对值越大越倾向于平稳
- **recommendations**: 基于结果的分析建议

## 🔧 技术架构

### 核心组件

- **ADFTester**: ADF检验核心算法实现
- **FastMCP**: 异步任务处理框架
- **statsmodels**: 统计模型计算引擎
- **pandas**: 数据处理和文件读取

### 处理流程

1. **数据输入**：接收文件路径或数据数组
2. **数据预处理**：清洗和验证数据
3. **ADF检验**：执行统计检验
4. **结果分析**：生成统计结果和建议
5. **结果输出**：返回详细的分析报告

## 🎉 项目优势

### 1. 无需训练
- 基于经典统计学理论
- 无需训练数据
- 即时检测结果

### 2. 高性能
- 检测时间：1-3毫秒
- 支持大文件处理
- 异步任务处理

### 3. 易用性
- 自然语言调用
- 详细的结果解释
- 完整的错误处理

### 4. 扩展性
- 模块化设计
- 易于添加新功能
- 支持多种数据格式

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 检查服务是否正常启动
2. 确认端口2230未被占用
3. 验证数据文件格式是否正确
4. 查看错误日志获取详细信息