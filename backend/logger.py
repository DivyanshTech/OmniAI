import os
import json
from datetime import datetime
from typing import Dict, Any
import logging

class ChatLogger:
    def __init__(self, log_dir: str = "../logs"):
        """Initialize chat logger with log directory"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup Python logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure Python logging"""
        log_file = os.path.join(self.log_dir, "app.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("ChatBot")
    
    def log_interaction(self, 
                       session_id: str,
                       user_message: str,
                       bot_response: str,
                       context_used: list = None,
                       processing_time: float = 0.0,
                       metadata: Dict = None):
        """
        Log a complete user-bot interaction
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "context_sources": len(context_used) if context_used else 0,
            "processing_time_seconds": processing_time,
            "metadata": metadata or {}
        }
        
        # Save to daily log file
        self._save_to_daily_log(interaction)
        
        # Log to console
        self.logger.info(f"Session: {session_id} | User: {user_message[:50]}... | Time: {processing_time:.2f}s")
    
    def _save_to_daily_log(self, interaction: Dict):
        """Save interaction to daily JSON log file"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"chat_log_{date_str}.json")
        
        # Read existing logs
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        # Append new interaction
        logs.append(interaction)
        
        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def log_error(self, error_message: str, context: Dict = None):
        """Log errors with context"""
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "error": error_message,
            "context": context or {}
        }
        
        self.logger.error(f"Error: {error_message}")
        
        # Save to error log file
        error_file = os.path.join(self.log_dir, "errors.json")
        errors = []
        
        if os.path.exists(error_file):
            try:
                with open(error_file, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            except:
                errors = []
        
        errors.append(error_log)
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2)
    
    def get_daily_stats(self, date_str: str = None) -> Dict:
        """Get statistics for a specific date"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        log_file = os.path.join(self.log_dir, f"chat_log_{date_str}.json")
        
        if not os.path.exists(log_file):
            return {
                "date": date_str,
                "total_interactions": 0,
                "average_processing_time": 0,
                "unique_sessions": 0
            }
        
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        sessions = set()
        total_time = 0
        
        for log in logs:
            sessions.add(log["session_id"])
            total_time += log.get("processing_time_seconds", 0)
        
        return {
            "date": date_str,
            "total_interactions": len(logs),
            "average_processing_time": total_time / len(logs) if logs else 0,
            "unique_sessions": len(sessions)
        }
    
    def export_logs(self, start_date: str, end_date: str) -> list:
        """Export logs for a date range"""
        # Implementation for exporting logs between dates
        # This is a placeholder - can be extended as needed
        pass
    
    def log_system_event(self, event_type: str, message: str, data: Any = None):
        """Log system events (startup, shutdown, errors, etc.)"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "data": data
        }
        
        self.logger.info(f"System Event - {event_type}: {message}")
        
        system_log = os.path.join(self.log_dir, "system.log")
        with open(system_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + "\n")


# Global logger instance
chat_logger = ChatLogger()

if __name__ == "__main__":
    # Test logger
    logger = ChatLogger()
    
    logger.log_interaction(
        session_id="test_123",
        user_message="How do I reset my password?",
        bot_response="To reset your password, go to the login page...",
        context_used=["doc1", "doc2"],
        processing_time=1.5
    )
    
    stats = logger.get_daily_stats()
    print(f"\n📊 Daily Stats: {stats}")
