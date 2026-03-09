import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

# --- Centralized state module ---
from api_utils.server_state import state


def clear_debug_logs() -> None:
    state.clear_debug_logs()


# --- Imports ---

from browser_utils.auth_rotation import perform_auth_rotation
from config import (
    GlobalState,
)


async def quota_watchdog():
    """Background watchdog to monitor quota exceeded events."""
    # Use state's logger if available
    logger = getattr(state, "logger", logging.getLogger("AIStudioProxyServer"))
    logger.info("👀 额度监视看门狗已启动")
    while True:
        try:
            await GlobalState.QUOTA_EXCEEDED_EVENT.wait()
            logger.critical(
                "🚨 看门狗监测到超额! 开始轮换..."
            )

            if not GlobalState.AUTH_ROTATION_LOCK.is_set():
                logger.info("看门狗: 轮换已经在进行中。请稍候...")
                await asyncio.sleep(1)
                continue

            GlobalState.start_recovery()
            try:
                current_model_id = state.current_ai_studio_model_id
                success = await perform_auth_rotation(
                    target_model_id=current_model_id or ""
                )
                if success:
                    logger.info("看门狗: 轮换成功。")
                else:
                    logger.error("看门狗: 轮换失败。")
            finally:
                GlobalState.finish_recovery()

            if GlobalState.IS_QUOTA_EXCEEDED:
                logger.warning("看门狗: 超额标志仍然被置位。强制重置。")
                GlobalState.reset_quota_status()

        except asyncio.CancelledError:
            logger.info("看门狗: 任务被取消。")
            break
        except Exception as e:
            logger.error(f"看门狗错误: {e}", exc_info=True)
            await asyncio.sleep(5)


# Register quota_watchdog in state for easier access and to avoid circular import issues
state.quota_watchdog = quota_watchdog


from api_utils import (
    create_app,
)

# --- FastAPI App ---
app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 2048))
    uvicorn.run(
        "server:app", host="0.0.0.0", port=port, log_level="info", access_log=False
    )
