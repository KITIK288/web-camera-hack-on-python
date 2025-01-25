import cv2  # Импорт библиотеки OpenCV для работы с видеопотоками
from flask import Flask, Response, render_template, redirect, url_for  # Импорт необходимых классов и функций из Flask
import threading  # Импорт модуля threading для работы с потоками

app = Flask(__name__)  # Создаем экземпляр приложения Flask
video_thread = None  # Переменная для хранения потока видеозаписи
cap = None  # Переменная для захвата видео
stream_active = False  # Флаг, указывающий, активен ли видеопоток

def start_video_stream():
    global cap  # Объявляем, что будем использовать глобальную переменную cap
    cap = cv2.VideoCapture(0)  # Инициализируем захват видео с камеры (индекс 0 - первая камера)
    while True:  # Бесконечный цикл для получения кадров
        if cap.isOpened():  # Проверяем, успешно ли открыт видеопоток
            success, frame = cap.read()  # Читаем кадр из видеопотока
            if not success:  # Если не удалось прочитать кадр, прерываем цикл
                break
            ret, buffer = cv2.imencode('.jpg', frame)  # Кодируем кадр в формат JPG
            frame = buffer.tobytes()  # Преобразуем закодированный кадр в байты
            yield (b'--frame\r\n'  # Формируем ответ для HTTP стрима
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Возвращаем заголовки и данные кадра

@app.route('/')  # Определяем маршрут для главной страницы
def index():
    return render_template('index.html')  # Возвращаем рендеринг шаблона index.html

@app.route('/video_feed')  # Определяем маршрут для видеопотока
def video_feed():
    return Response(start_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Возвращаем видеопоток

@app.route('/start_stream')  # Определяем маршрут для начала видеопотока
def start_stream():
    global video_thread, stream_active  # Объявляем, что будем использовать глобальные переменные
    if video_thread is None or not video_thread.is_alive():  # Проверяем, не запущен ли уже поток
        video_thread = threading.Thread(target=start_video_stream)  # Создаем новый поток для захвата видео
        video_thread.start()  # Запускаем поток
        stream_active = True  # Устанавливаем флаг, что поток активен
    return redirect(url_for('index'))  # Перенаправляем на главную страницу

@app.route('/stop_stream')  # Определяем маршрут для остановки видеопотока
def stop_stream():
    global cap, stream_active  # Объявляем, что будем использовать глобальные переменные
    if cap is not None:  # Если видеозахват существует
        cap.release()  # Освобождаем ресурс видеозахвата
        cap = None  # Обнуляем переменную cap
    stream_active = False  # Сбрасываем флаг, что поток остановлен
    return redirect(url_for('index'))  # Перенаправляем на главную страницу

@app.route('/hidden_video_stream')  # Определяем маршрут для скрытого видеопотока
def hidden_video_stream():
    if stream_active:  # Проверяем, активен ли поток
        return Response(start_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Возвращаем видеопоток
    else:
        return redirect(url_for('index'))  # Перенаправляем на главную страницу, если поток не активен

@app.route('/view_video')  # Определяем защищенную страницу для просмотра видео
def view_video():
    return render_template('video.html')  # Возвращаем рендеринг шаблона video.html

if __name__ == '__main__':  # Проверяем, является ли данный модуль основным
    app.run(host='0.0.0.0', port=5001)  # Запускаем приложение на всех интерфейсах на порту 5001
