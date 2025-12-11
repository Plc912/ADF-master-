"""
文件分析示例

演示如何通过文件路径直接分析数据。
"""

import requests
import json
import time


def analyze_file_via_api():
    """通过API分析文件"""
    
    # 服务器URL
    base_url = "http://localhost:2230"
    
    print("=" * 60)
    print("通过文件路径分析OpenSSH日志数据")
    print("=" * 60)
    
    # 1. 分析OpenSSH日志数据
    print("\n1. 分析OpenSSH日志数据")
    print("-" * 30)
    
    analysis_request = {
        "file_path": r"E:\software\MCP__Proj\100MCP\adf-master\OpenSSH_2k.log_structured.csv",
        "file_type": "csv",
        "analysis_type": "log_analysis",
        "time_window": "1min",
        "aggregation_method": "count",
        "regression": "c",
        "max_lags": 10,
        "lags_method": "aic",
        "save_model": True,
        "model_name": "openssh_log_analysis"
    }
    
    print(f"发送分析请求...")
    print(f"文件路径: {analysis_request['file_path']}")
    print(f"分析类型: {analysis_request['analysis_type']}")
    
    try:
        response = requests.post(f"{base_url}/tools/adf_analyze_file", json=analysis_request)
        
        if response.status_code == 200:
            result = response.json()
            print(f"请求成功!")
            print(f"任务状态: {result['status']}")
            print(f"任务ID: {result['task_id']}")
            
            # 等待任务完成
            task_id = result['task_id']
            print(f"\n等待任务完成...")
            
            while True:
                time.sleep(2)
                task_response = requests.post(f"{base_url}/tools/get_task", json={"task_id": task_id})
                
                if task_response.status_code == 200:
                    task_info = task_response.json()
                    progress = task_info.get('progress', 0)
                    status = task_info.get('status', 'unknown')
                    
                    print(f"进度: {progress:.1%} - 状态: {status}")
                    
                    if status == 'succeeded':
                        print("\n✅ 分析完成!")
                        print_result(task_info['result'])
                        break
                    elif status == 'failed':
                        print(f"\n❌ 分析失败: {task_info.get('error', '未知错误')}")
                        break
                else:
                    print(f"获取任务状态失败: {task_response.status_code}")
                    break
        else:
            print(f"请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")


def print_result(result):
    """打印分析结果"""
    print("\n" + "=" * 60)
    print("分析结果")
    print("=" * 60)
    
    if result.get('status') == 'success':
        print(f"✅ 分析成功!")
        print(f"文件路径: {result.get('file_path', 'N/A')}")
        print(f"分析类型: {result.get('analysis_type', 'N/A')}")
        
        # 数据摘要
        data_summary = result.get('data_summary', {})
        print(f"\n📊 数据摘要:")
        print(f"  时间序列长度: {data_summary.get('time_series_length', 'N/A')}")
        print(f"  时间范围: {data_summary.get('time_range', {}).get('start', 'N/A')} 到 {data_summary.get('time_range', {}).get('end', 'N/A')}")
        print(f"  数值范围: {data_summary.get('value_range', {}).get('min', 'N/A')} 到 {data_summary.get('value_range', {}).get('max', 'N/A')}")
        print(f"  平均值: {data_summary.get('value_range', {}).get('mean', 'N/A'):.2f}")
        print(f"  标准差: {data_summary.get('value_range', {}).get('std', 'N/A'):.2f}")
        
        # ADF检验结果
        adf_result = result.get('adf_result', {})
        print(f"\n🔍 ADF检验结果:")
        print(f"  统计量: {adf_result.get('statistic', 'N/A'):.6f}")
        print(f"  p值: {adf_result.get('p_value', 'N/A'):.6f}")
        print(f"  是否平稳: {'是' if adf_result.get('is_stationary', False) else '否'}")
        print(f"  滞后阶数: {adf_result.get('lags_used', 'N/A')}")
        print(f"  回归类型: {adf_result.get('regression_description', 'N/A')}")
        print(f"  滞后方法: {adf_result.get('lags_method_description', 'N/A')}")
        
        # 结果解释
        interpretation = result.get('interpretation', '')
        if interpretation:
            print(f"\n📝 结果解释:")
            print(interpretation)
        
        # 建议
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 分析建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # 模型信息
        model_path = result.get('model_path')
        if model_path:
            print(f"\n💾 模型已保存: {model_path}")
    else:
        print(f"❌ 分析失败: {result.get('error', '未知错误')}")


def demonstrate_natural_language_usage():
    """演示自然语言使用方式"""
    print("\n" + "=" * 60)
    print("自然语言使用示例")
    print("=" * 60)
    
    examples = [
        {
            "natural_language": "请帮我分析OpenSSH日志数据，训练一个ADF模型来检测日志活动的时间序列平稳性",
            "api_call": {
                "tool": "adf_analyze_file",
                "parameters": {
                    "file_path": r"E:\software\MCP__Proj\100MCP\adf-master\OpenSSH_2k.log_structured.csv",
                    "analysis_type": "log_analysis",
                    "save_model": True,
                    "model_name": "openssh_analysis"
                }
            }
        },
        {
            "natural_language": "分析这个CSV文件中的时间序列数据，看看是否平稳",
            "api_call": {
                "tool": "adf_analyze_file",
                "parameters": {
                    "file_path": "your_data.csv",
                    "file_type": "csv",
                    "timestamp_col": "timestamp",
                    "value_col": "value",
                    "analysis_type": "full"
                }
            }
        },
        {
            "natural_language": "快速分析这个日志文件，不需要保存模型",
            "api_call": {
                "tool": "adf_analyze_file",
                "parameters": {
                    "file_path": "log_file.txt",
                    "file_type": "txt",
                    "analysis_type": "quick",
                    "save_model": False
                }
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. 自然语言请求:")
        print(f"   \"{example['natural_language']}\"")
        print(f"\n   对应的API调用:")
        print(f"   {json.dumps(example['api_call'], indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    print("ADF文件分析示例")
    
    # 演示自然语言使用方式
    demonstrate_natural_language_usage()
    
    # 实际分析文件（需要先启动服务器）
    print(f"\n注意: 要运行实际分析，请先启动MCP服务器:")
    print(f"python adf_mcp_server.py")
    print(f"\n然后取消下面的注释来运行实际分析:")
    print(f"# analyze_file_via_api()")
    
    # 取消注释来运行实际分析
    # analyze_file_via_api()
