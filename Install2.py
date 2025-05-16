import os
import requests
import subprocess
import shutil
import psutil 
import time


# Diretórios temporários
temp_dir_updater = "C:\\TempHRCUpdater"
install_dir = "C:\\HRCStructureHHHHeadsUp"

def remove_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Erro ao excluir arquivo {file_path}: {e}")

# Função para encerrar o processo pelo nome do executável
def kill_process_by_name(process_name):
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == process_name:
            try:
                os.kill(process.info['pid'], 9)
            except OSError:
                pass

# Função para verificar e encerrar quaisquer processos relacionados
def close_related_processes():
    # Encerre
    kill_process_by_name('HRCStructureHHHHeadsUp.exe')
    # Encerre
    kill_process_by_name('main.exe')
    # Encerre
    kill_process_by_name('main.py')
    # Encerre
    kill_process_by_name('mai2.exe')
    # Encerre
    kill_process_by_name('favicon.ico')

# Função2 para verificar e encerrar quaisquer processos relacionados 
def terminate_processes_in_directory(install_dir):
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            process_exe = process.exe()
            if process_exe and install_dir in process_exe.lower():
                process.terminate()
                process.wait(timeout=10)  # Aguarde até 10 segundos para o processo encerrar completamente
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
            
def wait_for_updater_completion():
    updater_process_name = "UpdaterHrcStructure.exe"

    while True:
        # Verifique todos os processos em execução
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if process.info['name'] == updater_process_name:
                try:
                    updater_process = psutil.Process(process.info['pid'])
                    updater_process.terminate()  # Tente encerrar o processo normalmente
                    updater_process.wait(timeout=10)  # Aguarde até 10 segundos para o processo encerrar completamente
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass

        # Verifique se o processo UpdaterHrcStructure não está mais em execução
        if not any(p.info['name'] == updater_process_name for p in psutil.process_iter()):
            break

        # Aguarde um curto período antes de verificar novamente
        time.sleep(5)

def download_repository():
    # URL do repositório GitHub
    github_url = "https://github.com/1rforti/HRC-structure/archive/master.zip"
    temp_zip_path = os.path.join(temp_dir_updater, "temp.zip")

    try:
        response = requests.get(github_url, stream=True)
        response.raise_for_status()
        with open(temp_zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        return temp_zip_path
    except Exception as e:
        print(f"Erro ao baixar o repositório: {e}")
        return None

def get_latest_commit_sha():
    github_api_url = "https://api.github.com/repos/1rforti/HRC-structure/commits/master"
    
    try:
        response = requests.get(github_api_url)
        response.raise_for_status()
        commit_data = response.json()
        latest_commit_sha = commit_data["sha"]
        return latest_commit_sha
    except Exception as e:
        print(f"Erro ao obter o commit mais recente: {e}")
        return None
    
def update_commit_sha(latest_commit_sha):
    commit_sha_path = os.path.join(install_dir, "commit_sha.txt")

    with open(commit_sha_path, "w") as file:
        file.write(latest_commit_sha)


def run_main_exe(install_dir):
    main_exe_path = os.path.join(install_dir, "app.exe")
    if os.path.exists(main_exe_path):
        try:
            subprocess.run([main_exe_path], cwd=install_dir, check=True)
        except Exception as e:
            print(f"Erro ao executar o main.exe: {e}")

def main():
    print("Inicializando o Install...")
    
    print(" # Passo 1: Aguardar o UpdaterHrcStructure ser encerrado")
    # Passo 1: Aguardar o UpdaterHrcStructure ser encerrado
    wait_for_updater_completion()
    
    print(" # Passo 1.1: espera adicional de 10 segundos para garantir que o diretório esteja desocupado")
    # Passo 1.1 Inserir uma espera adicional de 10 segundos  para garantir que o diretório esteja desocupado
    time.sleep(5)
    

    print(" # Passo 2: Verificar e encerrar quaisquer processos relacionados")
    # Passo 2: Verificar e encerrar quaisquer processos relacionados
    close_related_processes()
    time.sleep(5)
    terminate_processes_in_directory(install_dir)

    print(" # Passo 2.2: espera adicional de 10 segundos para garantir que o diretório esteja desocupado")
    # Passo 2.1 Inserir uma espera adicional de 10 segundos  para garantir que o diretório esteja desocupado
    time.sleep(5)
    
    print(" # Passo 2.3: remove todos os arquivos dentro do diretorio")
    # passo2.3: remove todos os arquivos dentro do diretorio 
    remove_files_in_directory(install_dir)

    print(" # Inserir uma espera adicional de 10 segundos  para garantir que o diretório esteja desocupado")
    # Passo 2.4 Inserir uma espera adicional de 10 segundos  para garantir que o diretório esteja desocupado
    time.sleep(5)

    print(" # Passo 3: Verificar se o diretório de instalação existe e apagá-lo se existir")    
    # Passo 4: Verificar se o diretório de instalação existe e encerrar processos relacionados antes de apagar
    if os.path.exists(install_dir):
        terminate_processes_in_directory(install_dir)

    # Excluir todos os arquivos no diretório
    for root, dirs, files in os.walk(install_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Erro ao excluir o arquivo {file_path}: {e}")

    # Excluir o diretório agora que os arquivos foram removidos
    try:
        os.rmdir(install_dir)
    except Exception as e:
        print(f"Erro ao excluir o diretório {install_dir}: {e}")
         
    print(" # Passo 3.1: aguardando 5 segundos para criar o diretorio de instalação")  
    # Inserir uma espera de 5 segundos (você pode ajustar o tempo conforme necessário)
    time.sleep(5)
    
    print(" # Passo 4: Criar o diretório de instalação")
    # Passo 5: Criar o diretório de instalação
    os.makedirs(install_dir, exist_ok=True)
    
    print(" # Passo 4.1: aguardando 5 segundos para baixar o conteudo do repositorio")  
    # Inserir uma espera de 5 segundos (você pode ajustar o tempo conforme necessário)
    time.sleep(5)
    
    print(" Passo 5: Baixando todo o conteúdo do repositório")
    # Passo 3: Baixar todo o conteúdo do repositório
    zip_path = download_repository()
    if zip_path is None:
        return
        
    print(" # Passo 6: Descompactar o conteúdo do arquivo ZIP no diretório temporário") 
    # Passo 6: Descompactar o conteúdo do arquivo ZIP no diretório temporário
    try:
        shutil.unpack_archive(zip_path, temp_dir_updater)
    except Exception as e:
        print(f"Erro ao descompactar o arquivo ZIP: {e}")
        return

    print(" # Passo 6.1: aguardando 5 segundos para carregar o diretorio de instalação")    
    # Inserir uma espera de 5 segundos (você pode ajustar o tempo conforme necessário)
    time.sleep(5)
    
    print(" # Passo 7: Copiar o conteúdo da pasta temporária para o diretório de instalação")  
    # Passo 7: Copiar o conteúdo da pasta temporária para o diretório de instalação
    source_dir = os.path.join(temp_dir_updater, "HRC-structure-master")
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        destination_path = os.path.join(install_dir, item)
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, destination_path)
            
    # Passo 7.1: Inserir uma espera de 5 segundos 5
    print(" # Passo 7.1: aguardando 5 segundos para atualizar o sha do commit")   
    time.sleep(5)

    print(" # Passo 8: atualizando o arquivo commit_sha") 
    # Passo 8: atualizar o arquivo commit_sha
    latest_commit_sha = get_latest_commit_sha()
    if latest_commit_sha:
        update_commit_sha(latest_commit_sha)
    
    print(" # Passo 8.1: aguardando 5 segundos para executar o programa principal") 
    # Inserir uma espera de 5 segundos (você pode ajustar o tempo conforme necessário)
    time.sleep(5)
    
    print(" # Passo 9: executar programa principal") 
    # Passo 9: Executar o main.exe
    run_main_exe(install_dir)
    
    time.sleep(5)
    # Passo 10: Encerrar o Install
    return

if __name__ == "__main__":
    main()
