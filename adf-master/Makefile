# ADF检验MCP工具 Makefile

.PHONY: help install install-dev test clean run-server run-example

help:  ## 显示帮助信息
	@echo "ADF检验MCP工具 - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装项目依赖
	pip install -e .

install-dev:  ## 安装开发依赖
	pip install -e ".[dev]"

test:  ## 运行测试
	python test_adf_mcp.py

clean:  ## 清理临时文件
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-server:  ## 启动MCP服务器
	python adf_mcp_server.py

run-example:  ## 运行使用示例
	python example_usage.py

dev-setup: install-dev  ## 设置开发环境
	@echo "开发环境设置完成！"
	@echo "运行 'make test' 来测试"
	@echo "运行 'make run-server' 来启动服务器"