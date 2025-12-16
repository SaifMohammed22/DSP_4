import uuid
import time
import threading
import queue
import json
import os
from typing import Dict, Any, Callable, Optional, List
from enum import Enum
from dataclasses import dataclass, field

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    """Result of a task execution"""
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Task:
    """Represents a processing task"""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[TaskResult] = None
    callback: Optional[Callable] = None
    user_id: Optional[str] = None
    
    def update_progress(self, progress: float):
        """Update task progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
    
    def start(self):
        """Mark task as started"""
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()
    
    def complete(self, result: TaskResult):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result
        self.progress = 1.0
    
    def fail(self, error: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = time.time()
        self.result = TaskResult(error=error)
    
    def cancel(self):
        """Mark task as cancelled"""
        if self.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            self.status = TaskStatus.CANCELLED
            self.completed_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'status': self.status.value,
            'progress': self.progress,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'parameters': self.parameters,
            'result': {
                'data': self.result.data if self.result else None,
                'error': self.result.error if self.result else None,
                'execution_time': self.result.execution_time if self.result else 0.0
            } if self.result else None,
            'user_id': self.user_id
        }

class TaskManager:
    """Manages background tasks with progress tracking and cancellation"""
    
    def __init__(self, max_workers: int = 4, task_timeout: int = 300):
        self.max_workers = max_workers
        self.task_timeout = task_timeout  # seconds
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.Queue()
        self.workers: List[threading.Thread] = []
        self.is_running = False
        self.lock = threading.Lock()
        
        # Task type handlers
        self.task_handlers = {}
        
        # Start worker threads
        self.start_workers()
    
    def start_workers(self):
        """Start worker threads"""
        if not self.is_running:
            self.is_running = True
            for i in range(self.max_workers):
                worker = threading.Thread(
                    target=self._worker_loop,
                    name=f"TaskWorker-{i}",
                    daemon=True
                )
                worker.start()
                self.workers.append(worker)
    
    def _worker_loop(self):
        """Worker thread main loop"""
        while self.is_running:
            try:
                # Get task from queue
                task_id = self.task_queue.get(timeout=1)
                
                with self.lock:
                    if task_id not in self.tasks:
                        continue
                    
                    task = self.tasks[task_id]
                    
                    # Check if task was cancelled
                    if task.status == TaskStatus.CANCELLED:
                        self.task_queue.task_done()
                        continue
                    
                    # Start task
                    task.start()
                
                # Execute task
                self._execute_task(task)
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def _execute_task(self, task: Task):
        """Execute a task"""
        try:
            # Check for timeout
            start_time = time.time()
            
            # Get handler for task type
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                task.fail(f"No handler for task type: {task.task_type}")
                return
            
            # Execute handler
            result = handler(task)
            
            # Check if task was cancelled during execution
            with self.lock:
                if task.status == TaskStatus.CANCELLED:
                    return
            
            # Calculate execution time
            exec_time = time.time() - start_time
            
            # Create task result
            task_result = TaskResult(
                data=result,
                execution_time=exec_time
            )
            
            # Mark task as completed
            with self.lock:
                task.complete(task_result)
            
            # Execute callback if provided
            if task.callback:
                try:
                    task.callback(task)
                except Exception as e:
                    print(f"Callback error: {e}")
            
        except Exception as e:
            with self.lock:
                task.fail(str(e))
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a task type"""
        self.task_handlers[task_type] = handler
    
    def submit_task(self, task_type: str, parameters: Dict[str, Any], 
                   callback: Optional[Callable] = None, 
                   user_id: Optional[str] = None) -> str:
        """Submit a new task for execution"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            parameters=parameters,
            callback=callback,
            user_id=user_id
        )
        
        # Store task
        with self.lock:
            self.tasks[task_id] = task
        
        # Add to queue
        self.task_queue.put(task_id)
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and progress"""
        task = self.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    def update_task_progress(self, task_id: str, progress: float):
        """Update progress of a task"""
        task = self.get_task(task_id)
        if task:
            task.update_progress(progress)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        task = self.get_task(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.cancel()
            return True
        return False
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        tasks_to_remove = []
        
        with self.lock:
            for task_id, task in self.tasks.items():
                if task.completed_at:
                    age = current_time - task.completed_at
                    if age > max_age_seconds:
                        tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.tasks[task_id]
    
    def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a user"""
        user_tasks = []
        
        with self.lock:
            for task in self.tasks.values():
                if task.user_id == user_id:
                    user_tasks.append(task.to_dict())
        
        return user_tasks
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active (pending/running) tasks"""
        active_tasks = []
        
        with self.lock:
            for task in self.tasks.values():
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    active_tasks.append(task.to_dict())
        
        return active_tasks
    
    def save_state(self, filepath: str):
        """Save task manager state to file"""
        state = {
            'tasks': {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Load task manager state from file"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        with self.lock:
            for task_id, task_data in state.get('tasks', {}).items():
                # Recreate task objects
                task = Task(
                    task_id=task_data['task_id'],
                    task_type=task_data['task_type'],
                    parameters=task_data['parameters'],
                    user_id=task_data.get('user_id')
                )
                
                # Restore status
                task.status = TaskStatus(task_data['status'])
                task.progress = task_data['progress']
                task.created_at = task_data['created_at']
                task.started_at = task_data.get('started_at')
                task.completed_at = task_data.get('completed_at')
                
                # Restore result
                if task_data.get('result'):
                    task.result = TaskResult(
                        data=task_data['result'].get('data'),
                        error=task_data['result'].get('error'),
                        execution_time=task_data['result'].get('execution_time', 0.0)
                    )
                
                self.tasks[task_id] = task