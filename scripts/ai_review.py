#!/usr/bin/env python3
"""
Скрипт для ИИ-ревью Pull Request.
Использует OpenAI API для анализа изменений в PR и генерации комментария.
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional
import requests

# Конфигурация
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
GITHUB_PR_NUMBER = os.environ.get("GITHUB_PR_NUMBER")
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}"

def get_diff() -> str:
    """Получить diff изменений в PR."""
    try:
        # Используем git для получения diff между текущей веткой и целевой
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "--no-prefix"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Ошибка получения diff: {e}")
        # Альтернативный способ: использовать GitHub API
        return ""

def analyze_with_ai(diff_text: str) -> Optional[str]:
    """Анализ diff с помощью OpenAI API."""
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY не установлен. Используем заглушку.")
        return generate_stub_review(diff_text)
    
    prompt = f"""
Ты — опытный код-ревьюер. Проанализируй следующие изменения в коде и предоставь краткий отчёт:
1. Общее описание изменений
2. Потенциальные проблемы (баги, security issues, performance)
3. Советы по улучшению кода (стиль, лучшие практики)
4. Оценка качества изменений

Diff:
```
{diff_text[:4000]}  # Ограничиваем размер из-за лимитов токенов
```

Ответ должен быть на русском языке, структурированным, кратким и полезным.
"""
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Ты — опытный код-ревьюер Python/ FastAPI проектов."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Ошибка при запросе к OpenAI API: {e}")
        return generate_stub_review(diff_text)

def generate_stub_review(diff_text: str) -> str:
    """Заглушка для ревью, если API недоступно."""
    lines = diff_text.count('\n')
    files = len([line for line in diff_text.split('\n') if line.startswith('diff --git')])
    
    return f"""
## 🤖 Автоматическое ИИ-ревью (заглушка)

**Обзор изменений:**
- Изменено файлов: {files}
- Строк кода: {lines}

**Рекомендации:**
1. Проверьте, что все новые зависимости добавлены в requirements.txt
2. Убедитесь, что миграции базы данных корректно созданы
3. Проверьте покрытие тестами новых функций

*Примечание: Для полноценного ИИ-ревью установите OPENAI_API_KEY в секретах GitHub.*
"""

def post_comment_to_pr(comment: str) -> bool:
    """Опубликовать комментарий в PR."""
    if not GITHUB_TOKEN or not GITHUB_PR_NUMBER:
        print("GITHUB_TOKEN или GITHUB_PR_NUMBER не установлены. Пропускаем публикацию.")
        print("Сгенерированный комментарий:")
        print(comment)
        return False
    
    url = f"{GITHUB_API_URL}/issues/{GITHUB_PR_NUMBER}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 201:
            print("Комментарий успешно опубликован в PR.")
            return True
        else:
            print(f"Ошибка публикации комментария: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Ошибка при публикации комментария: {e}")
        return False

def main():
    """Основная функция."""
    print("🚀 Запуск ИИ-ревью PR...")
    
    # Получаем diff
    diff_text = get_diff()
    if not diff_text:
        print("Не удалось получить diff. Используем пустой diff.")
        diff_text = "Нет изменений для анализа."
    
    # Анализируем с ИИ
    review = analyze_with_ai(diff_text)
    
    # Публикуем комментарий
    success = post_comment_to_pr(review)
    
    if success:
        print("✅ ИИ-ревью завершено успешно.")
    else:
        print("⚠️ ИИ-ревью завершено с предупреждениями.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()