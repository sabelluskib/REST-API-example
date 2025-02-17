from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
from PIL import Image
import os
import mimetypes
import time
from subprocess import run,call


#указываем приложение FastAPI
app = FastAPI()

# Директория для хранения загружаемых файлов
U_DIR = "./uploads_files/"
MINIS = "./miniature/"
def ffmpeg(f_path_viedo: str ,p_save: str):
    call("ffmpeg -i " + f_path_viedo +" -ss 00:00:00 -vframes 1 "+p_save+" -y", shell=True, timeout=5)

#Указываем искомые директории
os.makedirs(U_DIR, exist_ok=True) 
os.makedirs(MINIS, exist_ok=True)
@app.put("/api/files/")
async def upload_file(file: UploadFile = File(...)):
    # Cоздаем UUID для файла
    f_id = uuid4()
    # Указываем путь для файла
    file_path = os.path.join(U_DIR, f"{f_id}_{file.filename}")
    # Чтение файла
    contents = await file.read()
    # Записываем файл
    with open(file_path, "wb") as f:
        f.write(contents)
    # Получаем объем файла
    file_size = os.path.getsize(file_path)
    #Определяем тип файла
    mimetype = mimetypes.guess_type(file_path)
    #Проверяем, какой файл нам отправили
    if ("image" in mimetype[0]) or ("video" in mimetype[0]): 
    #Отправляем информацию о файле
       return {"uuid": str(f_id), "size": file_size, "mime": mimetype[0]}
    else:
       raise HTTPException(status_code=500,detail="File is not an image or video") #отправляем ошибку, если он нас не удовлетворяет
       return {"File is not an image or video"}
@app.put("/api/files/{file_uuid}")
async def update_item(file_uuid: str, length: int | None = None, width: int | None = None ):
    #находим файл по UUID с перебором for
    #рассматриваем случай без создания миниаютр (None в размерах)
    k = 0
    if (width == None) and (length == None): 
        for filename in os.listdir(U_DIR):
            if file_uuid in filename:
                if len(file_uuid) == 36:
                    k = k+1
                    mime = mimetypes.guess_type(f"{U_DIR}/{filename}") #узнаем тип файла 
                    if "image" in mime[0]: #cлучай с фото
                        return FileResponse(f"{U_DIR}/{filename}")
                    if "video" in mime[0]: #случай с видео
                        full_path_video = f"{U_DIR}{filename}" #путь к видео
                        file_path_frame = os.path.join(MINIS, f"frame_{file_uuid}.png") #путь к кадру
                        ffmpeg(full_path_video, file_path_frame) #запускаем ffmpeg для обработки видео
                        return FileResponse(file_path_frame) #отправляем файл
                else:
                    raise HTTPException(status_code=404,detail="File not found")
    #рассмотрим случай, когда указан только один параметр
    if ((width == None) and (length != None)) or (((width != None) and (length == None))):
        if ((width == None) and (length != None)):
           raise HTTPException(status_code=500,detail="Width parameter not specified") #высылаем ошибку
           return {"width parameter not specified"} #записываем комментарий в файл
        if ((width != None) and (length == None)):
           raise HTTPException(status_code=500,detail="Length parameter not specified")
           return {"Length parameter not specified"}
       
    #рассмотрим случай, когда указаны оба параметра
    if (width != None) and (length != None):
        for filename in os.listdir(U_DIR):
            if file_uuid in filename:
                if len(file_uuid) == 36:
                    k = k + 1
                    mime = mimetypes.guess_type(f"{U_DIR}/{filename}") #проверяем тип файла
                    if "image" in mime[0]:
                        #фиксируем путь к файлу миниатюры
                        file_path_mini = os.path.join(MINIS, f"mini_{filename}")
                        #фиксируем путь к исходному файлу
                        filename_full = f"{U_DIR}/{filename}"
                        try: #пробуем создать миниатюру
                            with Image.open(filename_full) as img: #делаем сокращение
                                img.thumbnail((length,width)) #создаем миниатюру
                                img.save(file_path_mini) #записываем миниатюру
                                return FileResponse(file_path_mini) #возвращаем файл
                        except Exception as e: #высылаем ошибку в случае неудачи
                            raise HTTPException(status_code=500,detail="Не удается создать миниатюру.")
                    if "video" in mime[0]:
                        full_path_video = f"{U_DIR}{filename}" #путь к видео
                        file_path_frame = os.path.join(MINIS, f"frame_{file_uuid}.png") #путь к кадру
                        ffmpeg(full_path_video, file_path_frame) #запускаем ffmpeg
                        try: #пробуем выполнить 
                            with Image.open(file_path_frame) as img: #делаем сокращение
                                img.thumbnail((length,width)) #создаем миниатюру
                                img.save(file_path_frame) #записываем файл
                                return FileResponse(file_path_frame) #возвращаем файл
                        except Exception as e:
                            raise HTTPException(status_code=500,detail="Не удается создать миниатюру.") #возращаем ошибку в случае неудачи 
                        return FileResponse(file_path_frame)
                else:
                    raise HTTPException(status_code=404,detail="File not found")

    if k == 0:
        raise HTTPException(status_code=404,detail="File not found")