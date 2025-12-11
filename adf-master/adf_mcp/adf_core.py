"""
ADF检验核心功能实现

提供ADF检验的核心算法实现，包括统计量计算、p值计算等。
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Union, List
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.ar_model import AutoReg
import warnings

# 忽略statsmodels的警告
warnings.filterwarnings('ignore', category=UserWarning, module='statsmodels')


class ADFTester:
    """ADF检验器类"""
    
    def __init__(self):
        """初始化ADF检验器"""
        self.regression_types = {
            'n': '无常数项',
            'c': '有常数项', 
            'ct': '有常数项和趋势项'
        }
        
        self.lags_methods = {
            'aic': 'Akaike信息准则',
            'bic': 'Bayesian信息准则',
            't-stat': 't统计量'
        }
    
    def test_stationarity(
        self,
        data: Union[List[float], np.ndarray, pd.Series],
        regression: str = 'c',
        max_lags: int = 10,
        lags_method: str = 'aic'
    ) -> Dict[str, Any]:
        """
        执行ADF平稳性检验
        
        Args:
            data: 时间序列数据
            regression: 回归类型 ('n', 'c', 'ct')
            max_lags: 最大滞后阶数
            lags_method: 滞后选择方法 ('aic', 'bic', 't')
            
        Returns:
            包含检验结果的字典
        """
        # 数据预处理
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        elif isinstance(data, pd.Series):
            data = data.values
        
        # 移除NaN值
        data = data[~np.isnan(data)]
        
        if len(data) < 10:
            raise ValueError("数据长度必须至少为10个观测值")
        
        # 验证参数
        if regression not in self.regression_types:
            raise ValueError(f"回归类型必须是 {list(self.regression_types.keys())} 之一")
        
        if lags_method not in self.lags_methods:
            raise ValueError(f"滞后选择方法必须是 {list(self.lags_methods.keys())} 之一")
        
        if max_lags < 0:
            raise ValueError("最大滞后阶数必须非负")
        
        # 限制最大滞后阶数
        max_lags = min(max_lags, len(data) // 2 - 1)
        
        try:
            # 执行ADF检验
            result = adfuller(
                data,
                regression=regression,
                maxlag=max_lags,
                autolag=lags_method
            )
            
            # 解析结果
            statistic = result[0]
            p_value = result[1]
            critical_values = result[4]
            lags_used = result[2]
            
            # 判断是否平稳（基于5%显著性水平）
            is_stationary = bool(p_value < 0.05)
            
            # 构建结果
            result_dict = {
                'statistic': float(statistic),
                'p_value': float(p_value),
                'critical_values': {
                    '1%': float(critical_values['1%']),
                    '5%': float(critical_values['5%']),
                    '10%': float(critical_values['10%'])
                },
                'is_stationary': is_stationary,
                'lags_used': int(lags_used),
                'regression_type': regression,
                'regression_description': self.regression_types[regression],
                'lags_method': lags_method,
                'lags_method_description': self.lags_methods[lags_method],
                'data_length': len(data),
                'max_lags': max_lags
            }
            
            return result_dict
            
        except Exception as e:
            raise RuntimeError(f"ADF检验执行失败: {str(e)}")
    
    def get_interpretation(self, result: Dict[str, Any]) -> str:
        """
        获取检验结果的解释
        
        Args:
            result: ADF检验结果字典
            
        Returns:
            结果解释文本
        """
        statistic = result['statistic']
        p_value = result['p_value']
        is_stationary = result['is_stationary']
        critical_values = result['critical_values']
        
        interpretation = f"""
ADF检验结果解释：

1. 检验统计量: {statistic:.6f}
2. p值: {p_value:.6f}
3. 临界值:
   - 1%显著性水平: {critical_values['1%']:.6f}
   - 5%显著性水平: {critical_values['5%']:.6f}
   - 10%显著性水平: {critical_values['10%']:.6f}

4. 结论: {'时间序列是平稳的' if is_stationary else '时间序列是非平稳的'}
   - 在5%显著性水平下，{'拒绝' if is_stationary else '不能拒绝'}原假设（序列存在单位根）
   - p值 {p_value:.6f} {'<' if p_value < 0.05 else '>'} 0.05

5. 技术细节:
   - 使用的回归类型: {result['regression_description']}
   - 滞后选择方法: {result['lags_method_description']}
   - 实际使用滞后阶数: {result['lags_used']}
   - 数据长度: {result['data_length']}
        """
        
        return interpretation.strip()
    
    def batch_test(
        self,
        data_dict: Dict[str, Union[List[float], np.ndarray, pd.Series]],
        regression: str = 'c',
        max_lags: int = 10,
        lags_method: str = 'aic'
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量执行ADF检验
        
        Args:
            data_dict: 包含多个时间序列的字典
            regression: 回归类型
            max_lags: 最大滞后阶数
            lags_method: 滞后选择方法
            
        Returns:
            包含所有检验结果的字典
        """
        results = {}
        
        for name, data in data_dict.items():
            try:
                results[name] = self.test_stationarity(
                    data, regression, max_lags, lags_method
                )
            except Exception as e:
                results[name] = {
                    'error': str(e),
                    'success': False
                }
        
        return results
