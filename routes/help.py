"""
Маршруты: Страница помощи с загрузкой из файлов
"""

import os
from flask import Blueprint, render_template
from database import get_db_connection

bp = Blueprint('help', __name__)


@bp.route('/help')
def help_page():
    """Страница помощи с загрузкой из текстовых файлов"""

    arch_folder = os.path.join('help_text', 'architecture')
    code_folder = os.path.join('help_text', 'code')

    # Чтение файлов архитектуры
    arch_files = []
    if os.path.exists(arch_folder):
        for filename in sorted(os.listdir(arch_folder)):
            if filename.endswith('.txt'):
                filepath = os.path.join(arch_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                title = filename[:-4].replace('_', ' ').title()
                arch_files.append({
                    'title': title,
                    'content': content,
                    'filename': filename
                })

    # Чтение файлов с кодом
    code_files = []
    if os.path.exists(code_folder):
        for filename in sorted(os.listdir(code_folder)):
            if filename.endswith('.txt'):
                filepath = os.path.join(code_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                title = filename[:-4].replace('_', ' ').title()
                code_files.append({
                    'title': title,
                    'content': content,
                    'filename': filename
                })

    return render_template('help.html',
                           arch_sections=arch_files,
                           code_sections=code_files)