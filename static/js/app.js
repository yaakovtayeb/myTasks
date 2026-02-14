// Modal Management
function showAddTaskModal() {
    document.getElementById('addTaskModal').classList.remove('hidden');
}

function showAddSubtaskModal(taskId) {
    document.getElementById('subtaskTaskId').value = taskId;
    document.getElementById('addSubtaskModal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
    // Reset forms
    if (modalId === 'addTaskModal') {
        document.getElementById('addTaskForm').reset();
    } else if (modalId === 'addSubtaskModal') {
        document.getElementById('addSubtaskForm').reset();
    } else if (modalId === 'editTaskModal') {
        document.getElementById('editTaskForm').reset();
    }
}

// Task Details Toggle
function toggleTaskDetails(taskId) {
    const details = document.getElementById('details-' + taskId);
    if (details) {
        details.classList.toggle('hidden');
    }
}

// Add Task Handler
function handleAddTask(event) {
    event.preventDefault();

    const title = document.getElementById('taskTitle').value.trim();
    const type = document.getElementById('taskType').value;
    const status = document.getElementById('taskStatus').value;
    const timeEstimate = document.getElementById('taskTimeEstimate').value.trim();
    const notes = document.getElementById('taskNotes').value.trim();
    const linksText = document.getElementById('taskLinks').value.trim();
    const links = linksText ? linksText.split('\n').map(l => l.trim()).filter(l => l) : [];

    fetch('/api/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title,
            type: type,
            status: status,
            time_estimate: timeEstimate,
            notes: notes,
            links: links
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Task added successfully', 'success');
            closeModal('addTaskModal');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding task', 'error');
    });
}

// Complete Task Handler
function handleTaskComplete(taskId) {
    const finishDate = prompt('Enter finish date (YYYY-MM-DD):');
    if (!finishDate) {
        // User cancelled, uncheck the checkbox
        event.target.checked = false;
        return;
    }

    // Validate date format
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    if (!datePattern.test(finishDate)) {
        showNotification('Invalid date format. Use YYYY-MM-DD', 'error');
        event.target.checked = false;
        return;
    }

    fetch(`/api/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            finish_date: finishDate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Task completed', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
            event.target.checked = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error completing task', 'error');
        event.target.checked = false;
    });
}

// Move Task to Current
function moveToCurrentTask(taskId) {
    if (!confirm('Move this task to current status?')) {
        return;
    }

    fetch(`/api/tasks/${taskId}/current`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Task moved to current', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error moving task', 'error');
    });
}

// Show Edit Task Modal
function showEditTaskModal(taskId) {
    // Fetch task details
    fetch(`/api/tasks/${taskId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const task = data.task;

            // Populate form fields
            document.getElementById('editTaskId').value = task.id;
            document.getElementById('editTaskTitle').value = task.title;
            document.getElementById('editTaskType').value = task.type;
            document.getElementById('editTaskTimeEstimate').value = task.time_estimate || '';
            document.getElementById('editTaskNotes').value = task.notes || '';
            document.getElementById('editTaskLinks').value = task.links ? task.links.join('\n') : '';

            // Show modal
            document.getElementById('editTaskModal').classList.remove('hidden');
        } else {
            showNotification('Error loading task: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error loading task', 'error');
    });
}

// Edit Task Handler
function handleEditTask(event) {
    event.preventDefault();

    const taskId = document.getElementById('editTaskId').value;
    const title = document.getElementById('editTaskTitle').value.trim();
    const type = document.getElementById('editTaskType').value;
    const timeEstimate = document.getElementById('editTaskTimeEstimate').value.trim();
    const notes = document.getElementById('editTaskNotes').value.trim();
    const linksText = document.getElementById('editTaskLinks').value.trim();
    const links = linksText ? linksText.split('\n').map(l => l.trim()).filter(l => l) : [];

    fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title,
            type: type,
            time_estimate: timeEstimate,
            notes: notes,
            links: links
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Task updated successfully', 'success');
            closeModal('editTaskModal');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating task', 'error');
    });
}

// Add Subtask Handler
function handleAddSubtask(event) {
    event.preventDefault();

    const taskId = document.getElementById('subtaskTaskId').value;
    const title = document.getElementById('subtaskTitle').value.trim();

    fetch(`/api/tasks/${taskId}/subtasks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Subtask added', 'success');
            closeModal('addSubtaskModal');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding subtask', 'error');
    });
}

// Toggle Subtask Completion
function toggleSubtask(taskId, subtaskId) {
    fetch(`/api/tasks/${taskId}/subtasks/${subtaskId}/toggle`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Subtask updated', 'success');
            // Optionally reload to update UI
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating subtask', 'error');
    });
}

// Notification Display
function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = 'notification ' + type;
    setTimeout(() => {
        notification.className = 'notification hidden';
    }, 3000);
}

// Close modals on clicking outside
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.add('hidden');
    }
});
