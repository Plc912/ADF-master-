"""
ADF检验MCP服务器
基于FastMCP框架的ADF（Augmented Dickey-Fuller）检验工具
专注于统计学检测，无需训练数据
"""

from typing import Optional, Dict, Any, List
import threading
import uuid
import os
import datetime
import traceback
import numpy as np
import pandas as pd
from fastmcp import FastMCP

from adf_mcp.adf_core import ADFTester

# 创建FastMCP实例
mcp = FastMCP("adf-mcp", debug=True, log_level="DEBUG")

# 创建ADF检验器实例
adf_tester = ADFTester()

# ---- 后台任务基础设施 ----
TASKS: Dict[str, Dict[str, Any]] = {}
TASKS_LOCK = threading.Lock()

# 并发控制
MAX_CONCURRENT = int(os.getenv("ADF_MAX_CONCURRENT", "2"))
TASKS_SEM = threading.Semaphore(MAX_CONCURRENT)

# 中国标准时间 (UTC+08:00)
TZ_CN = datetime.timezone(datetime.timedelta(hours=8))

def _now_iso() -> str:
    return datetime.datetime.now(TZ_CN).isoformat()

def _create_task(task_type: str, params: Dict[str, Any]) -> str:
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "type": task_type,
        "params": params,
        "status": "queued",
        "progress": 0.0,
        "created_at": _now_iso(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
        "traceback": None,
    }
    with TASKS_LOCK:
        TASKS[task_id] = task
    return task_id

def _set_task(task_id: str, **updates):
    with TASKS_LOCK:
        if task_id in TASKS:
            TASKS[task_id].update(**updates)

def _get_task(task_id: str) -> Dict[str, Any]:
    with TASKS_LOCK:
        return dict(TASKS.get(task_id, {}))

def _list_tasks() -> List[Dict[str, Any]]:
    with TASKS_LOCK:
        return [dict(t) for t in TASKS.values()]

def _start_background(target, *args):
    t = threading.Thread(target=target, args=args, daemon=True)
    t.start()
    return t


# 工具：adf_test
# 作用：对单个时间序列进行ADF检验
@mcp.tool()
def adf_test(
    data: List[float],
    regression: str = "c",
    max_lags: int = 10,
    lags_method: str = "aic"
) -> Dict[str, Any]:
    """
    对单个时间序列进行ADF平稳性检验。
    
    参数:
    - data: List[float] - 时间序列数据
    - regression: str - 回归类型，默认为'c'
    - max_lags: int - 最大滞后阶数，默认为10
    - lags_method: str - 滞后选择方法，默认为'aic'
    
    返回:
    - dict: 检验结果
    """
    try:
        if not data or len(data) < 10:
            return {"status": "failed", "error": "数据长度必须至少为10个观测值"}
        
        if regression not in ['n', 'c', 'ct']:
            return {"status": "failed", "error": "回归类型必须是 'n', 'c', 'ct' 之一"}
        
        if lags_method not in ['aic', 'bic', 't-stat']:
            return {"status": "failed", "error": "滞后选择方法必须是 'aic', 'bic', 't-stat' 之一"}
        
        result = adf_tester.test_stationarity(data, regression, max_lags, lags_method)
        return {"status": "success", "result": result}
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# 工具：adf_batch_test
# 作用：批量检验多个时间序列
@mcp.tool()
def adf_batch_test(
    data_dict: Dict[str, List[float]],
    regression: str = "c",
    max_lags: int = 10,
    lags_method: str = "aic"
) -> Dict[str, Any]:
    """
    批量检验多个时间序列的平稳性。
    
    参数:
    - data_dict: Dict[str, List[float]] - 包含多个时间序列的字典
    - regression: str - 回归类型，默认为'c'
    - max_lags: int - 最大滞后阶数，默认为10
    - lags_method: str - 滞后选择方法，默认为'aic'
    
    返回:
    - dict: 批量检验结果
    """
    try:
        if not data_dict:
            return {"status": "failed", "error": "数据字典不能为空"}
        
        results = {}
        for name, data in data_dict.items():
            try:
                if len(data) < 10:
                    results[name] = {"status": "failed", "error": "数据长度必须至少为10个观测值"}
                    continue
                
                result = adf_tester.test_stationarity(data, regression, max_lags, lags_method)
                results[name] = {"status": "success", "result": result}
            except Exception as e:
                results[name] = {"status": "failed", "error": str(e)}
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# 工具：adf_interpret
# 作用：解释ADF检验结果
@mcp.tool()
def adf_interpret(
    statistic: float,
    p_value: float,
    critical_values: Dict[str, float],
    regression: str = "c"
) -> Dict[str, Any]:
    """
    解释ADF检验结果。
    
    参数:
    - statistic: float - ADF统计量
    - p_value: float - p值
    - critical_values: Dict[str, float] - 临界值
    - regression: str - 回归类型
    
    返回:
    - dict: 解释结果
    """
    try:
        interpretation = adf_tester.get_interpretation({
            "statistic": statistic,
            "p_value": p_value,
            "critical_values": critical_values,
            "regression_type": regression
        })
        
        return {"status": "success", "interpretation": interpretation}
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# 工具：adf_analyze_file
# 作用：通过文件路径直接分析数据（AI可直接调用）
@mcp.tool()
def adf_analyze_file(
    csv: Optional[str] = None,
    txt: Optional[str] = None,
    timestamp_col: str = "Date",
    value_col: str = "EventId",
    delimiter: str = " ",
    has_header: bool = True,
    regression: str = "c",
    max_lags: int = 10,
    lags_method: str = "aic",
    analysis_type: str = "log_analysis"
) -> Dict[str, Any]:
    """
    通过文件路径直接分析数据并执行ADF检验（AI可直接调用）。
    
    参数:
    - csv: str, optional - CSV文件路径，与txt二选一
    - txt: str, optional - TXT文件路径，与csv二选一
    - timestamp_col: str - 时间戳列名（CSV文件）
    - value_col: str - 数值列名（CSV文件）
    - delimiter: str - 分隔符（TXT文件）
    - has_header: bool - 是否有标题行（TXT文件）
    - regression: str - 回归类型，默认为'c'
    - max_lags: int - 最大滞后阶数，默认为10
    - lags_method: str - 滞后选择方法，默认为'aic'
    - analysis_type: str - 分析类型 ("log_analysis", "full", "quick")
    
    返回:
    - dict: {"status": "queued", "task_id": str, "type": "adf_analyze_file"}
    """
    params = {
        "csv": csv,
        "txt": txt,
        "timestamp_col": timestamp_col,
        "value_col": value_col,
        "delimiter": delimiter,
        "has_header": has_header,
        "regression": regression,
        "max_lags": max_lags,
        "lags_method": lags_method,
        "analysis_type": analysis_type,
    }
    
    # 参数验证
    if (csv and txt) or (not csv and not txt):
        msg = "请指定csv或txt文件路径中的一个"
        task_id = _create_task("adf_analyze_file", params)
        _set_task(task_id, status="failed", error=msg, completed_at=_now_iso())
        return {"status": "failed", "task_id": task_id, "type": "adf_analyze_file", "error": msg}
    
    # 检查文件是否存在
    file_path = csv or txt
    if not os.path.exists(file_path):
        msg = f"文件不存在: {file_path}"
        task_id = _create_task("adf_analyze_file", params)
        _set_task(task_id, status="failed", error=msg, completed_at=_now_iso())
        return {"status": "failed", "task_id": task_id, "type": "adf_analyze_file", "error": msg}
    
    task_id = _create_task("adf_analyze_file", params)
    _start_background(_analyze_file_worker, task_id, params)
    return {"status": "queued", "task_id": task_id, "type": "adf_analyze_file"}


def _analyze_file_worker(task_id: str, params: Dict[str, Any]):
    """文件分析后台工作线程"""
    try:
        with TASKS_SEM:
            _set_task(task_id, status="running", started_at=_now_iso(), progress=0.1)
            
            csv_path = params.get("csv")
            txt_path = params.get("txt")
            analysis_type = params["analysis_type"]
            
            # 确定文件路径和类型
            if csv_path:
                file_path = csv_path
                file_type = "csv"
            else:
                file_path = txt_path
                file_type = "txt"
            
            _set_task(task_id, progress=0.2)
            
            # 读取数据
            if file_type == "csv":
                df = pd.read_csv(file_path)
                
                # 检查必需的列
                if params["timestamp_col"] not in df.columns:
                    _set_task(task_id, status="failed", error=f"时间戳列 '{params['timestamp_col']}' 不存在", completed_at=_now_iso())
                    return
                
                if params["value_col"] not in df.columns:
                    _set_task(task_id, status="failed", error=f"数值列 '{params['value_col']}' 不存在", completed_at=_now_iso())
                    return
                
                # 提取时间序列数据
                if analysis_type == "log_analysis":
                    # 日志数据分析：按时间窗口聚合事件计数
                    df[params["timestamp_col"]] = pd.to_datetime(df[params["timestamp_col"]])
                    df = df.set_index(params["timestamp_col"])
                    time_series = df.resample('1min').size().values
                else:
                    # 标准分析：直接使用数值列
                    time_series = df[params["value_col"]].values
            else:
                # TXT文件处理
                data = []
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    if params["has_header"]:
                        lines = lines[1:]  # 跳过标题行
                    
                    for line in lines:
                        values = line.strip().split(params["delimiter"])
                        for value in values:
                            try:
                                data.append(float(value))
                            except ValueError:
                                continue
                
                time_series = np.array(data)
            
            _set_task(task_id, progress=0.5)
            
            # 数据验证
            if len(time_series) < 10:
                _set_task(task_id, status="failed", error="数据长度必须至少为10个观测值", completed_at=_now_iso())
                return
            
            # 移除NaN值
            time_series = time_series[~np.isnan(time_series)]
            
            if len(time_series) < 10:
                _set_task(task_id, status="failed", error="有效数据长度必须至少为10个观测值", completed_at=_now_iso())
                return
            
            _set_task(task_id, progress=0.7)
            
            # 执行ADF检验
            adf_result = adf_tester.test_stationarity(
                time_series,
                regression=params["regression"],
                max_lags=params["max_lags"],
                lags_method=params["lags_method"]
            )
            
            _set_task(task_id, progress=0.9)
            
            # 构建结果
            result = {
                "status": "success",
                "analysis_type": analysis_type,
                "file_path": file_path,
                "file_type": file_type,
                "data_summary": {
                    "time_series_length": len(time_series),
                    "value_range": {
                        "min": float(np.min(time_series)),
                        "max": float(np.max(time_series)),
                        "mean": float(np.mean(time_series)),
                        "std": float(np.std(time_series))
                    }
                },
                "adf_result": adf_result,
                "interpretation": adf_tester.get_interpretation(adf_result),
                "recommendations": _generate_recommendations(adf_result, len(time_series))
            }
            
            _set_task(task_id, status="succeeded", progress=1.0, completed_at=_now_iso(), result=result)
            
    except Exception as ex:
        _set_task(task_id, status="failed", completed_at=_now_iso(), 
                 error=str(ex), traceback=traceback.format_exc())


def _generate_recommendations(adf_result: Dict, data_length: int) -> List[str]:
    """生成分析建议"""
    recommendations = []
    
    if adf_result["is_stationary"]:
        recommendations.append("时间序列是平稳的，适合进行ARIMA建模")
        recommendations.append("可以考虑进行短期预测")
    else:
        recommendations.append("时间序列是非平稳的，建议进行差分处理")
        recommendations.append("可以考虑使用ARIMA模型进行建模")
    
    if data_length < 100:
        recommendations.append("数据量较少，建议收集更多数据以提高分析可靠性")
    
    return recommendations


# 工具：list_tasks
# 作用：查询当前所有后台任务
@mcp.tool()
def list_tasks() -> Dict[str, Any]:
    """
    列出所有后台任务。
    
    返回:
    - dict: 任务列表
    """
    tasks = _list_tasks()
    return {"count": len(tasks), "tasks": tasks}


# 工具：get_task
# 作用：查询指定任务的状态、进度与结果
@mcp.tool()
def get_task(task_id: str) -> Dict[str, Any]:
    """
    获取指定任务的详细状态。
    
    参数:
    - task_id: str - 任务ID
    
    返回:
    - dict: 任务详细信息
    """
    return _get_task(task_id)


if __name__ == "__main__":
    # 启动SSE传输的MCP服务器，默认端口2230
    mcp.run(transport="sse", port=2230)