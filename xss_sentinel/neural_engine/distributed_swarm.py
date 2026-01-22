"""
Distributed Neural Swarm - Multi-Node Parallel Scanning
Distributes XSS testing across multiple nodes for massive parallelization
"""

import asyncio
import json
import hashlib
import time
from typing import List, Dict, Set, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import requests

@dataclass
class ScanTask:
    """Represents a scanning task"""
    task_id: str = None
    url: str = ""
    injection_point: Dict = field(default_factory=dict)
    payloads: List[str] = field(default_factory=list)
    priority: int = 1
    node_id: Optional[str] = None
    status: str = 'pending'  # pending, assigned, running, completed, failed
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.task_id is None:
            content = f"{self.url}_{self.injection_point}_{time.time()}"
            self.task_id = hashlib.md5(content.encode()).hexdigest()


@dataclass
class WorkerNode:
    """Represents a worker node in the swarm"""
    node_id: str
    status: str = 'idle'  # idle, busy, offline
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_task_time: float = 0.0
    last_heartbeat: float = None
    capabilities: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = time.time()
        if not self.capabilities:
            self.capabilities = {'max_concurrent': 5, 'neural_engine': True}


class DistributedSwarmCoordinator:
    """
    Coordinates distributed XSS scanning across multiple worker nodes
    Uses work-stealing algorithm for load balancing
    """
    
    def __init__(self, coordinator_port=5000, max_workers=10):
        self.coordinator_port = coordinator_port
        self.max_workers = max_workers
        
        # Task management
        self.task_queue = queue.PriorityQueue()
        self.tasks: Dict[str, ScanTask] = {}
        self.completed_tasks: Dict[str, ScanTask] = {}
        
        # Worker management
        self.workers: Dict[str, WorkerNode] = {}
        self.worker_assignments: Dict[str, List[str]] = {}
        
        # Results aggregation
        self.vulnerabilities_found: List[Dict] = []
        self.payload_success_rate: Dict[str, float] = {}
        
        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'vulnerabilities_found': 0,
            'total_payloads_tested': 0,
            'start_time': None,
            'end_time': None,
        }
        
        # Locks for thread safety
        self.task_lock = threading.Lock()
        self.worker_lock = threading.Lock()
        
        print(f"[SWARM] Distributed Swarm Coordinator initialized")
        print(f"   Max workers: {max_workers}")
        print(f"   Coordinator port: {coordinator_port}")
    
    def register_worker(self, worker_id: str, capabilities: Dict = None) -> WorkerNode:
        """Register a new worker node"""
        with self.worker_lock:
            if worker_id in self.workers:
                print(f"[WARN] Worker {worker_id} already registered, updating...")
            
            worker = WorkerNode(
                node_id=worker_id,
                capabilities=capabilities or {}
            )
            self.workers[worker_id] = worker
            self.worker_assignments[worker_id] = []
            
            print(f"[SWARM] Worker {worker_id} registered")
            return worker
    
    def submit_scan_job(self, target_url: str, injection_points: List[Dict], 
                       payloads: List[str]) -> str:
        """
        Submit a scanning job to be distributed across workers
        
        Args:
            target_url: Target URL to scan
            injection_points: List of injection points to test
            payloads: Payloads to test at each point
        
        Returns:
            Job ID
        """
        job_id = hashlib.md5(f"{target_url}_{time.time()}".encode()).hexdigest()
        
        print(f"[SWARM] Submitting scan job {job_id}")
        print(f"   Target: {target_url}")
        print(f"   Injection points: {len(injection_points)}")
        print(f"   Payloads: {len(payloads)}")
        
        # Create tasks for each injection point
        tasks_created = 0
        for point in injection_points:
            # Split payloads into chunks for parallel testing
            chunk_size = 10
            for i in range(0, len(payloads), chunk_size):
                payload_chunk = payloads[i:i + chunk_size]
                
                task = ScanTask(
                    task_id=None,  # Will be auto-generated
                    url=target_url,
                    injection_point=point,
                    payloads=payload_chunk,
                    priority=self._calculate_priority(point, target_url)
                )
                
                with self.task_lock:
                    self.tasks[task.task_id] = task
                    # Use negative priority for max-heap behavior (higher priority first)
                    self.task_queue.put((-task.priority, task.task_id))
                    self.stats['total_tasks'] += 1
                
                tasks_created += 1
        
        print(f"[SWARM] Created {tasks_created} tasks for job {job_id}")
        return job_id
    
    def _calculate_priority(self, injection_point: Dict, url: str) -> int:
        """Calculate task priority based on injection point characteristics"""
        priority = 1
        
        # Form inputs are higher priority than URL params
        if injection_point.get('type') == 'form':
            priority += 2
        
        # Login/auth endpoints are higher priority
        if any(kw in url.lower() for kw in ['login', 'auth', 'admin', 'dashboard']):
            priority += 3
        
        # Reflected parameters are higher priority
        if injection_point.get('reflected', False):
            priority += 2
        
        return priority
    
    def get_next_task(self, worker_id: str) -> Optional[ScanTask]:
        """Get next task for a worker (work-stealing algorithm)"""
        with self.worker_lock:
            if worker_id not in self.workers:
                print(f"[WARN] Unknown worker {worker_id}")
                return None
            
            worker = self.workers[worker_id]
            if worker.status != 'idle':
                return None
        
        # Try to get task from queue
        try:
            _, task_id = self.task_queue.get_nowait()
            
            with self.task_lock:
                if task_id not in self.tasks:
                    return None
                
                task = self.tasks[task_id]
                if task.status != 'pending':
                    return None
                
                # Assign task to worker
                task.status = 'assigned'
                task.node_id = worker_id
                task.started_at = time.time()
            
            with self.worker_lock:
                worker.status = 'busy'
                worker.current_task = task_id
                self.worker_assignments[worker_id].append(task_id)
            
            return task
        
        except queue.Empty:
            return None
    
    def submit_task_result(self, worker_id: str, task_id: str, result: Dict):
        """Worker submits completed task result"""
        with self.task_lock:
            if task_id not in self.tasks:
                print(f"[WARN] Unknown task {task_id}")
                return
            
            task = self.tasks[task_id]
            task.status = 'completed'
            task.completed_at = time.time()
            task.result = result
            
            # Move to completed
            self.completed_tasks[task_id] = task
            del self.tasks[task_id]
            
            self.stats['completed_tasks'] += 1
            self.stats['total_payloads_tested'] += len(task.payloads)
            
            # Process results
            if result.get('vulnerable', False):
                self.vulnerabilities_found.append({
                    'url': task.url,
                    'injection_point': task.injection_point,
                    'payload': result.get('payload'),
                    'evidence': result.get('evidence'),
                    'discovered_by': worker_id,
                    'timestamp': task.completed_at
                })
                self.stats['vulnerabilities_found'] += 1
                print(f"[SWARM] Vulnerability found by worker {worker_id}!")
        
        # Update worker status
        with self.worker_lock:
            if worker_id in self.workers:
                worker = self.workers[worker_id]
                worker.status = 'idle'
                worker.current_task = None
                worker.tasks_completed += 1
                
                # Update average task time
                if task.completed_at and task.started_at:
                    task_time = task.completed_at - task.started_at
                    if worker.avg_task_time == 0:
                        worker.avg_task_time = task_time
                    else:
                        worker.avg_task_time = (worker.avg_task_time * 0.9 + task_time * 0.1)
    
    def report_task_failure(self, worker_id: str, task_id: str, error: str):
        """Worker reports task failure"""
        with self.task_lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = 'failed'
            task.completed_at = time.time()
            task.result = {'error': error}
            
            self.stats['failed_tasks'] += 1
            
            # Requeue task with lower priority
            new_priority = max(0, task.priority - 1)
            task.priority = new_priority
            task.status = 'pending'
            task.node_id = None
            self.task_queue.put((-new_priority, task_id))
        
        with self.worker_lock:
            if worker_id in self.workers:
                worker = self.workers[worker_id]
                worker.status = 'idle'
                worker.current_task = None
                worker.tasks_failed += 1
    
    def worker_heartbeat(self, worker_id: str):
        """Worker sends heartbeat signal"""
        with self.worker_lock:
            if worker_id in self.workers:
                self.workers[worker_id].last_heartbeat = time.time()
    
    def get_progress(self) -> Dict:
        """Get overall scanning progress"""
        total = self.stats['total_tasks']
        completed = self.stats['completed_tasks']
        failed = self.stats['failed_tasks']
        pending = total - completed - failed
        
        progress = (completed / total * 100) if total > 0 else 0
        
        # Calculate ETA
        if self.stats['start_time'] and completed > 0:
            elapsed = time.time() - self.stats['start_time']
            rate = completed / elapsed if elapsed > 0 else 0
            eta = (total - completed) / rate if rate > 0 else 0
        else:
            eta = 0
        
        return {
            'total_tasks': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'progress_percent': progress,
            'vulnerabilities_found': self.stats['vulnerabilities_found'],
            'active_workers': sum(1 for w in self.workers.values() if w.status == 'busy'),
            'total_workers': len(self.workers),
            'eta_seconds': eta,
            'payloads_tested': self.stats['total_payloads_tested']
        }
    
    async def run_distributed_scan(self, target_url: str, injection_points: List[Dict],
                                   payloads: List[str], num_local_workers: int = 4):
        """
        Run a complete distributed scan with local workers
        
        Args:
            target_url: Target URL
            injection_points: Injection points to test
            payloads: Payloads to test
            num_local_workers: Number of local worker threads
        """
        print("\n[SWARM] Starting Distributed Swarm Scan")
        print("="*70)
        
        self.stats['start_time'] = time.time()
        
        # Register local workers
        for i in range(num_local_workers):
            worker_id = f"local_worker_{i}"
            self.register_worker(worker_id, {
                'type': 'local',
                'max_concurrent': 5
            })
        
        # Submit job
        job_id = self.submit_scan_job(target_url, injection_points, payloads)
        
        # Start worker threads
        executor = ThreadPoolExecutor(max_workers=num_local_workers)
        worker_futures = []
        
        for worker_id in list(self.workers.keys()):
            future = executor.submit(self._worker_loop, worker_id)
            worker_futures.append(future)
        
        # Monitor progress
        while True:
            progress = self.get_progress()
            
            print(f"\r[SWARM] Progress: {progress['progress_percent']:.1f}% | "
                  f"Completed: {progress['completed']}/{progress['total_tasks']} | "
                  f"Vulnerabilities: {progress['vulnerabilities_found']} | "
                  f"Workers: {progress['active_workers']}/{progress['total_workers']}", 
                  end='', flush=True)
            
            if progress['completed'] + progress['failed'] >= progress['total_tasks']:
                break
            
            await asyncio.sleep(1)
        
        # Cleanup
        executor.shutdown(wait=True)
        
        self.stats['end_time'] = time.time()
        
        print("\n\n[SWARM] Distributed scan complete!")
        self._print_final_report()
        
        return self.get_results()
    
    def _worker_loop(self, worker_id: str):
        """Worker processing loop"""
        while True:
            # Get next task
            task = self.get_next_task(worker_id)
            
            if task is None:
                # No tasks available
                time.sleep(0.5)
                
                # Check if all tasks are done
                progress = self.get_progress()
                if progress['pending'] == 0 and progress['active_workers'] == 0:
                    break
                continue
            
            # Process task
            try:
                result = self._execute_task(task)
                self.submit_task_result(worker_id, task.task_id, result)
            except Exception as e:
                self.report_task_failure(worker_id, task.task_id, str(e))
            
            # Heartbeat
            self.worker_heartbeat(worker_id)
    
    def _execute_task(self, task: ScanTask) -> Dict:
        """Execute a scanning task"""
        for payload in task.payloads:
            try:
                # Inject payload
                if task.injection_point.get('type') == 'url_param':
                    params = {task.injection_point.get('param_name', 'q'): payload}
                    response = requests.get(task.url, params=params, timeout=10)
                else:
                    data = {task.injection_point.get('param_name', 'input'): payload}
                    response = requests.post(task.url, data=data, timeout=10)
                
                # Check if vulnerable
                if payload in response.text:
                    return {
                        'vulnerable': True,
                        'payload': payload,
                        'evidence': response.text[:500],
                        'status_code': response.status_code
                    }
            
            except Exception as e:
                continue
        
        return {'vulnerable': False}
    
    def get_results(self) -> Dict:
        """Get final scan results"""
        duration = 0
        if self.stats['end_time'] and self.stats['start_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
        
        return {
            'vulnerabilities': self.vulnerabilities_found,
            'statistics': self.stats,
            'duration': duration,
            'worker_performance': {
                worker_id: {
                    'tasks_completed': worker.tasks_completed,
                    'tasks_failed': worker.tasks_failed,
                    'avg_task_time': worker.avg_task_time
                }
                for worker_id, worker in self.workers.items()
            }
        }
    
    def _print_final_report(self):
        """Print final scan report"""
        duration = 0
        if self.stats['end_time'] and self.stats['start_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "="*70)
        print("[SWARM] DISTRIBUTED SCAN REPORT")
        print("="*70)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Total tasks: {self.stats['total_tasks']}")
        print(f"Completed: {self.stats['completed_tasks']}")
        print(f"Failed: {self.stats['failed_tasks']}")
        print(f"Vulnerabilities found: {self.stats['vulnerabilities_found']}")
        print(f"Payloads tested: {self.stats['total_payloads_tested']}")
        if duration > 0:
            print(f"Rate: {self.stats['total_payloads_tested'] / duration:.1f} payloads/sec")
        print(f"Workers used: {len(self.workers)}")
        print("="*70)


# ==================== CLOUD WORKER INTEGRATION ====================

class CloudWorkerLauncher:
    """
    Launches workers on cloud platforms (AWS Lambda, Google Cloud Functions)
    """
    
    def __init__(self, platform='aws'):
        self.platform = platform
        self.deployed_functions = []
    
    async def deploy_workers(self, count: int, coordinator_url: str):
        """Deploy serverless workers to cloud"""
        print(f"[CLOUD] Deploying {count} workers to {self.platform}...")
        
        if self.platform == 'aws':
            await self._deploy_aws_lambda(count, coordinator_url)
        elif self.platform == 'gcp':
            await self._deploy_gcp_functions(count, coordinator_url)
        
        print(f"[CLOUD] {count} cloud workers deployed")
    
    async def _deploy_aws_lambda(self, count: int, coordinator_url: str):
        """Deploy to AWS Lambda"""
        # This would use boto3 to deploy Lambda functions
        # Simplified for demonstration
        print(f"   Deploying to AWS Lambda...")
        print(f"   Region: us-east-1")
        print(f"   Memory: 512 MB")
        print(f"   Timeout: 300 seconds")
        
        for i in range(count):
            function_name = f"xss-sentinel-worker-{i}"
            # boto3.client('lambda').create_function(...)
            self.deployed_functions.append(function_name)
    
    async def _deploy_gcp_functions(self, count: int, coordinator_url: str):
        """Deploy to Google Cloud Functions"""
        print(f"   Deploying to Google Cloud Functions...")
        # Implementation here


# ==================== USAGE EXAMPLE ====================

async def main():
    # Initialize coordinator
    coordinator = DistributedSwarmCoordinator(max_workers=10)
    
    # Define target
    target_url = "https://example.com/search"
    injection_points = [
        {'type': 'url_param', 'param_name': 'q'},
        {'type': 'url_param', 'param_name': 'category'},
    ]
    
    # Generate payloads (would use neural engine here)
    payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
    ] * 10  # 30 payloads total
    
    # Run distributed scan
    results = await coordinator.run_distributed_scan(
        target_url,
        injection_points,
        payloads,
        num_local_workers=4
    )
    
    print(f"\n[SWARM] Found {len(results['vulnerabilities'])} vulnerabilities")
    for vuln in results['vulnerabilities']:
        print(f"   - {vuln['url']} | {vuln['payload'][:50]}")


if __name__ == "__main__":
    asyncio.run(main())
