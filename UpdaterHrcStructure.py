import os
import requests
import subprocess
import shutil
import time


print("Iniciando Atualização")
# Diretórios temporários

temp_dir_updater = "C:\\TempHRCUpdater"
temp_dir_install = "C:\\TempHRCInstall"


print("Baixando Install do GitHub")
# URL do Install.exe no GitHub
install_exe_url = "https://github.com/1rforti/HRC-structure/raw/master/install.exe"

print("Baixando Install2  e atualizando Updater")
# URLs dos arquivos adicionais
updater_gif_url = "https://github.com/1rforti/HRC-structure/raw/master/HRCStructure_updater.gif"
favicon_ico_url = "https://github.com/1rforti/HRC-structure/raw/master/favicon.ico"


print("Criando Diretorios temporários")
def create_temp_directories():
    # Verificar e apagar diretórios temporários se existirem
    
    if os.path.exists(temp_dir_updater):
        shutil.rmtree(temp_dir_updater)
    if os.path.exists(temp_dir_install):
        shutil.rmtree(temp_dir_install)

    # Criar diretórios temporários
    
    os.makedirs(temp_dir_updater, exist_ok=True)
    os.makedirs(temp_dir_install, exist_ok=True)

def download_file(url, destination_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(destination_path, "wb") as file:
            file.write(response.content)
    except Exception as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return None

    return destination_path

def main():
    create_temp_directories()
    
    print("Carregando Diretorios temporários")
    time.sleep(10)
    
    # Baixar o Install.exe
    install_path = download_file(install_exe_url, os.path.join(temp_dir_install, "Install.exe"))
    
    # Baixar o HRCStructure_updater.gif
    updater_gif_path = download_file(updater_gif_url, os.path.join(temp_dir_install, "HRCStructure_updater.gif"))
    
    # Baixar o Install2.py
    favicon_ico_path = download_file(favicon_ico_url, os.path.join(temp_dir_install, "favicon.ico"))
    
  
    print("Inicializando Instalação limpa")
    time.sleep(10)


    if install_path:
        # Executar o Install.exe

        # Defina o diretório de trabalho atual como o diretório onde o Install.exe está localizado
        install_dir = os.path.dirname(install_path)       

        try:
            subprocess.Popen("C:\\TempHRCInstall\\Install.exe", cwd=install_dir)
            print("Install.exe iniciado com sucesso.")
        except FileNotFoundError:
            print("O arquivo Install.exe não foi encontrado.")
        except PermissionError:
            print("Permissão negada para executar o Install.exe.")
        except Exception as e:
            print(f"Erro ao executar o Install.exe: {e}")
        except Exception as e:  
           
    
            print("Encerrando HRCStructure_updater e Inicializando Instalação limpa")
            time.sleep(10)


if __name__ == "__main__":
    main()
