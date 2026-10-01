import json
import time
from fastapi import WebSocket, WebSocketDisconnect
from src.api.call_leg_manager import CallLegManager
from src.utils.logger import get_logger

logger = get_logger("WebSocketHandler")


async def handle_asr_websocket(websocket: WebSocket, session_manager: CallLegManager):
    """WebSocket connection handler for continuous binary audio streaming and transcript push."""
    await websocket.accept()
    session_id = f"session_{int(time.time() * 1000)}"
    model_name = "qwen3_asr"
    language = "en"

    # Wait for initial configuration frame (JSON control frame)
    try:
        init_data = await websocket.receive_text()
        init_json = json.loads(init_data)
        if init_json.get("action") == "start":
            session_id = init_json.get("session_id", session_id)
            model_name = init_json.get("model", "qwen3_asr")
            language = init_json.get("language", "en")
    except Exception as e:
        logger.warning(f"No control frame received, proceeding with defaults ({e})")

    session = await session_manager.start_call_leg(session_id, model_name=model_name, language=language)
    engine = session_manager.get_or_create_engine(model_name)

    await websocket.send_json({
        "event": "connected",
        "session_id": session_id,
        "model": model_name,
        "language": language,
        "status": "ready"
    })

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                pcm_bytes = message["bytes"]
                start_time = time.time()

                # Process chunk using ASR engine
                result = await engine.process_chunk(session_id=session_id, pcm_bytes=pcm_bytes, is_last=False)
                proc_duration = time.time() - start_time
                audio_dur = len(pcm_bytes) / 32000.0

                # Record telemetry
                session_manager.telemetry_collector.record_chunk_processed(
                    latency_ms=result.latency_ms,
                    processing_time_sec=proc_duration,
                    audio_duration_sec=audio_dur
                )

                # Send partial transcript result to Web UI
                await websocket.send_json({
                    "event": "transcript",
                    "session_id": session_id,
                    "chunk_index": result.chunk_index,
                    "text": result.text,
                    "is_final": result.is_final,
                    "latency_ms": round(result.latency_ms, 2),
                    "rtf": round(session_manager.telemetry_collector.get_rtf(), 4),
                    "active_legs": session_manager.get_active_legs_count()
                })

            elif "text" in message and message["text"]:
                txt = message["text"]
                try:
                    msg_json = json.loads(txt)
                    if msg_json.get("action") == "stop":
                        # Process end-of-stream final chunk
                        final_res = await engine.process_chunk(session_id=session_id, pcm_bytes=b"", is_last=True)
                        await websocket.send_json({
                            "event": "transcript",
                            "session_id": session_id,
                            "chunk_index": final_res.chunk_index,
                            "text": final_res.text,
                            "is_final": True,
                            "latency_ms": round(final_res.latency_ms, 2),
                            "rtf": round(session_manager.telemetry_collector.get_rtf(), 4),
                            "active_legs": session_manager.get_active_legs_count()
                        })
                        await websocket.send_json({"event": "eos", "session_id": session_id, "status": "completed"})
                        break
                except Exception:
                    pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: session '{session_id}'")
    finally:
        await session_manager.end_call_leg(session_id)
