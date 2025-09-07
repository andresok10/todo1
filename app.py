from flask import (Flask,render_template,request,send_from_directory,redirect,url_for,
    send_file,
    flash,
    get_flashed_messages,
    jsonify,
)
import json
import requests
import calendar, os
from datetime import datetime
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.context_processor
def inject_globals():
    return {"hoy": datetime.today()}

signos = [
        ("Capricornio", (12, 22), (1, 19)),
        ("Acuario", (1, 20), (2, 18)),
        ("Piscis", (2, 19), (3, 20)),
        ("Aries", (3, 21), (4, 19)),
        ("Tauro", (4, 20), (5, 20)),
        ("Géminis", (5, 21), (6, 20)),
        ("Cáncer", (6, 21), (7, 22)),
        ("Leo", (7, 23), (8, 22)),
        ("Virgo", (8, 23), (9, 22)),
        ("Libra", (9, 23), (10, 22)),
        ("Escorpio", (10, 23), (11, 21)),
        ("Sagitario", (11, 22), (12, 21)),
]
@app.route("/", methods=["GET", "POST"])
@app.route("/calen", methods=["GET", "POST"])
def calendario():
    msg = ""
    hoy = datetime.today()
    meses = [
        {
            "nombre": calendar.month_name[m],
            "mes_numero": m,
            "semanas": calendar.Calendar().monthdayscalendar(hoy.year, m),
        }
        for m in range(hoy.month, 13)
    ]
    #print(meses)

    edad = ""
    fn = ""
    signo = ""
    cumple = ""
    faltan = None
    descuento = None

    if request.method == "POST":
        try:
            fnx = datetime.strptime(request.form.get("fecha_nacimiento", ""), "%d/%m/%Y")
            edad = hoy.year - fnx.year - ((hoy.month, hoy.day) < (fnx.month, fnx.day))
            cumplex = fnx.replace(year=hoy.year)
            print(cumplex)
            ###########
            if cumplex < hoy:
                cumplex = cumplex.replace(year=hoy.year + 1)
            ###########
            faltan = (cumplex - hoy).days
            ###########
            #signo = next(s for s, (m1, d1), (m2, d2) in signos
            #    if (fnx.month == m1 and fnx.day >= d1) or (fnx.month == m2 and fnx.day <= d2)
            #)
            
            for s, (m1, d1), (m2, d2) in signos:
                if (fnx.month == m1 and fnx.day >= d1) or (fnx.month == m2 and fnx.day <= d2):
                    signo = s
                    break
            ###########
            # aquí conviertes a string formateado
            fn = fnx.strftime("%d/%m/%Y")
            cumple = cumplex.strftime("%d/%m/%Y")
            print(cumple)
        except:
            #edad = "Ingrese fecha correcta: dia/mes/año"
            msg = ""
        ###############################################################
        try:
            monto = float(request.form.get("monto", 0))
            porcentaje = float(request.form.get("porcentaje", 0))
            descuento = monto - (monto * porcentaje / 100)
        except:
            #descuento = "Error en los datos ingresados"
            msg = ""
    
    # recoger mensajes de la descarga si existen
    msg = request.args.get("msg", "")
    msg_type = request.args.get("msg_type", "")
    download_url = request.args.get("download_url", "") # download_url=download_url,

    return render_template("app.html",
        msg=msg,
        msg_type=msg_type,
        download_url=download_url,
        hoy=hoy,
        meses=meses,
        edad=edad,
        fn=fn,
        signo=signo,
        cumple=cumple,
        faltan=faltan,
        descuento=descuento,
    )

############################################################################
# Carpeta base donde están los archivos que vas a descargar
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
# Crear la carpeta si no existe
# os.makedirs(BASE_DIR, exist_ok=True)

# @app.route("/descargar", methods=["GET", "POST"])
@app.route("/descargar", methods=["POST"])
def descargar():
    # download_url = None
    #msg = ""
    #msg_type = ""
    if request.method == "POST":
        url = request.form.get("url").split("?")[0]  # Limpiar la URL
        # url = request.form.get("url")
        download_type = request.form.get("download_type")
        # extension = 'mp3' if download_type == 'audio' else 'mp4'
        extension = "m4a" if download_type == "audio" else "webm"
        counter = 1
        while True:
            # filename = os.path.join(output1, f"{counter}.{extension}")
            # output_file = os.path.join(DOWNLOADS_DIR, f"{counter}.{extension}")
            filename = os.path.join(BASE_DIR, f"{counter}.{extension}")
            if not os.path.exists(filename):
                break
            counter += 1
        format_flag = "bestaudio" if download_type == "audio" else "best"
        ydl_opts = {
            "format": format_flag,
            "outtmpl": filename,
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            msgx = f"{download_type.capitalize()} descargado con éxito como {os.path.basename(filename)}."
            #print(msg.data)
            #msg = json.loads(msgx.data)
            #return redirect(url_for("calendario",msg))
            #return render_template("app.html",msg=msg)
            return jsonify(
                {
                    "status": "success",
                    "msg": msgx,
                    "download_url": url_for("serve_download", filename=os.path.basename(filename)),
                }
            )
        except Exception as e:
                msg = "Error al descargar el archivo: URL no válida"
                return jsonify({"status": "error", "msg": msg})

## Si quieres habilitar descarga directa de archivos:
'''@app.route("/downloads/<path:filename>")
# @app.route("/download/<path:output_file>")
def serve_download(filename):
    filename = os.path.basename(filename)
    # print(filename) # 1.webm
    # filename = os.path.join(BASE_DIR, os.path.basename(filename))
    # print(filename)
    # file_path = os.path.join(BASE_DIR, filename)

    # return send_from_directory(file_path, filename, as_attachment=True)
    # return send_from_directory("downloads", output_file, as_attachment=True)
    return send_from_directory(BASE_DIR, filename, as_attachment=True)'''
    
@app.route("/descargar_flutter", methods=["POST"])
def descargarx():
    try:
        data = request.get_json()  # <- Esto reemplaza request.form
        url = data.get("url")
        download_type = data.get("download_type", "video")

        if not url:
            return jsonify({"status": "error", "msg": "No se proporcionó URL"}), 400

        # Limpiar la URL eliminando parámetros
        url = url.split("?")[0]

        extension = "m4a" if download_type == "audio" else "webm"
        counter = 1
        while True:
            filename = os.path.join(BASE_DIR, f"{counter}.{extension}")
            if not os.path.exists(filename):
                break
            counter += 1

        format_flag = "bestaudio" if download_type == "audio" else "best"
        ydl_opts = {
            "format": format_flag,
            "outtmpl": filename,
            "quiet": True,
            "no_warnings": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        msgx = f"{download_type.capitalize()} descargado con éxito como {os.path.basename(filename)}."
        return jsonify({
            "status": "success",
            "msg": msgx,
            "download_url": f"/downloads/{os.path.basename(filename)}"
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"Error al descargar el archivo: {str(e)}"}), 500

@app.route("/downloads/<path:filename>")
def serve_download(filename):
    return send_from_directory(BASE_DIR, os.path.basename(filename), as_attachment=True)

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)