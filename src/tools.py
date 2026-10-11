from langchain_core.tools import tool  # 导入`@tool`装饰器，用它装饰的函数会自动被 LangChain 识别为 Agent 可用工具，函数名、参数、docstring 都会被 LLM 读取
import subprocess  # 子进程
import tempfile  # 临时文件
import os  # 文件操作
import uuid  # 生成唯一文件名，防止保存代码时被覆盖
from .config import Config  # 超时配置


@tool  # 装饰器，把这个函数注册为 LangChain 工具
def execute_python_code(code: str) -> str:
    """
    在独立子进程中执行Python代码并返回运行结果。
    当需要验证生成的代码是否能正常运行、计算结果或调试代码时使用此工具。
    参数:
        code: 要执行的完整Python代码字符串
    """
    # 在独立子进程中执行Python代码并返回运行结果。
    # 当需要验证生成的代码是否能正常运行、计算结果或调试代码时使用此工具。
    tmp_path = None  # 初始化临时文件路径

    # ========== 新增：自动补全print输出 ==========
    code_lines = code.strip().splitlines()
    if code_lines:
        last_line = code_lines[-1].strip()
        # 最后一行不是print、不是赋值、不是空行、不是注释，就自动包print
        if (not last_line.startswith('print')
                and '=' not in last_line
                and last_line
                and not last_line.startswith('#')):
            code_lines[-1] = f'print({last_line})'
            code = '\n'.join(code_lines)
    # ======================================

    try:
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'  # 写模式、后缀加.py、不自动删除，utf-8防止中文乱码
        ) as f:  # 创建临时文件
            f.write(code)  # 把LLM代码写入临时文件
            tmp_path = f.name

        result = subprocess.run(  # 独立子进程中执行
            ['python', tmp_path],  # 相当于在终端启动py
            capture_output=True,  # 捕获stdout、stderr
            text=True,  # true为字符串形式返回，f为字节
            timeout=Config.CODE_TIMEOUT,  # 超时保护
        )

        if result.returncode == 0:  # 成功、失败、超时、兜底
            return f"执行成功\n输出：\n{result.stdout}" if result.stdout.strip() else "执行成功 ，无输出"
        else:
            return f"执行失败（退出码{result.returncode})\n标准输出：\n{result.stdout}\n输出错误：\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return f"执行超时（超过{Config.CODE_TIMEOUT}秒），代码已被强制终止"
    except Exception as e:
        return f"工具内部错误：{str(e)}"
    finally:  # 无论成功失败都执行：清理
        if tmp_path and os.path.exists(tmp_path):  # 文件存在且有路径
            os.unlink(tmp_path)  # 删除



@tool
def save_code_to_file(code: str, filename: str = None) -> str:
    """
    将生成的代码保存到本地output目录下的文件中。
    参数:
        code: 要保存的代码内容
        filename: 文件名（可选，不填则自动生成）
    """
    # 将生成的代码保存到本地output目录
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 创建目录

    if not filename:  # 未指定文件名
        filename = f"code_{uuid.uuid4().hex[:8]}.py"  # uuid的前八位生成文件名，hex去掉连字符

    if not filename.endswith('.py'):  # 忘补py，补py
        filename += '.py'

    file_path = os.path.join(output_dir, filename)  # 拼接路径

    try:
        with open(file_path, "w", encoding='utf-8') as f:  # 写入到某文件
            f.write(code)
        return f"代码已保存到：{file_path}"
    except Exception as e:  # 兜底捕获
        return f"保存失败：{str(e)}"


@tool
def read_file(file_path: str) -> str:
    """
    读取本地文件内容并返回。
    用于查看已生成的代码文件、项目文件或其他文本文件。
    参数:
        file_path: 要读取的文件路径（相对或绝对路径）
    """
    # 查看已生成的文件
    if not os.path.exists(file_path):
        return f"文件不存在：{file_path}"

    if os.path.getsize(file_path) > 100 * 1024:
        return f"文件过大，不读取，防止上下文溢出"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"文件内容（{file_path}）：\n\n{content}"  # 返回时带上文件名
    except UnicodeDecodeError:
        return "无法读取：文件不是utf-8编码文件"
    except Exception as e:
        return f"读取失败：{str(e)}"


def get_tool():  # 工具列表
    return [execute_python_code, save_code_to_file, read_file]
