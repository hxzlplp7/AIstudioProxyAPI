import re

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    replacements = {
        # General Status & Dependency Checks
        r'--- Step 1: Check Dependencies ---': r'--- 第一步: 检查依赖 ---',
        r'Checking Python modules:': r'检查 Python 模块:',
        r'✓ Module \'{module_name}\' found.': r'✓ 找到模块 \'{module_name}\'。',
        r'❌ Dependency check failed!': r'❌ 依赖检查失败!',
        r'✅ All launcher dependency checks passed.': r'✅ 所有启动器依赖检查通过。',
        r'Checking and ensuring auth directories exist...': r'检查并确保认证目录存在...',
        r'✓ Active auth directory ready: {ACTIVE_AUTH_DIR}': r'✓ 活动认证目录就绪: {ACTIVE_AUTH_DIR}',
        r'✓ Saved auth directory ready: {SAVED_AUTH_DIR}': r'✓ 已保存认证目录就绪: {SAVED_AUTH_DIR}',
        r'✓ Emergency auth directory ready: {EMERGENCY_AUTH_DIR}': r'✓ 紧急认证目录就绪: {EMERGENCY_AUTH_DIR}',
        
        # Launcher Start/Stop
        r'🚀 Camoufox Launcher Started 🚀': r'🚀 Camoufox 启动器已启动 🚀',
        r'🚀 Camoufox Launcher Main Logic Finished 🚀': r'🚀 Camoufox 启动器主逻辑完成 🚀',
        r'Log level set to: {logging.getLevelName\(logger.getEffectiveLevel\(\)\)}': r'日志级别设置为: {logging.getLevelName(logger.getEffectiveLevel())}',
        r'Log file path: {LAUNCHER_LOG_FILE_PATH}': r'日志文件路径: {LAUNCHER_LOG_FILE_PATH}',
        r'--- Select Launch Mode \(not specified via args\) ---': r'--- 选择启动模式 (未通过参数指定) ---',
        r'  Read default launch mode from \.env: {env_launch_mode} -> {default_mode_from_env}': r'  从 .env 读取默认启动模式: {env_launch_mode} -> {default_mode_from_env}',
        r'Invalid input \'{user_mode_choice}\' or timeout, using default mode: {final_launch_mode} mode': r'无效输入 \'{user_mode_choice}\' 或超时，使用默认模式: {final_launch_mode} 模式',
        r'Final selected launch mode: {final_launch_mode\.replace\(\'_\', \' \'\)} mode': r'最终选择的启动模式: {final_launch_mode.replace(\'_\', \' \')} 模式',
        r'Unrecognized system \'{current_system_for_camoufox}\'\. Camoufox OS simulation defaulting to: {simulated_os_for_camoufox}': r'未识别的系统 \'{current_system_for_camoufox}\'。Camoufox 操作系统模拟默认为: {simulated_os_for_camoufox}',
        r'Based on system \'{current_system_for_camoufox}\', Camoufox OS simulation auto-set to: {simulated_os_for_camoufox}': r'基于系统 \'{current_system_for_camoufox}\', Camoufox 操作系统模拟自动设置为: {simulated_os_for_camoufox}',
        
        # Ports & Processes
        r'--- Step 2: Check if FastAPI server target port \({server_target_port}\) is in use ---': r'--- 第二步: 检查 FastAPI 服务器目标端口 ({server_target_port}) 是否被占用 ---',
        r'✅ Port {server_target_port} \(host {uvicorn_bind_host}\) is currently available.': r'✅ 端口 {server_target_port} (主机 {uvicorn_bind_host}) 目前可用。',
        r'❌ Port {server_target_port} \(host {uvicorn_bind_host}\) currently in use.': r'❌ 端口 {server_target_port} (主机 {uvicorn_bind_host}) 目前被占用。',
        r'✅ Port {server_target_port} \(host {uvicorn_bind_host}\) is now available.': r'✅ 端口 {server_target_port} (主机 {uvicorn_bind_host}) 现已可用。',
        r'❌ Port {server_target_port} \(host {uvicorn_bind_host}\) still in use after termination attempt.': r'❌ 终止尝试后端口 {server_target_port} (主机 {uvicorn_bind_host}) 仍在使用。',
        r'Identified PIDs potentially using port {server_target_port}: {pids_on_port}': r'识别到可能占用端口 {server_target_port} 的 PID: {pids_on_port}',
        r'User selected to attempt termination...': r'用户选择尝试终止...',
        r'User selected not to auto-terminate or timed out. Continuing server start attempt.': r'用户未选择自动终止或已超时。继续尝试启动服务器。',
        r'Headless mode will not attempt auto-termination of port-hogging processes. Server start may fail.': r'无头模式不会尝试自动终止占用端口的进程。服务器启动可能会失败。',
        r'Could not auto-identify processes using port {server_target_port}. Server start may fail.': r'无法自动识别使用端口 {server_target_port} 的进程。服务器启动可能会失败。',
        r'--- Port {server_target_port} might still be in use. Continuing, server will handle binding. ---': r'--- 端口 {server_target_port} 可能仍在被使用。继续，服务器将处理绑定。 ---',
        
        # Execution & Internal Camoufox
        r'--- Step 3: Prepare and start Camoufox internal process ---': r'--- 第三步: 准备并启动 Camoufox 内部进程 ---',
        r'Attempting to use path from --active-auth-json: \'{args\.active_auth_json}\'': r'尝试使用 --active-auth-json 的路径: \'{args.active_auth_json}\'',
        r'Using resolved auth file from --active-auth-json: {effective_active_auth_json_path}': r'使用来自 --active-auth-json 解析的认证文件: {effective_active_auth_json_path}',
        r'❌ Specified auth file \(--active-auth-json=\'{args\.active_auth_json}\'\) not found or not a file.': r'❌ 指定的认证文件 (--active-auth-json=\'{args.active_auth_json}\') 未找到或不是文件。',
        r'Debug Mode: Scanning directories to prompt user selection from available auth files...': r'调试模式: 扫描目录以提示用户从可用的认证文件中选择...',
        r'--active-auth-json not provided. Checking default auth file in \'{ACTIVE_AUTH_DIR}\'\.\.\.': r'未提供 --active-auth-json。在 \'{ACTIVE_AUTH_DIR}\' 中检查默认认证文件...',
        r'Using first alphabetic JSON file in \'{ACTIVE_AUTH_DIR}\': {os\.path\.basename\(effective_active_auth_json_path\)}': r'使用 \'{ACTIVE_AUTH_DIR}\' 中第一个按字母顺序排列的 JSON 文件: {os.path.basename(effective_active_auth_json_path)}',
        r'Directory \'{ACTIVE_AUTH_DIR}\' empty or contains no JSON files.': r'目录 \'{ACTIVE_AUTH_DIR}\' 为空或未包含 JSON 文件。',
        r'Directory \'{ACTIVE_AUTH_DIR}\' does not exist.': r'目录 \'{ACTIVE_AUTH_DIR}\' 不存在。',
        r'Error scanning \'{ACTIVE_AUTH_DIR}\': {e_scan_active}': r'扫描 \'{ACTIVE_AUTH_DIR}\' 时出错: {e_scan_active}',
        r'\[DIAGNOSTIC\] Scanning for profiles in: active, saved, emergency.': r'[诊断] 正在扫描 active, saved, emergency 中的配置文件。',
        r'⚠️ Warning: Cannot read directory \'{profile_dir_path_str}\': {e}': r'⚠️ 警告: 无法读取目录 \'{profile_dir_path_str}\': {e}',
        r'Selected to load auth file: {selected_profile\[\'name\'\]}': r'选择加载认证文件: {selected_profile[\'name\']}',
        r'Invalid selection number or timeout. Will not load auth file.': r'选择编号无效或超时。将不会加载认证文件。',
        r'Invalid input\. Will not load auth file\.': r'无效输入。将不会加载认证文件。',
        r'Okay, no auth file loaded or timeout\.': r'好的，未加载认证文件或已超时。',
        r'No auth files found\. Using browser current state\.': r'未找到认证文件。使用浏览器当前状态。',
        r'⚠️ No active profile selected, but profiles exist in saved/emergency and auto-rotation is enabled. Allowing startup \(runtime rotation will select one\).': r'⚠️ 未选择活动配置文件，但 saved/emergency 中存在配置且已启用自动轮换。允许启动 (运行时转轮将进行选择)。',
        r'❌ {final_launch_mode} Mode Error: No active profile found in \'{ACTIVE_AUTH_DIR}\' and AUTO_AUTH_ROTATION_ON_STARTUP is disabled.': r'❌ {final_launch_mode} 模式错误: 在 \'{ACTIVE_AUTH_DIR}\' 中未找到活动配置文件，且 AUTO_AUTH_ROTATION_ON_STARTUP 已禁用。',
        r'Please ensure a profile exists in \'{ACTIVE_AUTH_DIR}\' or enable auto-rotation.': r'请确保在 \'{ACTIVE_AUTH_DIR}\' 中存在配置文件，或启用自动轮换。',
        r'❌ {final_launch_mode} Mode Error: --active-auth-json not provided, active/ is empty, and no backup profiles found in saved/emergency.': r'❌ {final_launch_mode} 模式错误: 未提供 --active-auth-json，active/为空，并且在 saved/emergency 中未找到备用配置文件。',
        r'Executing Camoufox internal launch command: {\' \'\.join\(camoufox_internal_cmd_args\)}': r'执行 Camoufox 内部启动命令: {\' \'.join(camoufox_internal_cmd_args)}',
        r'Camoufox internal process started \(PID: {camoufox_proc\.pid}\)\. Waiting for WebSocket endpoint output \(max {ENDPOINT_CAPTURE_TIMEOUT}s\)\.\.\.': r'Camoufox 内部进程已启动 (PID: {camoufox_proc.pid})。等待 WebSocket 端点输出 (最大 {ENDPOINT_CAPTURE_TIMEOUT}秒)...',
        r'Camoufox internal process \(PID: {camoufox_proc\.pid}\) exited unexpectedly while waiting for WebSocket endpoint, exit code: {camoufox_proc\.poll\(\)}\.': r'等待 WebSocket 端点时 Camoufox 内部进程 (PID: {camoufox_proc.pid}) 意外退出，退出代码: {camoufox_proc.poll()}。',
        r'\[InternalCamoufox-{stream_name}-PID:{camoufox_proc\.pid}\] Output stream closed \(EOF\)\.': r'[InternalCamoufox-{stream_name}-PID:{camoufox_proc.pid}] 输出流已关闭 (EOF)。',
        r'All output streams of Camoufox internal process \(PID: {camoufox_proc\.pid}\) closed\.': r'Camoufox 内部进程 (PID: {camoufox_proc.pid}) 的所有输出流已关闭。',
        r'✅ Successfully captured WebSocket endpoint from Camoufox internal process: {captured_ws_endpoint\[:40\]}\.\.\.': r'✅ 成功捕获来自 Camoufox 内部进程的 WebSocket 端点: {captured_ws_endpoint[:40]}...',
        r'❌ Failed to capture WebSocket endpoint from Camoufox internal process \(PID: {camoufox_proc\.pid}\) within {ENDPOINT_CAPTURE_TIMEOUT} seconds\.': r'❌ 无法在 {ENDPOINT_CAPTURE_TIMEOUT} 秒内从 Camoufox 内部进程 (PID: {camoufox_proc.pid}) 捕获 WebSocket 端点。',
        r'Camoufox internal process still running but didn\'t output expected WebSocket endpoint\. Check its logs\.': r'Camoufox 内部进程仍在运行，但未输出预期的 WebSocket 端点。请检查其日志。',
        r'❌ Camoufox internal process exited, and failed to capture WebSocket endpoint\.': r'❌ Camoufox 内部进程已退出，且未能捕获 WebSocket 端点。',
        r'❌ Failed to capture WebSocket endpoint\.': r'❌ 无法捕获 WebSocket 端点。',
        r'❌ Fatal error launching internal Camoufox or capturing WebSocket endpoint: {e_launch_camoufox_internal}': r'❌ 启动内部 Camoufox 或捕获 WebSocket 端点时发生严重错误: {e_launch_camoufox_internal}',
        
        # Cleanup & Signal Handling
        r'--- Starting cleanup routine \(launch_camoufox\.py\) ---': r'--- 开始清理程序 (launch_camoufox.py) ---',
        r'Terminating Camoufox internal subprocess \(PID: {pid}\)\.\.\.': r'正在终止 Camoufox 内部子进程 (PID: {pid})...',
        r'Sending SIGTERM to Camoufox process group \(PGID: {pgid}\)\.\.\.': r'正在发送 SIGTERM 给 Camoufox 进程组 (PGID: {pgid})...',
        r'Camoufox process group \(PID: {pid}\) not found, attempting direct termination\.\.\.': r'未找到 Camoufox 进程组 (PID: {pid})，尝试直接终止...',
        r'🔥 \[ID-02\] Windows Force-Kill Strategy: Using immediate /F /T for process tree \(PID: {pid}\)': r'🔥 [ID-02] Windows 强制结束策略: 立即使用 /F /T 结束进程树 (PID: {pid})',
        r'✅ Successfully force-killed Camoufox process tree via taskkill\.': r'✅ 成功通过 taskkill 强制终止 Camoufox 进程树。',
        r'⚠️ Taskkill /F /T returned code {result\.returncode}: {result\.stderr\.strip\(\)}': r'⚠️ Taskkill /F /T 返回代码 {result.returncode}: {result.stderr.strip()}',
        r'Sending SIGTERM to Camoufox \(PID: {pid}\)\.\.\.': r'正在向 Camoufox 发送 SIGTERM (PID: {pid})...',
        r'✓ Camoufox \(PID: {pid}\) successfully terminated via SIGTERM\.': r'✓ Camoufox (PID: {pid}) 已成功通过 SIGTERM 终止。',
        r'⚠️ Camoufox \(PID: {pid}\) SIGTERM timed out\. Sending SIGKILL to force terminate\.\.\.': r'⚠️ Camoufox (PID: {pid}) SIGTERM 超时。发送 SIGKILL 强制终止...',
        r'Sending SIGKILL to Camoufox process group \(PGID: {pgid}\)\.\.\.': r'正在发送 SIGKILL 给 Camoufox 进程组 (PGID: {pgid})...',
        r'Camoufox process group \(PID: {pid}\) not found during SIGKILL, attempting direct force kill\.\.\.': r'在发送 SIGKILL 期间未找到 Camoufox 进程组 (PID: {pid})，尝试直接强制终结...',
        r'🔥 \[ID-02\] Fallback: Force killing Camoufox process tree \(PID: {pid}\)': r'🔥 [ID-02] 回退方案: 强制终止 Camoufox 进程树 (PID: {pid})',
        r'✅ Fallback: Successfully force-killed Camoufox process tree\.': r'✅ 回退方案: 成功强制终止 Camoufox 进程树。',
        r'⚠️ Fallback taskkill failed \(code {result\.returncode}\): {result\.stderr\.strip\(\)}': r'⚠️ 回退方案 taskkill 失败 (代码 {result.returncode}): {result.stderr.strip()}',
        r'✓ Camoufox \(PID: {pid}\) successfully terminated via SIGKILL\.': r'✓ Camoufox (PID: {pid}) 已成功通过 SIGKILL 终止。',
        r'❌ Error waiting for Camoufox \(PID: {pid}\) SIGKILL completion: {e_kill}': r'❌ 等待 Camoufox (PID: {pid}) SIGKILL 完成时发生错误: {e_kill}',
        r'❌ Error terminating Camoufox \(PID: {pid}\): {e_term}': r'❌ 终止 Camoufox 时发生错误 (PID: {pid}): {e_term}',
        r'Camoufox internal subprocess \(PID: {camoufox_proc\.pid if hasattr\(camoufox_proc, \'pid\'\) else \'N/A\'}\) ended previously, exit code: {camoufox_proc\.poll\(\)}\.': r'Camoufox 内部子进程 (PID: {camoufox_proc.pid if hasattr(camoufox_proc, \'pid\') else \'N/A\'}) 已在之前结束，退出代码: {camoufox_proc.poll()}。',
        r'Camoufox internal subprocess not running or already cleaned up\.': r'Camoufox 内部子进程未在运行或已被清理。',
        r'--- Cleanup routine finished \(launch_camoufox\.py\) ---': r'--- 清理程序已完成 (launch_camoufox.py) ---',
        r'Received signal {signal\.Signals\(sig\)\.name} \({sig}\)\. Setting IS_SHUTTING_DOWN event\.\.\.': r'收到信号 {signal.Signals(sig).name} ({sig})。 正在设置 IS_SHUTTING_DOWN 事件...',
        r'Initiating exit procedure \(Force Exit\)\.\.\.': r'启动退出程序 (强制退出)...',
        r'Error during cleanup in signal handler: {e}': r'信号处理器的清理程序发生错误: {e}',
        r'Exiting with os\._exit\(0\)': r'退出 os._exit(0)',
        
        # Helper mode
        r'Helper mode enabled, endpoint: {args\.helper}': r'助手模式已启用，端点: {args.helper}',
        r'Attempting to extract SAPISID from auth file \'{os\.path\.basename\(effective_active_auth_json_path\)}\'\.\.\.': r'尝试从认证文件 \'{os.path.basename(effective_active_auth_json_path)}\' 提取 SAPISID...',
        
        # Kill Process Interactive
        r'Attempting to terminate process PID: {pid}\.\.\.': r'尝试终止进程 PID: {pid}...',
        r'✓ PID {pid} sent SIGTERM signal\.': r'✓ 向 PID {pid} 发送了 SIGTERM 信号。',
        r'PID {pid} SIGTERM failed: {result_term\.stderr\.strip\(\) or result_term\.stdout\.strip\(\)}\. Attempting SIGKILL\.\.\.': r'PID {pid} SIGTERM 失败: {result_term.stderr.strip() or result_term.stdout.strip()}。正在尝试 SIGKILL...',
        r'✓ PID {pid} sent SIGKILL signal\.': r'✓ 向 PID {pid} 发送了 SIGKILL 信号。',
        r'✗ PID {pid} SIGKILL failed: {result_kill\.stderr\.strip\(\) or result_kill\.stdout\.strip\(\)}\.': r'✗ PID {pid} SIGKILL 失败: {result_kill.stderr.strip() or result_kill.stdout.strip()}。',
        r'✓ PID {pid} terminated via taskkill /F\.': r'✓ 进程 PID {pid} 已通过 taskkill /F 终止。',
        r'PID {pid} not found during taskkill \(might have exited\)\.': r'在执行 taskkill 时未找到 PID {pid} (可能已退出)。',
        r'✗ PID {pid} taskkill /F failed: {\(error_output \+ \' \' \+ output\)\.strip\(\)}\.': r'✗ PID {pid} 的 taskkill /F 操作失败: {(error_output + \' \' + output).strip()}。',
        r'Unsupported OS \'{system_platform}\' for process termination\.': r'不支持用于终止进程的 OS \'{system_platform}\'。',
        r'Unexpected error terminating PID {pid}: {e}': r'终止 PID {pid} 时发生意外错误: {e}',
        
        # Thread
        r'{log_prefix} Decode error: {decode_err}\. Raw data \(first 100 bytes\): {line_bytes\[:100\]}': r'{log_prefix} 解码错误: {decode_err}。 原始数据（前100个字节）: {line_bytes[:100]}',
        r'{log_prefix} ValueError \(Stream might be closed\)\.': r'{log_prefix} 值错误 (数据流可能已关闭)。',
        r'{log_prefix} Unexpected error reading stream: {e}': r'{log_prefix} 读取流时发生意外错误: {e}',
        r'{log_prefix} Thread exiting\.': r'{log_prefix} 线程正在退出。',
        
        # Proxy & Misc
        r'Command \'{cmd_name}\' not found\.': r'找不到命令 \'{cmd_name}\'。',
        r'Command \'{command}\' timed out\.': r'命令 \'{command}\' 超时。',
        r'Setting unified proxy config: {proxy_config\[\'source\'\]}': r'设置统一代理配置: {proxy_config[\'source\']}',
        r'--- Check Xvfb \(Virtual Display\) Dependency ---': r'--- 检查 Xvfb (虚拟显示) 依赖 ---',
        r'✓ Xvfb found\.': r'✓ 找到 Xvfb。',
        r'❌ Xvfb not found\. Virtual display mode requires Xvfb\. Please install \(e\.g\., sudo apt-get install xvfb\) and retry\.': r'❌ 找不到 Xvfb。虚拟显示模式需要 Xvfb。请安装 (例如: sudo apt-get install xvfb) 并重试。',
        r'Environment variables set for server\.app:': r'为 server.app 设置了的环境变量:',
        r'    {key}={val_to_log}': r'    {key}={val_to_log}',
        r'    {key}= \(Not Set\)': r'    {key}= (未设置)',
        
        # From server.py
        r'👀 Quota Watchdog Started': r'👀 额度监视看门狗已启动',
        r'🚨 Watchdog detected Quota Exceeded! Initiating Rotation\.\.\.': r'🚨 看门狗监测到超额! 开始轮换...',
        r'Watchdog: Rotation already in progress\. Waiting\.\.\.': r'看门狗: 轮换已经在进行中。请稍候...',
        r'Watchdog: Rotation successful\.': r'看门狗: 轮换成功。',
        r'Watchdog: Rotation failed\.': r'看门狗: 轮换失败。',
        r'Watchdog: Quota flag still set\. Forcing reset\.': r'看门狗: 超额标志仍然被置位。强制重置。',
        r'Watchdog: Task cancelled\.': r'看门狗: 任务被取消。',
        r'Watchdog Error: {e}': r'看门狗错误: {e}'
    }

    for en, cn in replacements.items():
        original = content
        # Because we're matching Python source code, we use string replacements where possible to avoid regex escaping headaches, or we use regex if necessary.
        # It's safer to use regex substitution for Python code when we've escaped the regex properly.
        # Wait, using regex for source code can be tricky. Let's do simple string replace if it matches exactly.
        # The strings above have {} braces unescaped for f-strings because they literally appear that way.
        # Let's unescape some regex specific things like \. \( \[\{, but wait, those were literal in the python file.
        content = re.sub(en, cn, content)
        
    # Additional translations via simple string replace
    simple_replacements = {
        'logger.info(f"Log level set to: {logging.getLevelName(logger.getEffectiveLevel())}")': 'logger.info(f"日志级别设置为: {logging.getLevelName(logger.getEffectiveLevel())}")',
        'logger.info("=================================================")': 'logger.info("=================================================")',
        'logger.warning("  ⚠️ \'camoufox.server\' imported, but \'camoufox.DefaultAddons\' not imported. Addon exclusion features might be limited.")': 'logger.warning("  ⚠️ 导入了 \'camoufox.server\'，未导入 \'camoufox.DefaultAddons\'。附加组件排除功能可能受限。")',
        'logger.error("  ❌ Internal launch mode (--internal-*) requires \'camoufox\' package, but import failed.")': 'logger.error("  ❌ 内部启动模式 (--internal-*) 需要 \'camoufox\' 库，但导入失败。")',
        'logger.info("Internal launch mode not requested and camoufox.server not imported, skipping \'camoufox\' Python package check.")': 'logger.info("未请求内部启动模式并且也未导入 camoufox.server，将跳过 \'camoufox\' 包的检查。")',
        'logger.info("  ✓ Successfully imported \'app\' object from \'server.py\'.")': 'logger.info("  ✓ 成功从 \'server.py\' 导入 \'app\' 对象。")',
        'logger.error(f"  ❌ Failed to import \'app\' object from \'server.py\': {e_import_server}")': 'logger.error(f"  ❌ 无法从 \'server.py\' 导入 \'app\' 对象: {e_import_server}")',
        'logger.error("     Please ensure \'server.py\' exists and has no import errors.")': 'logger.error("     请确保 \'server.py\' 存在并且没有导入错误。")',
        'logger.info("✅ All launcher dependency checks passed.")': 'logger.info("✅ 所有启动器依赖检查通过。")'
    }
    for k, v in simple_replacements.items():
        content = content.replace(k, v)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


translate_file('d:/AIstudioProxyAPI/AIstudioProxyAPI/launch_camoufox.py')
translate_file('d:/AIstudioProxyAPI/AIstudioProxyAPI/server.py')
