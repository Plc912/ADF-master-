"""
测试文件分析功能
"""

import requests
import json
import time
import os


def test_file_analysis():
    """测试文件分析功能"""
    
    # 检查文件是否存在
    file_path = r"E:\software\MCP_Proj\100MCP\adf-master\OpenSSH_2k.log_structured.csv"
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    print(f"✅ 文件存在: {file_path}")
    
    # 服务器URL
    base_url = "http://localhost:2230"
    
    print("\n🔍 测试文件分析功能...")
    
    # 测试分析请求
    analysis_request = {
        "file_path": file_path,
        "file_type": "csv",
        "analysis_type": "log_analysis",
        "time_window": "1min",
        "aggregation_method": "count",
        "regression": "c",
        "max_lags": 10,
        "lags_method": "aic",
        "save_model": True,
        "model_name": "test_openssh_analysis"
    }
    
    try:
        print("📤 发送分析请求...")
        response = requests.post(f"{base_url}/tools/adf_analyze_file", json=analysis_request, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功!")
            print(f"   状态: {result['status']}")
            print(f"   任务ID: {result['task_id']}")
            
            # 等待任务完成
            task_id = result['task_id']
            print(f"\n⏳ 等待任务完成...")
            
            max_wait_time = 60  # 最大等待60秒
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                time.sleep(2)
                
                try:
                    task_response = requests.post(f"{base_url}/tools/get_task", json={"task_id": task_id}, timeout=5)
                    
                    if task_response.status_code == 200:
                        task_info = task_response.json()
                        progress = task_info.get('progress', 0)
                        status = task_info.get('status', 'unknown')
                        
                        print(f"   进度: {progress:.1%} - 状态: {status}")
                        
                        if status == 'succeeded':
                            print("\n🎉 分析完成!")
                            print_analysis_result(task_info['result'])
                            return True
                        elif status == 'failed':
                            print(f"\n❌ 分析失败: {task_info.get('error', '未知错误')}")
                            return False
                    else:
                        print(f"   获取任务状态失败: {task_response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"   请求异常: {e}")
                    continue
            
            print(f"\n⏰ 等待超时 ({max_wait_time}秒)")
            return False
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保MCP服务器正在运行 (python adf_mcp_server.py)")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


def print_analysis_result(result):
    """打印分析结果"""
    print("\n" + "=" * 60)
    print("📊 分析结果")
    print("=" * 60)
    
    if result.get('status') == 'success':
        print(f"✅ 分析成功!")
        print(f"📁 文件路径: {result.get('file_path', 'N/A')}")
        print(f"🔍 分析类型: {result.get('analysis_type', 'N/A')}")
        
        # 数据摘要
        data_summary = result.get('data_summary', {})
        print(f"\n📈 数据摘要:")
        print(f"   时间序列长度: {data_summary.get('time_series_length', 'N/A')}")
        
        time_range = data_summary.get('time_range', {})
        if time_range:
            print(f"   时间范围: {time_range.get('start', 'N/A')} 到 {time_range.get('end', 'N/A')}")
        
        value_range = data_summary.get('value_range', {})
        if value_range:
            print(f"   数值范围: {value_range.get('min', 'N/A')} 到 {value_range.get('max', 'N/A')}")
            print(f"   平均值: {value_range.get('mean', 'N/A'):.2f}")
            print(f"   标准差: {value_range.get('std', 'N/A'):.2f}")
        
        # ADF检验结果
        adf_result = result.get('adf_result', {})
        print(f"\n🔬 ADF检验结果:")
        print(f"   统计量: {adf_result.get('statistic', 'N/A'):.6f}")
        print(f"   p值: {adf_result.get('p_value', 'N/A'):.6f}")
        print(f"   是否平稳: {'是' if adf_result.get('is_stationary', False) else '否'}")
        print(f"   滞后阶数: {adf_result.get('lags_used', 'N/A')}")
        print(f"   回归类型: {adf_result.get('regression_description', 'N/A')}")
        print(f"   滞后方法: {adf_result.get('lags_method_description', 'N/A')}")
        
        # 结果解释
        interpretation = result.get('interpretation', '')
        if interpretation:
            print(f"\n📝 结果解释:")
            print(f"   {interpretation}")
        
        # 建议
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 分析建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # 模型信息
        model_path = result.get('model_path')
        if model_path:
            print(f"\n💾 模型已保存: {model_path}")
            if os.path.exists(model_path):
                print(f"   ✅ 模型文件存在")
            else:
                print(f"   ❌ 模型文件不存在")
    else:
        print(f"❌ 分析失败: {result.get('error', '未知错误')}")


def test_server_connection():
    """测试服务器连接"""
    base_url = "http://localhost:2230"
    
    try:
        print("🔌 测试服务器连接...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ 服务器连接成功: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ 服务器连接失败: 请启动MCP服务器")
        print("   启动命令: python adf_mcp_server.py")
        return False
    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False


if __name__ == "__main__":
    print("🧪 ADF文件分析功能测试")
    print("=" * 60)
    
    # 测试服务器连接
    if not test_server_connection():
        exit(1)
    
    # 测试文件分析
    success = test_file_analysis()
    
    if success:
        print("\n🎉 所有测试通过!")
    else:
        print("\n❌ 测试失败!")
