// knowledge_base.js
// Пока заглушка — интерактив добавим позже

document.addEventListener('DOMContentLoaded', function() {
    console.log('📚 База знаний загружена');

    // Пример: клик по папке (пока просто лог)
    document.querySelectorAll('.folder-item').forEach(item => {
        item.addEventListener('click', function() {
            const folderId = this.dataset.id;
            console.log('Выбрана папка:', folderId);
            // Позже: загрузка заметок этой папки через AJAX
        });
    });

    // Пример: клик по заметке
    document.querySelectorAll('.note-card').forEach(card => {
        card.addEventListener('click', function() {
            const noteId = this.dataset.id;
            console.log('Открыта заметка:', noteId);
            // Позже: переход к редактору
        });
    });
});