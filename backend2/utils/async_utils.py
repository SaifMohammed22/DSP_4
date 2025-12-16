import asyncio
import concurrent.futures
import threading
import queue
import time
import uuid
import json
import os
from typing import Dict, List, Callable, Any, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import traceback

# Global thread pool executor for CPU-bound tasks
_thread_pool_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# Global I/O executor for I/O-bound tasks
_io_executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)

class TaskStatus(Enum):
    """Status of async tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AsyncTaskResult:
    """Result container for async tasks"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'progress': self.progress,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'metadata': self.metadata
        }

class AsyncTaskManager:
    """
    Manager for asynchronous tasks with progress tracking and cancellation.
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: Dict[str, AsyncTaskResult] = {}
        self.task_queue = queue.Queue()
        self.worker_threads: List[threading.Thread] = []
        self.is_running = False
        self.lock = threading.Lock()
        
        # Callbacks
        self.progress_callbacks: Dict[str, Callable] = {}
        self.completion_callbacks: Dict[str, Callable] = {}
        
        # Start workers
        self.start_workers()
    
    def start_workers(self):
        """Start worker threads"""
        if not self.is_running:
            self.is_running = True
            for i in range(self.max_workers):
                worker = threading.Thread(
                    target=self._worker_loop,
                    name=f"AsyncWorker-{i}",
                    daemon=True
                )
                worker.start()
                self.worker_threads.append(worker)
    
    def _worker_loop(self):
        """Main worker loop"""
        while self.is_running:
            try:
                # Get task from queue
                task_id = self.task_queue.get(timeout=1)
                
                with self.lock:
                    if task_id not in self.tasks:
                        self.task_queue.task_done()
                        continue
                    
                    task_result = self.tasks[task_id]
                    
                    # Check if task was cancelled
                    if task_result.status == TaskStatus.CANCELLED:
                        self.task_queue.task_done()
                        continue
                    
                    # Mark as running
                    task_result.status = TaskStatus.RUNNING
                    task_result.started_at = time.time()
                
                # Execute task
                self._execute_task(task_id, task_result)
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def _execute_task(self, task_id: str, task_result: AsyncTaskResult):
        """Execute a single task"""
        try:
            # Get the actual task function and args from metadata
            func = task_result.metadata.get('func')
            args = task_result.metadata.get('args', [])
            kwargs = task_result.metadata.get('kwargs', {})
            
            if not func:
                raise ValueError("No task function provided")
            
            # Execute
            result = func(*args, **kwargs)
            
            # Check if cancelled during execution
            with self.lock:
                if task_result.status == TaskStatus.CANCELLED:
                    return
            
            # Update task
            with self.lock:
                task_result.status = TaskStatus.COMPLETED
                task_result.result = result
                task_result.progress = 1.0
                task_result.completed_at = time.time()
            
            # Call completion callback
            callback = self.completion_callbacks.get(task_id)
            if callback:
                try:
                    callback(task_result)
                except Exception as e:
                    print(f"Completion callback error: {e}")
            
        except Exception as e:
            with self.lock:
                task_result.status = TaskStatus.FAILED
                task_result.error = str(e)
                task_result.completed_at = time.time()
    
    def submit_task(self, func: Callable, *args, 
                   progress_callback: Optional[Callable] = None,
                   completion_callback: Optional[Callable] = None,
                   metadata: Optional[Dict] = None, **kwargs) -> str:
        """
        Submit a task for asynchronous execution.
        
        Args:
            func: Function to execute
            *args: Function arguments
            progress_callback: Callback for progress updates
            completion_callback: Callback for task completion
            metadata: Additional task metadata
            **kwargs: Function keyword arguments
        
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        # Create task result
        task_result = AsyncTaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            metadata={
                'func': func,
                'args': args,
                'kwargs': kwargs,
                **(metadata or {})
            }
        )
        
        # Store task
        with self.lock:
            self.tasks[task_id] = task_result
        
        # Store callbacks
        if progress_callback:
            self.progress_callbacks[task_id] = progress_callback
        if completion_callback:
            self.completion_callbacks[task_id] = completion_callback
        
        # Add to queue
        self.task_queue.put(task_id)
        
        return task_id
    
    def update_progress(self, task_id: str, progress: float):
        """
        Update progress of a task.
        
        Args:
            task_id: Task ID
            progress: Progress value (0.0 to 1.0)
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].progress = max(0.0, min(1.0, progress))
                
                # Call progress callback
                callback = self.progress_callbacks.get(task_id)
                if callback:
                    try:
                        callback(self.tasks[task_id])
                    except Exception as e:
                        print(f"Progress callback error: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get status of a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task status dictionary or None if not found
        """
        with self.lock:
            task_result = self.tasks.get(task_id)
            if task_result:
                return task_result.to_dict()
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if task was cancelled, False otherwise
        """
        with self.lock:
            if task_id in self.tasks:
                task_result = self.tasks[task_id]
                if task_result.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    task_result.status = TaskStatus.CANCELLED
                    task_result.completed_at = time.time()
                    return True
        return False
    
    def wait_for_task(self, task_id: str, timeout: float = None) -> AsyncTaskResult:
        """
        Wait for task to complete.
        
        Args:
            task_id: Task ID
            timeout: Maximum time to wait in seconds
        
        Returns:
            Task result
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                task_result = self.tasks.get(task_id)
                
                if not task_result:
                    raise ValueError(f"Task {task_id} not found")
                
                if task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    return task_result
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timed out")
            
            # Sleep a bit
            time.sleep(0.1)
    
    def cleanup_old_tasks(self, max_age: float = 3600):
        """
        Clean up old completed tasks.
        
        Args:
            max_age: Maximum age in seconds
        """
        current_time = time.time()
        tasks_to_remove = []
        
        with self.lock:
            for task_id, task_result in self.tasks.items():
                if task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    age = current_time - task_result.completed_at
                    if age > max_age:
                        tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                # Remove from dictionaries
                self.tasks.pop(task_id, None)
                self.progress_callbacks.pop(task_id, None)
                self.completion_callbacks.pop(task_id, None)
    
    def get_active_tasks(self) -> List[Dict]:
        """
        Get all active (pending/running) tasks.
        
        Returns:
            List of task status dictionaries
        """
        active_tasks = []
        
        with self.lock:
            for task_result in self.tasks.values():
                if task_result.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    active_tasks.append(task_result.to_dict())
        
        return active_tasks
    
    def stop(self):
        """Stop all workers"""
        self.is_running = False
        for worker in self.worker_threads:
            worker.join(timeout=5)
        self.worker_threads.clear()

# Global task manager instance
global_task_manager = AsyncTaskManager(max_workers=4)

def run_async_task(func: Callable, *args, **kwargs) -> str:
    """
    Run a function asynchronously using global task manager.
    
    Args:
        func: Function to execute
        *args, **kwargs: Function arguments
    
    Returns:
        Task ID
    """
    return global_task_manager.submit_task(func, *args, **kwargs)

async def run_in_threadpool(func: Callable, *args, **kwargs) -> Any:
    """
    Run a CPU-bound function in thread pool.
    
    Args:
        func: Function to execute
        *args, **kwargs: Function arguments
    
    Returns:
        Function result
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_thread_pool_executor, 
                                      lambda: func(*args, **kwargs))

async def run_in_io_pool(func: Callable, *args, **kwargs) -> Any:
    """
    Run an I/O-bound function in I/O thread pool.
    
    Args:
        func: Function to execute
        *args, **kwargs: Function arguments
    
    Returns:
        Function result
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_io_executor,
                                      lambda: func(*args, **kwargs))

class ProgressTracker:
    """
    Helper class for tracking progress of long-running operations.
    """
    
    def __init__(self, task_id: str, total_steps: int = 100):
        self.task_id = task_id
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
    
    def update(self, step: Optional[int] = None, message: str = ""):
        """
        Update progress.
        
        Args:
            step: Current step (if None, increment by 1)
            message: Progress message
        """
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        # Calculate progress
        progress = min(1.0, self.current_step / self.total_steps)
        
        # Update task manager
        global_task_manager.update_progress(self.task_id, progress)
        
        # Throttle updates to avoid overwhelming
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:  # Update at most 10 times per second
            self.last_update_time = current_time
            
            # Calculate estimated time remaining
            elapsed = current_time - self.start_time
            if progress > 0:
                estimated_total = elapsed / progress
                estimated_remaining = estimated_total - elapsed
            else:
                estimated_remaining = 0
            
            # Update metadata with progress info
            with global_task_manager.lock:
                if self.task_id in global_task_manager.tasks:
                    task_result = global_task_manager.tasks[self.task_id]
                    task_result.metadata.update({
                        'progress_message': message,
                        'estimated_remaining': estimated_remaining,
                        'current_step': self.current_step,
                        'total_steps': self.total_steps
                    })
    
    def complete(self, result: Any = None):
        """Mark progress as complete"""
        self.current_step = self.total_steps
        global_task_manager.update_progress(self.task_id, 1.0)
        return result

def async_with_progress(total_steps: int = 100):
    """
    Decorator to add progress tracking to async functions.
    
    Args:
        total_steps: Total number of progress steps
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract or generate task ID
            task_id = kwargs.pop('task_id', str(uuid.uuid4()))
            
            # Create progress tracker
            tracker = ProgressTracker(task_id, total_steps)
            
            # Add tracker to kwargs
            kwargs['progress_tracker'] = tracker
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                tracker.complete(result)
                return result
            except Exception as e:
                # Update task with error
                with global_task_manager.lock:
                    if task_id in global_task_manager.tasks:
                        global_task_manager.tasks[task_id].status = TaskStatus.FAILED
                        global_task_manager.tasks[task_id].error = str(e)
                raise
        
        return wrapper
    return decorator

def background_task(func):
    """
    Decorator to run function in background thread.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Store in task manager
        global_task_manager.tasks[task_id] = AsyncTaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING
        )
        
        def run_task():
            try:
                # Mark as running
                global_task_manager.tasks[task_id].status = TaskStatus.RUNNING
                global_task_manager.tasks[task_id].started_at = time.time()
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Mark as completed
                global_task_manager.tasks[task_id].status = TaskStatus.COMPLETED
                global_task_manager.tasks[task_id].result = result
                global_task_manager.tasks[task_id].completed_at = time.time()
                global_task_manager.tasks[task_id].progress = 1.0
                
            except Exception as e:
                # Mark as failed
                global_task_manager.tasks[task_id].status = TaskStatus.FAILED
                global_task_manager.tasks[task_id].error = str(e)
                global_task_manager.tasks[task_id].completed_at = time.time()
        
        # Start thread
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        
        return task_id
    
    return wrapper

class WebSocketProgressManager:
    """
    Manager for sending progress updates via WebSocket.
    """
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.connections = {}  # task_id -> socket_id mapping
    
    def register_connection(self, task_id: str, socket_id: str):
        """Register WebSocket connection for a task"""
        self.connections[task_id] = socket_id
    
    def send_progress(self, task_id: str, progress: float, message: str = ""):
        """Send progress update via WebSocket"""
        if task_id in self.connections:
            socket_id = self.connections[task_id]
            try:
                self.socketio.emit('task_progress', {
                    'task_id': task_id,
                    'progress': progress,
                    'message': message,
                    'timestamp': time.time()
                }, room=socket_id)
            except Exception as e:
                print(f"WebSocket progress error: {e}")
    
    def send_completion(self, task_id: str, result: Any):
        """Send task completion via WebSocket"""
        if task_id in self.connections:
            socket_id = self.connections[task_id]
            try:
                self.socketio.emit('task_complete', {
                    'task_id': task_id,
                    'result': result,
                    'timestamp': time.time()
                }, room=socket_id)
            except Exception as e:
                print(f"WebSocket completion error: {e}")
    
    def remove_connection(self, task_id: str):
        """Remove WebSocket connection"""
        self.connections.pop(task_id, None)

def run_long_computation(func: Callable, *args, task_name: str = "", **kwargs) -> str:
    """
    Run a long computation with proper async handling.
    
    Args:
        func: Function to execute
        task_name: Name of the task for logging
        *args, **kwargs: Function arguments
    
    Returns:
        Task ID
    """
    task_id = str(uuid.uuid4())
    
    def wrapped_func():
        try:
            print(f"Starting {task_name or 'task'} {task_id}")
            result = func(*args, **kwargs)
            print(f"Completed {task_name or 'task'} {task_id}")
            return result
        except Exception as e:
            print(f"Failed {task_name or 'task'} {task_id}: {e}")
            raise
    
    # Submit to global task manager
    return global_task_manager.submit_task(
        wrapped_func,
        metadata={'task_name': task_name, 'started_at': datetime.now().isoformat()}
    )

def monitor_task_progress(task_id: str, interval: float = 0.5, 
                         callback: Optional[Callable] = None):
    """
    Monitor task progress and call callback with updates.
    
    Args:
        task_id: Task ID to monitor
        interval: Check interval in seconds
        callback: Callback function for progress updates
    """
    def monitor():
        last_progress = -1
        
        while True:
            task_status = global_task_manager.get_task_status(task_id)
            
            if not task_status:
                break
            
            progress = task_status.get('progress', 0)
            
            # Only call callback if progress changed
            if progress != last_progress and callback:
                try:
                    callback(task_status)
                except Exception as e:
                    print(f"Progress callback error: {e}")
            
            last_progress = progress
            
            # Stop if task completed
            if task_status['status'] in ['completed', 'failed', 'cancelled']:
                if callback:
                    try:
                        callback(task_status)
                    except Exception as e:
                        print(f"Final callback error: {e}")
                break
            
            time.sleep(interval)
    
    # Start monitor thread
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    
    return thread

# Import functools for wraps
from functools import wraps

# Initialize global task manager on module import
global_task_manager.start_workers()