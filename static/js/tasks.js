/**
 * Завершение задачи через AJAX
 */
function completeTask(taskId, xpReward) {
    if (!confirm('Выполнить задачу и получить ' + xpReward + ' XP?')) {
        return;
    }

    fetch(`/api/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Находим карточку задачи и скрываем её
            const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
            if (taskCard) {
                taskCard.style.opacity = '0.5';
                taskCard.style.pointerEvents = 'none';
                setTimeout(() => {
                    taskCard.remove();
                }, 500);
            }

            // Показываем уведомление
            showNotification(`+${xpReward} XP получено! 🎉`);
        } else {
            showNotification('Ошибка при выполнении задачи', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка соединения', 'error');
    });
}

/**
 * Показ уведомления
 */
function showNotification(message, type = 'success') {
    const notif = document.createElement('div');
    notif.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? 'linear-gradient(135deg, #4CAF50, #66BB6A)' : 'linear-gradient(135deg, #f44336, #ef5350)'};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
        animation: slideIn 0.3s ease;
        z-index: 10000;
    `;
    notif.textContent = message;
    document.body.appendChild(notif);

    setTimeout(() => {
        notif.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

// Добавляем анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);