# pip install opencv-python flask

import tkinter as tk
from tkinter import messagebox
import cv2
import threading
from flask import Flask, Response

# Variável global para controlar o fluxo da câmara
capture = None

# Função para iniciar a câmara
def start_camera():
    global capture
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        messagebox.showerror("Erro", "Não foi possível acessar a câmara.")
        return

    def show_camera():
        while capture.isOpened():
            ret, frame = capture.read()
            if not ret:
                break
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) == 27:  # Pressione 'ESC' para sair
                break
        capture.release()
        cv2.destroyAllWindows()

    threading.Thread(target=show_camera).start()

# Função para iniciar o servidor de streaming
def start_stream_server():
    app = Flask(__name__)

    def gen_frames():
        global capture
        while True:
            success, frame = capture.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    messagebox.showinfo("Servidor de Streaming", "Servidor iniciado em http://0.0.0.0:5000/video_feed")

# Função para sair da aplicação
def quit_app():
    if capture and capture.isOpened():
        capture.release()
    root.destroy()

# Criação da interface gráfica
root = tk.Tk()
root.title("Controle de Streaming")

btn_start_camera = tk.Button(root, text="Ligar Câmara", command=start_camera)
btn_start_camera.pack(pady=10)

btn_start_server = tk.Button(root, text="Ligar Servidor de Stream", command=start_stream_server)
btn_start_server.pack(pady=10)

btn_quit = tk.Button(root, text="Sair", command=quit_app)
btn_quit.pack(pady=10)

root.mainloop()
