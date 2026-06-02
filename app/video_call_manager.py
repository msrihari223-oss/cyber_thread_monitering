import json
from typing import Dict, List
from fastapi import WebSocket
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CallConnection:
    """Represents an active video call connection"""
    
    def __init__(self, call_id: int, caller_id: int, callee_id: int):
        self.call_id = call_id
        self.caller_id = caller_id
        self.callee_id = callee_id
        self.caller_websocket: WebSocket = None
        self.callee_websocket: WebSocket = None
        self.start_time = datetime.utcnow()
        self.status = "pending"
        self.ice_candidates = {"caller": [], "callee": []}
    
    async def connect_caller(self, websocket: WebSocket):
        await websocket.accept()
        self.caller_websocket = websocket
        logger.info(f"Caller {self.caller_id} connected to call {self.call_id}")
    
    async def connect_callee(self, websocket: WebSocket):
        await websocket.accept()
        self.callee_websocket = websocket
        logger.info(f"Callee {self.callee_id} connected to call {self.call_id}")
    
    async def send_to_caller(self, message: dict):
        if self.caller_websocket:
            try:
                await self.caller_websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to caller: {e}")
    
    async def send_to_callee(self, message: dict):
        if self.callee_websocket:
            try:
                await self.callee_websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to callee: {e}")
    
    async def disconnect_caller(self):
        if self.caller_websocket:
            try:
                await self.caller_websocket.close()
            except:
                pass
            self.caller_websocket = None
    
    async def disconnect_callee(self):
        if self.callee_websocket:
            try:
                await self.callee_websocket.close()
            except:
                pass
            self.callee_websocket = None
    
    def add_ice_candidate(self, side: str, candidate: dict):
        """Store ICE candidate for later retrieval"""
        self.ice_candidates[side].append(candidate)
    
    def get_ice_candidates(self, side: str) -> List[dict]:
        """Get all stored ICE candidates for a side"""
        candidates = self.ice_candidates[side]
        self.ice_candidates[side] = []  # Clear after retrieval
        return candidates


class VideoCallManager:
    """Manages all active video calls and signaling"""
    
    def __init__(self):
        self.calls: Dict[int, CallConnection] = {}
        self.user_calls: Dict[int, List[int]] = {}  # user_id -> list of call_ids
    
    def create_call(self, call_id: int, caller_id: int, callee_id: int) -> CallConnection:
        """Create a new call connection"""
        call = CallConnection(call_id, caller_id, callee_id)
        self.calls[call_id] = call
        
        if caller_id not in self.user_calls:
            self.user_calls[caller_id] = []
        if callee_id not in self.user_calls:
            self.user_calls[callee_id] = []
        
        self.user_calls[caller_id].append(call_id)
        self.user_calls[callee_id].append(call_id)
        
        logger.info(f"Created call {call_id} between {caller_id} and {callee_id}")
        return call
    
    def get_call(self, call_id: int) -> CallConnection:
        """Get an active call"""
        return self.calls.get(call_id)
    
    def end_call(self, call_id: int):
        """End a call and cleanup"""
        if call_id in self.calls:
            call = self.calls[call_id]
            
            # Remove from user_calls
            if call.caller_id in self.user_calls:
                if call_id in self.user_calls[call.caller_id]:
                    self.user_calls[call.caller_id].remove(call_id)
            
            if call.callee_id in self.user_calls:
                if call_id in self.user_calls[call.callee_id]:
                    self.user_calls[call.callee_id].remove(call_id)
            
            # Remove call
            del self.calls[call_id]
            logger.info(f"Ended call {call_id}")
    
    async def disconnect_call(self, call_id: int):
        """Disconnect both parties and cleanup"""
        if call_id in self.calls:
            call = self.calls[call_id]
            await call.disconnect_caller()
            await call.disconnect_callee()
            self.end_call(call_id)
    
    def get_user_calls(self, user_id: int) -> List[int]:
        """Get all active calls for a user"""
        return self.user_calls.get(user_id, [])
    
    async def send_offer(self, call_id: int, sdp: str):
        """Send SDP offer from caller to callee"""
        call = self.get_call(call_id)
        if call:
            await call.send_to_callee({
                "type": "offer",
                "sdp": sdp
            })
    
    async def send_answer(self, call_id: int, sdp: str):
        """Send SDP answer from callee to caller"""
        call = self.get_call(call_id)
        if call:
            await call.send_to_caller({
                "type": "answer",
                "sdp": sdp
            })
    
    async def send_ice_candidate(self, call_id: int, from_user: int, candidate: dict):
        """Send ICE candidate to the other party"""
        call = self.get_call(call_id)
        if call:
            if from_user == call.caller_id:
                await call.send_to_callee({
                    "type": "ice_candidate",
                    "candidate": candidate
                })
            else:
                await call.send_to_caller({
                    "type": "ice_candidate",
                    "candidate": candidate
                })
    
    def update_call_status(self, call_id: int, status: str):
        """Update call status"""
        call = self.get_call(call_id)
        if call:
            call.status = status
            logger.info(f"Call {call_id} status updated to {status}")


# Global instance
video_call_manager = VideoCallManager()
