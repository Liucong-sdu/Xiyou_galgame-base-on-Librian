import subprocess
import sys
from tqdm import tqdm
import time

def run_script(script_name, description):
    # 显示带边框的启动提示
    print(f"\n╭{'─' * (len(description) + 2)}╮")
    print(f"│ {description} │")
    print(f"╰{'─' * (len(description) + 2)}╯")
    
    # 创建进度条
    pbar = tqdm(total=100, desc=script_name, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')
    
    try:
        # 启动子进程
        process = subprocess.Popen(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # 实时读取输出并更新进度
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                # 假设脚本输出进度百分比（例如：PROGRESS: 50）
                if "PROGRESS:" in output:
                    progress = int(output.split(":")[1].strip())
                    pbar.n = progress
                    pbar.refresh()
                sys.stdout.write(output)
                sys.stdout.flush()
        
        pbar.n = 100
        pbar.close()
        print(f"{script_name} 完成！✓")
        print("─" * 50)
        
    except Exception as e:
        pbar.close()
        print(f"执行 {script_name} 时出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # 检查tqdm是否安装
    try:
        from tqdm import tqdm
    except ImportError:
        print("正在安装tqdm库...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    
    # 运行第一个脚本
    run_script("process_text.py", "正在处理文本数据")
    
    # 运行第二个脚本
    run_script("process_script.py", "正在处理脚本数据")
    
    print("\n所有任务已完成！✓")
